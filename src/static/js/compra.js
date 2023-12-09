// Envuelve tu código en un bloque document ready
$(document).ready(function() {

    // Función para cambiar interruptores
    function toggleSwitch(clickedSwitch) {
        const allSwitches = document.querySelectorAll('.switch input');

        allSwitches.forEach(function(switchInput) {
            if (switchInput !== clickedSwitch) {
                switchInput.checked = false;
            }
        });
    }

    // Función para limpiar el formulario
    function limpiarFormulario() {
        document.getElementById("miFormulario").reset();
    }

    // Función para calcular los totales
    function calcularTotales() {
        var montoGravado10 = parseFloat($("#montoGravado10").val()) || 0;
        var impuestoGravado10 = montoGravado10 * 0.1;
        var montoGravado5 = parseFloat($("#montoGravado5").val()) || 0;
        var impuestoGravado5 = montoGravado5 * 0.05;
        var montoExento = parseFloat($("#montoExento").val()) || 0;

        var totalIVA = impuestoGravado10 + impuestoGravado5;
        var totalComprobante = montoGravado10 + impuestoGravado10 + montoGravado5 + impuestoGravado5 + montoExento;

        $("#totalIVA").text(totalIVA.toFixed(2));
        $("#totalComprobante").text(totalComprobante.toFixed(2));
    }

    // Configura eventos de cambio en los campos de entrada para recalcular los totales
    $(".cuadro-pequeno").on("input", calcularTotales);

    // Inicializa los totales al cargar la página
    calcularTotales();

    // Obtén el ID del cliente de la URL
    var idcliente = getParameterByName('idcliente');
    console.log('ID del cliente:', idcliente);

    // Agrega aquí el resto de tu código, si lo tienes.

});

// Agrega aquí el resto de tu código, si lo tienes.
