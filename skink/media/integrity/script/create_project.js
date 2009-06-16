$(function(){
    $('#lnkAddTab').click(function(){
        $div = $('#additional_tabs');
        newItem = $('#additional_tab_template').clone()
        $div.append(newItem);
        newItem.show()
    });
    $('#lnkAddFileLocator').click(function(){
        $div = $('#additional_file_locators');
        newItem = $('#additional_file_locator_template').clone()
        $div.append(newItem);
        newItem.show()
    });
});
