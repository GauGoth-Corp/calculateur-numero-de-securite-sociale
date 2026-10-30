"""
== Calculateur Numéro de Sécurité Sociale ==

Sécurité Sociale (NIR) - Numéro d'Inscription au Répertoire national d'identification des personnes physiques
Ce module fournit des fonctions pour calculer et valider le numéro de sécurité sociale français (NIR) basé sur les informations personnelles telles que le sexe, l'année et le mois de naissance, le code INSEE de naissance et le numéro d'ordre. Il inclut également une interface interactive pour faciliter l'utilisation.

Auteur: GauGoth Corp.

Copyright: Copyright (c) 2021-2026 GauGoth Corp. Tous droits réservés.

Version: 1.0
"""

import sys
import os
try:
    from rich.console import Console
    from rich.panel import Panel
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

#%%#################### RICH CONSOLE OUTPUT ########################
####################################################################

def print_info(msg, width=60):
    """
    Prints an informational message to the console in blue color.
    """
    __print_message(msg, "INFO", "blue", width=width)


def print_success(msg, width=60):
    """
    Prints a success message to the console in green color.
    """
    __print_message(msg, "SUCCESS", "green", width=width)


def print_warning(msg, width=60):
    """
    Prints a warning message to the console in yellow color.
    """
    __print_message(msg, "WARNING", "yellow", width=width)


def print_error(msg, width=60):
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

#%############## RICH CONSOLE INPUT ########################
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


def prompt_postal_code(prompt, default=None) -> str:
    retry = True
    outputStr = ""
    while retry:
        outputStr = prompt_input(prompt, default=default)
        if outputStr is not None:
            outputStr = str(outputStr).strip().upper()
        else:
            outputStr = ""

        # Peut être de la forme "2B153" (Corse) ou "13005" (ex. Marseille 5ème arrondissement) ou "01053" (Ain)
        if (len(outputStr) == 5 and outputStr.isdigit()) or (
            len(outputStr) == 5 and outputStr[:2] in ["2A", "2B"] and outputStr[2:].isdigit()
        ):
            retry = False
        else:
            print_warning("Veuillez entrer un code de commune INSEE valide (5 chiffres ou 2A/2B suivi de 3 chiffres).")
    return outputStr

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
    :param bornMonth: Mois de naissance sur 2 chiffres (ex: 05 pour mai, 12 pour décembre)
    :param postalCode: Code INSEE de naissance (5 caractères, ex: 13005 pour Marseille 5ème arrondissement, 01053 pour Ain, 2A004 pour la Corse)
    :param orderNumber: Numéro d'ordre sur 3 chiffres (ex: 001, 002, 152) - 1 par défaut, pour tester l'outil si la personne ne connaît pas son numéro d'ordre
    (Seule information qu'on ne connaît pas nécessairement, mais qui est indispensable pour calculer le NIR complet)

    :return: Le numéro de sécurité sociale complet sur 15 caractères sous forme de chaîne
    """
    str_sex = str(sex).strip()

    # Conserve / formate l'année sur 2 chiffres
    if isinstance(bornYear, int):
        str_year = f"{bornYear:02d}"
    else:
        str_year = str(bornYear).strip().zfill(2)

    # Conserve / formate le mois sur 2 chiffres
    if isinstance(bornMonth, int):
        str_month = f"{bornMonth:02d}"
    else:
        str_month = str(bornMonth).strip().zfill(2)

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


def isValidNIR(nir: int | str) -> bool:
    """
    Vérifie la validité d'un numéro de sécurité sociale (NIR) sur 15 caractères.

    :param nir: Le numéro de sécurité sociale à vérifier
    :return: True si le NIR est valide, False sinon
    """
    nir_str = str(nir).strip().replace(" ", "").upper()
    if len(nir_str) != 15:
        return False

    baseNIR = nir_str[:13]
    try:
        controlKey = int(nir_str[-2:])
        return calcControlKey(baseNIR) == controlKey
    except ValueError:
        return False


def interactiveNIRPrompt():
    """
    Interactive prompt to calculate and validate a French social security number (NIR).
    """
    print_info("Bienvenue dans le calculateur de numéro de sécurité sociale (NIR).", width=100)

    sex = prompt_int("Entrez votre sexe (1 pour homme, 2 pour femme)", 1)
    bornYear = prompt_int("Entrez votre année de naissance sur 2 chiffres (ex: 85 pour 1985, 03 pour 2003)", 2)
    bornMonth = prompt_int("Entrez votre mois de naissance sur 2 chiffres (ex: 05 pour mai, 12 pour décembre)", 2)
    print_info("Spécificité du code INSEE de naissance :\n- Pour la Corse, utilisez 2A ou 2B suivi de 3 chiffres (ex: 2A004 pour Ajaccio)\n- Pour les autres communes, utilisez le code INSEE à 5 chiffres\n- Pour les arrondissements de Paris, Lyon et Marseille, utilisez bien le code de l'arrondissement (et non de la ville-même) (ex: 13005 pour Marseille 5ème arrondissement, 75117 pour Paris 17ème arrondissement).\n- Si vous êtes né(e) à l'étranger, utilisez le code 99 suivi des 3 chiffres du code du pays de naissance.\n- Si vous êtes né(e) en Algérie française (avant 1964), utilisez les codes 91, 92, 93, ou 94 suivi des 3 chiffres du code de la commune de naissance.\n- Même logique si vous êtes né(e) avant 1956 en Tunisie (code 96) ou au Maroc (code 95).", width=80)
    postalCode = prompt_postal_code("Entrez le code INSEE de votre commune de naissance (5 chiffres ou 2A/2B suivi de 3 chiffres)")
    print_info("Si vous ne connaissez pas votre numéro d'ordre, laissez le champ vide. Le calcul sera effectué avec 001 par défaut, mais le résultat ne sera probablement pas votre NIR réel.\nLe numéro d'ordre correspond à votre position de naissance dans la liste des naissances de votre commune.")
    orderNumber = prompt_int("Entrez votre numéro d'ordre sur 3 chiffres (ex: 001, 002, ...)", 3, "001")

    nir = calcNIR(sex, bornYear, bornMonth, postalCode, orderNumber)
    print_success(f"Votre numéro de sécurité sociale (NIR) est: {nir}")

    if isValidNIR(nir):
        print_success("Le NIR calculé est valide.")
    else:
        print_error("Le NIR calculé n'est pas valide.")


if __name__ == "__main__":
    interactiveNIRPrompt()