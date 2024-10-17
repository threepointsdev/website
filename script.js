// script.js
window.addEventListener('load', function () {
    // Nascondi la schermata di caricamento con un effetto di dissolvenza
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.opacity = '0';

    loadingScreen.style.display = 'none';
    // Mostra il contenuto del sito con un effetto di dissolvenza
    const siteContent = document.getElementById('site-content');
    siteContent.style.display = 'block';
  
});

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