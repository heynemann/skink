$(function(){
    $("#delete-project").click(function(){
          if (confirm('Are you sure you want to delete the project? \nThis action cannot be reverted!')) {
            location.href = $(this).attr("rel");
          }
    });
    $("#build-project").click(function(){
          location.href = $(this).attr("rel");
    });

});
