$(document).ready(function() {

    $('.auto').autoNumeric('init', {mDec: 0});

    // Al guardar removemos los separadores de miles
    $('#submit-id-guardar').click(guardar);
    function guardar(){
        $('.auto').each(function () {
            $(this).val($(this).autoNumeric('get'));
        });
    }

    var input_categoria = $('#id_categoria');
    var input_operacion = $('#id_operacion');
    var input_tipo_documento = $('#id_tipo_documento_egreso');

    var checkbox_aporta_iva = $('#id_aporta_iva');

    var input_total_iva_10 = $('#id_total_iva_10');
    var input_gravada_iva_10 = $('#id_gravada_iva_10');
    var input_iva_10 = $('#id_iva_10');
    var input_total_iva_5 = $('#id_total_iva_5');
    var input_gravada_iva_5 = $('#id_gravada_iva_5');
    var input_iva_5 = $('#id_iva_5');
    var input_exentas = $('#id_exentas');
    var input_total_factura = $('#id_total_factura');
    var input_total_pagado = $('#id_total_pagado');

    var input_egreso_total = $('#id_egreso_total');
    var input_condicion_venta = $('#id_condicion_venta');

    tipo_documento = $(input_tipo_documento).val();
    categoria = $(input_categoria).val();
    operacion = $(input_operacion).val();
    condicion_venta = $(input_condicion_venta).val();
    pagado = $(input_total_pagado).val();
    aporta_iva = checkbox_aporta_iva.prop("checked");

    // Al editar el egreso
    editarEgreso();

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
        calcularEgreso();
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
    changeAportaIVA();
    changePagado();
    changeCondicionVenta();
    changeMontoEgreso();


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
                ocultarDatosEmpleador();
                ocultarDespacho();

                mostrarFecha();
                mostrarCondicionVenta();
                mostrarTimbrado();
                mostrarPartner();

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
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarTimbrado();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "2"){
                // Autofactura
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarCondicionVenta();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarTimbrado();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "3"){
                // Boleta de Venta
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarCondicionVenta();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarTimbrado();
                mostrarPartner();

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
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarMes();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "6"){
                // Extracto de cuenta IPS
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarFecha();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarDespacho();
                ocultarPagado();
                ocultarPartner();

                mostrarMes();
                mostrarDatosEmpleador();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "7"){
                // Extracto Tarjeta
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "9"){
                // Transferencia
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarTimbrado();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarCuenta();
                mostrarFecha();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "10"){
                // Comprobante exterior
                ocultarOtroTipoDocumento();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarMes();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarNumeroOtroTipoDocumento();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "11"){
                // Comprobante ingreso entidad publica
                ocultarOtroTipoDocumento();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarMes();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarNumeroOtroTipoDocumento();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "12"){
                // Ticket
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarCondicionVenta();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarTimbrado();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "13"){
                // Despacho
                ocultarOtroTipoDocumento();
                ocultarNumeroOtroTipoDocumento();
                ocultarMes();
                ocultarCuenta();
                ocultarTimbrado();
                ocultarDatosEmpleador();
                ocultarPagado();
                ocultarPartner();

                mostrarFecha();
                mostrarDespacho();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
            else if(tipo_documento === "14"){
                // Otros documentos
                ocultarCuenta();
                ocultarTimbrado();
                ocultarMes();
                ocultarDatosEmpleador();
                ocultarDespacho();
                ocultarPagado();

                mostrarFecha();
                mostrarOtroTipoDocumento();
                mostrarNumeroOtroTipoDocumento();
                mostrarPartner();

                cambiarTextoPartner(tipo_documento);
                cambiarTextoDatosFactura(tipo_documento);
            }
        });
    }

    // Cambiar aporta iva
    function changeAportaIVA(){
        $(checkbox_aporta_iva).change(function () {
            aporta_iva = checkbox_aporta_iva.prop("checked");
            calcularEgreso();
        });
    }

    // Cambiar pagado
    function changePagado() {
        $(input_total_pagado).on("change paste keyup", function () {
            pagado = input_total_pagado.val();
            calcularEgreso();
        });
    }

    // Cambiar condicion de venta
    function changeCondicionVenta() {
        $(input_condicion_venta).change(function () {
            condicion_venta = $(input_condicion_venta).val();

            if(condicion_venta === 'CREDITO'){
                mostrarPagado();
            }
            else {
                ocultarPagado();
            }
            calcularEgreso();
        });
    }

    // Cambiar el monto de Ingreso
    function changeMontoEgreso(){
        $(input_total_factura).on("change paste keyup", function () {
            if (tipo_documento !== "1" && tipo_documento !== "3" && tipo_documento !== "4") {
                calcularEgreso();
            }
        });
    }


    // Calculos egresos
    function calcularEgreso() {
        if (tipo_documento === "1" || tipo_documento === "4") {
            calcularEgresoFactura();
        }
        else if (tipo_documento === "3"){
            calcularEgresoBoletaVenta();
        }
        else{
            calcularEgresoGeneral();
        }
    }

    // Calculos egresos factura
    function calcularEgresoFactura() {
        var egreso_sin_iva, egreso_con_iva;

        if (condicion_venta === 'CREDITO'){

            if (aporta_iva === true){
                egreso_sin_iva = calcularTotalPagadoSinIVA(); // total pagado sin iva

            }
            else{
                egreso_con_iva = $(input_total_pagado).autoNumeric('get')?$(input_total_pagado).autoNumeric('get'):0; // total pagado con iva
            }

            mostrarPagado();
        }
        else {

            if (aporta_iva === true){
                egreso_sin_iva = calcularTotalSinIVA(); // total factura sin iva
            }
            else{
                egreso_con_iva = $(input_total_factura).autoNumeric('get')?$(input_total_factura).autoNumeric('get'):0; // total factura con iva
            }

            ocultarPagado();
        }

        // Monto Egreso
        if (aporta_iva === true){
            $(input_egreso_total).autoNumeric('set', egreso_sin_iva);
        }
        else {
            $(input_egreso_total).autoNumeric('set', egreso_con_iva);
        }
    }


    // Calculos Egresos bolets de venta
    function calcularEgresoBoletaVenta() {
        var total_factura = $(input_total_factura).autoNumeric('get')?$(input_total_factura).autoNumeric('get'):0;

        $(input_egreso_total).autoNumeric('set', total_factura);
    }

    // Calculos Egresos General
    function calcularEgresoGeneral() {
        var total_factura = $(input_total_factura).autoNumeric('get')?$(input_total_factura).autoNumeric('get'):0;

        $(input_egreso_total).autoNumeric('set', total_factura);
    }

    function calcularTotalSinIVA() {
        var gravada_iva_10 = $(input_gravada_iva_10).autoNumeric('get')?$(input_gravada_iva_10).autoNumeric('get'):0;
        var gravada_iva_5 = $(input_gravada_iva_5).autoNumeric('get')?$(input_gravada_iva_5).autoNumeric('get'):0;
        var exentas = $(input_exentas).autoNumeric('get')?$(input_exentas).autoNumeric('get'):0;

        var total_factura_sin_iva = Math.round(
            parseInt(gravada_iva_10) + parseInt(gravada_iva_5) + parseInt(exentas)
        );

        return total_factura_sin_iva;
    }

    function calcularTotalPagadoSinIVA() {
        var total_pagado = parseInt($(input_total_pagado).autoNumeric('get')?$(input_total_pagado).autoNumeric('get'):0);
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
            porc_iva_5 = parseFloat((total_iva_5 / total_factura).toFixed(4));
            porc_iva_10 = parseFloat(0);
            porc_exenta = parseFloat((1 - parseFloat(porc_iva_5)).toFixed(4));
        }
        else {
            porc_iva_10 = parseFloat((total_iva_10 / total_factura)).toFixed(4);
            porc_iva_5 = parseFloat((total_iva_5 / total_factura)).toFixed(4);
            porc_exenta = parseFloat((exentas / total_factura)).toFixed(4);
        }

        var total_pagado_gravada_iva_10 = Math.round((total_pagado * porc_iva_10) / 1.1);
        var total_pagado_gravada_iva_5 = Math.round((total_pagado * porc_iva_5) / 1.05);
        var total_pagado_exenta = Math.round(total_pagado * porc_exenta);

        return total_pagado_gravada_iva_10 + total_pagado_gravada_iva_5 + total_pagado_exenta
    }


    // Funciones para ocultar campos
    function ocultarPagado() {
        $('#div_id_fieldset_pagado').closest('fieldset').hide();
    }

    function mostrarPagado() {
        $('#div_id_fieldset_pagado').closest('fieldset').show();
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

    function ocultarPartner() {
        $('#div_id_fieldset_partner').closest('fieldset').hide();
    }

    function mostrarPartner() {
        $('#div_id_fieldset_partner').closest('fieldset').show();
    }

    function ocultarDatosEmpleador() {
        $('#div_id_fieldset_datos_empleador').closest('fieldset').hide();
    }

    function mostrarDatosEmpleador() {
        $('#div_id_fieldset_datos_empleador').closest('fieldset').show();
    }

    function ocultarDespacho() {
        $('#div_id_fieldset_despacho').closest('fieldset').hide();
    }

    function mostrarDespacho() {
        $('#div_id_fieldset_despacho').closest('fieldset').show();
    }

    function cambiarTextoPartner(tipo_documento) {
        var div_partner = $('#div_id_fieldset_partner');
        if (tipo_documento === "1"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "4"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "2"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "3"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "5"){
            $(div_partner).text('Datos del Pagador');
        }
        else if (tipo_documento === "7"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "9"){
            $(div_partner).text('Vendedor del Bien o Servicio o Beneficiario del Pago');
        }
        else if (tipo_documento === "10"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "11"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "12"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "13"){
            $(div_partner).text('Vendedor del Bien o Servicio');
        }
        else if (tipo_documento === "14"){
            $(div_partner).text('Vendedor del Bien o Servicio o Beneficiario del Pago');
        }
    }

    function cambiarTextoDatosFactura(tipo_documento) {
        var div_datos_factura = $('#div_id_fieldset_datos_factura');
        var label_total_factura = $('#div_id_total_factura > label');

        if (tipo_documento === "1"){
            $(div_datos_factura).text('Datos de Factura');
            mostrarDatosFactura();
            desactivarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "4"){
            $(div_datos_factura).text('Datos de Factura');
            mostrarDatosFactura();
            desactivarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "2"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "3"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "5"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "6"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "7"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "9"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "10"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "11"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "12"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "13"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
        else if (tipo_documento === "14"){
            $(div_datos_factura).text('Monto del Egreso');
            $(label_total_factura).text('Monto del Egreso');
            ocultarDatosFactura();
            activarSoloLecturaCampoMontoEgreso();
        }
    }

    function ocultarDatosFactura() {
        $('#div_id_aporta_iva').hide();
        $('#div_id_total_iva_10').hide();
        $('#div_id_gravada_iva_10').hide();
        $('#div_id_iva_10').hide();
        $('#div_id_total_iva_5').hide();
        $('#div_id_gravada_iva_5').hide();
        $('#div_id_iva_5').hide();
        $('#div_id_exentas').hide();
    }

    function mostrarDatosFactura() {
        $('#div_id_aporta_iva').show();
        $('#div_id_total_iva_10').show();
        $('#div_id_gravada_iva_10').show();
        $('#div_id_iva_10').show();
        $('#div_id_total_iva_5').show();
        $('#div_id_gravada_iva_5').show();
        $('#div_id_iva_5').show();
        $('#div_id_exentas').show();
    }

    function activarSoloLecturaCampoMontoEgreso() {
        $(input_total_factura).attr('readonly', false);
    }

    function desactivarSoloLecturaCampoMontoEgreso() {
        $(input_total_factura).attr('readonly', true);
    }

    // Edicion de Egreso
    function editarEgreso(){
        tipo_documento = $(input_tipo_documento).val();
        operacion = $(input_operacion).val();
        condicion_venta = $(input_condicion_venta).val();

        if(tipo_documento === "1"){
            // Factura
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarCondicionVenta();
            mostrarTimbrado();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);

            if (condicion_venta === 'CREDITO'){
                mostrarPagado();
            }
        }
        else if(tipo_documento === "4"){
            // Nota de crédito
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarCondicionVenta();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarTimbrado();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "2"){
            // Autofactura
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarCondicionVenta();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarTimbrado();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "3"){
            // Boleta de Venta
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarCondicionVenta();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarTimbrado();
            mostrarPartner();

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
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarMes();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "6"){
            // Extracto de cuenta IPS
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarFecha();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarDespacho();
            ocultarPagado();
            ocultarPartner();

            mostrarMes();
            mostrarDatosEmpleador();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "7"){
            // Extracto Tarjeta
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "9"){
            // Transferencia
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarTimbrado();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarCuenta();
            mostrarFecha();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "10"){
            // Comprobante exterior
            ocultarOtroTipoDocumento();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarMes();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarNumeroOtroTipoDocumento();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "11"){
            // Comprobante ingreso entidad publica
            ocultarOtroTipoDocumento();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarMes();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarNumeroOtroTipoDocumento();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "12"){
            // Ticket
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarCondicionVenta();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarTimbrado();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "13"){
            // Despacho
            ocultarOtroTipoDocumento();
            ocultarNumeroOtroTipoDocumento();
            ocultarMes();
            ocultarCuenta();
            ocultarTimbrado();
            ocultarDatosEmpleador();
            ocultarPagado();
            ocultarPartner();

            mostrarFecha();
            mostrarDespacho();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }
        else if(tipo_documento === "14"){
            // Otros documentos
            ocultarCuenta();
            ocultarTimbrado();
            ocultarMes();
            ocultarDatosEmpleador();
            ocultarDespacho();
            ocultarPagado();

            mostrarFecha();
            mostrarOtroTipoDocumento();
            mostrarNumeroOtroTipoDocumento();
            mostrarPartner();

            cambiarTextoPartner(tipo_documento);
            cambiarTextoDatosFactura(tipo_documento);
        }

    }

});