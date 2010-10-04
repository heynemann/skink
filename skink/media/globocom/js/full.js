theQueue = $({});

loadProjects();



function loadProjects(){
    $.ajax({
      url: '/buildstatus',
      dataType: 'json',
      cache: false,
      success: function(data) {
          $.map(data, function(data) {
              theQueue.queue('projects', function(next) {
                  changeProject(data.name, data.status, data.author, data.gravatar, data.commit_text);
              });
          });
          theQueue.queue('projects', loadProjects);
          theQueue.dequeue('projects');
          
      },
    });
}


function changeProject(name, status, author, gravatar, commit_text) {
    $("#projectname").animate({width:'0', opacity: 0.8},500);
    $("#projectname").queue(function () {
        $(this).html(name);

        $("#log").html(commit_text);
        $("#gravatar").attr("src",gravatar +"?s=120");
        $("#author").html(author);

        if (status == 'Successful'){
            $("body").animate({ backgroundColor:'#669900'},1000);
        } else if (status == 'Failed'){
            $("body").animate({ backgroundColor:'#CC3300'},1000);
        } else {
            $("body").animate({ backgroundColor:'#000000'},1000);
        }

        $(this).dequeue();
    });
      
    $("#projectname").animate({width:'80%', opacity: 1},500);

    if (status == 'Successful'){
        $("#projectname").animate({width:'-=0'},2000);
    } else {
        $("#projectname").animate({width:'-=0'},2000);
    }
    
    $("#projectname").queue(function () {
        $(this).dequeue();
        theQueue.dequeue('projects');
    });
    

}