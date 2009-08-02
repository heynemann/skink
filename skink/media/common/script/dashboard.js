$(function(){
    $(this).everyTime(3000, query_status);
    query_status();

    $('a.build_project').click(build_project);

    $('#more_info_dialog').dialog({
                        modal: true,
                        width: 720,
                        height:580,
                        minWidth: 500,
                        minHeight:380,
                        autoOpen: false,
                        close: function(event, ui) {
                            $(document).stopTime('current_build_status');
                            $('#more_info_current_log').html('');
                        }
                });

    $('#not_authenticated_dialog').dialog({
                modal: true,
                width: 350,
                height:170,
                resizable: false,
                autoOpen: false
        });

    $('img.img_more_info').click(show_more_info);
});

function show_more_info() {
    $img = $(this);
    project_id = parseInt($img.attr('id').replace('more_info_', ''));

    $('#more_info_dialog').dialog('open');
    $('#more_info_dialog').dialog('option', 'title', 'Retrieving Project Information');

    $(document).everyTime(1000, 'current_build_status', function(){ current_build(project_id); });
    current_build(project_id);
}

function current_build(project_id){
    $.ajax({
        type: "GET",
        url: "/currentstatus",
        dataType: "json",
        cache: false,
        success: function(data){
            command = data.command;
            log = data.log;
            project = data.project;
            current_project_id = data.project_id;

            if (current_project_id != project_id){
                $('#more_info_dialog').dialog('option', 'title', 'This project is not currently being built');
                return;
            }
            else{
                $('#more_info_dialog').dialog('option', 'title', 'Building project ' + project + '...');
            }

            if (log != null){
                $('#more_info_current_log').html(log);
            }
        }
    });
}

function build_project(){
    $link = $(this);
    url = $link.attr('href');

    if (!document.authenticated){
        $('#not_authenticated_dialog').dialog('open');
        return false;
    }

    $.ajax({
        type: "POST",
        url: url,
        dataType: "text",
        data: {},
        cache: false,
        success: function(data){
            alert('build queued!');
        }
    });

    return false;
}

function query_status(){
    $.ajax({
        type: "GET",
        url: "/buildstatus",
        dataType: "text",
        cache: false,
        success: function(data){
            data_items = data.split('\n');
            for (i=0; i < data_items.length; i++){
                item = data_items[i];

                item_data = item.split("=");
                project_id = item_data[0];

                name_and_status = item_data[1].split("@@");
                project_name = name_and_status[0];
                project_status = name_and_status[1];

                $project = $('#project_' + project_id);

                if (project_status == 'BUILDING') {
                    $project.find('div.project_built').hide()
                    $project.find('div.project_building').show()
                }
                if (project_status == 'BUILT') {
                    $project.find('div.project_built').show()
                    $project.find('div.project_building').hide()
                }
            }
        }
    });
}

