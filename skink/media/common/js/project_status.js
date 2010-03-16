url = '/project/{{project_id}}';
building_image = '/media/common/images/building.gif'
built_image = '/media/common/images/accept.png'
unknown_image = '/media/common/images/error.png'

$(function(){
    $(this).everyTime(10000, query_status);
    query_status();
});

function query_status(){
    $('#currently_building').hide();
    $.ajax({
        type: "GET",
        url: "/buildstatus",
        dataType: "json",
        cache: false,
        success: function(data){
            for (var idx in data){
                project = data[idx];
                project_id = project.id;
                project_name = project.name;
                project_execution_status = project.execution_status
                project_status = project.status;

                $project_div = $('#project_' + project_id);
                
                if (project_execution_status == 'BUILDING') {
                    $project_div.removeClass(project_status);
                    $project_div.addClass('Building');
                    
                    $('#currently_building').html('Currently building project ' + project_name + '. <a href="/currentbuild">[more info]</a>');
                    $('#currently_building').show()
                }
                if (project_execution_status == 'BUILT') {
                    $project_div.addClass(project_status)
                }
            }
        }
    });
}
