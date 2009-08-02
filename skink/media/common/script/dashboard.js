$(function(){
    $(this).everyTime(3000, query_status);
    query_status();

    $('a.build_project').click(build_project);
});

function build_project(){
    $link = $(this);
    url = $link.attr('href');

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

