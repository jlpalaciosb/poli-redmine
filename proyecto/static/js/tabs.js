$(document).ready(function() {

    // Activamos el tab correspondiente a Ingreso o Egreso
    var window_querystring = window.location.search;
    if(window_querystring !== ""){
        if(window_querystring.includes('ingreso')){
            $('li > a[data-toggle="tab"]').first().tab('show');
        }
        else if (window_querystring.includes('egreso')){
            $('li > a[data-toggle="tab"]').last().tab('show');
        }
    }

    // Acciones al hacer click en los tabs
    $('li > a[data-toggle="tab"]').on('click', function (ev) {
        console.log($(this).data("target"));
        var window_url = window.location.href;
        var base_url = window_url.split('?')[0];
        var window_querystring = window.location.search;
        var new_url = window_url;
        var parsed_url = '';

        var tab_target = $(this).data("target");

        // Recargamos la pagina
        if(tab_target === '#tab_ingresos'){
            // Si se hace click en el tab ingresos
            if(window_querystring !== ""){
                parsed_url = jQuery.query.load(window_url);
                new_url = parsed_url.set('tipo', 'ingreso').toString();
                window.document.location = base_url + new_url;
            }
            else {
                window.document.location = new_url + '?tipo=ingreso';
            }
        }
        else if (tab_target === '#tab_egresos'){
            // Si se hace click en el tab egresos
            if(window_querystring !== ""){
                parsed_url = jQuery.query.load(window_url);
                new_url = parsed_url.set('tipo', 'egreso').toString();
                window.document.location = base_url + new_url;
            }
            else {
                window.document.location = new_url + '?tipo=egreso';
            }
        }

    });
});