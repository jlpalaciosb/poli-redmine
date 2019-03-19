$(document).ready(function() {

    $('.auto').autoNumeric('init', {mDec: 0});

    // Al guardar removemos los separadores de miles
    $('#submit-id-guardar').click(guardar);
    function guardar(){
        $('.auto').each(function () {
            $(this).val($(this).autoNumeric('get'));
        });
    }

    var input_operacion = $('#id_operacion');
    var input_tipo_documento = $('#id_tipo_documento_ingreso');

    var input_tipo_renta_por_venta = $('#id_tipo_renta_por_venta');
    var checkbox_bien_ganancial = $('#id_bien_ganancial');

    var input_total_iva_10 = $('#id_total_iva_10');
    var input_gravada_iva_10 = $('#id_gravada_iva_10');
    var input_iva_10 = $('#id_iva_10');
    var input_total_iva_5 = $('#id_total_iva_5');
    var input_gravada_iva_5 = $('#id_gravada_iva_5');
    var input_iva_5 = $('#id_iva_5');
    var input_exentas = $('#id_exentas');
    var input_total_factura = $('#id_total_factura');
    var input_total_cobrado = $('#id_total_cobrado');
    var input_valor_venta = $('#id_valor_venta');
    var input_valor_compra = $('#id_valor_compra');
    var input_renta_neta_real = $('#id_renta_neta_real');
    var input_renta_neta_presunta = $('#id_renta_neta_presunta');
    var input_ingreso_gravado = $('#id_ingreso_gravado');
    var input_ingreso_no_gravado = $('#id_ingreso_no_gravado');
    var input_ingreso_total = $('#id_ingreso_total');
    var input_condicion_venta = $('#id_condicion_venta');

    tipo_documento = $(input_tipo_documento).val();
    operacion = $(input_operacion).val();
    condicion_venta = $(input_condicion_venta).val();
    cobrado = $(input_total_cobrado).val();
    tipo_renta_por_venta = input_tipo_renta_por_venta.val();
    bien_ganancial = checkbox_bien_ganancial.prop("checked");
    valor_compra = input_valor_compra.val();

    grava = true;
    grava_porcentaje = 100;

    // Al editar el ingreso
    editarIngreso();

    // Calculos IVA 10%
    $(input_total_iva_10).on("change paste keyup", function () {
        calcularGravada10();
        calcularIva10();
    });

    function calcularGravada10() {
        var gravada_iva_10 = Math.round($(input_total_iva_10).autoNumeric('get')/1.1);
        $(input_gravada_iva_10).autoNumeric('set', gravada_iva_10);
    }

    function calcularIva10() {
        var iva_10 = Math.round($(input_gravada_iva_10).autoNumeric('get')*0.1);
        $(input_iva_10).autoNumeric('set', iva_10);
    }

    // Calculos IVA 5%
    $(input_total_iva_5).on("change paste keyup", function () {
        calcularGravada5();
        calcularIva5();
    });

    function calcularGravada5() {
        var gravada_iva_5 = Math.round($(input_total_iva_5).autoNumeric('get')/1.05);
        $(input_gravada_iva_5).autoNumeric('set', gravada_iva_5);
    }

    function calcularIva5() {
        var iva_5 = Math.round($(input_gravada_iva_5).autoNumeric('get')*0.05);
        $(input_iva_5).autoNumeric('set', iva_5);
    }

    // Calculos Total Factura
    $([input_total_iva_10.selector, input_total_iva_5.selector, input_exentas.selector].join(", ")).on("change paste keyup", function () {
        calcularTotalFactura();
        calculosVentaOcasional();
        calcularIngresoGravado();
    });

    function calcularTotalFactura() {
        var total_iva_10 = $(input_total_iva_10).autoNumeric('get')?$(input_total_iva_10).autoNumeric('get'):0;
        var total_iva_5 = $(input_total_iva_5).autoNumeric('get')?$(input_total_iva_5).autoNumeric('get'):0;
        var exentas = $(input_exentas).autoNumeric('get')?$(input_exentas).autoNumeric('get'):0;

        var total_factura = Math.round(
            parseInt(total_iva_10) + parseInt(total_iva_5) + parseInt(exentas)
        );
        $(input_total_factura).autoNumeric('set', total_factura);
    }

    // Eventos al cambiar los campos
    changeTipoDocumento();
    changeOperacion();
    changeCondicionVenta();
    changeCobrado();
    changeTipoRentaVenta();
    changeValorcompra();
    changeBienGanancial();
    changeMontoIngreso();

    // Cambiar tipo de documento
    function changeTipoDocumento() {
        $(input_tipo_documento).change(function () {
            tipo_documento = $(input_tipo_documento).val();

            if(tipo_documento === "1"){
                // Factura
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();

                mostrarFecha();
                mostrarCondicionVenta();
                mostrarTimbrado();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "4"){
                // Nota de crédito
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarCondicionVenta();
                ocultarCobrado();

                mostrarFecha();
                mostrarTimbrado();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "5"){
                // Liquidacion de Salario
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarFecha();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarVentaOcasional();
                ocultarCobrado();

                mostrarMes();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "8"){
                // Extracto de cuenta
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarFecha();
                ocultarTimbrado();
                ocultarVentaOcasional();
                ocultarCobrado();

                mostrarCuenta();
                mostrarFecha();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "14"){
                // Otros documentos
                ocultarCuenta();
                ocultarTimbrado();
                ocultarMes();
                ocultarCobrado();
                ocultarVentaOcasional();

                mostrarFecha();
                mostrarOtroTipoDocumento();
                mostrarNumeroOtroTipoDocumento();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
        });
    }

    // Cambiar operacion
    function changeOperacion() {
        $(input_operacion).change(function () {
            operacion = $(input_operacion).val();

            obtenerPorcentajeGravado(operacion);

        });
    }

    // Cambiar condicion de venta
    function changeCondicionVenta() {
        $(input_condicion_venta).change(function () {
            condicion_venta = $(input_condicion_venta).val();

            if(condicion_venta === 'CREDITO'){
                mostrarCobrado();
            }
            else {
                ocultarCobrado();
            }

            calculosVentaOcasional();
            calcularIngresoGravado();
        });
    }

    // Cambiar cobrado
    function changeCobrado() {
        $(input_total_cobrado).on("change paste keyup", function () {
            cobrado = input_total_cobrado.val();
            calculosVentaOcasional();
            calcularIngresoGravado();
        });
    }

    // Cambiar venta ocasional
    function changeTipoRentaVenta(){
        $(input_tipo_renta_por_venta).change(function () {
            tipo_renta_por_venta = input_tipo_renta_por_venta.val();
            calculosVentaOcasional();
            calcularIngresoGravado();
        });
    }

    // Cambiar valor compra
    function changeValorcompra() {
        $(input_valor_compra).on("change paste keyup", function () {
            valor_compra = input_valor_compra.val();
            calculosVentaOcasional();
            calcularIngresoGravado();
        });
    }

    // Cambiar bien ganancial
    function changeBienGanancial(){
        $(checkbox_bien_ganancial).change(function () {
            bien_ganancial = checkbox_bien_ganancial.prop("checked");
            calculosVentaOcasional();
            calcularIngresoGravado();
        });
    }

    // Cambiar venta tipo de venta ocasional
    function calculosVentaOcasional() {
        if (operacion !== "" && ( operacion === "11" || operacion === "12")){
            calcularValorVenta();
            mostrarVentaOcasional();
            
            if (input_tipo_renta_por_venta.val() === "RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL"){
                calcularRentaNetaReal();
                mostrarRentaNetaPresunta();
                calcularRentaNetaPresunta();
            }
            else if (input_tipo_renta_por_venta.val() === "RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL_IRACIS"){
                calcularRentaNetaReal();
                ocultarRentaNetaPresunta();
            }
        }
        else {
            ocultarVentaOcasional();
        }
    }

    // Cambiar el monto de Ingreso
    function changeMontoIngreso(){
        $(input_total_factura).on("change paste keyup", function () {
            if (tipo_documento === "5" || tipo_documento === "8" || tipo_documento === "14") {
                calcularIngresoGravado();
            }
        });
    }

    // Calculos Venta Ocasional
    function calcularValorVenta() {
        var gravada_iva_10 = $(input_gravada_iva_10).autoNumeric('get')?$(input_gravada_iva_10).autoNumeric('get'):0;
        var gravada_iva_5 = $(input_gravada_iva_5).autoNumeric('get')?$(input_gravada_iva_5).autoNumeric('get'):0;
        var exentas = $(input_exentas).autoNumeric('get')?$(input_exentas).autoNumeric('get'):0;

        var valor_venta = Math.round(
            parseInt(gravada_iva_10) + parseInt(gravada_iva_5) + parseInt(exentas)
        );

        valor_venta = calcularBienGanancial(valor_venta);

        $(input_valor_venta).autoNumeric('set', valor_venta);
    }

    function calcularBienGanancial(valor_venta) {
        if(checkbox_bien_ganancial.prop("checked")){
            valor_venta = Math.round(valor_venta/2);
        }
        return valor_venta
    }

    function calcularRentaNetaReal() {
        var valor_venta = $(input_valor_venta).autoNumeric('get')?$(input_valor_venta).autoNumeric('get'):0;
        var valor_compra = $(input_valor_compra).autoNumeric('get')?$(input_valor_compra).autoNumeric('get'):0;
        var renta_neta_real = Math.round(valor_venta-valor_compra) > 0 ? Math.round(valor_venta-valor_compra) : 0;

        $(input_renta_neta_real).autoNumeric('set', renta_neta_real);
    }

    function calcularRentaNetaPresunta() {
        var valor_venta = $(input_valor_venta).autoNumeric('get')?$(input_valor_venta).autoNumeric('get'):0;
        var renta_neta_presunta = Math.round(valor_venta*30/100) > 0 ? Math.round(valor_venta*30/100) : 0;

        $(input_renta_neta_presunta).autoNumeric('set', renta_neta_presunta);
    }

    function calcularIngresoGravadoVentaOcasional() {
        var renta_neta_real = $(input_renta_neta_real).autoNumeric('get')?$(input_renta_neta_real).autoNumeric('get'):0;
        var renta_neta_presunta = $(input_renta_neta_presunta).autoNumeric('get')?$(input_renta_neta_presunta).autoNumeric('get'):0;
        var renta_imponible = renta_neta_real > renta_neta_presunta ? renta_neta_presunta : renta_neta_real;

        var valor_venta = $(input_valor_venta).autoNumeric('get')?$(input_valor_venta).autoNumeric('get'):0;

        $(input_ingreso_gravado).autoNumeric('set', renta_imponible);
        $(input_ingreso_no_gravado).autoNumeric('set', valor_venta - renta_imponible);

        var ingreso_gravado = $(input_ingreso_gravado).autoNumeric('get')?$(input_ingreso_gravado).autoNumeric('get'):0;
        var ingreso_no_gravado = $(input_ingreso_no_gravado).autoNumeric('get')?$(input_ingreso_no_gravado).autoNumeric('get'):0;
        var ingreso_total = parseInt(ingreso_gravado) + parseInt(ingreso_no_gravado);

        $(input_ingreso_total).autoNumeric('set', ingreso_total);
    }

    function calcularIngresoGravadoVentaOcasionalIRACIS() {
        var renta_imponible = $(input_renta_neta_real).autoNumeric('get')?$(input_renta_neta_real).autoNumeric('get'):0;
        var valor_venta = $(input_valor_venta).autoNumeric('get')?$(input_valor_venta).autoNumeric('get'):0;

        $(input_ingreso_gravado).autoNumeric('set', renta_imponible);
        $(input_ingreso_no_gravado).autoNumeric('set', valor_venta - renta_imponible);

        var ingreso_gravado = $(input_ingreso_gravado).autoNumeric('get')?$(input_ingreso_gravado).autoNumeric('get'):0;
        var ingreso_no_gravado = $(input_ingreso_no_gravado).autoNumeric('get')?$(input_ingreso_no_gravado).autoNumeric('get'):0;
        var ingreso_total = parseInt(ingreso_gravado) + parseInt(ingreso_no_gravado);

        $(input_ingreso_total).autoNumeric('set', ingreso_total);
    }

    // Calculos Ingresos Gravados y No Gravados
    function calcularIngresoGravado() {
        if (operacion !== "" && ( operacion === "11" || operacion === "12")){

            if (input_tipo_renta_por_venta.val() === "RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL"){
                calcularIngresoGravadoVentaOcasional();

            }
            else if (input_tipo_renta_por_venta.val() === "RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL_IRACIS"){
                calcularIngresoGravadoVentaOcasionalIRACIS();
            }
        }
        else {

            calculosIngresosGravadoGeneral();

        }
    }

    // Calculos
    function calculosIngresosGravadoGeneral() {
        var ingreso_sin_iva;

        if(condicion_venta === 'CREDITO'){
            ingreso_sin_iva = calcularTotalCobradoSinIVA();
            mostrarCobrado();

        }
        else {
            var gravada_iva_10 = $(input_gravada_iva_10).autoNumeric('get')?$(input_gravada_iva_10).autoNumeric('get'):0;
            var gravada_iva_5 = $(input_gravada_iva_5).autoNumeric('get')?$(input_gravada_iva_5).autoNumeric('get'):0;
            var exentas = $(input_exentas).autoNumeric('get')?$(input_exentas).autoNumeric('get'):0;

            ingreso_sin_iva = Math.round(
                parseInt(gravada_iva_10) + parseInt(gravada_iva_5) + parseInt(exentas)
            );

            ocultarCobrado();
        }


        calcularMontoGravadoNoGravado(ingreso_sin_iva);
    }


    function calcularTotalCobradoSinIVA() {
        var total_cobrado = parseInt($(input_total_cobrado).autoNumeric('get')?$(input_total_cobrado).autoNumeric('get'):0);
        var total_factura = parseInt($(input_total_factura).autoNumeric('get')?$(input_total_factura).autoNumeric('get'):0);
        var total_iva_10 = parseInt($(input_total_iva_10).autoNumeric('get')?$(input_total_iva_10).autoNumeric('get'):0);
        var total_iva_5 = parseInt($(input_total_iva_5).autoNumeric('get')?$(input_total_iva_5).autoNumeric('get'):0);
        var exentas = parseInt($(input_exentas).autoNumeric('get')?$(input_exentas).autoNumeric('get'):0);

        var porc_iva_10 = 0;
        var porc_iva_5 = 0;
        var porc_exenta = 0;

        if (total_iva_10 > 0 && total_iva_5 > 0 && exentas > 0){
            porc_iva_10 = parseFloat(total_iva_10 / total_factura).toFixed(4);
            porc_iva_5 = parseFloat(total_iva_5 / total_factura).toFixed(4);
            porc_exenta = parseFloat(1 - (parseFloat(porc_iva_10) + parseFloat(porc_iva_5))).toFixed(4);
        }
        else if (total_iva_10 > 0 && total_iva_5 > 0 && exentas === 0){
            porc_iva_10 = parseFloat((total_iva_10 / total_factura)).toFixed(4);
            porc_iva_5 = parseFloat((1 - parseFloat(porc_iva_10))).toFixed(4);
            porc_exenta = parseFloat(0);
        }
        else if (total_iva_10 > 0 && total_iva_5 === 0 && exentas > 0){
            porc_iva_10 = parseFloat((total_iva_10 / total_factura)).toFixed(4);
            porc_iva_5 = parseFloat(0);
            porc_exenta = parseFloat((1 - parseFloat(porc_iva_10))).toFixed(4);
        }
        else if (total_iva_10 === 0 && total_iva_5 > 0 && exentas > 0){
            porc_iva_5 = parseFloat((total_iva_5 / total_factura)).toFixed(4);
            porc_iva_10 = parseFloat(0);
            porc_exenta = parseFloat((1 - parseFloat(porc_iva_5))).toFixed(4);
        }
        else {
            porc_iva_10 = parseFloat((total_iva_10 / total_factura)).toFixed(4);
            porc_iva_5 = parseFloat((total_iva_5 / total_factura)).toFixed(4);
            porc_exenta = parseFloat((exentas / total_factura)).toFixed(4);
        }

        var total_cobrado_gravada_iva_10 = Math.round((total_cobrado * porc_iva_10) / 1.1);
        var total_cobrado_gravada_iva_5 = Math.round((total_cobrado * porc_iva_5) / 1.05);
        var total_cobrado_exenta = Math.round(total_cobrado * porc_exenta);

        return total_cobrado_gravada_iva_10 + total_cobrado_gravada_iva_5 + total_cobrado_exenta
    }


    // Calcular Ingreso Gravado para no ventas
    function calcularMontoGravadoNoGravado(ingreso_sin_iva) {
        var gravado = 0;
        var no_gravado = 0;

        if (tipo_documento === "5" || tipo_documento === "8" || tipo_documento === "14"){
            ingreso_sin_iva = $(input_total_factura).autoNumeric('get')?$(input_total_factura).autoNumeric('get'):0;
        }

        if (grava){
            gravado = Math.round(ingreso_sin_iva * grava_porcentaje /100);
            no_gravado = Math.round(ingreso_sin_iva - gravado)
        }
        else {
            gravado = 0;
            no_gravado = ingreso_sin_iva;
        }

        gravado = calcularBienGanancial(gravado);
        no_gravado = calcularBienGanancial(no_gravado);

        $(input_ingreso_gravado).autoNumeric('set', gravado);
        $(input_ingreso_no_gravado).autoNumeric('set', no_gravado);
        $(input_ingreso_total).autoNumeric('set', gravado + no_gravado);
    }

    function obtenerPorcentajeGravado(operacion) {
        // Se trae por ajax el valor del grava y grava_porcentaje de la operacion seleccionada
        $.ajax({
            url: '/contribuyentes/ingreso/operacion-porcentaje-gravado/',
            data: {
                'operacion_id': operacion
            },
            dataType: 'json',
            type: 'get',
            success: function (data) {
                if(data){
                    grava = data.grava;
                    grava_porcentaje = (data.grava_porcentaje)?parseFloat(data.grava_porcentaje):0;

                    calculosVentaOcasional();
                    calcularIngresoGravado();
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Error, no se pudo realizar la consulta de los datos de la operacion");
            }

        })
    }

    // Funciones para ocultar campos
    function ocultarRentaNetaPresunta() {
        $('#div_id_renta_neta_presunta').hide();
    }

    function mostrarRentaNetaPresunta() {
        $('#div_id_renta_neta_presunta').show();
    }

    function ocultarCobrado() {
        $('#div_id_fieldset_cobrado').closest('fieldset').hide();
    }

    function mostrarCobrado() {
        $('#div_id_fieldset_cobrado').closest('fieldset').show();
    }

    function ocultarVentaOcasional() {
        $('#div_id_fieldset_venta_ocasional').closest('fieldset').hide();
    }

    function mostrarVentaOcasional() {
        $('#div_id_fieldset_venta_ocasional').closest('fieldset').show();
    }

    function ocultarOtroTipoDocumento() {
        $('#div_id_otro_tipo_documento').hide();
    }

    function mostrarOtroTipoDocumento() {
        $('#div_id_otro_tipo_documento').show();
    }

    function ocultarNumeroOtroTipoDocumento() {
        $('#div_id_numero_otro_tipo_documento').hide();
    }

    function mostrarNumeroOtroTipoDocumento() {
        $('#div_id_numero_otro_tipo_documento').show();
    }

    function ocultarMes() {
        $('#div_id_mes').hide();
    }

    function mostrarMes() {
        $('#div_id_mes').show();
    }

    function ocultarFecha() {
        $('#div_id_fecha_documento').hide();
    }

    function mostrarFecha() {
        $('#div_id_fecha_documento').show();
    }

    function ocultarCondicionVenta() {
        $('#div_id_condicion_venta').hide();
    }

    function mostrarCondicionVenta() {
        $('#div_id_condicion_venta').show();
    }

    function ocultarCuenta() {
        $('#div_id_fieldset_cuenta').closest('fieldset').hide();
    }

    function mostrarCuenta() {
        $('#div_id_fieldset_cuenta').closest('fieldset').show();
    }

    function ocultarTimbrado() {
        $('#div_id_fieldset_timbrado').closest('fieldset').hide();
    }

    function mostrarTimbrado() {
        $('#div_id_fieldset_timbrado').closest('fieldset').show();
    }

    function cambiarTextoPartner(tipo_documento) {
        var div_partner = $('#div_id_fieldset_partner');
        if (tipo_documento === "1"){
            $(div_partner).text('Cliente / Comprador del Bien o Servicio');
        }
        else if (tipo_documento === "4"){
            $(div_partner).text('Cliente / Comprador del Bien o Servicio');
        }
        else if (tipo_documento === "5"){
            $(div_partner).text('Datos del Pagador');
        }
        else if (tipo_documento === "8"){
            $(div_partner).text('Datos del Pagador');
        }
        else if (tipo_documento === "14"){
            $(div_partner).text('Cliente / Comprador del Bien o Servicio');
        }
    }

    function cambiarTextoDatosFactura(tipo_documento) {
        var div_datos_factura = $('#div_id_fieldset_datos_factura');
        var label_total_factura = $('#div_id_total_factura > label');
        if (tipo_documento === "1"){
            $(div_datos_factura).text('Datos de Factura');
            mostrarDatosFactura();
            desactivarSoloLecturaCampoMontoIngreso();
        }
        else if (tipo_documento === "4"){
            $(div_datos_factura).text('Datos de Factura');
            mostrarDatosFactura();
            desactivarSoloLecturaCampoMontoIngreso();
        }
        else if (tipo_documento === "5"){
            $(div_datos_factura).text('Monto del Ingreso');
            $(label_total_factura).text('Monto del Ingreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoIngreso();
        }
        else if (tipo_documento === "8"){
            $(div_datos_factura).text('Monto del Ingreso');
            $(label_total_factura).text('Monto del Ingreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoIngreso();
        }
        else if (tipo_documento === "14"){
            $(div_datos_factura).text('Monto del Ingreso');
            $(label_total_factura).text('Monto del Ingreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoIngreso();
        }
    }
    
    function ocultarDatosFactura() {
        $('#div_id_total_iva_10').hide();
        $('#div_id_gravada_iva_10').hide();
        $('#div_id_iva_10').hide();
        $('#div_id_total_iva_5').hide();
        $('#div_id_gravada_iva_5').hide();
        $('#div_id_iva_5').hide();
        $('#div_id_exentas').hide();
    }

    function mostrarDatosFactura() {
        $('#div_id_total_iva_10').show();
        $('#div_id_gravada_iva_10').show();
        $('#div_id_iva_10').show();
        $('#div_id_total_iva_5').show();
        $('#div_id_gravada_iva_5').show();
        $('#div_id_iva_5').show();
        $('#div_id_exentas').show();
    }

    function activarSoloLecturaCampoMontoIngreso() {
        $(input_total_factura).attr('readonly', false);
    }

    function desactivarSoloLecturaCampoMontoIngreso() {
        $(input_total_factura).attr('readonly', true);
    }

    // Edicion de Ingreso
    function editarIngreso(){
        tipo_documento = $(input_tipo_documento).val();
        operacion = $(input_operacion).val();
        condicion_venta = $(input_condicion_venta).val();
        tipo_renta_por_venta = $(input_tipo_renta_por_venta).val();

        if(tipo_documento === "1"){
            // Factura
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarVentaOcasional();
            ocultarCobrado();

            mostrarFecha();
            mostrarCondicionVenta();
            mostrarTimbrado();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);

            if (operacion === "11" || operacion === "12"){
                mostrarVentaOcasional();
            }

            if (condicion_venta === 'CREDITO'){
                mostrarCobrado();
            }

            if (tipo_renta_por_venta === 'RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL_IRACIS'){
                ocultarRentaNetaPresunta();
            }
        }
        else if(tipo_documento === "4"){
            // Nota de crédito
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarCondicionVenta();
            ocultarVentaOcasional();
            ocultarCobrado();

            mostrarFecha();
            mostrarTimbrado();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);

            if (operacion === "11" || operacion === "12"){
                mostrarVentaOcasional();
            }

            if (tipo_renta_por_venta === 'RENTA_NETA_IMPONIBLE_VENTA_OCASIONAL_IRACIS'){
                ocultarRentaNetaPresunta();
            }
        }
        else if(tipo_documento === "5"){
            // Liquidacion de Salario
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarFecha();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarVentaOcasional();
            ocultarCobrado();

            mostrarMes();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "8"){
            // Extracto de cuenta
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarFecha();
            ocultarTimbrado();
            ocultarCobrado();
            ocultarVentaOcasional();

            mostrarCuenta();
            mostrarFecha();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "14"){
            // Otros documentos
            ocultarCuenta();
            ocultarTimbrado();
            ocultarMes();
            ocultarCobrado();
            ocultarVentaOcasional();

            mostrarFecha();
            mostrarOtroTipoDocumento();
            mostrarNumeroOtroTipoDocumento();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
    }
});