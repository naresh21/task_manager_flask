function remove_task(task_id) {
    var btn_confirm = confirm('Are you sure you want to delete this Task ?');
    if (btn_confirm) {
        window.location = "/remove_task/" + task_id
    }
}

function remove_developer(task_id) {
    var btn_confirm = confirm('Are you sure you want to delete this User ?');
    if (btn_confirm) {
        window.location = "/remove_client/" + task_id
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


    // $('#quick_date').change(function () {
    //     var str = $('#quick_date').val();
    //     var date_changed = str.replace("/", "_");
    //     str = date_changed.replace("/", "_");
    //     console.log(str);
    //
    //     $.ajax
    //     ({
    //         type: "Post",
    //         url: "/quickview/" + str,
    //         success: function (result) {
    //             // window.location.reload()
    //         }
    //     });
    // });


    $('#estimated_hours').timepicker(
        {
            showMeridian: false,
            defaultTime: '08:00',
            icons: {
                up: 'fa fa-sort-up',
                down: 'fa fa-sort-down'
            }
        }
    );

    $('#example').DataTable({
        "scrollY": 200,
        "scrollX": true
    });
    $('#tl_table').DataTable({
        "scrollY": 200,
        "scrollX": true
    });

    $('#tl_table_dashboard').DataTable({
        "scrollY": 500,
        "scrollX": true
    });
});

