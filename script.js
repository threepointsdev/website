// script.js
window.addEventListener('load', function () {
    // Nascondi la schermata di caricamento con un effetto di dissolvenza
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.opacity = '0';

    // Aspetta la fine della transizione prima di nascondere l'elemento dal flusso del layout
    setTimeout(() => {
        loadingScreen.style.display = 'none';

        // Mostra il contenuto del sito con un effetto di dissolvenza
        const siteContent = document.getElementById('site-content');
        siteContent.style.opacity = '1';
    }, 200); // Tempo corrispondente alla durata della transizione in CSS (0.2s)
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