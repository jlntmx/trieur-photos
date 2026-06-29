# Trieur de photos

Petit outil en Python pour ranger automatiquement photos, vidéos et sons
par date de prise de vue, dans une arborescence claire `année/année-mois`.

## Ce qu'il fait

- Trie les **photos** (JPEG, PNG, HEIF/HEIC...) par date EXIF
- Trie les **vidéos** (MP4, MOV...) par date des métadonnées
- Trie les **sons** (MP3, M4A...) par date
- Regroupe les **documents** (PDF, Word, Excel...) dans un dossier à classer
- Détecte les **doublons** par contenu (même renommés) et les met de côté
- Ne supprime jamais rien : il copie ou déplace, jamais d'effacement direct

## Utilisation

1. Installer les dépendances :
