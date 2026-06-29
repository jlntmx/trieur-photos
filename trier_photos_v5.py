#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trier_photos.py - Version corrigée
----------------------------------
Range photos et vidéos par date de prise de vue, dans une arborescence
annee/annee-mois (option annee/mois/jour).

Corrections par rapport à la version précédente :
  - import de timedelta ajouté (sinon crash sur les vidéos quand ffprobe
    est absent)
  - repli vidéo propre : si ffprobe n'est pas installé, on bascule sans
    erreur sur la lecture interne de l'entête MP4/MOV
  - import inutile (TAGS) retiré

Dépendances Python :  pip install pillow pillow-heif tqdm
Optionnel (vidéos)  :  FFmpeg installé et dans le PATH (fournit ffprobe).
                       Si absent, le script fonctionne quand même.
"""

import os
import re
import shutil
import hashlib
import subprocess
import logging
from datetime import datetime, timedelta   # <-- timedelta réintégré
from pathlib import Path
from typing import Optional, Tuple

# ==================== CONFIGURATION ====================
SOURCE = r"D:\MEDIAS A TRIER"
DESTINATION = r"D:\MEDIAS TRIÉS"

COPIER = False          # True = copie (recommandé au début), False = déplace
SIMULATION = False      # True = mode test (recommandé pour le premier essai)
PAR_JOUR = False       # True = dossiers par jour (2026/2026-06/2026-06-14)
IGNORER_DOUBLONS = True # True = détecte les photos identiques même renommées

# Séparer photos et vidéos dans deux sous-dossiers distincts.
# Si True, le résultat ressemble à :
#   MEDIAS TRIÉS / Photos / 2026 / 2026-06 / ...
#   MEDIAS TRIÉS / Vidéos / 2026 / 2026-06 / ...
SEPARER_PHOTOS_VIDEOS = True
DOSSIER_PHOTOS = "Photos"   # nom du sous-dossier des photos (modifiable)
DOSSIER_VIDEOS = "Vidéos"   # nom du sous-dossier des vidéos (modifiable)
DOSSIER_AUDIO = "Audio"     # nom du sous-dossier des sons (rangés par date)

# Documents (PDF, Word, Excel...) : regroupés EN VRAC, sans tri par date,
# pour que tu les classes ensuite à la main par projet.
DOSSIER_DOCUMENTS = "A CLASSER - DOCUMENTS"

# Doublons : au lieu d'être laissés en place, ils sont déplacés dans un
# sous-dossier du dossier source, pour que tu puisses les supprimer d'un bloc
# sans risquer d'effacer d'autres fichiers (sons, etc.) par un Ctrl+A.
DEPLACER_DOUBLONS = True
DOSSIER_DOUBLONS = "_DOUBLONS"

LOG_FILE = "trier_photos.log"

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff", ".webp", ".gif"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".3gp", ".avi", ".mkv"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".opus"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
           ".txt", ".odt", ".ods", ".odp", ".rtf", ".csv"}
# ======================================================

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_OK = True
except ImportError:
    HEIF_OK = False

from PIL import Image
from tqdm import tqdm

# Détecte une seule fois si ffprobe est disponible, pour éviter d'essayer
# (et de logguer une erreur) sur chaque vidéo s'il est absent.
FFPROBE_OK = shutil.which("ffprobe") is not None


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def date_exif(chemin: str) -> Optional[datetime]:
    """EXIF - DateTimeOriginal (priorité maximale)."""
    try:
        img = Image.open(chemin)
        exif = img.getexif()
        if not exif:
            return None

        candidats = []
        try:
            sous = exif.get_ifd(0x8769)
            candidats.extend([sous.get(36867), sous.get(36868)])
        except Exception:
            pass
        candidats.extend([exif.get(36867), exif.get(306)])

        for val in candidats:
            if val:
                date_str = str(val)[:19]
                for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
    except Exception as e:
        logging.debug(f"EXIF échoué pour {chemin}: {e}")
    return None


def date_video_ffprobe(chemin: str) -> Optional[datetime]:
    """Lecture fiable via ffprobe (si FFmpeg est installé)."""
    if not FFPROBE_OK:
        return None
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_entries", "format_tags=creation_time", str(chemin),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            ct = data.get("format", {}).get("tags", {}).get("creation_time")
            if ct:
                d = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                # on renvoie une date "naïve" (sans fuseau) pour rester
                # homogène avec les autres sources de date
                return d.replace(tzinfo=None)
    except Exception as e:
        logging.debug(f"ffprobe échoué pour {chemin}: {e}")
    return None


def date_video_mvhd(chemin: str) -> Optional[datetime]:
    """Repli : lecture de la date dans l'entête MP4/MOV (atome 'mvhd')."""
    try:
        with open(chemin, "rb") as f:
            data = f.read(1_500_000)
        idx = data.find(b"mvhd")
        if idx == -1:
            return None
        pos = idx + 4
        version = data[pos]
        pos += 4
        if version == 1:
            secs = int.from_bytes(data[pos:pos + 8], "big")
        else:
            secs = int.from_bytes(data[pos:pos + 4], "big")
        d = datetime(1904, 1, 1) + timedelta(seconds=secs)
        if 1990 < d.year < 2100:
            return d
    except Exception as e:
        logging.debug(f"mvhd échoué pour {chemin}: {e}")
    return None


def date_nom_fichier(chemin: str) -> Optional[datetime]:
    """Date trouvée dans le nom du fichier (ex: 2026-06-14 ou 20260614)."""
    nom = Path(chemin).stem
    for pattern in (r"(20\d{2})[-_.](\d{2})[-_.](\d{2})", r"(20\d{2})(\d{2})(\d{2})"):
        m = re.search(pattern, nom)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                continue
    return None


def trouver_date(chemin: str, ext: str) -> datetime:
    """Cascade : EXIF/vidéo -> nom de fichier -> date de modification."""
    d = None
    if ext in PHOTO_EXT:
        d = date_exif(chemin)
    elif ext in VIDEO_EXT:
        d = date_video_ffprobe(chemin) or date_video_mvhd(chemin)

    if d is None:
        d = date_nom_fichier(chemin)
    if d is None:
        d = datetime.fromtimestamp(os.path.getmtime(chemin))
        logging.warning(f"Date de modification utilisée pour {Path(chemin).name}")
    return d


def empreinte_partielle(chemin: Path, taille_max: int = 10_000_000) -> str:
    """Hash MD5 du début (+ fin si gros fichier) : rapide sur les vidéos."""
    h = hashlib.md5()
    taille = chemin.stat().st_size
    with open(chemin, "rb") as f:
        h.update(f.read(4_000_000))
        if taille > taille_max:
            f.seek(-4_000_000, os.SEEK_END)
            h.update(f.read(4_000_000))
    return h.hexdigest()


def cible_unique(dossier: Path, nom: str, source: Path) -> Tuple[Path, bool]:
    """Évite d'écraser : doublon identique -> ignoré ; sinon -> _1, _2, ..."""
    cible = dossier / nom
    if not cible.exists():
        return cible, False
    if empreinte_partielle(cible) == empreinte_partielle(source):
        return cible, True
    tige, suf = os.path.splitext(nom)
    i = 1
    while (dossier / f"{tige}_{i}{suf}").exists():
        i += 1
    return dossier / f"{tige}_{i}{suf}", False


def main():
    setup_logging()
    src = Path(SOURCE)
    dst = Path(DESTINATION)

    if not src.is_dir():
        logging.error(f"Dossier source introuvable : {src}")
        return
    if not HEIF_OK:
        logging.warning("pillow-heif non installé → HEIC/HEIF moins bien supportés.")
    if not FFPROBE_OK:
        logging.info("ffprobe absent → lecture des vidéos via l'entête MP4/MOV (repli).")

    logging.info(f"{'[SIMULATION] ' if SIMULATION else ''}Début du tri : {src} → {dst}")

    photos = videos = audios = docs = autres = doublons = 0
    fichiers_a_traiter = []

    # Mémoire des fichiers déjà vus, par empreinte de contenu.
    deja_vus = {}

    # Dossier où regrouper les doublons (à l'intérieur de la source).
    dossier_doublons = src / DOSSIER_DOUBLONS

    for racine, sous_dossiers, fichiers in os.walk(src):
        # On ne re-parcourt pas le dossier des doublons déjà mis de côté.
        if DOSSIER_DOUBLONS in sous_dossiers:
            sous_dossiers.remove(DOSSIER_DOUBLONS)
        for f in fichiers:
            chemin = Path(racine) / f
            ext = chemin.suffix.lower()
            if ext not in PHOTO_EXT and ext not in VIDEO_EXT \
               and ext not in AUDIO_EXT and ext not in DOC_EXT:
                autres += 1
                continue
            fichiers_a_traiter.append((chemin, ext))

    def ranger_doublon(chemin):
        """Déplace un doublon dans le dossier _DOUBLONS (sauf en simulation)."""
        if not (DEPLACER_DOUBLONS and not SIMULATION):
            return
        dossier_doublons.mkdir(parents=True, exist_ok=True)
        cible, identique = cible_unique(dossier_doublons, chemin.name, chemin)
        if identique:   # déjà un exemplaire identique dans _DOUBLONS
            return
        shutil.move(str(chemin), str(cible))

    for chemin, ext in tqdm(fichiers_a_traiter, desc="Tri des fichiers"):
        try:
            # --- Doublons : même contenu, peu importe le nom ou l'emplacement ---
            if IGNORER_DOUBLONS:
                signature = empreinte_partielle(chemin)
                if signature in deja_vus:
                    doublons += 1
                    logging.info(f"Doublon : {chemin.name} "
                                 f"(identique à {deja_vus[signature]})")
                    ranger_doublon(chemin)
                    continue
                deja_vus[signature] = chemin.name

            # --- Choix de la destination selon le TYPE de fichier ---
            if ext in DOC_EXT:
                # Documents : en vrac, sans tri par date.
                dossier = dst / DOSSIER_DOCUMENTS
            else:
                # Médias (photo / vidéo / son) : rangés par date.
                d = trouver_date(str(chemin), ext)
                base = dst
                if SEPARER_PHOTOS_VIDEOS:
                    if ext in PHOTO_EXT:
                        base = dst / DOSSIER_PHOTOS
                    elif ext in VIDEO_EXT:
                        base = dst / DOSSIER_VIDEOS
                    elif ext in AUDIO_EXT:
                        base = dst / DOSSIER_AUDIO
                if PAR_JOUR:
                    dossier = base / f"{d.year}" / f"{d.year}-{d.month:02d}" / f"{d.year}-{d.month:02d}-{d.day:02d}"
                else:
                    dossier = base / f"{d.year}" / f"{d.year}-{d.month:02d}"

            if not SIMULATION:
                dossier.mkdir(parents=True, exist_ok=True)

            cible, est_doublon = cible_unique(dossier, chemin.name, chemin)
            if est_doublon:
                doublons += 1
                logging.info(f"Doublon : {chemin.name}")
                ranger_doublon(chemin)
                continue

            logging.info(f"{chemin.name} → {dossier.relative_to(dst)}/")

            if not SIMULATION:
                if COPIER:
                    shutil.copy2(chemin, cible)
                else:
                    shutil.move(str(chemin), str(cible))

            if ext in PHOTO_EXT:
                photos += 1
            elif ext in VIDEO_EXT:
                videos += 1
            elif ext in AUDIO_EXT:
                audios += 1
            elif ext in DOC_EXT:
                docs += 1

        except Exception as e:
            logging.error(f"Erreur sur {chemin}: {e}")

    logging.info("── Bilan ──")
    logging.info(f"Photos traitées    : {photos}")
    logging.info(f"Vidéos traitées    : {videos}")
    logging.info(f"Sons traités       : {audios}")
    logging.info(f"Documents rangés   : {docs}")
    logging.info(f"Doublons mis de côté : {doublons}")
    logging.info(f"Autres fichiers ignorés : {autres}")

    if SIMULATION:
        print("\n=== MODE SIMULATION ===")
        print("Aucun fichier n'a été modifié.")
        print("Change SIMULATION = False pour exécuter réellement.")


if __name__ == "__main__":
    main()
