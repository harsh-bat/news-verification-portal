  function toggleResetPswd(e){
    e.preventDefault();
    $('#logreg-forms .form-signin').toggle() // display:block or none
    $('#logreg-forms .form-reset').toggle() // display:block or none
}

function toggleSignUp(e){
    e.preventDefault();
    $('#logreg-forms .form-signin').toggle(); // display:block or none
    $('#logreg-forms .form-signup').toggle(); // display:block or none
}

$(()=>{
    $('#logreg-forms #forgot_pswd').click(toggleResetPswd);
    $('#logreg-forms #cancel_reset').click(toggleResetPswd);
    $('#logreg-forms #btn-signup').click(toggleSignUp);
    $('#logreg-forms #cancel_signup').click(toggleSignUp);
})


$('#signup_type').change(function(){
    var selected = $(this).children("option:selected").val();
    if(selected=="JJJ"){
        $("#signup_idproof").attr("required", "true");
    }
    else if(selected=="AAA"){
        $("#signup_idproof").attr("required", "true"); 
    }
    else{
        $("#signup_idproof").attr("required", false); 
    }
});
