$(function(){
    $('#lnkAddTab').click(function(){
        $div = $('#additional_tabs');
        newItem = $('#additional_tab_template').clone()
        $div.append(newItem);
        newItem.show()
    });
});
