$(function(){
    function refreshTableHeight(){
        var windowHeight = $(window).height() - 15;
        $('table.full-height').each(function(){
            var tbl = $(this);
            if (tbl.height() < windowHeight)
                tbl.height(windowHeight);
        });
    }

    refreshTableHeight();

    $(window).resize(function(){
      refreshTableHeight();
    });
});
