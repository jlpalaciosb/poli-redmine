$(document).ready(function () {
    $('.auto').autoNumeric('init', {mDec: 0});

    // Al guardar removemos los separadores de miles
    $('#submit-id-guardar').click(guardar);
    function guardar(){
        $('.auto').each(function () {
            $(this).val($(this).autoNumeric('get'));
        });
    }
});