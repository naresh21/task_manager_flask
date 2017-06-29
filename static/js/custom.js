function remove_task(task_id) {
    var btn_confirm = confirm('Are you sure you want to delete this Task ?');
    if (btn_confirm) {
        // window.location = "/remove_task/" + task_id
        $.ajax({
            url: '/remove_task/' + task_id,
            type: 'POST',
            success: function () {
                window.location.reload()
            }
        });
    }
}

function remove_developer(username) {
    var btn_confirm = confirm('Are you sure you want to delete this User ?');
    if (btn_confirm) {
        window.location = "/remove_developer/" + username
    }
}


$(document).ready(function () {

    $('.input-daterange').datepicker({
        format: 'dd/mm/yyyy',
        autoclose: true
    });

    $('#quick_date').datepicker({
        format: 'dd/mm/yyyy',
        autoclose: true
    });

    $('#all_tasks_date').datepicker({
        format: 'dd/mm/yyyy',
        autoclose: true
    });


    $('#quick_date').change(function () {
        document.getElementById('quickview').submit();
    });


    $('.estimated_hours').timepicker(
        {
            showMeridian: false,
            defaultTime: '08:00',
            icons: {
                up: 'fa fa-sort-up',
                down: 'fa fa-sort-down'
            }
        }
    );

    $('#search_date').datepicker({
        format: 'dd/mm/yyyy',
        autoclose: true
    });
    $('#search_date').change(function () {
        var date = $('#search_date').datepicker('getDate');
        alert("hi");
        document.getElementById('search_query_form').submit();
    });

    $('#custom_data_table').DataTable({
        "scrollY": 500,
        "scrollX": true,
        "searching": false,
        "bPaginate": false, // to disable pagination of datatables
        "info": false  // for hiding showing entries text
        // "order": [[ 1, "desc" ]] for custom default sorting
        // "lengthMenu": [[10, 20, 30], [10, 20, 30]], // define show entries
    });
});

