# Website
Sito web ThreePoints.

# Architettura
Sito statico composto da pagine `index.html` (una per cartella), `styles.css` e `script.js`.

Immagini nella cartella `images`, font Roboto e icone Material Symbols ospitati in `fonts`
(nessuna richiesta a Google Fonts).

# Foglio di stile
`styles.css` è il sorgente e si modifica a mano. Le pagine caricano `styles.min.css`,
generato con [csso](https://github.com/css/csso): dopo ogni modifica a `styles.css` va rigenerato.

```bash
npx csso-cli styles.css -o styles.min.css
```
