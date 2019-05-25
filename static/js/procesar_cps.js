/*
 * Script para procesar los campos personalizados en los form para crear y editar user stories.
 * Lo que hace es básicamente ocultar el textarea donde está el json de los campos personalizados
 * y controla el contenido de ese textarea
 */

let TUS = {}; // define los campos personalizados con sus tipos
let CPS = {}; // define los campos personalizados con sus valores

$('document').ready(function() {
   document.getElementById('div_id_valoresCPs').style.display = 'none';

   CPS = JSON.parse(document.getElementById('id_valoresCPs').value);
   getTUS(true);

   document.getElementById('id_tipo').onchange = tuschange;

   document.getElementById('submit-id-guardar').setAttribute('type', 'button');
   document.getElementById('submit-id-guardar').onclick = enviar;
});

/* muestra los campos personalizados en el form para que el usuario pueda editar sus valores */
function mostrarCPS() {
    document.querySelectorAll('.campo-personalizado').forEach(e => e.remove());

    for(let campo in CPS) {
        let valor = CPS[campo];

        let campoDiv = document.createElement('div');
        campoDiv.setAttribute('id', `div_id_${campo}`);
        campoDiv.setAttribute('class', 'form-group campo-personalizado');

        let campoLabel = document.createElement('label');
        campoLabel.setAttribute('for', `id_${campo}`);
        campoLabel.setAttribute('class', 'control-label col-lg-2');
        campoLabel.innerText = campo;

        let campoSubDiv = document.createElement('div');
        campoSubDiv.setAttribute('class', 'controls col-lg-8');

        let campoInput = document.createElement('input');
        campoInput.setAttribute('id', `id_${campo}`);
        campoInput.setAttribute('type', getType(campo));
        campoInput.setAttribute('step', '0.000001');
        campoInput.setAttribute('class', 'textinput textInput form-control');
        campoInput.value = CPS[campo];

        campoDiv.appendChild(campoLabel);
        campoDiv.appendChild(campoSubDiv);
        campoSubDiv.appendChild(campoInput);

        insertAfter(document.getElementById('div_id_tipo'), campoDiv);
    }
}

/* función que se ejecuta cuando selecciona un tipo */
function tuschange() {
    TUS = {};
    getTUS(false);
}

/* obtiene la definición del tipo vía ajax */
function getTUS(initial) {
    if(!initial) CPS = {};

    let tus_id = document.getElementById('id_tipo').value;

    if(tus_id === '' || tus_id === null || tus_id === undefined) {
        mostrarCPS();
    } else {
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                TUS = JSON.parse(this.responseText);
                if(!initial) {
                    for (let campo in TUS) CPS[campo] = null;
                }
                mostrarCPS();
            }
        };
        let url = `/proyectos/${proyecto_id}/tipous/${tus_id}/json`;
        xhttp.open("GET", url, true);
        xhttp.send();
    }
}

/* retorna el tipo de un campo */
function getType(campo) {
    if(TUS[campo] === 'STRING') return 'text';
    else return 'number';
}

/* envia el form */
function enviar() {
    for(let campo in CPS) {
        CPS[campo] = document.getElementById(`id_${campo}`).value;
    }
    document.getElementById('id_valoresCPs').value = JSON.stringify(CPS);
    document.getElementById('submit-id-guardar').setAttribute('type', 'submit');
    document.getElementById('submit-id-guardar').click();
}

/* inserta un elemento después de otro en el DOM */
function insertAfter(referenceNode, newNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
