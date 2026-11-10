# Biglietto da visita nel Wallet

Script che generano il biglietto da visita per **Apple Wallet** (file `.pkpass`) e **Google Wallet**
(link «Aggiungi a Google Wallet»). Il QR sul pass contiene la scheda contatto: chi lo inquadra con la
fotocamera la aggiunge alla rubrica, anche senza connessione.

La cartella inizia con `_`, quindi Jekyll (GitHub Pages) non la pubblica.

| File | |
|---|---|
| `card.json` | dati del biglietto, unica fonte per entrambi i pass |
| `apple.py` | crea `wallet/<slug>.pkpass` |
| `google.py` | crea o aggiorna il pass su Google e stampa il link; rigenera `images/wallet-logo.png` |
| `common.py` | scheda contatto (vCard) e immagini condivise |

Dipendenze: `pip install pillow cryptography pyjwt`.

## Dati

In `card.json`: `telefono` va scritto con il prefisso (`+39 333 123 4567`), `linkedin` e `foto`
sono facoltativi. `foto` è un percorso relativo a `_wallet/` e compare solo nel pass Apple, accanto
al nome. Gli script si rifiutano di partire finché resta un `TODO`.

## Segreti

Certificati e chiavi stanno **fuori dal repository**, in `~/.config/threepoints-wallet/`
(o nella cartella indicata da `WALLET_SECRETS`):

| File | Per |
|---|---|
| `pass.key` | Apple: chiave privata |
| `pass.cer` | Apple: certificato del Pass Type ID |
| `AppleWWDRCAG4.cer` | Apple: certificato intermedio WWDR G4 |
| `service-account.json` | Google: chiave del service account |

## Apple Wallet

Serve l'Apple Developer Program (99 €/anno), intestato all'azienda.

1. Su developer.apple.com → *Certificates, Identifiers & Profiles* → *Identifiers* → **+** →
   *Pass Type IDs*: registra `pass.dev.threepoints.card`.
2. Crea chiave e richiesta di certificato:
   ```bash
   mkdir -p ~/.config/threepoints-wallet && cd ~/.config/threepoints-wallet
   openssl req -new -newkey rsa:2048 -nodes -keyout pass.key -out pass.csr -subj "/CN=Threepoints Wallet/C=IT"
   ```
3. Sul Pass Type ID → *Create Certificate* → carica `pass.csr`, scarica il certificato e salvalo
   come `pass.cer` nella stessa cartella.
4. Da <https://www.apple.com/certificateauthority/> scarica *Worldwide Developer Relations - G4*
   e salvalo come `AppleWWDRCAG4.cer`.
5. Copia il Team ID (*Membership details*) in `apple.teamIdentifier` di `card.json`.
6. `python3 _wallet/apple.py` → `wallet/andrea-poggi.pkpass`.

Il pass Apple non si aggiorna da solo: dopo una modifica va rigenerato e ripubblicato. Il numero di
serie resta lo stesso, quindi riaprendo il nuovo file l'iPhone sostituisce quello vecchio.

## Google Wallet

L'account emittente è gratuito.

1. Su <https://pay.google.com/business/console> attiva la *Google Wallet API* e crea l'account
   emittente; copia l'Issuer ID in `google.issuerId` di `card.json`.
2. Su Google Cloud crea un progetto, abilita la *Google Wallet API*, crea un service account e
   scarica una chiave JSON: salvala come `service-account.json`.
3. Nella console di Google Wallet → *Users* invita l'email del service account come *Developer*.
4. `images/wallet-logo.png` deve essere già online: Google lo scarica dal sito.
5. `python3 _wallet/google.py --prova` per controllare cosa verrebbe inviato, poi
   `python3 _wallet/google.py` per pubblicare e ottenere il link.

Finché l'account è in modalità demo il pass si salva solo con gli account autorizzati nella console.
Per renderlo disponibile a tutti va chiesto a Google l'accesso in produzione.

Rilanciando `google.py` dopo una modifica, il pass si aggiorna anche sui telefoni che l'hanno già salvato.
