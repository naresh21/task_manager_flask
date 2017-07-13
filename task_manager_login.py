# coding=utf-8
"""
Just for practicing urllib and urllib2.
When this code will be executed it will login to task manager and new task will be added.
Then current day's task details will be converted in xls downloaded at last.
"""
import cookielib
import os
import urllib
import urllib2

USERNAME = 'satyakam.pandya@drcsystems.com'
PASSWORD = 'Drc@1234'

url_task_manager_login = 'http://localhost:8080/login'
url_dev_today_task_download = 'http://localhost:8080/save_tasks'
url_task_manager_logout = 'http://localhost:8080/logout'
url_add_new_task = 'http://localhost:8080/developer'

login_info = {
    'username': USERNAME,
    'password': PASSWORD
}
new_task = {
    'project_id': "10427",
    'task_title': "Learn URLLIB",
    'milestone': "Development",
    'start_date': "13/07/2017",
    'end_date': "13/07/2017",
    'estimated_hours': "08:00",
    'qa': " ",
    'priority': "High",
    'type': "New",
    'description': "abcdefghijklmnopqrstuvwxyz"
}


def download_file(url):
    """
    Downloads file from given url
    """
    try:
        download = opener.open(url)
        print "downloading..."
        # Open our local file for writing
        with open(os.path.basename('download.xls'), "wb") as local_file:
            local_file.write(download.read())

    # handle errors
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code
    except urllib2.URLError, e:
        print "URL Error:", e.reason


cookies = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

# Login to Task Manager using login_info
login = opener.open(url_task_manager_login, urllib.urlencode(login_info))

# Adding new task for logged in user
add_new_task = opener.open(url_add_new_task, urllib.urlencode(new_task))

# Downloading xls for current day
download_file(url_dev_today_task_download)

# Logout from the system
logout = opener.open(url_task_manager_logout)
