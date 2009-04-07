$(function(){
    $('#delete_project').click(function(){
        return confirm('Are you sure you want to delete the project? \nThis action cannot be reverted!');
    });
});
