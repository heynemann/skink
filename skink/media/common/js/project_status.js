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

                $image = $('#build_status_' + project_id);
                $row = $image.parent().parent();
                $last_build_row = $image.parent().parent().parent();
                $row.removeClass('doing-build');
                $last_build_row.removeClass('doing-build');
               
                if ($image.length>0){
                    if (project_status == 'UNKNOWN') {
                        new_image = unknown_image;
                        new_title = 'This project has never been built.';
                    }
                    if (project_status == 'BUILDING') {
                        new_image = building_image;
                        new_title = 'Currently in the process of building...';
                        $row.addClass('doing-build');
                        $last_build_row.addClass('doing-build');
                        $('#currently_building').html('currently building project ' + project_name + '. <a href="/currentbuild">[more info]</a>');
                        $('#currently_building').show()
                    }
                    if (project_status == 'BUILT') {
                        new_image = built_image;
                        new_title = 'This project has been built.';
                    }
                    

                    if ($image.attr('src').toLowerCase() != new_image.toLowerCase())
                        if (new_image == built_image){
                            location.reload(true);
                        }
                        else{
                            $image.attr('src', new_image);
                            $image.attr('title', new_title);
                            $image.attr('alt', new_title);
                        }
                }
            }
        }
    });
}
