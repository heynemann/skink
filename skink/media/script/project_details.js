$(function(){
    $('#delete_project').click(function(){
        return confirm('Are you sure you want to delete the project? \nThis action cannot be reverted!');
    });
    
    function fixBuildLogWidth(){
        build_log = $('#build_log');
        build_log_td = $('#build_log_td');
        
        build_log.width(build_log_td.width() - 50);
    }
    
    fixBuildLogWidth();
    
    $(window).resize(function(){
      fixBuildLogWidth();
    });
});
