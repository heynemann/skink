$(function(){
    $('#cancel').click(function(){
        window.location='/';
        return false;
    });

    $('.rounded').corners({ 
        inColor: '#e0ffda', 
        outColor: '#e0ffda',
        borderSize: 2, 
        borderColor: '#307822'
    });
});
