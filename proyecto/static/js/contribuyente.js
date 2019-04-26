function mostrarSociedad(valor){
    if(valor){
        $('#div_id_tipo_sociedad').show()
    }else{
        $('#div_id_tipo_sociedad').hide();
    }
}

function tipoPersonaCheck (elem){
    var valor = false;
    if (elem.val()=='JURIDICA'){
        valor = true
    }
    mostrarSociedad(valor)

}
$(document).ready(function() {

    tipoPersonaCheck($('#id_tipo_persona'));

    $('#id_tipo_persona').change(function () {
        tipoPersonaCheck($(this));
    });

});