$(function(){
    $('#doLogin').click(function(){
        user = $('#login').val();
        pass = $('#password').val();

        if (!user || !pass || user == 'nome de usuário'){
            $('#login').addClass('invalid');
            $('#password').addClass('invalid');
            return false;
        }
    });
});
