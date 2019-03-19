$(document).ready(function () {
    var error_importacion_id = $('#error_importacion_id').val()!==undefined ? $('#error_importacion_id').val() : "";

    if(error_importacion_id!==''){
        window.location.replace('/media/' + error_importacion_id);
    }

});