
// Función para limpiar el formulario
function limpiarFormulario() {
    document.getElementById("miFormulario").reset();
    // Limpia los campos específicos 
    $("#montoGravado10").val(0);
    $("#montoGravado5").val(0);
    $("#montoExento").val(0);

    // Limpia los resultados de los totales
    $("#total10").text("0.00");
    $("#total5").text("0.00");
    $("#totalIVA").text("0.00");
    $("#totalComprobante").text("0");
}


$(document).ready(function() {
    //aca tambien se necesita el token para poder envia los datos a python
    var csrfToken = document.getElementById('csrf_token').value;
    console.log(csrfToken);
    var tipoOperacion = "";
        // Evento de clic en un botón de compra
    $("#compraBoton").on("click", function() {
        tipoOperacion = "compra";
        // Actualiza la URL a la que se enviarán los datos
        urlEnviarDatos = "/obtener_compra/";
    });

    // Evento de clic en un botón de venta
    $("#ventaBoton").on("click", function() {
        tipoOperacion = "venta";
        // Actualiza la URL a la que se enviarán los datos
        urlEnviarDatos = "/obtener_datos_venta/";
    });
    // Obtener parámetro de la URL
    function getParameterByName(name) {
        const url = window.location.href;
        name = name.replace(/[\[\]]/g, '\\$&');
        
        const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
        
        if (!results) return null;
        if (!results[2]) return '';
        
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }
    


    // Función para calcular los totales
    function calcularTotales() {
        var total10= 0;     
        var total5= 0;
        var montoGravado10 = parseInt($("#montoGravado10").val()) || 0;
        var impuestoGravado10 = montoGravado10 /11;
        var montoGravado5 = parseFloat($("#montoGravado5").val()) || 0;
        var impuestoGravado5 = montoGravado5 /21;
        var montoExento = parseFloat($("#montoExento").val()) || 0;

        total10 = total10+impuestoGravado10;
        total5 = total5 + impuestoGravado5;
        var totalIVA = impuestoGravado10 + impuestoGravado5;
        var totalComprobante = parseInt(montoGravado10 + montoGravado5 + montoExento);
        $("#total10").text(total10.toFixed(2));
        $("#total5").text(total5.toFixed(2));
        $("#totalIVA").text(totalIVA.toFixed(2));
        $("#totalComprobante").text(totalComprobante);
        
    }

    // Configura eventos de cambio en los campos de entrada para recalcular los totales
    $(".cuadro-pequeno").on("input", calcularTotales);

    // Inicializa los totales al cargar la página
    calcularTotales();

    // Obténer el idcliente de la URL
    var idcliente = getParameterByName('idcliente');
    console.log('ID del cliente:', idcliente);

    // Evento de clic en un botón (ficticio) para enviar datos a Python
    $("#enviarDatosBoton").on("click", function() {
        //if (tipoOperacion === "compra") {
          //  enviarDatos("/obtener_compra/");
        //} else if (tipoOperacion === "venta") {
          //  enviarDatos("/obtener_venta/");
        //}
    

        // Aquí podrías construir un objeto con los datos que deseas enviar
        var datosAEnviar = {
            idcliente: idcliente,
            montoGravado10: $("#montoGravado10").text(),
            total10: $("#total10").text(),
            montoGravado5: $("#montoGravado5").text(),
            montoExento: $("#montoExento").text(),
            total5: $("#total5").text(),
            totalIVA: $("#totalIVA").text(),
            totalComprobante: $("#totalComprobante").text()
           
        };
        
            $.ajax({
                type: "POST",
                url: "/obtener_compra/",
                data: JSON.stringify(datosAEnviar),
                contentType: "application/json",
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function(response) {
                    console.log('Respuesta del servidor:', response);
                },
                error: function(xhr, status, error) {
                    console.error('Error en la solicitud Ajax:', error);
                    console.log('Estado de la solicitud:', status);
                    console.log('Respuesta del servidor:', xhr.responseText);
                }
            });
        
        
       
    });
   
    

    $("#limpiarBoton").on("click", limpiarFormulario);
    // Click event for an imaginary button to send data

});

