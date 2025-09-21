# Jeu du Pendu — Console (FR)

Un **pendu** fun en Python avec :
- 3 modes de jeu (ordi, à deux, **Mode Histoire**),
- une **boutique**, un **inventaire** et une **hotbar** (4 slots),
- **35 niveaux scénarisés** en crescendo,
- **sauvegarde auto** de la progression.

> Zéro dépendance externe. Fonctionne sur Windows, macOS, Linux.

---

## 📦 Contenu du dépôt

```
pendu.py               # jeu console classique (vs ordi / à deux / accès Mode Histoire)
pendu_histoire.py      # Mode Histoire XXL (niveaux, boutique, inventaire + hotbar)
words.txt              # (optionnel) dictionnaire perso — 1 mot par ligne
pendu.save.json        # (auto) sauvegarde (créée/MAJ en jeu)
```

---

## 🚀 Installation

1) **Pré-requis**
- Python **3.9+**
- Un terminal (cmd/PowerShell, Terminal, etc.)

2) **Cloner ou télécharger** le projet, puis ouvrir le dossier.

3) (Optionnel) créer un venv :
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

> Aucune librairie à installer : **tout est en standard**.

---

## ▶️ Lancer le jeu

### Mode classique + Histoire (menu)
```bash
python pendu.py
```

- `1` : **Contre l’ordinateur** — mot au hasard (depuis `words.txt` s’il existe).
- `2` : **À deux** — Joueur 1 saisit un mot **masqué**, Joueur 2 devine.
- `3` : **Mode Histoire** — si `pendu_histoire.py` est présent.

---

## 🎮 Commandes (rappel)

### Pendu classique
- Tape une **lettre** `a–z` pour jouer.

### Mode Histoire
- **Lettre `a–z`** : deviner
- **`!`** : ouvrir la **boutique**
- **`?`** : afficher le **HUD** (vies, points, inventaire, hotbar)
- **`1` `2` `3` `4`** : **utiliser** l’objet du **slot** correspondant (hotbar)

### Boutique (coûts)
- `indice` **20** — révèle 1 lettre
- `voyelles` **35** — révèle toutes les voyelles
- `vie+` **50** — +1 vie (max 5)
- `skip` **120** — passe le niveau

> Les achats vont dans l’**inventaire**.  
> Pour les **utiliser**, équipe-les sur la **hotbar** puis appuie sur **1–4** pendant la manche.

---

## 📖 Mode Histoire — détails

- **35 niveaux** avec narration courte :
  - **Niveaux 1–15** : simples (mots courts, temps généreux, 7–8 erreurs).
  - **16–25** : moyens.
  - **26–35** : exigeants (mots plus longs, temps réduit).
- **Points** gagnés si victoire :  
  `10 + (temps_restant // 5) + 3*(erreurs_épargnées)`
- **Sauvegarde** auto dans `pendu.save.json` (niveau, vies, points, inventaire, hotbar).
- Fin de partie : option de **réinitialiser** la sauvegarde.

---

## 🧩 Personnaliser les mots

### Option 1 — `words.txt` (recommandé)
Crée un fichier **`words.txt`** dans le même dossier, avec **1 mot par ligne** :
```
chien
plage
chateau
lampe
foret
...
```
> Le jeu ne garde que `a–z` (sans accents) pour que la saisie reste simple.  
> Idéalement, mets tes mots **sans espaces ni accents**.

### Option 2 — modifier les listes internes
- `pendu.py` : liste simple **sans accents** (classique).
- `pendu_histoire.py` : **FALLBACK_WORDS** (liste FR riche, avec accents — gérée en interne).

---

## 🧠 Conseils & astuces

- Dans le Mode Histoire, avant la manche, tu peux **acheter** puis **gérer la hotbar** :
  - ex : `1 indice`, `2 voyelles`, `clear 2`, `ok`…
- Tu manques de points ? Privilégie **indice** (20) pour un boost rapide.
- Utilise **skip** avec parcimonie (cher) pour franchir un niveau **vraiment** difficile.

---

## 🛠️ Dépannage

- **Windows / accents** : si tu vois des caractères bizarres, essaye :
  ```bash
  chcp 65001
  ```
- **Saisie masquée** qui ne marche pas dans l’IDE** : certains IDE gèrent mal `getpass`.
  Lance dans un **terminal** :
  ```bash
  python pendu.py
  ```
- **Reset complet** :
  - supprimer `pendu.save.json`
  - relancer `python pendu.py`

---

## 🗂️ Structure du code

### `pendu.py`
- Menu modes (1, 2, 3 si Histoire dispo)
- Pendu **classique** :
  - tirage du mot
  - boucle de jeu (état ASCII, lettres trouvées/ratées)
- Mode **à deux** avec saisie masquée
- Import optionnel du **Mode Histoire**

### `pendu_histoire.py`
- **Niveaux** (classe `Level` + liste `STORY_LEVELS`)
- **Sauvegarde** (classe `Save` → JSON)
- **HUD** / **boutique** / **inventaire** / **hotbar**
- **Effets** des objets (`indice`, `voyelles`, `vie+`, `skip`)
- Boucle **manche** + **récompenses**
- API : `run_story_mode(words: list[str]|None = None, levels: list[Level]|None = None)`

---

## 🧰 Exemples de commandes

Lancer directement le Mode Histoire (si tu veux bypasser le menu, en important manuellement) :
```python
# depuis un shell Python
from pendu_histoire import run_story_mode
run_story_mode()  # utilisera la liste interne si tu ne fournis pas de mots
```

---

## 🗺️ Roadmap (idées futures)

- Catégories au lancement (Animaux / Nature / Objets / Mix)
- Niveaux “**boss**” (règles spéciales : temps gelé, lettres piégées…)
- **High-scores** multi-profils
- **Journal** des mots découverts
- **Export CSV** des runs (points, temps, erreurs)

---

## 📜 Licence

Fais-en ce que tu veux pour apprendre, jouer, ou le customiser.  
Si tu le partages, un petit crédit “basé sur le Pendu FR console par EstebanD4” fait plaisir 😉

---

## 💬 Contact / feedback

Tu veux :
- un **`words.txt`** prêt à coller (300+ mots sans accents) ?
- un **mode ironman** (1 vie) ?
- une **version GUI** (tkinter / PySide) plus tard ?

Dis-moi et je regarderais se que je peux faire  !
