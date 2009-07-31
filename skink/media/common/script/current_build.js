url = '/project/{{project_id}}';
building_image = '/media/common/images/building.gif'
built_image = '/media/common/images/accept.png'
unknown_image = '/media/common/images/error.png'

$(function(){
    document.has_shown_already = false;
    $(this).everyTime(1000, current_build);
    current_build();
});

function current_build(){
    $.ajax({
        type: "GET",
        url: "/currentstatus",
        dataType: "json",
        cache: false,
        success: function(data){
            command = data.command;
            log = data.log;
            project = data.project;
            project_id = data.project_id;

            if (command == null){
                if (!document.has_shown_already){
                    $('#no_current_builds').show();
                    $('#current_command').hide();
                    $('#current_log').hide();
                    $('#current_project').hide()
                }
                else{
                    if (!document.command_finished){
                        $('#current_command').html($('#current_command').html() + '<br /><br /><b style="text-align:center">FINISHED</b><br /><br />');
                        document.command_finished = true;
                    }
                }
            }
            else{
                document.command_finished = false;
                document.has_shown_already = true;
                $('#no_current_builds').hide();
                $('#current_command').show();
                $('#current_project').show()
                $('#current_log').show();
                $('#current_project').html('<b>Project</b>: <a href="/project/' + project_id + '">' + project + '</a>');
                $('#current_command').html('<b>Command</b>:<br />' + command +'<br /><br />Please note that these are the last 20 lines of the command log.');
                $('#current_log').html('<pre class="output">' + log + '</pre>');
            }
        }
    });
}
