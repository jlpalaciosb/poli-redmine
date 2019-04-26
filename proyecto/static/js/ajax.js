$(document).ready(function() {
    var elem_tipo_identificacion = $('#id_tipo_identificacion');
    var elem_numero_identificacion = $('#id_numero_identificacion');
    var nombres_o_razon_social = $('#id_nombres_o_razon_social');

    $(elem_tipo_identificacion).focusout(function () {
        if(camposCompletos()){
            getDatosPartner($(elem_tipo_identificacion).val(), $(elem_numero_identificacion).val());
        }
    });

    $(elem_numero_identificacion).focusout(function () {
        if(camposCompletos()){
            getDatosPartner($(elem_tipo_identificacion).val(), $(elem_numero_identificacion).val());
        }
    });

    function camposCompletos() {
        // Chequeamos si ambos campos están completos
        var valor_tipo_identificacion = $(elem_tipo_identificacion).val();
        var valor_numero_identificacion = $(elem_numero_identificacion).val();

        if (valor_tipo_identificacion !== "" && valor_numero_identificacion !== "") {
            return true;
        }
        return false;

    }

    function getDatosPartner(tipo_identificacion, numero_identificacion) {
        // Se trae por ajax el valor del nombre o razon social del Partner
        $.ajax({
            url: '/contribuyentes/partner/informacion-partner/',
            data: {
                'tipo_identificacion': tipo_identificacion,
                'numero_identificacion': numero_identificacion
            },
            dataType: 'json',
            type: 'get',
            success: function (data) {
                if(data){
                    $(nombres_o_razon_social).val(data.nombres);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Error, no se pudo realizar la consulta de los datos del partner");
            }

        })
    }

    $('#id_ruc').keyup(function () {
        var ruc = $(this).val();
        if(ruc != ""){
            calcularDV(ruc);
        }
    });

    function calcularDV(ruc) {
        $.ajax({
            url: '/contribuyentes/calcular_dv/',
            data: {
                'ruc': ruc,
            },
            dataType:'json',
            type: 'get',
            success: function (data) {
                if (data) {
                    $('#id_dv').val(data.dv)
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus);
                $('#id_dv').val(0);
            }
        })

    }

});