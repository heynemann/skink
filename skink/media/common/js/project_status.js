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
                project_execution_status = project.execution_status;
                project_status = project.status;
                author_photo = project.gravatar;
                author_name = project.author;
                author_email = project.email;
                commit_text = project.commit_text;

                $project_div = $('#project_' + project_id);

                if (project_status == 'UNKNOWN') {
                    $project_div.find(".photo_project").html("<img src=\"/media/globocom/img/skink52x52.jpg\"/>");
                    $project_div.find(".email").html("<p>Skink ci <br /><span>&nbsp;</span></p>");
                    $project_div.find(".comments").html("Project " + project_name + ". <br \> No builds happened so far.");
                } else { 
                    $project_div.find(".photo_project").html("<img src=\""+author_photo+"?s=52\"/>");
                    $project_div.find(".email").html("<p>" + author_name + "<br /><span>"  + author_email + "</span></p>");
                    $project_div.find(".comments").html(commit_text);
                }
                
                if (project_execution_status == 'BUILDING') {
                    $project_div.removeClass(project_status);
                    $project_div.addClass('Building');
                    $('#currently_building').html('Currently building project ' + project_name + '. <a href="/currentbuild">[more info]</a>');
                    $('#currently_building').show()
                }
                
                if (project_execution_status == 'BUILT') {
                    $project_div.removeClass('Building')
                    $project_div.addClass(project_status)
                    
                }
            }
        }
    });
}
