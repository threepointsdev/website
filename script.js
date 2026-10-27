// script.js

const nextFrame = () => new Promise(resolve => requestAnimationFrame(resolve));

// Aspetta i pesi di Roboto usati nell'hero (al massimo 1.5s), così il testo
// non cambia font mentre si muove
function heroFontsLoaded() {
    if (!document.fonts) {
        return Promise.resolve();
    }
    const fonts = Promise.all([
        document.fonts.load('900 100px Roboto'),
        document.fonts.load('300 20px Roboto'),
        document.fonts.load('500 16px Roboto'),
    ]).catch(() => { });
    return Promise.race([fonts, new Promise(resolve => setTimeout(resolve, 1500))]);
}

// Ingresso dell'hero con la Web Animations API: solo transform e opacity,
// così l'animazione gira sul compositor e non risente del lavoro della pagina
async function playHeroEntrance() {
    const root = document.documentElement;
    const items = [...document.querySelectorAll('[data-in]')];
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (reduce || !items.length || !Element.prototype.animate) {
        root.classList.remove('pre');
        root.classList.add('done');
        return;
    }

    // Livelli GPU preparati prima della partenza, non durante
    items.forEach(el => { el.style.willChange = 'transform, opacity'; });
    await nextFrame();

    const animations = items.map((el, i) => el.animate(
        el.dataset.in === 'line'
            ? [{ transform: 'translate3d(0, 110%, 0)' }, { transform: 'translate3d(0, 0, 0)' }]
            : [{ opacity: 0, transform: 'translate3d(0, 16px, 0)' }, { opacity: 1, transform: 'translate3d(0, 0, 0)' }],
        { duration: 900, delay: 120 + i * 90, easing: 'cubic-bezier(.16, 1, .3, 1)', fill: 'both' }
    ));
    // fill "both" applica già il primo fotogramma: lo stato CSS iniziale non serve più
    root.classList.remove('pre');

    await Promise.all(animations.map(a => a.finished));

    // Fine: animazioni rimosse e livelli GPU liberati
    animations.forEach(a => a.cancel());
    items.forEach(el => { el.style.willChange = ''; });
    root.classList.add('done');
}

// Comparsa dei blocchi delle sezioni durante lo scroll: blocchi piccoli (titoli,
// card, domande) e non sezioni intere, solo transform e opacity, una volta sola
const SECTION_ITEMS = '.section-head, .prose, .svc, .value, .cliente-card, .place, .remote, .faq-list details, .contact-actions, .case-facts, .stat, .steps li, .arch-layer, .arch-notes > div';

function setupSectionReveal() {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window) || !Element.prototype.animate) {
        return;
    }

    // Si nasconde solo ciò che è ancora sotto lo schermo: quello già visibile resta com'è
    const items = [...document.querySelectorAll(SECTION_ITEMS)]
        .filter(el => el.getBoundingClientRect().top > window.innerHeight);
    items.forEach(el => el.classList.add('rv-wait'));

    const observer = new IntersectionObserver(entries => {
        const entering = entries.filter(entry => entry.isIntersecting).map(entry => entry.target);
        entering.forEach((el, i) => {
            observer.unobserve(el);
            const animation = el.animate(
                [{ opacity: 0, transform: 'translate3d(0, 20px, 0)' }, { opacity: 1, transform: 'translate3d(0, 0, 0)' }],
                { duration: 600, delay: Math.min(i, 5) * 60, easing: 'cubic-bezier(.16, 1, .3, 1)', fill: 'both' }
            );
            el.classList.remove('rv-wait');
            animation.finished.then(() => animation.cancel()).catch(() => { });
        });
    }, { rootMargin: '0px 0px -10% 0px' });

    items.forEach(el => observer.observe(el));
}

window.addEventListener('load', async function () {
    const loadingScreen = document.getElementById('loading-screen');
    const siteContent = document.getElementById('site-content');

    try {
        // Mostra il contenuto sotto la schermata di caricamento: la lettura di
        // offsetHeight forza il layout, così il browser richiede subito i font
        if (siteContent) {
            siteContent.style.display = 'block';
            void siteContent.offsetHeight;
        }

        await heroFontsLoaded();

        // Due fotogrammi: il contenuto viene disegnato prima che parta qualsiasi animazione
        await nextFrame();
        await nextFrame();

        // Le pagine locali non hanno la schermata di caricamento
        if (loadingScreen) {
            const fade = loadingScreen.animate(
                [{ opacity: 1 }, { opacity: 0 }],
                { duration: 300, easing: 'ease-out', fill: 'forwards' }
            );
            fade.finished.then(() => { loadingScreen.style.display = 'none'; });
        }

        await playHeroEntrance();
        setupSectionReveal();
    } catch (error) {
        // In caso di errore il contenuto deve comunque essere visibile
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
        document.documentElement.classList.remove('pre');
        document.documentElement.classList.add('done');
    }
});

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

    // Animazioni dell'hero in pausa quando non è visibile
    const hero = document.querySelector('.hero-v2');
    if (hero && 'IntersectionObserver' in window) {
        new IntersectionObserver(([entry]) => {
            hero.classList.toggle('is-offscreen', !entry.isIntersecting);
        }).observe(hero);
    }
});
