document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var mensajeExito = document.querySelector('.alert-success');
        if (mensajeExito) {
            mensajeExito.style.display = 'none';
        }
    }, 1000); 
});