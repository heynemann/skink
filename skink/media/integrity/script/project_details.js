$(function(){
    $('#delete_project').click(function(){
        return confirm('Are you sure you want to delete this project?\nAll the pipelines this project participates will also be deleted.\nThis action cannot be undone.');
    });
    
    $("#current-build-tabs").tabs();
});
