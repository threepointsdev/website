"""Dati e funzioni condivise dai pass Apple Wallet e Google Wallet."""

import io
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

QUI = Path(__file__).resolve().parent
SITO = QUI.parent
MARCHIO = SITO / "images" / "logo.png"
NERO = (10, 10, 10)  # --tp-ink
ARANCIO = (245, 124, 0)  # --tp-orange

CONTATTO = ("slug", "nome", "cognome", "ruolo", "organizzazione", "telefono", "email", "sito")


def segreti() -> Path:
    """Cartella di certificati e chiavi: sta fuori dal repository."""
    return Path(os.environ.get("WALLET_SECRETS", Path.home() / ".config" / "threepoints-wallet"))


def carica(percorso=None) -> dict:
    return json.loads(Path(percorso or QUI / "card.json").read_text(encoding="utf-8"))


def verifica(dati: dict, *chiavi: str) -> None:
    """Esce con un errore se una delle chiavi (anche annidate, es. "apple.teamIdentifier") è vuota o TODO."""
    mancanti = []
    for chiave in chiavi:
        valore = dati
        for parte in chiave.split("."):
            valore = valore.get(parte) if isinstance(valore, dict) else None
        if valore in (None, "", "TODO"):
            mancanti.append(chiave)
    if mancanti:
        sys.exit("Da compilare in card.json: " + ", ".join(mancanti))


def nome_completo(d: dict) -> str:
    return f"{d['nome']} {d['cognome']}"


def telefono_link(d: dict) -> str:
    return "tel:" + "".join(c for c in d["telefono"] if c.isdigit() or c == "+")


def sito_breve(d: dict) -> str:
    return d["sito"].removeprefix("https://").removeprefix("http://").rstrip("/")


def indirizzo_righe(d: dict) -> str:
    a = d["indirizzo"]
    return f"{a['via']}\n{a['cap']} {a['citta']} ({a['provincia']})"


def vcard(d: dict) -> str:
    """Scheda contatto da mettere nel QR: la fotocamera di iPhone e Android la propone come nuovo contatto."""

    def e(s: str) -> str:
        return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")

    a = d["indirizzo"]
    righe = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{e(d['cognome'])};{e(d['nome'])};;;",
        f"FN:{e(nome_completo(d))}",
        f"ORG:{e(d['organizzazione'])}",
        f"TITLE:{e(d['ruolo'])}",
        f"TEL;TYPE=CELL:{d['telefono']}",
        f"EMAIL;TYPE=WORK:{d['email']}",
        f"URL:{d['sito']}",
    ]
    if d.get("linkedin"):
        righe.append(f"URL:{d['linkedin']}")
    righe += [
        f"ADR;TYPE=WORK:;;{e(a['via'])};{e(a['citta'])};{e(a['provincia'])};{e(a['cap'])};{e(a['paese'])}",
        "END:VCARD",
    ]
    return "\r\n".join(righe)


def marchio(lato: int, sfondo=None, proporzione: float = 1.0) -> Image.Image:
    """Il marchio arancio centrato in un quadrato di `lato` px, su sfondo trasparente o pieno."""
    tela = Image.new("RGBA", (lato, lato), (*sfondo, 255) if sfondo else (0, 0, 0, 0))
    m = round(lato * proporzione)
    logo = Image.open(MARCHIO).convert("RGBA").resize((m, m), Image.Resampling.LANCZOS)
    tela.alpha_composite(logo, ((lato - m) // 2, (lato - m) // 2))
    return tela


def ritaglio_quadrato(percorso: Path, lato: int) -> Image.Image:
    return ImageOps.fit(Image.open(percorso).convert("RGB"), (lato, lato), Image.Resampling.LANCZOS)


def png(immagine: Image.Image) -> bytes:
    buffer = io.BytesIO()
    immagine.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()
