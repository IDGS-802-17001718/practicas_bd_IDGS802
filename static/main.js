$(document).ready(function () {
    $('#confirmar_pedido').on('click', function () {
        // Calculate the total of subtotals
        var total = 0;
        $('#pedido tbody tr').each(function () {
            var subtotal = parseFloat($(this).find('td:last').text());
            total += isNaN(subtotal) ? 0 : subtotal;
        });

        // Display the total in the modal
        $('#total_pedido').text('Total de pedido: $' + total.toFixed(2));
        var nombre = document.getElementById('nombre').value;
        var direccion = document.getElementById('direccion').value;
        var telefono = document.getElementById('telefono').value;
        var fecha = document.getElementById('fecha').value;
    
        // Set modal form inputs
        document.getElementById('modalNombre').value = nombre;
        document.getElementById('modalDireccion').value = direccion;
        document.getElementById('modalTelefono').value = telefono;
        document.getElementById('modalFecha').value = fecha;

    });
});


function showHideInputFields() {
    var radioDay = document.getElementById('radioDay');
    var radioMonth = document.getElementById('radioMonth');
    var radioDate = document.getElementById('radioDate');

    var selectDay = document.getElementById('selectDay');
    var selectMonth = document.getElementById('selectMonth');
    var inputDate = document.getElementById('inputDate');

    selectDay.style.display = radioDay.checked ? 'block' : 'none';
    selectMonth.style.display = radioMonth.checked ? 'block' : 'none';
    inputDate.style.display = radioDate.checked ? 'block' : 'none';
}

const hiddenInput = document.querySelector('#modalFecha');

document.querySelector('#fecha')
    .addEventListener('change', (event) => {
        hiddenInput.value = event.target.value;
        console.log(hiddenInput.value);
    });

