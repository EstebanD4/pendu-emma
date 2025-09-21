#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pendu_histoire.py — Mode Histoire XXL (console)
================================================

Objectif
--------
Version lisible et "humaine" du mode histoire : mêmes fonctionnalités, code
clarifié et commenté, sans dépendances externes.

Fonctionnalités conservées (identiques à avant)
----------------------------------------------
- 35 niveaux scénarisés avec crescendo (niveaux 1–15 faciles)
- Boutique : indice (20), voyelles (35), vie+ (50), skip (120)
- Inventaire + HOTBAR (4 slots), commandes :
    * lettre a–z : deviner
    * '!' : ouvrir la boutique
    * '?' : afficher le HUD (vies, points, inventaire, hotbar)
    * '1'..'4' : utiliser l'objet sur le slot correspondant
- Sauvegarde persistante JSON : niveau / vies / points / inventaire / hotbar
- Récompense : 10 + (temps restant // 5) + 3*(erreurs épargnées)
- Dictionnaire FR interne (fallback) si la liste passée est vide

API publique (inchangée)
------------------------
- run_story_mode(words: list[str] | None = None, levels: list[Level] | None = None) -> None

Notes d'implémentation
----------------------
- Le code est structuré en sections courtes, avec fonctions mono-responsabilité.
- Les noms sont explicites et les messages utilisateur sont centralisés.
- Le format de sauvegarde et les commandes clavier ne changent PAS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import json
import random
import time

# ================================================================
# Constantes & configuration
# ================================================================
SAVE_FILE = Path("pendu.save.json")
MAX_LIVES = 5
HOTBAR_SLOTS = 4
ITEMS = ("indice", "voyelles", "vie+", "skip")  # noms d'objets utilisés partout
SHOP_PRICES = {"indice": 20, "voyelles": 35, "vie+": 50, "skip": 120}

# Messages (centralisés pour cohérence)
MSG_HUD_HINT = "Actions: lettre | '!' boutique | '?' HUD | '1-4' hotbar"
MSG_NOT_ENOUGH_POINTS = "Pas assez de points."
MSG_TIME_UP = "⏰ Temps écoulé !"
MSG_LEVEL_SKIPPED = "⏭️  Niveau passé !"
MSG_LIFE_MAX = "Vies déjà au maximum."
MSG_LETTER_PROMPT = "> "
MSG_ENTER_LETTER = "➡️  Entre une lettre a–z."
MSG_LETTER_REPEAT = "➡️  Lettre déjà proposée."

# ================================================================
# Dictionnaire interne FR (fallback si la liste fournie est vide)
# ================================================================
FALLBACK_WORDS: List[str] = [
    # Animaux
    "chien","chat","cheval","âne","mule","vache","taureau","veau","mouton","brebis","chèvre",
    "porc","truie","lapin","hamster","rat","souris","gerbille","furet","renard","loup","lynx",
    "tigre","lion","panthère","léopard","guépard","ours","koala","panda","zèbre","girafe",
    "éléphant","hippopotame","rhinocéros","dauphin","baleine","requin","raie","pieuvre","méduse",
    "crabe","homard","huître","escargot","grenouille","triton","salamandre","lézard","gecko",
    "crocodile","alligator","tortue","aigle","faucon","hibou","chouette","perroquet","rossignol",
    "moineau","colombe","canari","canard","oie","cygne","dindon","poule","coq","dromadaire",
    "chameau","lama","alpaga","yack","bison","antiloppe","gazelle","chevreuil","cerf","sanglier",
    # Nature
    "arbre","forêt","branche","racine","fleur","pétale","rose","tulipe","lys","jonquille",
    "pâquerette","pollen","grain","graine","prairie","champ","colline","montagne","vallée",
    "falaise","grotte","caverne","rivière","ruisseau","torrent","cascade","lac","océan","mer",
    "plage","dune","désert","oasis","glacier","iceberg","neige","grêle","pluie","bruine",
    "nuage","ciel","aurore","crépuscule","étoile","constellation","comète","lune","soleil",
    "éclair","tonnerre","orage","tempête","ouragan","cyclone","brise","zéphyr",
    # Objets du quotidien
    "table","chaise","tabouret","canapé","fauteuil","lampe","ampoule","rideau","volet","fenêtre",
    "porte","clé","serrure","miroir","horloge","montre","calendrier","couteau","fourchette",
    "cuillère","assiette","bol","verre","bouteille","carafe","tasse","théière","casserole",
    "poêle","faitout","louche","écumoire","entonnoir","éponge","balai","seau","serpillière",
    "bouton","fil","aiguille","ciseaux","colle","papier","carnet","cahier","stylo","crayon",
    "règle","trousse","cartable","valise","sac","parapluie","capuche","manteau","chapeau",
    "bonnet","gants","écharpe","chaussure","botte","pantoufle",
    # Nourriture
    "pain","baguette","brioche","croissant","beignet","gâteau","tarte","crêpe","galette",
    "chocolat","vanille","caramel","miel","confiture","yaourt","fromage","beurre","lait",
    "œuf","omelette","huile","vinaigre","sel","poivre","herbes","épices","basilic","thym",
    "romarin","curry","piment","riz","pâtes","semoule","blé","farine","pomme","poire",
    "banane","orange","citron","pamplemousse","fraise","framboise","cerise","raisin","figue",
    "abricot","pêche","melon","pastèque","kiwi","ananas","tomate","carotte","oignon","ail",
    "échalote","poireau","chou","salade","concombre","courgette","aubergine","brocoli",
    "petitpois","haricot","lentille","pois chiche","maïs","poisson","truite","saumon","thon",
    "crevette","moule","huître","calamar","viande","bœuf","veau","porc","agneau","poulet",
    "dinde","canard","saucisse","jambon",
    # Lieux & constructions
    "maison","cabane","chalet","immeuble","appartement","grenier","cave","garage","atelier",
    "hangar","grange","ferme","château","tour","donjon","citadelle","palais","temple","église",
    "cathédrale","mosquée","synagogue","bibliothèque","musée","théâtre","cinéma","hôtel","auberge",
    "restaurant","boulangerie","boucherie","épicerie","marché","place","parc","jardin","serre",
    "zoo","aquarium","hôpital","clinique","école","collège","lycée","université","laboratoire",
    "mairie","préfecture","tribunal","prison","caserne","gare","aéroport","port","phare","pont",
    "route","autoroute","tunnel","rondpoint","parking","station",
    # Transports
    "voiture","camion","bus","car","métro","tramway","train","locomotive","wagon","vélo",
    "trotinette","moto","scooter","avion","hélicoptère","planeur","bateau","voilier","yacht",
    "canoë","kayak","pagaie","raquette","patin","luge","traîneau","montgolfière",
    # Concepts & divers
    "amour","amitié","joie","tristesse","colère","peur","courage","honneur","espoir","rêve",
    "légende","mythe","magie","sortilège","sorcier","sorcière","dragon","chevalier","princesse",
    "prince","roi","reine","pirate","corsaire","trésor","carte","boussole","lanterne","torche",
    "armure","bouclier","épée","lance","arc","flèche","carquois","harpe","flûte","tambour",
    "violon","piano","trompette","guitare","clarinette","saxophone","accordéon",
]

# ================================================================
# Modèles de données
# ================================================================
@dataclass
class Level:
    """Décrit les contraintes d'un niveau de l'histoire."""
    name: str
    min_len: int
    max_len: int | None
    max_errors: int
    time_limit: int
    flavor: str  # narration concise

@dataclass
class Save:
    """État persistant de la progression du joueur."""
    level_idx: int = 0
    lives: int = 3
    points: int = 0
    inventory: Dict[str, int] = field(default_factory=lambda: {k: 0 for k in ITEMS})
    hotbar: List[str] = field(default_factory=lambda: ["", "", "", ""])  # 4 slots

    @classmethod
    def load(cls) -> "Save":
        """Charge la sauvegarde JSON si disponible, sinon valeurs par défaut."""
        if SAVE_FILE.exists():
            try:
                data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
                s = cls()
                s.level_idx = int(data.get("level_idx", s.level_idx))
                s.lives = int(data.get("lives", s.lives))
                s.points = int(data.get("points", s.points))
                inv = data.get("inventory", {})
                s.inventory = {k: int(inv.get(k, 0)) for k in ITEMS}
                hb = data.get("hotbar", s.hotbar)
                if isinstance(hb, list) and len(hb) == HOTBAR_SLOTS:
                    s.hotbar = [v if v in ITEMS else "" for v in hb]
                return s
            except Exception:
                # sauvegarde corrompue → repartir proprement
                pass
        return cls()

    def store(self) -> None:
        """Écrit la sauvegarde JSON (format stable)."""
        payload = {
            "level_idx": self.level_idx,
            "lives": self.lives,
            "points": self.points,
            "inventory": self.inventory,
            "hotbar": self.hotbar,
        }
        SAVE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

# ================================================================
# Niveaux scénarisés — 35 étapes (1–15 faciles, puis crescendo)
# ================================================================
STORY_LEVELS: List[Level] = [
    # 1–15 : faciles
    Level("Village",        3, 5, 8, 150, "Tu démarres dans un village paisible."),
    Level("Prairie",        3, 5, 8, 140, "L'herbe ondule sous la brise légère."),
    Level("Verger",         3, 6, 8, 140, "Des fruits mûrs parfument l'air."),
    Level("Ruisseau",       3, 6, 8, 135, "L'eau claire te montre le chemin."),
    Level("Fourré",         3, 6, 8, 130, "Des feuillages bruissent autour de toi."),
    Level("Bosquet",        3, 6, 7, 130, "Tu avances entre les troncs serrés."),
    Level("Sentier",        3, 6, 7, 125, "Le sentier serpente, tranquille."),
    Level("Pont de bois",   4, 6, 7, 125, "Un vieux pont grince à chacun de tes pas."),
    Level("Moulin",         4, 6, 7, 120, "Les ailes tournent au rythme du vent."),
    Level("Chapelle",       4, 6, 7, 120, "Un silence sacré t'encourage à poursuivre."),
    Level("Forêt",          4, 7, 7, 115, "Les grands arbres cachent la lumière."),
    Level("Marais",         4, 7, 7, 110, "Le sol s'enfonce sous tes pas prudents."),
    Level("Colline",        4, 7, 7, 110, "La vue s'élargit à mesure que tu montes."),
    Level("Tour en ruine",  4, 7, 7, 105, "Des pierres moussues murmurent l'ancien temps."),
    Level("Rempart",        4, 7, 7, 105, "Des créneaux veillent sur la vallée."),
    # 16–25 : moyen
    Level("Vallée",         5, 8, 6, 100, "Un écho ramène tes pas vers toi-même."),
    Level("Rivière",        5, 8, 6, 100, "Le courant te défie, mais un gué apparaît."),
    Level("Grotte",         5, 8, 6,  95, "La roche suinte, l'air se fait frais."),
    Level("Marbre ancien",  5, 8, 6,  95, "Un dallage gravé t'intrigue."),
    Level("Pont de pierre", 6, 9, 6,  90, "Le fleuve rugit sous tes pas confiants."),
    Level("Falaises",       6, 9, 6,  90, "Le vent hurle, la mer écume au loin."),
    Level("Montagnes",      6,10, 6,  85, "L'air devient mince, le ciel se durcit."),
    Level("Bastion",        6,10, 6,  85, "Des meurtrières surveillent l'horizon."),
    Level("Canyon",         7,10, 6,  80, "Les parois rouges enferment ta voix."),
    Level("Glacier",        7,10, 6,  80, "La glace craque comme un parchemin."),
    # 26–35 : difficile
    Level("Jungle",         8,11, 5,  75, "Des cris lointains déchirent la canopée."),
    Level("Temple",         8,11, 5,  75, "Des fresques racontent une histoire perdue."),
    Level("Labyrinthe",     9,12, 5,  70, "Chaque tournant peut t'égarer."),
    Level("Catacombes",     9,12, 5,  70, "Les couloirs sentent la poussière des âges."),
    Level("Forteresse",    10,13, 5,  65, "Des portes massives défient ta volonté."),
    Level("Observatoire",  10,13, 5,  65, "Les astres semblent guider tes pas."),
    Level("Mécanismes",    10,14, 5,  60, "Des rouages grincent dans l'ombre."),
    Level("Hall des échos",10,14, 5,  60, "Chaque mot devient énigme et indice."),
    Level("Avant-cour",    11,15, 5,  55, "La Citadelle n'est plus qu'à un souffle."),
    Level("Citadelle",     12,None,4,  55, "Le cœur du mystère bat derrière ces portes."),
]

# ================================================================
# Affichage & saisie
# ================================================================
PENDU_STAGES_ASCII = [
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


def _normalize_letter(s: str) -> str:
    """Renvoie la première lettre a–z de la saisie (en minuscule), sinon ''."""
    s = s.strip().lower()
    for ch in s:
        if "a" <= ch <= "z":
            return ch
    return ""


def _mask_word(word: str, found: set[str]) -> str:
    return " ".join(ch if ch in found else "_" for ch in word)


def _print_state(word: str, found: set[str], missed: set[str], errors: int, max_errors: int, time_left: int | None) -> None:
    stage_idx = min(errors, len(PENDU_STAGES_ASCII) - 1)
    print(PENDU_STAGES_ASCII[stage_idx])
    print(f"Mot :  {_mask_word(word, found)}")
    if missed:
        print("Ratées : " + ", ".join(sorted(missed)))
    if found:
        print("Trouvées : " + ", ".join(sorted(found)))
    extra = f" | Temps restant : {time_left}s" if time_left is not None else ""
    print(f"Erreurs : {errors}/{max_errors}{extra}\n")


def _print_hud(save: Save) -> None:
    inv = " ".join(f"{k}:{save.inventory.get(k, 0)}" for k in ITEMS)
    hb = " ".join(f"[{i + 1}:{(save.hotbar[i] or '-')}]" for i in range(HOTBAR_SLOTS))
    print(f"HUD → Vies:{save.lives}  Points:{save.points}  Inv: {inv}  Hotbar: {hb}")

# ================================================================
# Boutique / Hotbar
# ================================================================

def _shop_menu(save: Save) -> str | None:
    """Achète un objet si points suffisants. Retourne l'objet acheté ou None."""
    print("\n🛒 Boutique — Points:", save.points)
    print("  (i) indice (20)   (v) voyelles (35)   (l) vie+1 (50)   (s) skip niveau (120)   (autre) quitter")
    choice = input("Choix: ").strip().lower()
    mapping = {"i": "indice", "v": "voyelles", "l": "vie+", "s": "skip"}
    item = mapping.get(choice)
    if not item:
        return None
    price = SHOP_PRICES[item]
    if save.points < price:
        print(MSG_NOT_ENOUGH_POINTS)
        return None
    save.points -= price
    save.inventory[item] = save.inventory.get(item, 0) + 1
    print(f"✔️  {item} acheté. Inv[{item}] = {save.inventory[item]}")
    return item


def _manage_hotbar(save: Save) -> None:
    """Permet d'assigner les objets de l'inventaire aux 4 slots de la hotbar."""
    _print_hud(save)
    if not input("Configurer la hotbar ? (o/n) : ").strip().lower().startswith("o"):
        return
    while True:
        _print_hud(save)
        print("Tape 'slot index' (ex: 1 indice), 'clear n' pour vider un slot, ou 'ok' pour finir.")
        cmd = input(MSG_LETTER_PROMPT).strip().lower()
        if cmd in ("ok", "quit", "q"):
            break
        if cmd.startswith("clear "):
            try:
                n = int(cmd.split()[1])
                if 1 <= n <= HOTBAR_SLOTS:
                    save.hotbar[n - 1] = ""
            except Exception:
                pass
            continue
        parts = cmd.split()
        if len(parts) == 2:
            try:
                n = int(parts[0])
            except ValueError:
                print("Format: <slot 1-4> <objet>")
                continue
            item = parts[1]
            if item not in ITEMS:
                print("Objet inconnu. Choix:", ", ".join(ITEMS))
                continue
            if 1 <= n <= HOTBAR_SLOTS:
                save.hotbar[n - 1] = item
        else:
            print("Exemples: '1 indice', '2 voyelles', 'clear 3', 'ok'")

# ================================================================
# Objets (application)
# ================================================================

def _apply_item(item: str, word: str, found: set[str], save: Save) -> Tuple[bool, str]:
    """Applique l'effet d'un objet.
    Retourne (consumé?, message). Ne modifie pas le compteur d'erreurs.
    """
    if item == "vie+":
        if save.lives >= MAX_LIVES:
            return False, MSG_LIFE_MAX
        save.lives += 1
        return True, "❤️ +1 vie !"

    if item == "skip":
        return True, MSG_LEVEL_SKIPPED

    if item == "voyelles":
        revealed = 0
        for ch in set("aeiouy") & set(word):
            if ch not in found:
                found.add(ch)
                revealed += 1
        msg = "💡 Aucune voyelle à révéler." if revealed == 0 else f"💡 Voyelles révélées (+{revealed})."
        return True, msg

    if item == "indice":
        remain = sorted(set(word) - found)
        if not remain:
            return False, "Aucune lettre restante à révéler."
        h = random.choice(remain)
        found.add(h)
        return True, f"💡 Indice : '{h}'"

    return False, "Objet inconnu."


def _use_hotbar(slot: int, word: str, found: set[str], save: Save) -> Tuple[bool, bool]:
    """Utilise l'objet d'un slot si présent. Retourne (utilisé?, skip_niveau?)."""
    if not (1 <= slot <= HOTBAR_SLOTS):
        return False, False
    item = save.hotbar[slot - 1]
    if not item:
        print("(slot vide)")
        return False, False
    if save.inventory.get(item, 0) <= 0:
        print(f"(pas de {item} en stock)")
        return False, False

    consumed, msg = _apply_item(item, word, found, save)
    print(msg)
    if consumed:
        save.inventory[item] -= 1
        if item == "skip":
            return True, True
    return consumed, False

# ================================================================
# Boucle de manche
# ================================================================

def _play_round(word: str, max_errors: int, time_limit: int, save: Save) -> Tuple[bool, int, int]:
    """Joue une manche et renvoie (victoire, erreurs_utilisées, temps_restant)."""
    found: set[str] = set()
    missed: set[str] = set()
    errors = 0
    start = time.time()

    # Préparation : boutique + hotbar
    _print_hud(save)
    if input("Ouvrir la boutique avant de jouer ? (o/n) : ").strip().lower().startswith("o"):
        while True:
            bought = _shop_menu(save)
            save.store()
            if not bought:
                break
            if not input("Acheter autre chose ? (o/n) : ").strip().lower().startswith("o"):
                break
    _manage_hotbar(save)
    save.store()

    # Boucle principale
    while errors < max_errors and not set(word).issubset(found):
        elapsed = int(time.time() - start)
        time_left = max(0, time_limit - elapsed)
        if time_left <= 0:
            print(MSG_TIME_UP)
            break

        _print_state(word, found, missed, errors, max_errors, time_left)
        _print_hud(save)
        print(MSG_HUD_HINT)

        raw = input(MSG_LETTER_PROMPT).strip().lower()
        if raw == '!':
            _shop_menu(save)
            save.store()
            continue
        if raw == '?':
            _print_hud(save)
            continue
        if raw in {'1','2','3','4'}:
            used, skip = _use_hotbar(int(raw), word, found, save)
            save.store()
            if skip:
                # niveau passé immédiatement
                elapsed = int(time.time() - start)
                time_left = max(0, time_limit - elapsed)
                return True, errors, time_left
            continue

        letter = _normalize_letter(raw)
        if not letter:
            print(MSG_ENTER_LETTER)
            continue
        if letter in found or letter in missed:
            print(MSG_LETTER_REPEAT)
            continue
        if letter in word:
            found.add(letter)
        else:
            missed.add(letter)
            errors += 1

    elapsed = int(time.time() - start)
    time_left = max(0, time_limit - elapsed)
    win = set(word).issubset(found)
    _print_state(word, found, missed, errors, max_errors, time_left)
    print(f"🎉 Bravo ! Mot trouvé : {word}\n" if win else f"💀 Dommage ! Le mot était : {word}\n")
    return win, errors, time_left

# ================================================================
# Score & sélection de mots
# ================================================================
def _compute_reward(win: bool, max_errors: int, errors_used: int, time_left: int) -> int:
    """Calcule le gain de points pour une manche gagnée."""
    if not win:
        return 0
    spared = max(0, max_errors - errors_used)
    return 10 + time_left // 5 + spared * 3


def _choose_word(pool: Iterable[str], min_len: int, max_len: int | None) -> str:
    """Choisit un mot satisfaisant les bornes, sinon fallback large."""
    candidates = [w for w in pool if len(w) >= min_len and (max_len is None or len(w) <= max_len)]
    if not candidates:
        # fallback très défensif
        candidates = list(pool) or FALLBACK_WORDS
    return random.choice(candidates)

# ================================================================
# API publique : run_story_mode
# ================================================================

def run_story_mode(words: List[str] | None = None, levels: List[Level] | None = None) -> None:
    """Lance le Mode Histoire.

    Paramètres
    ----------
    words : liste optionnelle de mots (chaîne ≥ 3). Si vide → dictionnaire interne FR.
    levels : liste optionnelle de niveaux pour surcharger le scénario par défaut.
    """
    # Prépare la banque de mots
    pool = [w.strip().lower() for w in (words or []) if isinstance(w, str) and len(w.strip()) >= 3]
    if not pool:
        pool = FALLBACK_WORDS[:]  # dictionnaire interne

    # Charge scénario & sauvegarde
    story = levels or STORY_LEVELS
    save = Save.load()

    print("\n🎮 MODE HISTOIRE — Reprise de sauvegarde" if SAVE_FILE.exists() else "\n🎮 MODE HISTOIRE — Nouvelle aventure")
    print(f"Niveau: {save.level_idx + 1}/{len(story)} | Vies: {save.lives} | Points: {save.points}\n")

    # Boucle d'aventure
    while save.lives > 0 and save.level_idx < len(story):
        lv = story[save.level_idx]
        print(f"=== Niveau {save.level_idx + 1}/{len(story)} — {lv.name} ===")
        print(lv.flavor)
        print(f"Objectif: {lv.min_len}–{lv.max_len or '∞'} lettres | Erreurs: {lv.max_errors} | Temps: {lv.time_limit}s\n")

        word = _choose_word(pool, lv.min_len, lv.max_len)
        win, used, tleft = _play_round(word, lv.max_errors, lv.time_limit, save)
        gained = _compute_reward(win, lv.max_errors, used, tleft)

        if win:
            save.points += gained
            save.level_idx += 1
            print(f"✨ +{gained} pts | Total: {save.points}\n")
        else:
            save.lives -= 1
            print(f"💔 Vie perdue ! Vies restantes: {save.lives}\n")

        save.store()

        # Pause entre niveaux si on continue
        if save.lives > 0 and save.level_idx < len(story):
            if not input("Continuer l'aventure ? (o/n) : ").strip().lower().startswith("o"):
                print("Sauvegarde enregistrée. À bientôt !")
                return

    # Épilogue
    if save.level_idx >= len(story):
        print("🏆 BRAVO ! Tu as percé le mystère de la Citadelle !")
    else:
        print("☠️  Game Over. Reviens plus fort !")

    # Option : reset de la sauvegarde
    if input("Réinitialiser la sauvegarde ? (o/n) : ").strip().lower().startswith("o"):
        try:
            SAVE_FILE.unlink(missing_ok=True)
            print("Sauvegarde supprimée.")
        except Exception:
            pass
