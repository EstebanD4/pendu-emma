#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pendu.py — Jeu du Pendu (console)

Modes :
  1) Contre l'ordinateur : mot aléatoire (depuis words.txt si présent)
  2) À deux : le Joueur 1 saisit un mot secret (saisie masquée)
  3) Mode Histoire : si pendu_histoire.py est présent (niveaux, boutique, etc.)

Fichiers attendus :
  - pendu.py                 (ce fichier)
  - pendu_histoire.py        (optionnel pour le mode histoire)
  - words.txt                (optionnel, un mot par ligne, a–z sans accents)

Exécution :
  python pendu.py
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
import random
import getpass
import sys

# Import optionnel du mode histoire (module séparé)
try:
    from pendu_histoire import run_story_mode  # type: ignore
except Exception:
    run_story_mode = None  # type: ignore


# ================================================================
# Configuration & ressources
# ================================================================
WORDS_FILE = Path(__file__).with_name("words.txt")

# Liste FR simple sans accents (évite les problèmes de saisie a–z)
DEFAULT_WORDS = [
    # Animaux
    "chien","chat","cheval","souris","lapin","renard","loup","poule","canard","vache","mouton",
    "chevre","cochon","ane","panda","zebre","girafe","tigre","lion","ours","dauphin","requin",
    "baleine","perroquet","hibou","escargot","grenouille","papillon","abeille","fourmi",
    # Nature
    "arbre","foret","fleur","rose","tulipe","rivière","lac","ocean","mer","plage","montagne",
    "prairie","colline","vallee","desert","grotte","volcan","neige","orage","pluie","soleil",
    "lune","etoile","nuage","vent",
    # Objets
    "table","chaise","lampe","voiture","camion","velo","moto","train","avion","bouteille",
    "verre","assiette","fourchette","couteau","casserole","chaussure","valise","parapluie",
    "cle","porte","fenetre","miroir","horloge","chapeau",
    # Nourriture
    "pain","baguette","brioche","gateau","tarte","crepe","chocolat","pomme","poire","banane",
    "orange","fraise","raisin","tomate","carotte","fromage","beurre","lait","yaourt","riz",
    "pates","pizza","miel","poisson","viande",
    # Lieux
    "maison","cabane","chateau","ecole","jardin","gare","musee","cinema","parc","zoo","hopital",
    "marche","palais","temple","pont","port","phare","tunnel",
    # Concepts simples
    "amour","amitie","courage","mystere","espoir","reve","voyage","musique","danse","histoire",
]

# Dessins ASCII (7 étapes)
PENDU_STAGES = [
    r"""
     _______
    |/      |
    |
    |
    |
    |
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |
    |
    |
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |       |
    |       |
    |
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |      /|
    |       |
    |
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |      /|\
    |       |
    |
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |      /|\
    |       |
    |      /
    |___
    """,
    r"""
     _______
    |/      |
    |      ( )
    |      /|\
    |       |
    |      / \
    |___   PERDU !
    """,
]
MAX_ERRORS = len(PENDU_STAGES) - 1


# ================================================================
# Outils
# ================================================================
def load_words() -> list[str]:
    """
    Charge words.txt si présent (un mot par ligne, garde a–z uniquement),
    sinon renvoie DEFAULT_WORDS.
    """
    if WORDS_FILE.exists():
        words: list[str] = []
        for line in WORDS_FILE.read_text(encoding="utf-8").splitlines():
            raw = line.strip().lower()
            # garde uniquement a–z (retire espaces/accents/punct)
            clean = "".join(ch for ch in raw if "a" <= ch <= "z")
            if len(clean) >= 3:
                words.append(clean)
        if words:
            return words
    return DEFAULT_WORDS[:]


def norm_letter(s: str) -> str:
    """Retourne la première lettre a–z trouvée, sinon ''. """
    s = s.strip().lower()
    for ch in s:
        if "a" <= ch <= "z":
            return ch
    return ""


def masked_word(word: str, found: set[str]) -> str:
    """Affiche le mot avec _ pour lettres non trouvées."""
    return " ".join(ch if ch in found else "_" for ch in word)


def print_state(word: str, found: set[str], missed: set[str], errors: int) -> None:
    """Affiche le pendu + l'état des lettres."""
    stage = PENDU_STAGES[min(errors, MAX_ERRORS)]
    print(stage)
    print(f"Mot :  {masked_word(word, found)}")
    if missed:
        print("Ratées   :", ", ".join(sorted(missed)))
    if found:
        print("Trouvées :", ", ".join(sorted(found)))
    print(f"Erreurs  : {errors}/{MAX_ERRORS}\n")


# ================================================================
# Mécanique d'une manche
# ================================================================
def ask_letter(already: set[str]) -> str:
    """Demande une lettre non encore proposée, a–z."""
    while True:
        raw = input("Propose une lettre : ")
        letter = norm_letter(raw)
        if not letter:
            print("➡️  Entre une lettre a–z.")
            continue
        if letter in already:
            print("➡️  Lettre déjà proposée.")
            continue
        return letter


def play_round(secret: str) -> bool:
    """
    Joue une manche sur 'secret'.
    Retourne True si victoire, False si défaite.
    """
    found: set[str] = set()
    missed: set[str] = set()
    errors = 0

    while errors < MAX_ERRORS and not set(secret).issubset(found):
        print_state(secret, found, missed, errors)
        letter = ask_letter(found | missed)
        if letter in secret:
            found.add(letter)
        else:
            missed.add(letter)
            errors += 1

    print_state(secret, found, missed, errors)

    if set(secret).issubset(found):
        print(f"🎉 Bravo ! Tu as deviné : {secret}\n")
        return True
    else:
        print(f"💀 Dommage ! Le mot était : {secret}\n")
        return False


# ================================================================
# Modes de jeu
# ================================================================
def choose_mode() -> str:
    """Menu des modes. Renvoie '1', '2' ou '3' (si story dispo)."""
    print("\n===== JEU DU PENDU =====\n")
    print("1) Contre l'ordinateur (mot au hasard)")
    print("2) À deux (Joueur 1 saisit le mot)")
    if run_story_mode is not None:
        print("3) Mode Histoire (niveaux, boutique, sauvegarde)")
    while True:
        choice = input("Choisis le mode [1/2/3] : ").strip()
        if choice in {"1", "2"}:
            return choice
        if choice == "3" and run_story_mode is not None:
            return choice
        print("➡️  Réponds par 1, 2" + (" ou 3" if run_story_mode is not None else "") + ".")


def random_word(pool: list[str]) -> str:
    """Tire un mot au hasard."""
    return random.choice(pool)


def input_secret_word() -> str:
    """
    Demande au Joueur 1 le mot secret, en saisie masquée.
    On garde seulement a–z et on exige 3+ lettres.
    """
    while True:
        raw = getpass.getpass("Joueur 1 — entre le mot secret (saisie masquée) : ").strip().lower()
        clean = "".join(ch for ch in raw if "a" <= ch <= "z")
        if len(clean) >= 3:
            return clean
        print("➡️  Mot invalide : 3 lettres minimum, uniquement a–z.")


# ================================================================
# Boucle principale
# ================================================================
def main() -> None:
    words = load_words()
    wins = 0
    games = 0

    while True:
        mode = choose_mode()

        if mode == "1":
            # contre l'ordi
            secret = random_word(words)
            games += 1
            if play_round(secret):
                wins += 1
            print(f"Score : {wins}/{games} victoires")

        elif mode == "2":
            # à deux
            secret = input_secret_word()
            games += 1
            if play_round(secret):
                wins += 1
            print(f"Score : {wins}/{games} victoires")

        else:
            # histoire
            if run_story_mode is None:
                print("Mode Histoire indisponible (pendu_histoire.py manquant).")
            else:
                run_story_mode(words)  # on passe la même banque de mots (facultatif)

        again = input("Revenir au menu ? (o/n) : ").strip().lower()
        if not again.startswith("o"):
            break

    print("Merci d'avoir joué ! 👋")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterruption. À bientôt !")
        sys.exit(0)
