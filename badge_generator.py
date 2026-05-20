import sys
import os
import platform
import requests
import re
import json
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
import browser_cookie3

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "badge.png")

rubriques_MAP = {
    "203": "App - Système",
    "69": "Cracking",
    "70": "Réaliste",
    "18": "Cryptanalyse",
    "16": "Web - Client",
    "68": "Web - Serveur",
    "208": "Forensic",
    "182": "Réseau",
    "189": "App - Script",
    "17": "Programmation",
    "67": "Stéganographie"
}

def load_browser_cookie():
    browser_functions = [
        ("Chrome", browser_cookie3.chrome),
        ("Firefox", browser_cookie3.firefox),
        ("Edge", browser_cookie3.edge),
        ("Opera", browser_cookie3.opera),
        ("Brave", browser_cookie3.brave),
        ("Vivaldi", browser_cookie3.vivaldi),
        ("Safari", browser_cookie3.safari)
    ]

    for name, func in browser_functions:
        try:
            cj = func(domain_name='root-me.org')
            if any('root-me.org' in cookie.domain for cookie in cj):
                return cj
        except Exception:
            continue

        print("Aucune session spip détectée, vérifiez que vous êtes bien connecté sur un navigateur présent sur votre ordinateur")
        sys.exit(1)

def get_challenges_count(session):
    url = "https://www.root-me.org/fr/Challenges/"
    try:
        res = session.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        chall_count = {}
        tiles = soup.find_all('div', class_='tile')
        for tile in tiles:
            a_tag = tile.find('a', href=re.compile(r'fr/Challenges/'))
            if not a_tag:
                continue
            cat_name = a_tag.get_text(strip=True)
            span = tile.find('span')
            if span:
                b_tag = span.find('b', class_='color1')
                if b_tag:
                    count = int(b_tag.get_text(strip=True))
                    chall_count[cat_name] = count

        return chall_count
        
    except Exception as e:
        print(f"Erreur de récupération des données : {e}")
        return {}

def get_rootme_stats(uid):
    url = f"https://api.www.root-me.org/auteurs/{uid}"
    system = platform.system().lower()
    cookies = load_browser_cookie()
    session = requests.Session()
    session.cookies = cookies
    if system == "windows":
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    elif system == "darwin":
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    else:
        user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "application/json"
    })

    res_user = session.get(url, timeout=15)
    if res_user.status_code in [401, 403]:
        print("Erreur : Session invalide ou expirée.")
        sys.exit(1)
    elif res_user.status_code == 404:
        print("Utilisateur introuvable.")
        sys.exit(1)
    
    user_text = res_user.text.strip()
    if not user_text.endswith('}'):
        for endpoint in [',"challenges"', ',"validations"', ',"solutions"']:
            if endpoint in user_text:
                user_text = user_text.split(endpoint)[0] + '}'
                break
    
    user_data = json.loads(user_text)
    chall_count = get_challenges_count(session)
    return user_data, chall_count

def calculate_stats(user_data, chall_count):
    user_validations = user_data.get("validations", [])
    if isinstance(user_validations, dict):
        user_validations = user_validations.values()
    
    done_per_id = {}
    for valid in user_validations:
        id_rub = valid.get("id_rubrique")
        if id_rub:
            id_rub = str(id_rub)
            done_per_id[id_rub] = done_per_id.get(id_rub, 0) + 1

    categories_stats = {}

    for id_rub, official_name in rubriques_MAP.items():
        max_total = chall_count.get(official_name, 0)
        done = done_per_id.get(id_rub, 0)

        if max_total > 0:
            percentage = (done / max_total) * 100
        else:
            percentage = 0

        categories_stats[official_name] = {
            "validé": done,
            "total": max_total,
            "pourcentage": round(percentage, 1)
        }

    return categories_stats

def generate_badge(data, stats_categories, output_path=path): 
    if isinstance(data, list):
        if len(data) > 0:
            data = data[0]
        else:
            print("Données data vides")
            sys.exit(1)

    username = data.get("nom", "Inconnu")
    score = data.get("score", "0")
    position = data.get("position", "N/A")
    rang = data.get("rang", "Visiteur")

    sorted_categories = sorted(stats_categories.items())

    width = 540
    row_height = 28
    header_height = 150
    footer_padding = 30
    height = header_height + (len(sorted_categories) * row_height) + footer_padding

    image = Image.new("RGBA", (width, height), "#1a1a1a")

    try:
        logo = Image.open("rootme_logo.png").convert("RGBA")
        logo = logo.resize((80, 80), Image.Resampling.LANCZOS)
        image.paste(logo, (width - 115, 35), logo)
    except Exception as e:
        print("Erreur de chargement du logo : {e}")

    draw = ImageDraw.Draw(image)

    draw.rectangle([(0, 0), (width - 1, height - 1)], outline="#e67e22", width=3)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 14)
        font_bold = ImageFont.truetype("DejaVuSans.ttf", 13)
    except IOError:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    draw.text((25, 20), username, fill="#e67e22", font=font_title)
    draw.text((25, 60), f"Rang : {rang}", fill="#a0a0a0", font=font_text)
    draw.text((25, 85), f"Score : {score} pts", fill="#2ecc71", font=font_text)
    draw.text((25, 110), f"Classement : #{position}", fill="#3498db", font=font_text)

    draw.line([(25, 140), (width - 25, 140)], fill="#333333", width=2)

    y_offset = 155
    for category_name, info in sorted_categories:
        draw.text((25, y_offset), category_name, fill="#ffffff", font=font_bold)

        stat_string = f"{info['validé']}/{info['total']}"
        draw.text((width - 175, y_offset), stat_string, fill="#888888", font=font_text)

        bar_x_start = width - 115
        bar_x_end = width - 25
        draw.rectangle([(bar_x_start, y_offset + 4), (bar_x_end, y_offset + 12)], fill="#222222", outline="#333333")

        if info['validé'] > 0 and info['total'] > 0:
            progress_width = int((bar_x_end - bar_x_start) * (info['pourcentage'] / 100))
            draw.rectangle([(bar_x_start, y_offset + 4), (bar_x_start + progress_width, y_offset + 12)], fill="#e67e22")

        y_offset += row_height

    image.save(output_path, "PNG")
    image.close()
    print(f"Badge généré dans : {output_path} !")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilisation : python3 badge_generator.py <user UID>")
        print("Exemple : python3 badge_generator.py 123456")
        print("L'UID de l'utilisateur peut être retrouvé dans les paramètres du compte Root-Me")
        sys.exit(1)

    uid_cible = sys.argv[1]

    user_data, chall_count = get_rootme_stats(uid_cible)
    stats_categories = calculate_stats(user_data, chall_count)
    generate_badge(user_data, stats_categories) 