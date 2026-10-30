"""
== Calculateur Numéro de Sécurité Sociale ==

Sécurité Sociale (NIR) - Numéro d'Inscription au Répertoire national d'identification des personnes physiques
Ce module fournit des fonctions pour calculer et valider le numéro de sécurité sociale français (NIR) basé sur les informations personnelles telles que le sexe, l'année et le mois de naissance, le code INSEE de naissance et le numéro d'ordre. Il inclut également une interface interactive pour faciliter l'utilisation.

Auteur: GauGoth Corp.

Copyright: Copyright (c) 2021-2026 GauGoth Corp. Tous droits réservés.

Version: 2.0
"""

import sys
import os
import json
import urllib.request
import urllib.error

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False
    print("\n== WARNING: Rich module not found. In order to have colored console output, please install rich with 'pip install rich'. ==")


def _is_pycharm_console():
    """
    Returns True when running in a PyCharm-hosted console.
    """
    return os.environ.get("PYCHARM_HOSTED") == "1" or "PYCHARM_DISPLAY_PORT" in os.environ


def _use_classic_output():
    """
    Uses plain prints when rich is unavailable or when PyCharm console is detected.
    """
    return (not RICH_AVAILABLE) or _is_pycharm_console()


def __print_message(msg, title, color, width=60):
    """
    Private function to print a message with a specific title and color. 
    Allows to skip error printing if rich is not installed, without breaking the code.

    :param msg: The message to print
    :param title: The title of the message (e.g., "INFO", "WARNING", "ERROR", "SUCCESS")
    :param color: The color to use for the message (e.g., "blue", "yellow", "red", "green")
    """
    if _use_classic_output():
        print(f"[{title}] {msg}")
        return

    try:
        console.print(Panel(msg, title=f"[bold]{title}[/bold]", border_style=color, width=width))
    except Exception:
        print(f"[{title}] {msg}")


def to_ordinal_number(n):
    """
    Converts an integer to its ordinal representation as a string (e.g., 1 -> "1st", 2 -> "2nd", etc.)

    :param n: The integer to convert
    :return: The ordinal representation of the integer as a string
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def to_french_ordinal(n: int) -> str:
    """
    Convertit un entier en son ordinal en français (1 -> 1er, 2 -> 2e).
    """
    return "1er" if n == 1 else f"{n}e"

#%%#################### RICH CONSOLE OUTPUT ########################
####################################################################

def print_info(msg, width=80):
    """
    Prints an informational message to the console in blue color.
    """
    __print_message(msg, "INFO", "blue", width=width)


def print_success(msg, width=80):
    """
    Prints a success message to the console in green color.
    """
    __print_message(msg, "SUCCESS", "green", width=width)


def print_warning(msg, width=80):
    """
    Prints a warning message to the console in yellow color.
    """
    __print_message(msg, "WARNING", "yellow", width=width)


def print_error(msg, width=80):
    """
    Prints an error message to the console in red color.
    """
    __print_message(msg, "ERROR", "red", width=width)


def print_countdown(seconds):
    """
    Prints a colored countdown with progress bar using rich.

    :param seconds: The number of seconds for the countdown
    """
    import time
    if _use_classic_output():
        for remaining in range(seconds, 0, -1):
            print(f"{remaining} ", end="", flush=True)
            time.sleep(1)
        print("Done!")
        return

    try:
        from rich.progress import Progress

        with Progress() as progress:
            task = progress.add_task("[cyan]Countdown[/cyan]", total=seconds)
            for remaining in range(seconds, 0, -1):
                progress.update(task, advance=1, description=f"[cyan]{remaining}s[/cyan]")
                time.sleep(1)
            progress.update(task, description="[green]Done![/green]")
    except Exception:
        for remaining in range(seconds, 0, -1):
            print(f"{remaining} ", end="", flush=True)
            time.sleep(1)
        print("Done!")

#%%############# RICH CONSOLE INPUT ########################
############################################################

def prompt_input(prompt, default=None) -> str:
    """
    Prompts the user for input with a colored prompt using rich.

    :param prompt: The prompt message to display
    :param default: The default value to return if the user provides no input
    :return: The user's input or the default value if no input is provided
    """
    if _use_classic_output():
        user_input = input(f"{prompt} ")
        return user_input if user_input else default

    try:
        from rich.prompt import Prompt
        user_input = Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]", default=default)
        return user_input
    except Exception:
        user_input = input(f"{prompt} ")
        return user_input if user_input else default


def prompt_int(prompt, requestNb=None, default=None) -> str:
    """
    Demande un entier positif sous forme de chaîne pour conserver les zéros initiaux.
    """
    retry = True
    outputStr = ""
    while retry:
        outputStr = prompt_input(prompt, default=default)
        if outputStr is not None:
            outputStr = str(outputStr).strip()
        else:
            outputStr = ""

        if requestNb is None or len(outputStr) == requestNb:
            if outputStr.isdigit():
                retry = False
            else:
                print_warning("Attention ! Veuillez entrer un nombre entier positif.")
        else:
            print_warning(f"Veuillez entrer exactement {requestNb} caractères !")
    return outputStr


def prompt_sex(prompt, default=None) -> str:
    """
    Demande le sexe de la personne (1 pour Homme, 2 pour Femme).
    """
    while True:
        val = prompt_input(prompt, default=default)
        if val is not None:
            val = str(val).strip()
        if val in ["1", "2"]:
            return val
        print_warning("Attention ! Veuillez entrer 1 pour un homme ou 2 pour une femme.")


def prompt_month(prompt, default=None) -> str:
    """
    Demande un mois de naissance valide compris strictement entre 01 et 12.
    """
    while True:
        val = prompt_input(prompt, default=default)
        if val is not None:
            val = str(val).strip()
        else:
            val = ""

        if val.isdigit():
            m = int(val)
            if 1 <= m <= 12:
                return f"{m:02d}"
        print_warning("Attention ! Le mois de naissance doit être compris entre 01 et 12 (ex: 05 pour mai).")


def prompt_postal_code(prompt, default=None) -> str:
    """
    Demande un code INSEE de commune, pays ou territoire et valide son existence effective.
    """
    while True:
        outputStr = prompt_input(prompt, default=default)
        if outputStr is not None:
            outputStr = str(outputStr).strip().upper()
        else:
            outputStr = ""

        # Format syntaxique attendu
        valid_format = (len(outputStr) == 5 and outputStr.isdigit()) or (
            len(outputStr) == 5 and outputStr[:2] in ["2A", "2B"] and outputStr[2:].isdigit()
        )

        if valid_format:
            location_name = get_insee_location(outputStr)
            if location_name:
                print_info(f"Lieu de naissance identifié : {location_name}")
                return outputStr
            else:
                print_warning(f"Le code INSEE '{outputStr}' n'a pas été trouvé dans le référentiel officiel. Veuillez entrer un code existant.")
        else:
            print_warning("Veuillez entrer un code de commune INSEE valide (5 chiffres ou 2A/2B suivi de 3 chiffres).")

#%%################ RÉFÉRENTIEL GÉOGRAPHIQUE INSEE #################
####################################################################

# Départements français officiels
DEPARTEMENTS_FRANCE = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes",
    "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron",
    "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal", "16": "Charente",
    "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud",
    "2B": "Haute-Corse", "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse",
    "24": "Dordogne", "25": "Doubs", "26": "Drôme", "27": "Eure",
    "28": "Eure-et-Loir", "29": "Finistère", "30": "Gard", "31": "Haute-Garonne",
    "32": "Gers", "33": "Gironde", "34": "Hérault", "35": "Ille-et-Vilaine",
    "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire",
    "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne",
    "48": "Lozère", "49": "Maine-et-Loire", "50": "Manche", "51": "Marne",
    "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle", "55": "Meuse",
    "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques", "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin",
    "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône", "71": "Saône-et-Loire",
    "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie", "75": "Paris",
    "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres",
    "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var",
    "84": "Vaucluse", "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne",
    "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort", "91": "Essonne",
    "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis", "94": "Val-de-Marne", "95": "Val-d'Oise",
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion",
    "975": "Saint-Pierre-et-Miquelon", "976": "Mayotte", "977": "Saint-Barthélemy",
    "978": "Saint-Martin", "984": "Terres australes et antarctiques françaises",
    "986": "Wallis-et-Futuna", "987": "Polynésie française", "988": "Nouvelle-Calédonie",
    "989": "Île de Clipperton"
}

# Base de données détaillée : Codes pays (COG 99XXX), Afrique du Nord historique, arrondissements PLM et chefs-lieux
INSEE_DATABASE = {
    # --- PAYS ÉTRANGERS (CODE OFFICIEL GÉOGRAPHIQUE COG - PRÉFIXE 99) ---
    # Europe
    "99101": "Danemark / Îles Féroé (Pays étranger)", "99102": "Islande (Pays étranger)",
    "99103": "Norvège (Pays étranger)", "99104": "Suède (Pays étranger)", "99105": "Finlande (Pays étranger)",
    "99106": "Estonie (Pays étranger)", "99107": "Lettonie (Pays étranger)", "99108": "Lituanie (Pays étranger)",
    "99109": "Allemagne (Pays étranger)", "99110": "Autriche (Pays étranger)", "99111": "Bulgarie (Pays étranger)",
    "99112": "Hongrie (Pays étranger)", "99113": "Liechtenstein (Pays étranger)", "99114": "Roumanie (Pays étranger)",
    "99115": "Tchécoslovaquie (ancien État) (Pays étranger)", "99116": "Tchéquie (République tchèque) (Pays étranger)",
    "99117": "Slovaquie (Pays étranger)", "99118": "Bosnie-Herzégovine (Pays étranger)", "99119": "Croatie (Pays étranger)",
    "99120": "Monténégro (Pays étranger)", "99121": "Serbie (Pays étranger)", "99122": "Pologne (Pays étranger)",
    "99123": "Russie / Ex-URSS (Pays étranger)", "99124": "Turquie d'Europe (Pays étranger)", "99125": "Albanie (Pays étranger)",
    "99126": "Grèce (Pays étranger)", "99127": "Italie (Pays étranger)", "99128": "Saint-Marin (Pays étranger)",
    "99129": "Vatican (Saint-Siège) (Pays étranger)", "99130": "Andorre (Pays étranger)", "99131": "Belgique (Pays étranger)",
    "99132": "Royaume-Uni (Grande-Bretagne, Irlande du Nord) (Pays étranger)", "99133": "Gibraltar (Pays étranger)",
    "99134": "Espagne (Pays étranger)", "99135": "Pays-Bas (Pays étranger)", "99136": "Irlande (Éire) (Pays étranger)",
    "99137": "Luxembourg (Pays étranger)", "99138": "Monaco (Pays étranger)", "99139": "Portugal (Pays étranger)",
    "99140": "Suisse (Pays étranger)", "99141": "République démocratique allemande (ex-RDA) (Pays étranger)",
    "99144": "Malte (Pays étranger)", "99145": "Slovénie (Pays étranger)", "99148": "Biélorussie (Pays étranger)",
    "99151": "Moldavie (Pays étranger)", "99155": "Ukraine (Pays étranger)", "99156": "Macédoine du Nord (Pays étranger)",
    "99157": "Kosovo (Pays étranger)",

    # Asie
    "99201": "Arabie saoudite (Pays étranger)", "99203": "Irak (Pays étranger)", "99204": "Iran (Pays étranger)",
    "99205": "Liban (Pays étranger)", "99206": "Syrie (Pays étranger)", "99207": "Israël (Pays étranger)",
    "99209": "Turquie d'Asie (Pays étranger)", "99212": "Afghanistan (Pays étranger)", "99213": "Pakistan (Pays étranger)",
    "99214": "Bhoutan (Pays étranger)", "99215": "Népal (Pays étranger)", "99216": "Chine (Pays étranger)",
    "99217": "Japon (Pays étranger)", "99222": "Jordanie (Pays étranger)", "99223": "Inde (Pays étranger)",
    "99224": "Birmanie (Myanmar) (Pays étranger)", "99225": "Brunei (Pays étranger)", "99227": "Malaisie (Pays étranger)",
    "99230": "Hong Kong (Pays étranger)", "99231": "Indonésie (Pays étranger)", "99232": "Macao (Pays étranger)",
    "99234": "Cambodge (Pays étranger)", "99235": "Sri Lanka (Pays étranger)", "99236": "Taïwan (Pays étranger)",
    "99237": "Corée (Pays étranger)", "99238": "Corée du Nord (Pays étranger)", "99239": "Corée du Sud (Pays étranger)",
    "99240": "Koweït (Pays étranger)", "99241": "Laos (Pays étranger)", "99242": "Mongolie (Pays étranger)",
    "99243": "Philippines (Pays étranger)", "99244": "Singapour (Pays étranger)", "99245": "Thaïlande (Pays étranger)",
    "99246": "Bangladesh (Pays étranger)", "99247": "Émirats arabes unis (Pays étranger)", "99249": "Bahreïn (Pays étranger)",
    "99250": "Qatar (Pays étranger)", "99251": "Oman (Pays étranger)", "99252": "Arménie (Pays étranger)",
    "99253": "Azerbaïdjan (Pays étranger)", "99254": "Chypre (Pays étranger)", "99255": "Géorgie (Pays étranger)",
    "99256": "Kazakhstan (Pays étranger)", "99257": "Kirghizistan (Pays étranger)", "99258": "Ouzbékistan (Pays étranger)",
    "99259": "Tadjikistan (Pays étranger)", "99260": "Turkménistan (Pays étranger)", "99261": "Viêt Nam (Pays étranger)",
    "99262": "Yémen (Pays étranger)", "99263": "Palestine (Pays étranger)",

    # Afrique
    "99301": "Égypte (Pays étranger)", "99302": "Libéria (Pays étranger)", "99303": "Afrique du Sud (Pays étranger)",
    "99304": "Gambie (Pays étranger)", "99311": "Namibie (Pays étranger)", "99312": "Rép. démocratique du Congo (Pays étranger)",
    "99314": "Guinée équatoriale (Pays étranger)", "99315": "Éthiopie (Pays étranger)", "99316": "Libye (Pays étranger)",
    "99317": "Érythrée (Pays étranger)", "99318": "Somalie (Pays étranger)", "99321": "Burundi (Pays étranger)",
    "99322": "Cameroun (Pays étranger)", "99323": "République centrafricaine (Pays étranger)", "99324": "Congo-Brazzaville (Pays étranger)",
    "99326": "Côte d'Ivoire (Pays étranger)", "99327": "Bénin (Pays étranger)", "99328": "Gabon (Pays étranger)",
    "99329": "Ghana (Pays étranger)", "99330": "Guinée (Pays étranger)", "99331": "Burkina Faso (Pays étranger)",
    "99332": "Kenya (Pays étranger)", "99333": "Madagascar (Pays étranger)", "99334": "Malawi (Pays étranger)",
    "99335": "Mali (Pays étranger)", "99336": "Mauritanie (Pays étranger)", "99337": "Niger (Pays étranger)",
    "99338": "Nigeria (Pays étranger)", "99339": "Ouganda (Pays étranger)", "99340": "Rwanda (Pays étranger)",
    "99341": "Sénégal (Pays étranger)", "99342": "Sierra Leone (Pays étranger)", "99343": "Soudan (Pays étranger)",
    "99345": "Tchad (Pays étranger)", "99346": "Togo (Pays étranger)", "99347": "Botswana (Pays étranger)",
    "99348": "Lesotho (Pays étranger)", "99349": "Soudan du Sud (Pays étranger)", "99350": "Maroc (Pays étranger)",
    "99351": "Tunisie (Pays étranger)", "99352": "Algérie (Pays étranger)", "99389": "Sahara occidental (Pays étranger)",
    "99390": "Maurice (Pays étranger)", "99391": "Eswatini (Swaziland) (Pays étranger)", "99392": "Guinée-Bissau (Pays étranger)",
    "99393": "Mozambique (Pays étranger)", "99394": "Sao Tomé-et-Principe (Pays étranger)", "99395": "Angola (Pays étranger)",
    "99396": "Cap-Vert (Pays étranger)", "99397": "Comores (Pays étranger)", "99398": "Seychelles (Pays étranger)",
    "99399": "Djibouti (Pays étranger)",

    # Amériques
    "99401": "États-Unis d'Amérique (Pays étranger)", "99404": "Canada (Pays étranger)", "99405": "Mexique (Pays étranger)",
    "99406": "Costa Rica (Pays étranger)", "99407": "Cuba (Pays étranger)", "99408": "République dominicaine (Pays étranger)",
    "99409": "Guatemala (Pays étranger)", "99410": "Haïti (Pays étranger)", "99411": "Honduras (Pays étranger)",
    "99412": "Nicaragua (Pays étranger)", "99413": "Panama (Pays étranger)", "99414": "Salvador (Pays étranger)",
    "99415": "Argentine (Pays étranger)", "99416": "Bolivie (Pays étranger)", "99417": "Brésil (Pays étranger)",
    "99418": "Chili (Pays étranger)", "99419": "Colombie (Pays étranger)", "99420": "Équateur (Pays étranger)",
    "99421": "Paraguay (Pays étranger)", "99422": "Pérou (Pays étranger)", "99423": "Uruguay (Pays étranger)",
    "99424": "Venezuela (Pays étranger)", "99426": "Guyana (Pays étranger)", "99427": "Suriname (Pays étranger)",
    "99428": "Jamaïque (Pays étranger)", "99429": "Bahamas (Pays étranger)", "99430": "Barbade (Pays étranger)",
    "99431": "Trinité-et-Tobago (Pays étranger)", "99435": "Grenade (Pays étranger)", "99436": "Sainte-Lucie (Pays étranger)",
    "99437": "Saint-Vincent-et-les-Grenadines (Pays étranger)", "99438": "Belize (Pays étranger)",
    "99439": "Antigua-et-Barbuda (Pays étranger)", "99440": "Saint-Christophe-et-Niévès (Pays étranger)",
    "99441": "Dominique (Pays étranger)",

    # Océanie
    "99501": "Australie (Pays étranger)", "99502": "Nouvelle-Zélande (Pays étranger)", "99504": "Papouasie-Nouvelle-Guinée (Pays étranger)",
    "99505": "Fidji (Pays étranger)", "99508": "Îles Salomon (Pays étranger)", "99509": "Vanuatu (Pays étranger)",
    "99510": "Samoa (Pays étranger)", "99511": "Tuvalu (Pays étranger)", "99512": "Kiribati (Pays étranger)",
    "99513": "Nauru (Pays étranger)", "99514": "Tonga (Pays étranger)", "99515": "Îles Marshall (Pays étranger)",
    "99516": "Micronésie (Pays étranger)", "99517": "Palaos (Pays étranger)",
    "99999": "Pays étranger indéterminé / inconnu",

    # --- ANCIENS DÉPARTEMENTS FRANÇAIS EN AFRIQUE DU NORD (AVANT INDÉPENDANCE) ---
    # Algérie française (1848 - 1962)
    "91352": "Algérie française - Département d'Alger (avant 1962)",
    "92352": "Algérie française - Département d'Oran (avant 1962)",
    "93352": "Algérie française - Département de Constantine (avant 1962)",
    "94352": "Algérie française - Territoires du Sud (avant 1962)",
    "91110": "Alger (Algérie française, avant 1962)",
    "92200": "Oran (Algérie française, avant 1962)",
    "93100": "Constantine (Algérie française, avant 1962)",
    "93200": "Bône / Annaba (Algérie française, avant 1962)",
    # Maroc sous protectorat français (avant 1956)
    "95350": "Maroc sous protectorat français (avant 1956)",
    # Tunisie sous protectorat français (avant 1956)
    "96351": "Tunisie sous protectorat français (avant 1956)",

    # --- ARRONDISSEMENTS MUNICIPAUX (PARIS, LYON, MARSEILLE) ---
    # Paris (75) : codes officiels et alias postaux
    "75056": "Paris (Commune générale)",
    **{f"751{i:02d}": f"Paris {i}{'er' if i == 1 else 'e'} Arrondissement" for i in range(1, 21)},
    **{f"750{i:02d}": f"Paris {i}{'er' if i == 1 else 'e'} Arrondissement (alias postal)" for i in range(1, 21)},

    # Marseille (13) : codes officiels 13201-13216 et alias couramment admis 13001-13016
    "13055": "Marseille (Commune générale)",
    **{f"132{i:02d}": f"Marseille {i}{'er' if i == 1 else 'e'} Arrondissement" for i in range(1, 17)},
    **{f"130{i:02d}": f"Marseille {i}{'er' if i == 1 else 'e'} Arrondissement (alias postal)" for i in range(1, 17)},

    # Lyon (69) : codes officiels 69381-69389 et alias 69001-69009
    "69123": "Lyon (Commune générale)",
    **{f"6938{i}": f"Lyon {i}{'er' if i == 1 else 'e'} Arrondissement" for i in range(1, 10)},
    **{f"6900{i}": f"Lyon {i}{'er' if i == 1 else 'e'} Arrondissement (alias postal)" for i in range(1, 10)},

    # --- CORSE (2A & 2B) : PRINCIPALES COMMUNES ---
    "2A004": "Ajaccio (Corse-du-Sud)", "2A041": "Bonifacio (Corse-du-Sud)", "2A247": "Porto-Vecchio (Corse-du-Sud)",
    "2A272": "Sartène (Corse-du-Sud)", "2A249": "Propriano (Corse-du-Sud)", "2B033": "Bastia (Haute-Corse)",
    "2B050": "Calvi (Haute-Corse)", "2B096": "Corte (Haute-Corse)", "2B134": "L'Île-Rousse (Haute-Corse)",

    # --- CHEFS-LIEUX ET GRANDES VILLES MÉTROPOLITAINES & OUTRE-MER ---
    "01053": "Bourg-en-Bresse (Ain)", "02408": "Laon (Aisne)", "03190": "Moulins (Allier)",
    "04070": "Digne-les-Bains (Alpes-de-Haute-Provence)", "05061": "Gap (Hautes-Alpes)", "06088": "Nice (Alpes-Maritimes)",
    "07186": "Privas (Ardèche)", "08105": "Charleville-Mézières (Ardennes)", "09122": "Foix (Ariège)",
    "10387": "Troyes (Aube)", "11069": "Carcassonne (Aude)", "12085": "Rodez (Aveyron)",
    "14118": "Caen (Calvados)", "15014": "Aurillac (Cantal)", "16015": "Angoulême (Charente)",
    "17300": "La Rochelle (Charente-Maritime)", "18033": "Bourges (Cher)", "19272": "Tulle (Corrèze)",
    "21231": "Dijon (Côte-d'Or)", "22278": "Saint-Brieuc (Côtes-d'Armor)", "23096": "Guéret (Creuse)",
    "24322": "Périgueux (Dordogne)", "25056": "Besançon (Doubs)", "26362": "Valence (Drôme)",
    "27229": "Évreux (Eure)", "28085": "Chartres (Eure-et-Loir)", "29019": "Brest (Finistère)", "29232": "Quimper (Finistère)",
    "30189": "Nîmes (Gard)", "31555": "Toulouse (Haute-Garonne)", "32160": "Auch (Gers)", "33063": "Bordeaux (Gironde)",
    "34172": "Montpellier (Hérault)", "35238": "Rennes (Ille-et-Vilaine)", "36044": "Châteauroux (Indre)",
    "37261": "Tours (Indre-et-Loire)", "38185": "Grenoble (Isère)", "39300": "Lons-le-Saunier (Jura)",
    "40192": "Mont-de-Marsan (Landes)", "41018": "Blois (Loir-et-Cher)", "42218": "Saint-Étienne (Loire)",
    "43157": "Le Puy-en-Velay (Haute-Loire)", "44109": "Nantes (Loire-Atlantique)", "45234": "Orléans (Loiret)",
    "46042": "Cahors (Lot)", "47001": "Agen (Lot-et-Garonne)", "48095": "Mende (Lozère)", "49007": "Angers (Maine-et-Loire)",
    "50502": "Saint-Lô (Manche)", "51108": "Châlons-en-Champagne (Marne)", "51454": "Reims (Marne)",
    "52121": "Chaumont (Haute-Marne)", "53130": "Laval (Mayenne)", "54395": "Nancy (Meurthe-et-Moselle)",
    "55029": "Bar-le-Duc (Meuse)", "56260": "Vannes (Morbihan)", "57463": "Metz (Moselle)", "58194": "Nevers (Nièvre)",
    "59350": "Lille (Nord)", "60057": "Beauvais (Oise)", "61001": "Alençon (Orne)", "62041": "Arras (Pas-de-Calais)",
    "63113": "Clermont-Ferrand (Puy-de-Dôme)", "64445": "Pau (Pyrénées-Atlantiques)", "65440": "Tarbes (Hautes-Pyrénées)",
    "66136": "Perpignan (Pyrénées-Orientales)", "67482": "Strasbourg (Bas-Rhin)", "68224": "Mulhouse (Haut-Rhin)",
    "70550": "Vesoul (Haute-Saône)", "71270": "Mâcon (Saône-et-Loire)", "72181": "Le Mans (Sarthe)",
    "73065": "Chambéry (Savoie)", "74010": "Annecy (Haute-Savoie)", "76540": "Rouen (Seine-Maritime)",
    "76351": "Le Havre (Seine-Maritime)", "77288": "Melun (Seine-et-Marne)", "78646": "Versailles (Yvelines)",
    "79191": "Niort (Deux-Sèvres)", "80021": "Amiens (Somme)", "81004": "Albi (Tarn)", "82121": "Montauban (Tarn-et-Garonne)",
    "83137": "Toulon (Var)", "84007": "Avignon (Vaucluse)", "85191": "La Roche-sur-Yon (Vendée)", "86194": "Poitiers (Vienne)",
    "87085": "Limoges (Haute-Vienne)", "88160": "Épinal (Vosges)", "89024": "Auxerre (Yonne)", "90010": "Belfort (Territoire de Belfort)",
    "91228": "Évry-Courcouronnes (Essonne)", "92050": "Nanterre (Hauts-de-Seine)", "93008": "Bobigny (Seine-Saint-Denis)",
    "94028": "Créteil (Val-de-Marne)", "95500": "Pontoise (Val-d'Oise)",
    # Outre-Mer
    "97105": "Basse-Terre (Guadeloupe)", "97120": "Pointe-à-Pitre (Guadeloupe)", "97209": "Fort-de-France (Martinique)",
    "97302": "Cayenne (Guyane)", "97304": "Kourou (Guyane)", "97411": "Saint-Denis (La Réunion)",
    "97501": "Saint-Pierre (Saint-Pierre-et-Miquelon)", "97611": "Mamoudzou (Mayotte)", "97701": "Saint-Barthélemy",
    "97801": "Saint-Martin", "98613": "Uvea (Wallis-et-Futuna)", "98735": "Papeete (Polynésie française)",
    "98818": "Nouméa (Nouvelle-Calédonie)", "98901": "Île de Clipperton"
}


def _fetch_commune_api(code: str) -> str | None:
    """
    Interroge l'API officielle geo.api.gouv.fr pour vérifier l'existence d'une commune française.
    Met en cache le résultat si la commune existe.
    """
    url = f"https://geo.api.gouv.fr/communes/{code}?fields=nom,codeDepartement"
    req = urllib.request.Request(url, headers={"User-Agent": "SecuriteSocialeNIR/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=1.8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                nom = data.get("nom")
                dep_code = data.get("codeDepartement")
                dep_nom = DEPARTEMENTS_FRANCE.get(dep_code, f"Département {dep_code}")
                full_name = f"{nom} ({dep_nom})"
                INSEE_DATABASE[code] = full_name
                return full_name
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
    except Exception:
        # Erreur réseau, timeout ou mode hors ligne
        pass
    return None


def get_insee_location(code: str) -> str | None:
    """
    Vérifie l'existence effective d'un code INSEE (commune française, DROM-COM, pays étranger,
    ou ancien département d'Afrique du Nord) et retourne son libellé complet.
    """
    code = str(code).strip().upper()
    if len(code) != 5:
        return None

    # 1. Vérification dans le dictionnaire local détaillé
    if code in INSEE_DATABASE:
        return INSEE_DATABASE[code]

    # 2. Cas des pays étrangers (99XXX)
    if code.startswith("99"):
        return None  # Si absent du dictionnaire COG 99XXX complet, le pays n'existe pas

    # 3. Cas de l'Algérie française (91, 92, 93, 94), Maroc (95) et Tunisie (96) avant décolonisation
    if code[:2] in ["91", "92", "93", "94", "95", "96"]:
        # Recherche prioritaire si commune métropolitaine moderne (Essonne 91, Hauts-de-Seine 92...)
        api_res = _fetch_commune_api(code)
        if api_res:
            return api_res
        if code[2:].isdigit():
            commune_num = int(code[2:])
            if 100 <= commune_num <= 999:
                territoires = {
                    "91": "Algérie française (Département d'Alger)",
                    "92": "Algérie française (Département d'Oran)",
                    "93": "Algérie française (Département de Constantine)",
                    "94": "Algérie française (Territoires du Sud)",
                    "95": "Maroc (Protectorat français avant 1956)",
                    "96": "Tunisie (Protectorat français avant 1956)"
                }
                desc = f"{territoires[code[:2]]} - Commune code {code[2:]}"
                INSEE_DATABASE[code] = desc
                return desc

    # 4. Communes de France métropolitaine et DROM (01-95, 2A, 2B, 971-988)
    dep_prefix = code[:2]
    dep_dom = code[:3]
    if dep_prefix in DEPARTEMENTS_FRANCE or dep_dom in DEPARTEMENTS_FRANCE:
        # Interrogation directe de l'API nationale
        api_res = _fetch_commune_api(code)
        if api_res:
            return api_res

        # Secours hors-ligne : validation de la cohérence de la plage communale si le réseau est inaccessible
        if (code[:2] in ["2A", "2B"] and code[2:].isdigit() and 1 <= int(code[2:]) <= 990) or (
            code.isdigit() and 1 <= int(code[2:]) <= 990
        ):
            dep_name = DEPARTEMENTS_FRANCE.get(dep_dom, DEPARTEMENTS_FRANCE.get(dep_prefix, "France"))
            fallback_desc = f"Commune du département {dep_name} (code {code})"
            return fallback_desc

    return None


def is_valid_insee_code(code: str) -> bool:
    """
    Retourne True si le code INSEE existe effectivement, False sinon.
    """
    return get_insee_location(code) is not None

#%######################### SECURITE SOCIALE #######################
"""
Le NIR (Numéro d'Inscription au Répertoire national d'identification des personnes physiques)
est le numéro d'identification unique utilisé en France pour la protection sociale et la santé, 
communément appelé : 

numéro de Sécurité sociale.
"""  

def calcControlKey(baseNIR: int | str) -> int:
    """
    Calcule la clé de contrôle sur la base des 13 premiers caractères du NIR.
    Gère également le cas de la Corse (2A -> 19, 2B -> 18).

    :param baseNIR: Les 13 premiers caractères du NIR
    :return: Clé de contrôle entre 1 et 97
    """
    nir_str = str(baseNIR).strip().upper()
    nir_str = nir_str.replace("2A", "19").replace("2B", "18")
    return 97 - (int(nir_str) % 97)


def calcNIR(sex: int | str, bornYear: int | str, bornMonth: int | str, postalCode: int | str, orderNumber: int | str = 1) -> str:
    """
    Calcule le numéro de sécurité sociale sur la base des paramètres fournis.

    :param sex: 1 pour homme, 2 pour femme
    :param bornYear: Année de naissance sur 2 chiffres (ex: 85 pour 1985, 03 pour 2003)
    :param bornMonth: Mois de naissance sur 2 chiffres (compris strictement entre 01 et 12)
    :param postalCode: Code INSEE de naissance (5 caractères, ex: 13005 pour Marseille 5ème arrondissement, 01053 pour Ain, 2A004 pour la Corse)
    :param orderNumber: Numéro d'ordre sur 3 chiffres (ex: 001, 002, 152) - 1 par défaut, pour tester l'outil si la personne ne connaît pas son numéro d'ordre
    (Seule information qu'on ne connaît pas nécessairement, mais qui est indispensable pour calculer le NIR complet)

    :return: Le numéro de sécurité sociale complet sur 15 caractères sous forme de chaîne
    """
    str_sex = str(sex).strip()
    if str_sex not in ["1", "2"]:
        raise ValueError("Le sexe doit être 1 (homme) ou 2 (femme).")

    # Conserve / formate l'année sur 2 chiffres
    if isinstance(bornYear, int):
        str_year = f"{bornYear:02d}"
    else:
        str_year = str(bornYear).strip().zfill(2)

    # Vérification et formatage strict du mois (01 à 12)
    m_int = int(bornMonth)
    if not (1 <= m_int <= 12):
        raise ValueError(f"Le mois de naissance ({bornMonth}) doit obligatoirement être compris entre 01 et 12.")
    str_month = f"{m_int:02d}"

    # Conserve / formate le code commune INSEE sur 5 caractères
    str_pc = str(postalCode).strip().upper()
    if not (str_pc.startswith("2A") or str_pc.startswith("2B")):
        str_pc = str_pc.zfill(5)

    # Conserve / formate le numéro d'ordre sur 3 chiffres
    if isinstance(orderNumber, int):
        str_order = f"{orderNumber:03d}"
    else:
        str_order = str(orderNumber).strip().zfill(3)

    baseNIR = f"{str_sex}{str_year}{str_month}{str_pc}{str_order}"
    control_key = calcControlKey(baseNIR)

    # Clé formatée obligatoirement sur 2 chiffres (ex: 07 et non 7)
    return f"{baseNIR}{control_key:02d}"


def get_nir_validation_errors(nir: int | str) -> list[str]:
    """
    Retourne la liste détaillée des anomalies d'un NIR pour faciliter le diagnostic utilisateur.
    """
    errors = []
    nir_str = str(nir).strip().replace(" ", "").upper()

    if len(nir_str) != 15:
        errors.append(f"Longueur invalide : {len(nir_str)} caractères au lieu des 15 requis.")
        return errors

    if nir_str[0] not in ["1", "2"]:
        errors.append(f"Chiffre du sexe invalide : '{nir_str[0]}' (doit être 1 pour homme ou 2 pour femme).")

    if not nir_str[1:3].isdigit():
        errors.append(f"Année de naissance invalide : '{nir_str[1:3]}' (doit comporter 2 chiffres).")

    if not nir_str[3:5].isdigit():
        errors.append(f"Mois de naissance invalide : '{nir_str[3:5]}' (doit être numérique).")
    else:
        m = int(nir_str[3:5])
        if not (1 <= m <= 12):
            errors.append(f"Mois de naissance impossible : {m:02d} (doit être compris entre 01 et 12).")

    insee_code = nir_str[5:10]
    if not is_valid_insee_code(insee_code):
        errors.append(f"Code INSEE introuvable ou inexistant : '{insee_code}'.")

    if not nir_str[10:13].isdigit():
        errors.append(f"Numéro d'ordre invalide : '{nir_str[10:13]}' (doit comporter 3 chiffres).")
    else:
        order = int(nir_str[10:13])
        if not (1 <= order <= 999):
            errors.append(f"Numéro d'ordre hors plage : '{nir_str[10:13]}' (doit être compris entre 001 et 999).")

    try:
        controlKey = int(nir_str[-2:])
        expectedKey = calcControlKey(nir_str[:13])
        if controlKey != expectedKey:
            errors.append(f"Clé de contrôle erronée : '{controlKey:02d}' (clé attendue : '{expectedKey:02d}').")
    except (ValueError, TypeError):
        errors.append("Impossible de calculer la clé de contrôle sur ce numéro.")

    return errors


def isValidNIR(nir: int | str) -> bool:
    """
    Vérifie la validité intégrale d'un numéro de sécurité sociale (NIR) sur 15 caractères :
    - Longueur et structure
    - Sexe (1 ou 2)
    - Année
    - Mois (strictement de 01 à 12)
    - Existence effective du code commune / pays INSEE
    - Numéro d'ordre (001 à 999)
    - Clé de contrôle modulo 97 (avec règle Corse 2A/2B)

    :param nir: Le numéro de sécurité sociale à vérifier
    :return: True si le NIR est intégralement valide, False sinon
    """
    return len(get_nir_validation_errors(nir)) == 0


def extract_nir_info(nir: int | str) -> dict:
    """
    Réalise le processus inverse du calcul du NIR : extrait et interprète l'ensemble des informations
    contenues dans le numéro de sécurité sociale.

    :param nir: Le numéro de sécurité sociale à analyser
    :return: Dictionnaire contenant toutes les informations décodées
    """
    clean_nir = str(nir).strip().replace(" ", "").upper()
    errors = get_nir_validation_errors(clean_nir)
    is_valid = len(errors) == 0

    if len(clean_nir) != 15:
        return {
            "nir_raw": clean_nir,
            "nir_formatted": clean_nir,
            "is_valid": False,
            "errors": errors
        }

    sex_code = clean_nir[0]
    sex_label = "Homme" if sex_code == "1" else ("Femme" if sex_code == "2" else f"Inconnu ({sex_code})")

    year_code = clean_nir[1:3]
    try:
        year_int = int(year_code)
        year_estimated = f"19{year_code} ou 20{year_code}"
    except ValueError:
        year_estimated = "Inconnue"

    month_code = clean_nir[3:5]
    month_names = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    try:
        m_int = int(month_code)
        month_label = f"{month_names.get(m_int, 'Inconnu')} ({month_code})" if 1 <= m_int <= 12 else f"Invalide ({month_code})"
    except ValueError:
        month_label = f"Invalide ({month_code})"

    insee_code = clean_nir[5:10]
    location_desc = get_insee_location(insee_code) or "Code commune / pays introuvable"

    order_code = clean_nir[10:13]
    try:
        order_int = int(order_code)
        order_label = f"{order_code} ({to_french_ordinal(order_int)} individu enregistré ce mois-ci)"
    except ValueError:
        order_label = order_code

    key_code = clean_nir[13:15]
    try:
        expected_key = calcControlKey(clean_nir[:13])
        key_valid = (int(key_code) == expected_key)
        key_label = f"{key_code} (Conforme)" if key_valid else f"{key_code} (Invalide, attendu: {expected_key:02d})"
    except Exception:
        expected_key = None
        key_valid = False
        key_label = f"{key_code} (Calcul impossible)"

    # Formatage visuel standard français : S AA MM CC CCC OOO KK
    formatted_nir = f"{clean_nir[0]} {clean_nir[1:3]} {clean_nir[3:5]} {clean_nir[5:10]} {clean_nir[10:13]} {clean_nir[13:15]}"

    return {
        "nir_raw": clean_nir,
        "nir_formatted": formatted_nir,
        "sex_code": sex_code,
        "sex_label": sex_label,
        "year_code": year_code,
        "year_estimated": year_estimated,
        "month_code": month_code,
        "month_label": month_label,
        "insee_code": insee_code,
        "location": location_desc,
        "order_code": order_code,
        "order_label": order_label,
        "key_code": key_code,
        "key_label": key_label,
        "is_valid": is_valid,
        "errors": errors
    }


def display_nir_info(info: dict):
    """
    Affiche de façon élégante l'ensemble des informations extraites d'un NIR.
    """
    if not info.get("is_valid", False) and len(info.get("nir_raw", "")) != 15:
        print_error(f"Le format du NIR est incorrect : {info.get('nir_raw')}")
        for err in info.get("errors", []):
            print_warning(f"• {err}")
        return

    content = (
        f"[bold cyan]NIR analysé :[/bold cyan] {info['nir_formatted']}\n\n"
        f"[bold]• Sexe               :[/bold] {info['sex_label']}\n"
        f"[bold]• Année de naissance :[/bold] {info['year_estimated']} (code: {info['year_code']})\n"
        f"[bold]• Mois de naissance  :[/bold] {info['month_label']}\n"
        f"[bold]• Lieu de naissance  :[/bold] {info['location']} (code: {info['insee_code']})\n"
        f"[bold]• Numéro d'ordre     :[/bold] {info['order_label']}\n"
        f"[bold]• Clé de contrôle    :[/bold] {info['key_label']}\n"
        f"[bold]• Statut global      :[/bold] {'[green]VALIDE (Conforme RNIPP)[/green]' if info['is_valid'] else '[red]INVALIDE[/red]'}"
    )

    if _use_classic_output():
        print("\n" + "=" * 70)
        print("   INFORMATIONS EXTRAITES DU NUMÉRO DE SÉCURITÉ SOCIALE")
        print("=" * 70)
        print(f"NIR formaté         : {info['nir_formatted']}")
        print(f"Sexe                : {info['sex_label']}")
        print(f"Année de naissance  : {info['year_estimated']}")
        print(f"Mois de naissance   : {info['month_label']}")
        print(f"Lieu de naissance   : {info['location']} [{info['insee_code']}]")
        print(f"Numéro d'ordre      : {info['order_label']}")
        print(f"Clé de contrôle     : {info['key_label']}")
        print(f"Statut global       : {'VALIDE' if info['is_valid'] else 'INVALIDE'}")
        if not info["is_valid"]:
            print("\nAnomalies détectées :")
            for err in info["errors"]:
                print(f" - {err}")
        print("=" * 70 + "\n")
    else:
        console.print(Panel(
            content,
            title="[bold green]Résultat du décodage du NIR[/bold green]" if info['is_valid'] else "[bold red]Résultat du décodage du NIR[/bold red]",
            border_style="green" if info['is_valid'] else "red",
            width=85
        ))
        if not info["is_valid"] and info.get("errors"):
            for err in info["errors"]:
                print_warning(f"• {err}", width=85)

#%%#################### MODULES INTERACTIFS ########################
####################################################################

def interactiveNIRPrompt():
    """
    Interactive prompt to calculate and validate a French social security number (NIR).
    """
    print_info("Bienvenue dans le calculateur de numéro de sécurité sociale (NIR).", width=100)

    sex = prompt_sex("Entrez votre sexe (1 pour homme, 2 pour femme)")
    bornYear = prompt_int("Entrez votre année de naissance sur 2 chiffres (ex: 85 pour 1985, 03 pour 2003)", 2)
    bornMonth = prompt_month("Entrez votre mois de naissance sur 2 chiffres (ex: 05 pour mai, 12 pour décembre)")

    print_info(
        "Spécificité du code INSEE de naissance :\n"
        "- Pour la Corse, utilisez 2A ou 2B suivi de 3 chiffres (ex: 2A004 pour Ajaccio)\n"
        "- Pour les autres communes, utilisez le code INSEE à 5 chiffres\n"
        "- Pour les arrondissements de Paris, Lyon et Marseille, utilisez bien le code de l'arrondissement (et non de la ville-même) (ex: 13005 pour Marseille 5ème arrondissement, 75117 pour Paris 17ème arrondissement).\n"
        "- Si vous êtes né(e) à l'étranger, utilisez le code 99 suivi des 3 chiffres du code du pays de naissance.\n"
        "- Si vous êtes né(e) en Algérie française (avant 1964), utilisez les codes 91, 92, 93, ou 94 suivi des 3 chiffres du code de la commune de naissance.\n"
        "- Même logique si vous êtes né(e) avant 1956 en Tunisie (code 96) ou au Maroc (code 95).",
        width=85
    )
    postalCode = prompt_postal_code("Entrez le code INSEE de votre commune de naissance (5 chiffres ou 2A/2B suivi de 3 chiffres)")

    print_info(
        "Si vous ne connaissez pas votre numéro d'ordre, laissez le champ vide. Le calcul sera effectué avec 001 par défaut, mais le résultat ne sera probablement pas votre NIR réel.\n"
        "Le numéro d'ordre correspond à votre position de naissance dans la liste des naissances de votre commune.",
        width=85
    )
    orderNumber = prompt_int("Entrez votre numéro d'ordre sur 3 chiffres (ex: 001, 002, ...)", 3, "001")

    nir = calcNIR(sex, bornYear, bornMonth, postalCode, orderNumber)
    print_success(f"Votre numéro de sécurité sociale (NIR) est: {nir}")

    if isValidNIR(nir):
        print_success("Le NIR calculé est valide.")
        info = extract_nir_info(nir)
        display_nir_info(info)
    else:
        print_error("Le NIR calculé n'est pas valide.")


def interactiveExtractPrompt():
    """
    Prompt interactif pour extraire et décoder toutes les informations d'un NIR.
    """
    print_info("Extraction des informations d'un numéro de sécurité sociale (NIR).", width=85)
    raw_nir = prompt_input("Entrez le NIR à analyser (15 caractères, espaces autorisés)")
    if not raw_nir:
        print_warning("Aucune saisie détectée. Retour au menu.")
        return

    info = extract_nir_info(raw_nir)
    display_nir_info(info)


def interactiveVerifyPrompt():
    """
    Prompt interactif pour vérifier la conformité intégrale d'un NIR.
    """
    print_info("Vérification de la validité complète d'un numéro de sécurité sociale (NIR).", width=85)
    raw_nir = prompt_input("Entrez le NIR à 15 caractères à vérifier (espaces autorisés)")
    if not raw_nir:
        print_warning("Aucune saisie détectée. Retour au menu.")
        return

    is_valid = isValidNIR(raw_nir)
    errors = get_nir_validation_errors(raw_nir)

    if is_valid:
        print_success("Le NIR saisi est PARFAITEMENT VALIDE sur l'ensemble de ses critères (sexe, date, commune/pays INSEE, numéro d'ordre et clé).")
        info = extract_nir_info(raw_nir)
        display_nir_info(info)
    else:
        print_error("Le NIR saisi est INVALIDE.")
        for err in errors:
            print_warning(f"• {err}", width=85)


def showPrivacyPolicy():
    """
    Affiche les crédits et la déclaration de confidentialité (GauGoth Corp.).
    """
    privacy_text = (
        "GauGoth Corp. est une organisation qui s'engage à protéger la vie privée de ses utilisateurs.\n\n"
        "Notre objectif n'est pas de gagner de l'argent mais simplement de nous amuser et de partager nos créations. "
        "C'est pourquoi cet outil est accessible gratuitement et ne contient aucune publicité ni traceur commercial.\n\n"
        "--- DÉCLARATION DE CONFIDENTIALITÉ ---\n"
        "• Date d'entrée en vigueur : 30/10/2026\n"
        "• Dernière mise à jour : 30/10/2026\n"
        "• Responsable de la protection des données : GauGoth Corp.\n\n"
        "1. Collecte et traitement local : Toutes les informations saisies dans ce logiciel (sexe, date et lieu de naissance, NIR) "
        "sont traitées exclusivement en mémoire vive sur votre machine. Aucun numéro de sécurité sociale n'est collecté, "
        "enregistré dans une base distante ou transmis à des tiers.\n\n"
        "2. Requêtes géographiques : Les requêtes d'identification communale effectuées auprès de l'API publique de l'État "
        "(geo.api.gouv.fr) portent uniquement sur le code commune à 5 chiffres, de manière totalement anonyme et découplée de toute identité.\n\n"
        "Pour en savoir plus, consultez la politique en ligne : https://gaugoth-corp.pages-perso.free.fr/privacy-policy/\n"
        "Copyright © 2021-2026 GauGoth Corp. All rights reserved."
    )

    if _use_classic_output():
        print("\n" + "=" * 80)
        print("          DÉCLARATION DE CONFIDENTIALITÉ & CRÉDITS - GAUGOTH CORP.")
        print("=" * 80)
        print(privacy_text)
        print("=" * 80 + "\n")
    else:
        console.print(Panel(
            privacy_text,
            title="[bold cyan]Règles de confidentialité | GauGoth Corp.[/bold cyan]",
            subtitle="[italic white]Copyright © 2021-2026 GauGoth Corp. All rights reserved[/italic white]",
            border_style="cyan",
            width=85
        ))

#%######################### BOUCLE PRINCIPALE #######################
#####################################################################

def main_menu():
    """
    Menu principal interactif en boucle infinie.
    """
    print_success("Bienvenue dans l'outil de calcul et de vérification du numéro de sécurité sociale (NIR) !\n"
                  "Cet outil vous permet de calculer, extraire et vérifier les informations d'un numéro de sécurité sociale français (NIR).\n"
                    "Toutes les données sont traitées localement et aucune information personnelle n'est collectée.\n"
                    "Copyright © 2021-2026 GauGoth Corp. All rights reserved.",
                  width=85)
    while True:
        menu_content = (
            "[bold white]1.[/bold white] Calculer le NIR\n"
            "[bold white]2.[/bold white] Extraire les infos du NIR\n"
            "[bold white]3.[/bold white] Vérifier un NIR\n"
            "[bold white]4.[/bold white] Voir les crédits et la déclaration de confidentialité\n"
            "[bold white]5.[/bold white] Quitter le programme"
        )

        if _use_classic_output():
            print("\n" + "=" * 65)
            print("=== SÉCURITÉ SOCIALE (NIR) - MENU PRINCIPAL ===")
            print("=" * 65)
            print("1. Calculer le NIR")
            print("2. Extraire les infos du NIR")
            print("3. Vérifier un NIR")
            print("4. Voir les crédits et la déclaration de confidentialité")
            print("5. Quitter le programme")
            print("=" * 65)
        else:
            console.print(Panel(
                menu_content,
                title="[bold cyan]Calculateur & Vérificateur NIR[/bold cyan]",
                subtitle="[italic]GauGoth Corp.[/italic]",
                border_style="cyan",
                width=70
            ))

        choice = prompt_input("Choisissez une option (1-5)")
        if choice is not None:
            choice = choice.strip()

        if choice == "1":
            interactiveNIRPrompt()
        elif choice == "2":
            interactiveExtractPrompt()
        elif choice == "3":
            interactiveVerifyPrompt()
        elif choice == "4":
            showPrivacyPolicy()
        elif choice == "5":
            print_info("Merci d'avoir utilisé notre outil de Sécurité Sociale. À bientôt !")
            break
        else:
            print_warning("Option invalide. Veuillez saisir un chiffre entre 1 et 5.")


if __name__ == "__main__":
    main_menu()