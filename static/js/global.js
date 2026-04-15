document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('menuBtn');
    const menuContent = document.getElementById('menuContent');
    const menuIcon = document.getElementById('menuIcon');

    menuBtn.addEventListener('click', () => {
        // Alternar clase active
        menuContent.classList.toggle('active');

        // Cambiar icono de flecha
        if (menuContent.classList.contains('active')) {
            menuIcon.classList.replace('bi-chevron-down', 'bi-chevron-up');
        } else {
            menuIcon.classList.replace('bi-chevron-up', 'bi-chevron-down');
        }
    });

    // Cerrar menú si se hace clic fuera
    document.addEventListener('click', (e) => {
        if (!menuBtn.contains(e.target) && !menuContent.contains(e.target)) {
            menuContent.classList.remove('active');
            menuIcon.classList.replace('bi-chevron-up', 'bi-chevron-down');
        }
    });
});