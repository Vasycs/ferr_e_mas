document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var mensajeExito = document.querySelector('#mensaje-exito');

        if (mensajeExito) {
            mensajeExito.style.display = 'none';
            window.location.href = '/';
        }
    }, 1000);
});
