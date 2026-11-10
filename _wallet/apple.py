"""Genera il pass Apple Wallet (.pkpass) del biglietto da visita.

    python3 _wallet/apple.py [--card card.json] [--out cartella]

Legge da `segreti()` la chiave privata (pass.key), il certificato del Pass Type ID (pass.cer)
e il certificato intermedio Apple WWDR G4 (AppleWWDRCAG4.cer). Vedi _wallet/README.md.
"""

import argparse
import hashlib
import io
import json
import os
import zipfile
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import pkcs7

from common import (CONTATTO, NERO, ARANCIO, QUI, SITO, carica, indirizzo_righe, marchio, nome_completo,
                    png, ritaglio_quadrato, segreti, sito_breve, verifica, vcard)


def rgb(colore) -> str:
    return "rgb({}, {}, {})".format(*colore)


def pass_json(d: dict) -> dict:
    retro = [
        {"key": "telefono", "label": "Telefono", "value": d["telefono"]},
        {"key": "email", "label": "Email", "value": d["email"]},
        {"key": "sito", "label": "Sito", "value": d["sito"]},
    ]
    if d.get("linkedin"):
        retro.append({"key": "linkedin", "label": "LinkedIn", "value": d["linkedin"]})
    retro += [
        {"key": "indirizzo", "label": "Indirizzo", "value": indirizzo_righe(d)},
        {"key": "piva", "label": "Partita IVA", "value": d["partitaIva"], "dataDetectorTypes": []},
        {"key": "qr", "label": "Salvare il contatto",
         "value": "Inquadra il QR sul fronte con la fotocamera del telefono: il contatto si aggiunge alla rubrica."},
    ]
    return {
        "formatVersion": 1,
        "passTypeIdentifier": d["apple"]["passTypeIdentifier"],
        "teamIdentifier": d["apple"]["teamIdentifier"],
        "serialNumber": d["slug"],
        "organizationName": d["organizzazione"],
        "description": f"Biglietto da visita di {nome_completo(d)}",
        "logoText": d["organizzazione"].upper(),
        "backgroundColor": rgb(NERO),
        "foregroundColor": rgb((255, 255, 255)),
        "labelColor": rgb(ARANCIO),
        "generic": {
            "primaryFields": [{"key": "nome", "label": d["ruolo"], "value": nome_completo(d)}],
            "secondaryFields": [{"key": "email", "label": "Email", "value": d["email"]}],
            "auxiliaryFields": [
                {"key": "telefono", "label": "Telefono", "value": d["telefono"]},
                {"key": "sito", "label": "Sito", "value": sito_breve(d)},
            ],
            "backFields": retro,
        },
        "barcodes": [{
            "format": "PKBarcodeFormatQR",
            "message": vcard(d),
            "messageEncoding": "iso-8859-1",
            "altText": "Inquadra per salvare il contatto",
        }],
    }


def immagini(d: dict) -> dict:
    """Icona (notifiche, Mail), logo in alto a sinistra e, se c'è, la foto accanto al nome."""
    file = {}
    for scala in (1, 2, 3):
        suffisso = "" if scala == 1 else f"@{scala}x"
        file[f"icon{suffisso}.png"] = png(marchio(29 * scala, NERO, 0.8))
        file[f"logo{suffisso}.png"] = png(marchio(50 * scala))
        if d.get("foto"):
            file[f"thumbnail{suffisso}.png"] = png(ritaglio_quadrato(QUI / d["foto"], 90 * scala))
    return file


def certificato(percorso: Path) -> x509.Certificate:
    dati = percorso.read_bytes()
    if dati.lstrip().startswith(b"-----BEGIN"):
        return x509.load_pem_x509_certificate(dati)
    return x509.load_der_x509_certificate(dati)


def firma(manifest: bytes, cartella: Path) -> bytes:
    """Firma PKCS#7 separata del manifest, con il certificato intermedio Apple incluso."""
    password = os.environ.get("WALLET_KEY_PASSWORD")
    chiave = serialization.load_pem_private_key(
        (cartella / "pass.key").read_bytes(), password.encode() if password else None)
    if not isinstance(chiave, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey)):
        raise SystemExit("pass.key deve essere una chiave RSA o EC")
    return (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(manifest)
        .add_signer(certificato(cartella / "pass.cer"), chiave, hashes.SHA256())
        .add_certificate(certificato(cartella / "AppleWWDRCAG4.cer"))
        .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.Binary])
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera il pass Apple Wallet (.pkpass).")
    parser.add_argument("--card", help="file dei dati (predefinito: _wallet/card.json)")
    parser.add_argument("--out", type=Path, default=SITO / "wallet", help="cartella di destinazione")
    args = parser.parse_args()

    d = carica(args.card)
    verifica(d, *CONTATTO, "apple.passTypeIdentifier", "apple.teamIdentifier")

    file = {"pass.json": json.dumps(pass_json(d), ensure_ascii=False, indent=2).encode(), **immagini(d)}
    manifest = json.dumps({nome: hashlib.sha1(b).hexdigest() for nome, b in file.items()}, indent=2).encode()
    file["manifest.json"] = manifest
    file["signature"] = firma(manifest, segreti())

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, contenuto in file.items():
            z.writestr(nome, contenuto)

    args.out.mkdir(parents=True, exist_ok=True)
    uscita = args.out / f"{d['slug']}.pkpass"
    uscita.write_bytes(buffer.getvalue())
    print(f"Creato {uscita}")


if __name__ == "__main__":
    main()
