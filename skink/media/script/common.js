$(function(){
    function refreshTableHeight(){
        var windowHeight = $(window).height();
        $('table.full-height').each(function(){
            var tbl = $(this);
            tbl.height(windowHeight);
        });
    }

    refreshTableHeight();

    $(window).resize(function(){
      refreshTableHeight();
    });
});
