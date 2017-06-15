# coding=utf-8
"""
This application is used to manage employees's task submissions
Task Manager for DRC Systems
Developed by: Satyakam Pandya, Dharm Shah
"""
import calendar
import glob
import os
import zipfile
from datetime import datetime, timedelta

import xlwt
from flask import Flask, redirect, url_for, flash, render_template, request, send_file, after_this_request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from configs import get_secret_key, get_sql_path, db, User, LoginForm, Details, RegisterForm, ChangePasswordForm

app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = get_sql_path()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target_save_path = os.path.join(APP_ROOT, 'xls_data/')

ERP_BASE_URL = "http://erp.drcsystems.com/pms/projects/details/"


@login_manager.user_loader
def load_user(user_id):
    """
    For getting current_user
    """
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """
    When 192.168.1.20 is loaded, user will be redirected to login page
      returns url for login page
    """
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    When 192.168.1.20 is called login page will be loaded
        case 1: it redirects to admin/developer page if already logged in
        case 2: it redirects to admin/developer page if username and password is correct
        case 3: it redirects to login page again if username and password is incorrect
        case 4: it redirects to login page when GET method is called
    """
    if current_user.get_id():
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user:
            return redirect(url_for(user.role))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for(user.role))
            else:
                flash("Invalid username/password")
                return render_template('login.html', form=form)
        flash("Invalid username/password")
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    """
    It is called when admin is logged in into account
        case 1: if admin tries to load this page, then redirects to admin page with developers regarding information
        case 2: if developer tries to load this page, then he/she is redirected to developer page
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        all_users = User.query.filter_by(role="developer")
        all_details = Details.query.all()

        return render_template('all_developer.html', user=user, developers=all_users, all_details=all_details)
    else:
        return redirect(url_for('developer'))


def get_perfect_time(estimated_hours):
    """
    Used for getting perfect time as per required format
    """
    hour = estimated_hours.split(":")[0]
    numbers = sum(c.isdigit() for c in hour)
    if numbers == 1:
        hour = "0" + hour
    return hour + ":" + estimated_hours.split(":")[1] + ":00"


@app.route('/developer', methods=['GET', 'POST'])
@login_required
def developer():
    """
    It is called when developer is logged in into account
        case 1: if developer is logged in then he/she is redirected to developer page with info
        case 2: if admin tried to load this page admin is redirected to admin page
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'developer':
        if request.method == "POST":
            project_id = request.form['project_id']
            task_title = request.form['task_title']
            milestone = request.form['milestone']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            estimated_hours = request.form['estimated_hours']
            qa = request.form['qa']
            priority = request.form['priority']
            _type = request.form['type']
            description = request.form['description']

            try:
                new_task_entry = Details(project_id=project_id,
                                         task_title=task_title,
                                         milestone=milestone,
                                         start_date=start_date,
                                         end_date=end_date,
                                         estimated_hours=get_perfect_time(estimated_hours),
                                         qa=qa,
                                         developer=user.username,
                                         priority=priority,
                                         type=_type,
                                         description=description,
                                         added_on=datetime.now().strftime("%d/%m/%Y"))
                user.latest_task = datetime.now().strftime("%d/%m/%Y")
                db.session.add(new_task_entry)
                db.session.commit()
            except Exception as e:
                print e
        else:
            formatted_date = get_next_date()
            is_task = Details.query.filter_by(developer=user.username,
                                              added_on=datetime.now().strftime("%d/%m/%Y")).first()
            if is_task:
                today_task_details = Details.query.filter_by(developer=user.username,
                                                             added_on=datetime.now().strftime("%d/%m/%Y"))
                return render_template("add_new_task.html", user=user, any_tasks=True, today=today_task_details,
                                       formatted_date=formatted_date)
            else:
                return render_template("add_new_task.html", user=user, any_tasks=False, formatted_date=formatted_date)
    return redirect(url_for('admin'))


@app.route('/quickview', methods=['GET', 'POST'])
@login_required
def quickview():
    """
    It is called by admin to have a quickview of task details
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        if request.method == "GET":
            date = datetime.now().strftime("%d/%m/%Y")
        else:
            date = request.form['quick_date']
        all_users = User.query.filter_by(role="developer").all()
        present = []
        absent = []
        for users in all_users:
            last_id = Details.query.filter_by(developer=users.username, added_on=date).first()
            if last_id:
                present.append(users.username)
            else:
                absent.append(users.username)
        return render_template('quickview.html', user=user, all_users=all_users,
                               present=present, absent=absent, date=date)

    return redirect(url_for('developer'))


def get_next_date():
    """
    It returns next working date
    """
    today_date = datetime.now()  # converting str to datetime obj
    weekday = calendar.day_name[today_date.weekday()]  # getting day of selected start_date

    if weekday == 'Friday':  # if its friday then add 3 days
        modified_date1 = today_date + timedelta(days=3)
    else:
        modified_date1 = today_date + timedelta(days=1)  # else add a day

    formatted_date = datetime.strftime(modified_date1, "%d/%m/%Y")  # yyyy-mm-dd to dd/mm/yyyy
    return formatted_date


@app.route('/save_tasks', methods=['GET', 'POST'])
@login_required
def save_tasks():
    """
    Developers uses this for adding their daily tasks
    """

    @after_this_request
    def delete(response):
        """
        Removes xls and zip file after download
        """
        try:
            os.chdir(target_save_path)
            xls_files = glob.glob('*.xls')
            for xls in xls_files:
                os.unlink(xls)

            os.chdir(APP_ROOT)
            xls_files = glob.glob('*.zip')
            for xls in xls_files:
                os.unlink(xls)
        except Exception as e:
            print e
        return response

    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'developer':
        task_details = Details.query.filter_by(developer=user.username,
                                               added_on=datetime.now().strftime("%d/%m/%Y")).first()
        if task_details:
            if request.method == "GET":
                generated_file = download_xls_data(user, datetime.now().strftime("%d/%m/%Y"))
                return send_file(generated_file,
                                 as_attachment=True,
                                 attachment_filename=generated_file.split("/")[-1])
        else:
            flash("No Tasks")
        return redirect(url_for('developer'))
    return redirect(url_for('admin'))


@app.route('/download/<username>/<date>', methods=['GET', 'POST'])
@login_required
def download(username, date):
    """
    Used to download specific user's xls file on specific date
    """

    @after_this_request
    def delete(response):
        """
        Removes xls and zip file after download
        """
        try:
            os.chdir(target_save_path)
            xls_files = glob.glob('*.xls')
            for xls in xls_files:
                os.unlink(xls)
            os.chdir(APP_ROOT)
            xls_files = glob.glob('*.zip')
            for xls in xls_files:
                os.unlink(xls)
        except Exception as e:
            print e
        return response

    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        current = User.query.filter_by(username=username).first()
        if request.method == "POST":
            date = request.form['all_tasks_date']
            all_tasks_of = Details.query.filter_by(developer=current.username)
            for task in all_tasks_of:
                if date in task.added_on:
                    generated_file = download_xls_data(current, date.replace("_", "/"))
                    return send_file(generated_file,
                                     as_attachment=True,
                                     attachment_filename=generated_file.split("/")[-1])

            flash("NoData")
            return redirect('/all_tasks/' + all_tasks_of[0].developer)

        generated_file = download_xls_data(current, date.replace("_", "/"))

    else:
        if request.method == "POST":
            date = request.form['all_tasks_date']
            all_tasks_of = Details.query.filter_by(developer=user.username)
            for task in all_tasks_of:
                if date in task.added_on:
                    generated_file = download_xls_data(user, date.replace("_", "/"))
                    return send_file(generated_file,
                                     as_attachment=True,
                                     attachment_filename=generated_file.split("/")[-1])

            flash("NoData")
            return redirect('/all_tasks/' + all_tasks_of[0].developer)

        generated_file = download_xls_data(user, date.replace("_", "/"))

    return send_file(generated_file,
                     as_attachment=True,
                     attachment_filename=generated_file.split("/")[-1])


def gather_project_titles(date, username):
    """
    It gathers unique project titles for given date and username
    """
    if username == "all":
        task_details = Details.query.filter_by(added_on=date)
    else:
        task_details = Details.query.filter_by(developer=username,
                                               added_on=date)
    all_titles = []
    for task in task_details:
        all_titles.append(str(task.project_id))
    my_titles = sorted(set(all_titles))
    return my_titles


def download_xls_data(user, date):
    """
    Generates XLS file for given user and date
    """
    projects = gather_project_titles(date, user.username)
    for project_id in projects:
        row = 1
        try:
            task_details = Details.query.filter_by(developer=user.username, project_id=project_id,
                                                   added_on=date)
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Sheet1')
            set_headers(ws)
            for task in task_details:
                fill_xls(ws, row,
                         task.task_title,
                         task.milestone,
                         task.start_date,
                         task.end_date,
                         task.estimated_hours,
                         task.qa,
                         task.developer,
                         task.priority,
                         task.type,
                         task.description)
                row = row + 1

            if not os.path.exists(target_save_path):
                os.makedirs(target_save_path)

            path = target_save_path + get_username(user.username) + "_" + date.replace("/",
                                                                                       "_") + "_" + project_id + '.xls'
            wb.save(path)
        except Exception as e:
            flash("Something Went Wrong")
            print e
    if len(projects) == 1:
        xls_filename = target_save_path + get_username(user.username) + "_" + date.replace("/", "_") + "_" + \
                       list(projects)[0] + '.xls'
        return xls_filename
    else:
        zf = zipfile.ZipFile(get_username(user.username) + "_" + date.replace("/", "_") + '.zip', "w")
        for dirname, subdirs, files in os.walk("xls_data"):
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        zip_filename = APP_ROOT + "/" + zf.filename
        return zip_filename


def gather_developers(date, project_id):
    """
    Ii gathers developer names for given date and project_id
    """
    developers_details = Details.query.filter_by(project_id=project_id, added_on=date)
    all_devs = []
    for dev in developers_details:
        all_devs.append(str(dev.developer))
    devs = sorted(set(all_devs))
    return devs


@app.route('/download_project/<date>', methods=['GET', 'POST'])
@login_required
def download_project(date):
    """
    Downloads project-wise of given date
    """

    @after_this_request
    def delete(response):
        """
        Removes xls and zip file after download
        """
        try:
            os.chdir(target_save_path)
            xls_files = glob.glob('*.xls')
            for xls in xls_files:
                os.unlink(xls)
            os.chdir(APP_ROOT)
            xls_files = glob.glob('*.zip')
            for xls in xls_files:
                os.unlink(xls)
        except Exception as e:
            print e
        return response

    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        generated_file = download_project_wise(date.replace("_", "/"))
        return send_file(generated_file,
                         as_attachment=True,
                         attachment_filename=generated_file.split("/")[-1])
    else:
        return redirect(url_for('developer'))


def download_project_wise(date):
    """
    Downloads xls data project-wise for given date
    """
    projects = gather_project_titles(date, "all")
    for project_id in projects:
        dev_on_this_project = gather_developers(date, project_id)
        row = 1
        try:
            wb = xlwt.Workbook()
            ws = wb.add_sheet('Sheet1')
            set_headers(ws)
            for dev in dev_on_this_project:
                # print project_id
                # print dev
                task_details = Details.query.filter_by(developer=dev, project_id=project_id,
                                                       added_on=date)
                for task in task_details:
                    fill_xls(ws, row,
                             task.task_title,
                             task.milestone,
                             task.start_date,
                             task.end_date,
                             task.estimated_hours,
                             task.qa,
                             task.developer,
                             task.priority,
                             task.type,
                             task.description)
                    row = row + 1

            if not os.path.exists(target_save_path):
                os.makedirs(target_save_path)

            path = target_save_path + project_id + "_" + date.replace("/", "_") + '.xls'
            wb.save(path)
        except Exception as e:
            flash("Something Went Wrong")
            print e
    if len(projects) == 1:
        xls_filename = target_save_path + list(projects)[0] + "_" + date.replace("/", "_") + '.xls'
        return xls_filename
    else:
        zf = zipfile.ZipFile("Tasks_Project_Wise_" + date.replace("/", "_") + '.zip', "w")
        for dirname, subdirs, files in os.walk("xls_data"):
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        zip_filename = APP_ROOT + "/" + zf.filename
        return zip_filename


@app.route('/download_all/<date>', methods=['GET', 'POST'])
@login_required
def download_all(date):
    """
    Downloads all developer's data on given date
    """

    @after_this_request
    def delete(response):
        """
        Removes xls and zip file after download
        """
        try:
            os.chdir(target_save_path)
            xls_files = glob.glob('*.xls')
            for xls in xls_files:
                os.unlink(xls)
            os.chdir(APP_ROOT)
            xls_files = glob.glob('*.zip')
            for xls in xls_files:
                os.unlink(xls)
        except Exception as e:
            print e
        return response

    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        generated_file = download_xls_all(date.replace("_", "/"))
        return send_file(generated_file,
                         as_attachment=True,
                         attachment_filename=generated_file.split("/")[-1])
    else:
        return redirect(url_for('developer'))


def download_xls_all(date):
    """
    Downloads all developer's data on given date
    """
    users = Details.query.filter_by(added_on=date)
    all_devs = []
    for dev in users:
        all_devs.append(str(dev.developer))
    devs = sorted(set(all_devs))

    for dev in devs:
        projects = gather_project_titles(date, dev)
        for project_id in projects:
            row = 1
            try:
                task_details = Details.query.filter_by(developer=dev, added_on=date, project_id=project_id)
                wb = xlwt.Workbook()
                ws = wb.add_sheet('Sheet1')
                set_headers(ws)
                for task in task_details:
                    fill_xls(ws, row,
                             task.task_title,
                             task.milestone,
                             task.start_date,
                             task.end_date,
                             task.estimated_hours,
                             task.qa,
                             task.developer,
                             task.priority,
                             task.type,
                             task.description)
                    row = row + 1

                if not os.path.exists(target_save_path):
                    os.makedirs(target_save_path)

                path = target_save_path + dev + "_" + date.replace("/", "_") + "_" + project_id + '.xls'
                wb.save(path)
            except Exception as e:
                flash("Something Went Wrong")
                print e
        if len(projects) != 1:
            zf = zipfile.ZipFile("All_Task" + date.replace("/", "_") + '.zip', "w")
            for dirname, subdirs, files in os.walk("xls_data"):
                for filename in files:
                    zf.write(os.path.join(dirname, filename))
            zf.close()

    if len(devs) == 1:
        xls_filename = target_save_path + list(devs)[0] + "_" + date.replace("/", "_") + "_" + project_id + '.xls'
        return xls_filename
    else:
        zf = zipfile.ZipFile("All_Task" + date.replace("/", "_") + '.zip', "w")
        for dirname, subdirs, files in os.walk("xls_data"):
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        zip_filename = APP_ROOT + "/" + zf.filename
        return zip_filename


def get_username(username):
    """
    Removes Extra spaces
    """
    return username.replace(" ", "_")


def set_headers(ws):
    """
    Sets headers in XLS file
    """
    style = xlwt.easyxf('font: bold on; pattern: pattern solid, fore_colour blue')
    ws.write(0, 0, "Task_Title", style)
    ws.write(0, 1, "Milestone", style)
    ws.write(0, 2, "Start_Date (DD/MM/YYYY)", style)
    ws.write(0, 3, "End_Date (DD/MM/YYYY)", style)
    ws.write(0, 4, "Estimated_Hours (HH:MM:SS)", style)
    ws.write(0, 5, "QA", style)
    ws.write(0, 6, "Developer", style)
    ws.write(0, 7, "Priority", style)
    ws.write(0, 8, "Type", style)
    ws.write(0, 9, "Description", style)


def fill_xls(ws, row, task_title, milestone, start_date, end_date, estimated_hours, qa,
             _developer, priority, _type, description):
    """
    For filling up XLS file
    """
    ws.write(row, 0, task_title)
    ws.write(row, 1, milestone)
    ws.write(row, 2, start_date)
    ws.write(row, 3, end_date)
    ws.write(row, 4, estimated_hours)
    ws.write(row, 5, qa)
    ws.write(row, 6, _developer)
    ws.write(row, 7, priority)
    ws.write(row, 8, _type)
    ws.col(9).width = len(description) * 256
    ws.write(row, 9, description.replace("\r\n", "").strip())


def update_database(task_id):
    """
    Updates database when task is to be deleted and returns username
    """
    task_to_delete = Details.query.filter_by(id=task_id).first()
    u = task_to_delete.developer
    Details.query.filter_by(id=task_id).delete()
    latest_task = Details.query.filter_by(developer=u).first()
    update_latest_task = User.query.filter_by(username=u).first()
    if latest_task:
        latest_task = Details.query.filter_by(developer=u).all()
        update_latest_task.latest_task = latest_task[-1].added_on
    else:
        update_latest_task.latest_task = "no"
    db.session.commit()
    return u


@app.route('/remove_task/<task_id>', methods=['GET', 'POST'])
@login_required
def remove_task(task_id):
    """
    It is used to remove specific tasks
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'developer':
        try:
            u = update_database(task_id)
            db.session.commit()
            flash("Deleted_task")
            return redirect(url_for('developer'))
        except Exception as e:
            print e
            db.session.rollback()
            flash("Something Went Wrong")
            os.abort(404)
    else:
        try:
            u = update_database(task_id)
            db.session.commit()
            flash("Deleted_task")
            return redirect('/all_tasks/' + u)
        except Exception as e:
            print e
            db.session.rollback()
            flash("Something Went Wrong")

    return redirect(url_for(user.role))


@app.route('/update_task/<task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    """
    It is used to update tasks
    """
    user = User.query.filter_by(id=current_user.get_id()).first()

    if request.method == "POST":
        project_id = request.form['project_id']
        task_title = request.form['task_title']
        milestone = request.form['milestone']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        estimated_hours = request.form['estimated_hours']
        qa = request.form['qa']
        priority = request.form['priority']
        _type = request.form['type']
        description = request.form['description']
        try:
            update_this_task = Details.query.filter_by(id=task_id).first()
            update_this_task.project_id = project_id
            update_this_task.task_title = task_title
            update_this_task.milestone = milestone
            update_this_task.start_date = start_date
            update_this_task.end_date = end_date
            update_this_task.estimated_hours = get_perfect_time(estimated_hours)
            update_this_task.qa = qa
            update_this_task.priority = priority
            update_this_task.type = _type
            update_this_task.description = description
            db.session.commit()
            if user.role == "developer":
                return redirect(url_for(request.args.get('next')))
            else:
                return redirect(request.args.get('next'))
        except Exception as e:
            print e

    return redirect(url_for(user.role))


@app.route('/all_tasks', methods=['GET', 'POST'])
@app.route('/all_tasks/<username>', methods=['GET', 'POST'])
@login_required
def all_tasks(username=""):
    """
    It is used to see all_tasks
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        if request.method == "GET":
            current = User.query.filter_by(username=username).first()
            is_there_details = Details.query.filter_by(developer=current.username).first()
            if is_there_details:
                all_tasks_of = Details.query.filter_by(developer=current.username)

                return render_template('all_tasks_of.html', user=user, developer=current,
                                       all_tasks=all_tasks_of)
            return render_template('all_tasks_of.html', user=user, developer=current)
    else:
        if request.method == "GET":
            current = User.query.filter_by(username=user.username).first()
            is_there_details = Details.query.filter_by(developer=current.username).first()
            if is_there_details:
                all_tasks_of = Details.query.filter_by(developer=current.username)

                return render_template('all_tasks_of.html', user=user, developer=current,
                                       all_tasks=all_tasks_of)
            return render_template('all_tasks_of.html', user=user, developer=current)


@app.route('/add_new_user', methods=['GET', 'POST'])
@login_required
def add_new_user():
    """
    It is called by admin to add new developer
        case 1: if new developer is added successfully then admin is redirected to admin page with Successfully created
        msg
        case 2: if GET method is called then add developer page is rendered with register form
        case 3: if developer tries to load this page developer is redirected to developer page
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data,
                            email=form.email.data,
                            password=hashed_password,
                            role=form.role.data,
                            latest_task="no")
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Added")
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                print e
                flash("Username/Email already Exists")
                return render_template('add_new_user.html',
                                       form=form,
                                       user=user)

        return render_template('add_new_user.html', form=form, user=user)
    return redirect(url_for('developer'))


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    It is used to change password
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    form = ChangePasswordForm()
    if form.validate_on_submit():

        if check_password_hash(user.password, form.current_password.data):
            if form.new_password.data == form.confirm_password.data \
                    and form.new_password.data != form.current_password.data:
                hashed_password = generate_password_hash(form.new_password.data, method='sha256')
                user.password = hashed_password
                db.session.commit()
                flash("Success")
                return redirect(url_for(user.role))
            else:
                flash("Both password should be same and differ from current password")
                if user.role == "developer":
                    return render_template("change_password.html",
                                           user=user,
                                           form=form)
        else:
            flash("Please enter old password correctly")
            return render_template("change_password.html",
                                   user=user,
                                   form=form)
    return render_template("change_password.html", form=form, user=user)


@app.route('/remove_developer/<username>', methods=['GET', 'POST'])
@login_required
def remove_developer(username):
    """
    It is used to remove developers
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role == 'admin':
        try:
            User.query.filter_by(username=username).delete()
            Details.query.filter_by(developer=username).delete()
            db.session.commit()
            flash("Deleted")
            return redirect(url_for('admin'))

        except Exception as e:
            print e
            os.abort(404)

    return redirect(url_for('developer'))


@app.route('/logout')
@login_required
def logout():
    """
    It logs out current user and redirects user to login page
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    user.logged_in = 0
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    """
    This method will be called when something goes wrong
    """
    return render_template('error.html', error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
