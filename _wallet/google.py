"""Pubblica il pass Google Wallet del biglietto da visita e stampa il link «Aggiungi a Google Wallet».

    python3 _wallet/google.py [--card card.json] [--prova]

Classe e oggetto vengono creati (o aggiornati) tramite la Google Wallet API con il service account
in `segreti()/service-account.json`; il link contiene solo il riferimento all'oggetto, perché
un JWT con tutti i dati supererebbe i 1800 caratteri che Google indica come limite sicuro.
Con --prova non contatta Google: stampa classe, oggetto e, se c'è il service account, il link.
"""

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt

from common import (CONTATTO, NERO, SITO, carica, indirizzo_righe, marchio, nome_completo, png,
                    segreti, telefono_link, verifica, vcard)

API = "https://walletobjects.googleapis.com/walletobjects/v1"
SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"
LIMITE_LINK = 1800
LOGO = SITO / "images" / "wallet-logo.png"


def testo(valore: str) -> dict:
    return {"defaultValue": {"language": "it", "value": valore}}


def id_classe(d: dict) -> str:
    return f"{d['google']['issuerId']}.{d['google']['classe']}"


def id_oggetto(d: dict) -> str:
    return f"{d['google']['issuerId']}.{d['slug']}"


def oggetto(d: dict) -> dict:
    link = [
        {"id": "chiama", "uri": telefono_link(d), "description": "Chiama"},
        {"id": "email", "uri": f"mailto:{d['email']}", "description": "Scrivi una email"},
        {"id": "sito", "uri": d["sito"], "description": "Sito web"},
    ]
    if d.get("linkedin"):
        link.append({"id": "linkedin", "uri": d["linkedin"], "description": "LinkedIn"})
    return {
        "id": id_oggetto(d),
        "classId": id_classe(d),
        "state": "ACTIVE",
        "cardTitle": testo(d["organizzazione"]),
        "subheader": testo(d["ruolo"]),
        "header": testo(nome_completo(d)),
        "logo": {
            "sourceUri": {"uri": urllib.parse.urljoin(d["sito"], "images/wallet-logo.png")},
            "contentDescription": testo(f"Logo {d['organizzazione']}"),
        },
        "hexBackgroundColor": "#{:02x}{:02x}{:02x}".format(*NERO),
        "barcode": {"type": "QR_CODE", "value": vcard(d), "alternateText": "Inquadra per salvare il contatto"},
        "textModulesData": [
            {"id": "telefono", "header": "Telefono", "body": d["telefono"]},
            {"id": "email", "header": "Email", "body": d["email"]},
            {"id": "indirizzo", "header": "Indirizzo", "body": indirizzo_righe(d)},
            {"id": "piva", "header": "Partita IVA", "body": d["partitaIva"]},
        ],
        "linksModuleData": {"uris": link},
    }


def token_accesso(sa: dict) -> str:
    ora = int(time.time())
    url = sa.get("token_uri", "https://oauth2.googleapis.com/token")
    asserzione = jwt.encode(
        {"iss": sa["client_email"], "scope": SCOPE, "aud": url, "iat": ora, "exp": ora + 3600},
        sa["private_key"], algorithm="RS256", headers={"kid": sa["private_key_id"]})
    corpo = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": asserzione}).encode()
    with urllib.request.urlopen(url, corpo) as risposta:
        return json.load(risposta)["access_token"]


def chiama(metodo: str, url: str, token: str, corpo: dict) -> None:
    richiesta = urllib.request.Request(url, method=metodo, data=json.dumps(corpo).encode(), headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    urllib.request.urlopen(richiesta).close()


def salva(risorsa: str, dati: dict, token: str) -> None:
    """Crea la classe o l'oggetto; se esiste già (409) lo sostituisce con i dati attuali."""
    try:
        chiama("POST", f"{API}/{risorsa}", token, dati)
        print(f"{risorsa} {dati['id']}: creato")
    except urllib.error.HTTPError as errore:
        if errore.code != 409:
            raise SystemExit(f"{risorsa} {dati['id']}: errore {errore.code}\n{errore.read().decode()}")
        chiama("PUT", f"{API}/{risorsa}/{urllib.parse.quote(dati['id'])}", token, dati)
        print(f"{risorsa} {dati['id']}: aggiornato")


def link_salvataggio(sa: dict, d: dict) -> str:
    token = jwt.encode({
        "iss": sa["client_email"],
        "aud": "google",
        "typ": "savetowallet",
        "iat": int(time.time()),
        "origins": [urllib.parse.urljoin(d["sito"], "/").rstrip("/")],
        "payload": {"genericObjects": [{"id": id_oggetto(d), "classId": id_classe(d)}]},
    }, sa["private_key"], algorithm="RS256")
    return f"https://pay.google.com/gp/v/save/{token}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Pubblica il pass Google Wallet e stampa il link di salvataggio.")
    parser.add_argument("--card", help="file dei dati (predefinito: _wallet/card.json)")
    parser.add_argument("--prova", action="store_true", help="non contatta Google, mostra cosa invierebbe")
    args = parser.parse_args()

    d = carica(args.card)
    verifica(d, *CONTATTO, "google.issuerId", "google.classe")

    # Google mostra il logo ritagliato in un cerchio: marchio su fondo pieno, con margine.
    LOGO.write_bytes(png(marchio(660, NERO, 0.6)))

    classe, ogg = {"id": id_classe(d)}, oggetto(d)
    file_sa = segreti() / "service-account.json"
    sa = json.loads(file_sa.read_text()) if file_sa.exists() else None

    if args.prova:
        print(json.dumps({"genericClass": classe, "genericObject": ogg}, ensure_ascii=False, indent=2))
    elif sa is None:
        raise SystemExit(f"Manca {file_sa}: vedi _wallet/README.md")
    else:
        token = token_accesso(sa)
        salva("genericClass", classe, token)
        salva("genericObject", ogg, token)

    if sa:
        link = link_salvataggio(sa, d)
        avviso = "" if len(link) <= LIMITE_LINK else f"  (attenzione: supera {LIMITE_LINK} caratteri)"
        print(f"\nLink «Aggiungi a Google Wallet» ({len(link)} caratteri){avviso}:\n{link}")


if __name__ == "__main__":
    main()
