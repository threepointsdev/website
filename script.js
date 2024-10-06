// script.js
document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menu-toggle");
    const mobileMenu = document.getElementById("mobile-menu");
    const closeMenu = document.getElementById("close-menu");

    const menuLinks = document.querySelectorAll('.menu-mobile-items a');

    menuToggle.addEventListener("click", function () {
        mobileMenu.classList.add("open");
    });

    closeMenu.addEventListener("click", function () {
        mobileMenu.classList.remove("open");
    });


    // Funzione per chiudere il menu quando viene selezionata una voce
    menuLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Chiude il menu quando una voce è selezionata
            mobileMenu.classList.remove('open');
        });
    });
});