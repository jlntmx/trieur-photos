# 📁 Trieur de photos

Un petit programme qui **range automatiquement** vos photos, vidéos et sons
dans des dossiers classés par date, et regroupe vos documents à part.

Fini le dossier « Photos » avec 5000 fichiers en vrac : le programme crée une
arborescence claire, du type :

```
MEDIAS TRIÉS/
├── Photos/
│   ├── 2024/
│   │   └── 2024-08/   (toutes vos photos d'août 2024)
│   └── 2026/
│       └── 2026-06/
├── Vidéos/
├── Audio/
└── A CLASSER - DOCUMENTS/   (vos PDF, Word, Excel à classer)
```

> **Ce programme ne supprime jamais rien.** Il copie ou déplace vos fichiers,
> mais n'efface aucun original sans votre action. Vous ne risquez pas de perdre
> vos souvenirs.

---

## ✨ Ce que fait le programme

- Range les **photos** (JPEG, PNG, HEIC/HEIF des téléphones...) par date de prise de vue
- Range les **vidéos** (MP4, MOV...) par date
- Range les **sons** (MP3, M4A...) par date
- Regroupe les **documents** (PDF, Word, Excel...) dans un dossier à classer vous-même
- Repère les **doublons** (même photo en double, même renommée) et les met de côté
- Laisse intacts les fichiers qu'il ne connaît pas

---

## 🟢 Pour les grands débutants : c'est quoi, au juste ?

Ce fichier (`trier_photos_v5.py`) est un **script**, c'est-à-dire une liste
d'instructions écrites dans un langage appelé **Python**. Pour qu'il fonctionne,
il faut deux choses : installer Python sur votre ordinateur (une fois pour
toutes), puis lancer le script. C'est ce que les étapes ci-dessous expliquent,
pas à pas. Aucune connaissance préalable n'est nécessaire.

---

## 1️⃣ Installer Python (à faire une seule fois)

### Sur Windows

1. Allez sur **https://www.python.org/downloads/**
2. Cliquez sur le gros bouton jaune **« Download Python »**
3. Lancez le fichier téléchargé
4. ⚠️ **TRÈS IMPORTANT** : sur la première fenêtre, cochez la case
   **« Add Python to PATH »** tout en bas, AVANT de cliquer sur « Install Now ».
   Sans cette case, rien ne marchera ensuite.
5. Cliquez sur **Install Now** et laissez faire.

### Sur Mac

1. Allez sur **https://www.python.org/downloads/**
2. Cliquez sur **« Download Python »**
3. Ouvrez le fichier `.pkg` téléchargé et suivez l'installation (Suivant,
   Suivant, Installer).

---

## 2️⃣ Ouvrir le « terminal »

Le terminal est une fenêtre où l'on tape des commandes. Pas d'inquiétude, vous
n'aurez qu'à copier-coller.

- **Windows** : appuyez sur la touche Windows, tapez `powershell`, appuyez sur Entrée.
- **Mac** : appuyez sur `Cmd + Espace`, tapez `terminal`, appuyez sur Entrée.

---

## 3️⃣ Installer les trois outils nécessaires

Dans le terminal, copiez-collez cette ligne et appuyez sur Entrée :

**Windows :**
```
pip install pillow pillow-heif tqdm
```

**Mac :**
```
pip3 install pillow pillow-heif tqdm
```

> Si un message dit que `pip` n'est pas reconnu, essayez `python -m pip install pillow pillow-heif tqdm`
> (Windows) ou `python3 -m pip install pillow pillow-heif tqdm` (Mac).

Ces trois outils permettent de lire les dates des photos (y compris les photos
de téléphone au format HEIC) et d'afficher une barre de progression.

---

## 4️⃣ Préparer vos dossiers

Créez **deux dossiers** sur votre ordinateur :

- Un dossier d'**entrée**, où vous mettrez vos fichiers en vrac
  (exemple : `MEDIAS A TRIER`)
- Un dossier de **sortie**, où le programme rangera tout
  (exemple : `MEDIAS TRIÉS`) — il sera créé automatiquement s'il n'existe pas.

Mettez vos photos, vidéos, etc. dans le dossier d'entrée. Vous pouvez tout
mélanger, le programme fait le tri lui-même. Il regarde aussi dans les
sous-dossiers, donc vous pouvez y déposer des dossiers entiers.

---

## 5️⃣ Indiquer vos dossiers au programme

Ouvrez le fichier `trier_photos_v5.py` avec un éditeur de texte
(le Bloc-notes sous Windows, TextEdit sous Mac, ou un éditeur comme
**VS Code** / **Cursor**, gratuits).

Tout en haut, trouvez ces deux lignes et remplacez les chemins par les vôtres :

```python
SOURCE = r"C:\Users\VotreNom\...\MEDIAS A TRIER"
DESTINATION = r"C:\Users\VotreNom\...\MEDIAS TRIÉS"
```

Sur **Mac**, les chemins ressemblent plutôt à :

```python
SOURCE = r"/Users/VotreNom/MEDIAS A TRIER"
DESTINATION = r"/Users/VotreNom/MEDIAS TRIÉS"
```

> 💡 Astuce pour trouver le bon chemin : sur Windows, ouvrez le dossier,
> cliquez dans la barre d'adresse en haut, copiez le texte. Sur Mac, faites
> clic droit sur le dossier → « Obtenir des informations » pour voir son emplacement.

**Laissez la ligne `SIMULATION = True` telle quelle pour l'instant**, et
enregistrez le fichier.

---

## 6️⃣ Premier essai (sans risque)

Dans le terminal, placez-vous dans le dossier où se trouve le script, puis
lancez-le :

**Windows :**
```
python trier_photos_v5.py
```

**Mac :**
```
python3 trier_photos_v5.py
```

Comme on est en mode **simulation**, le programme va seulement **afficher** ce
qu'il ferait, sans toucher à un seul fichier. Vérifiez que le bilan en bas
(nombre de photos, vidéos, etc.) a du sens.

---

## 7️⃣ Lancer pour de vrai

Si l'essai vous convient :

1. Rouvrez le fichier `trier_photos_v5.py`
2. Changez `SIMULATION = True` en `SIMULATION = False`
3. Enregistrez
4. Relancez la même commande qu'à l'étape 6

Cette fois, le programme range réellement vos fichiers. Par défaut il **copie**
(vos originaux restent en place), vous pouvez donc tout vérifier avant de
supprimer quoi que ce soit.

---

## ⚙️ Réglages (en haut du fichier)

Vous pouvez personnaliser le comportement en modifiant ces lignes :

| Réglage | Ce qu'il fait |
|---|---|
| `COPIER = True` | `True` = copie (sûr). `False` = déplace les fichiers. |
| `SIMULATION = True` | `True` = essai sans rien modifier. `False` = exécute. |
| `PAR_JOUR = False` | `True` = ajoute un niveau de dossier par jour. |
| `SEPARER_PHOTOS_VIDEOS = True` | Sépare photos, vidéos et sons dans des dossiers distincts. |
| `IGNORER_DOUBLONS = True` | Repère et met de côté les fichiers identiques. |

---

## ❓ Problèmes fréquents

**« python n'est pas reconnu »** (Windows)
→ Python a été installé sans cocher « Add Python to PATH ». Réinstallez-le en
cochant bien cette case.

**« pip n'est pas reconnu »**
→ Utilisez `python -m pip install ...` (Windows) ou `python3 -m pip install ...` (Mac).

**Le programme dit « 0 fichier traité »**
→ Le chemin du dossier `SOURCE` est probablement incorrect, ou le dossier est
vide. Vérifiez le chemin (attention aux fautes de frappe et aux accents).

**Les vidéos ne sont pas bien datées**
→ Pour une lecture optimale des dates de vidéos, vous pouvez installer FFmpeg
(facultatif). Sans lui, le programme fonctionne quand même.

---

## 📜 Licence

Ce programme est libre d'utilisation. Faites-en bon usage, et n'oubliez pas de
toujours garder une sauvegarde de vos photos sur un second support (disque
externe ou cloud) !
