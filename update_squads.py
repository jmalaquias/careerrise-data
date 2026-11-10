import json
import urllib.request
import csv
import datetime
import re

# Ligas femininas para não misturar nos plantéis masculinos
            ligas_femininas = [
                "google pixel frauen-bundesliga", "frauen-bundesliga", 
                "barclays women's super league", "wsl", "liga f", 
                "d1 arkema", "nwsl", "women's champions league"
            ]

            for row in reader:
                liga = (row.get('league') or '').strip().lower()
                gender = (row.get('gender') or '').strip().upper()

                # Ignora jogadoras femininas para os plantéis de treinador masculino
                if gender == 'F' or any(lf in liga for lf in ligas_femininas):
                    continue
                    
def gerar_url_foto(player_id):
    """Gera o URL oficial da CDN da foto do jogador com base no ID da EA/Sofifa"""
    try:
        pid = int(player_id)
        if pid <= 0:
            return ""
        # Formato Sofifa / EA Sports CDN (ex: ID 241096 -> 241/096/25_120.png)
        pid_str = str(pid).zfill(6)
        p1 = pid_str[:3]
        p2 = pid_str[3:]
        return f"https://cdn.sofifa.net/players/{p1}/{p2}/25_120.png"
    except Exception:
        return ""

def gerar_url_clube(clube_nome, club_id=None):
    """Gera o URL oficial do emblema do clube"""
    if club_id and str(club_id).isdigit() and int(club_id) > 0:
        return f"https://cdn.sofifa.net/meta/team/{club_id}/120.png"
    
    # Mapeamento dos principais clubes para garantir emblemas imediatos em alta definição
    clubes_ids = {
        "Sporting CP": "237",
        "SL Benfica": "234",
        "FC Porto": "236",
        "SC Braga": "1896",
        "Vitória SC": "1887",
        "Boavista": "1898",
        "Famalicão": "113007",
        "Rio Ave": "744",
        "Gil Vicente": "110940",
        "Manchester City": "10",
        "Arsenal": "1",
        "Liverpool": "9",
        "Real Madrid": "243",
        "FC Barcelona": "241",
        "Atlético de Madrid": "240",
        "Paris Saint-Germain": "73",
        "Bayern München": "21",
        "Borussia Dortmund": "22",
        "Juventus": "45",
        "Inter": "44",
        "Milan": "47"
    }
    cid = clubes_ids.get(clube_nome)
    if cid:
        return f"https://cdn.sofifa.net/meta/team/{cid}/120.png"
    return ""

def extrair_todos_jogadores_fc():
    print("🌍 A iniciar download da Base Mundial do EA Sports FC com Fotos e Emblemas...")

    # URL oficial codificado com %20 no espaço
    DATASET_URL = "https://raw.githubusercontent.com/LakshmiKanth11/EA_FC_ANALYSIS/main/EA_FC_PLAYERS_DATASET_AND_%20DASHBOARD/data/players.csv"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    req = urllib.request.Request(DATASET_URL, headers=headers)

    posicoes_pt = {
        "GK": "GR",
        "CB": "DC",
        "LB": "DE",
        "RB": "DD",
        "LWB": "ADE",
        "RWB": "ADD",
        "CDM": "MDC",
        "CM": "MC",
        "CAM": "MO",
        "LM": "ME",
        "RM": "MD",
        "LW": "EE",
        "RW": "ED",
        "CF": "SA",
        "ST": "PL"
    }

    jogadores = []
    ano_referencia = 2026

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            lines = [line.decode('utf-8', errors='ignore') for line in response.readlines()]
            reader = csv.DictReader(lines)

            for row in reader:
                # 1. ID do Jogador
                player_id = row.get('player_id') or row.get('fifa_id') or "0"

                # 2. Nome do Jogador
                display_name = (row.get('display_name') or '').strip()
                if not display_name:
                    first = (row.get('first_name') or '').strip()
                    last = (row.get('last_name') or '').strip()
                    display_name = f"{first} {last}".strip() if (first or last) else "Jogador"

                # 3. Clube e Liga
                clube = (row.get('club') or '').strip() or "Sem Clube"
                liga = (row.get('league') or '').strip() or "Outras Ligas"
                club_id = row.get('club_id')

                # 4. Posição
                pos_original = (row.get('position') or 'CM').strip().upper()
                posicao = posicoes_pt.get(pos_original, pos_original)

                # 5. Overall Rating
                try:
                    overall = int(row.get('overall_rating') or row.get('overall') or 65)
                except Exception:
                    overall = 65

                # 6. Idade Real
                idade = None
                col_age = row.get('age')
                if col_age:
                    try:
                        val = int(col_age)
                        if 15 <= val <= 43:
                            idade = val
                    except Exception:
                        pass

                if idade is None:
                    birthdate = str(row.get('birthdate') or '')
                    anos = re.findall(r'\b(19\d{2}|20\d{2})\b', birthdate)
                    if anos:
                        calc = ano_referencia - int(anos[0])
                        if 15 <= calc <= 44:
                            idade = calc

                if idade is None:
                    idade = 24

                # 7. Potencial
                col_pot = row.get('potential')
                if col_pot:
                    try:
                        potencial = int(col_pot)
                    except Exception:
                        potencial = overall
                else:
                    if idade <= 21:
                        potencial = min(96, overall + max(3, 24 - idade))
                    elif idade <= 24:
                        potencial = min(94, overall + max(1, 26 - idade))
                    else:
                        potencial = overall

                # 8. URLs de Imagens (Cara e Emblema)
                photo_url = gerar_url_foto(player_id)
                club_logo_url = gerar_url_clube(clube, club_id)

                jogadores.append({
                    "name": display_name,
                    "club": clube,
                    "league": liga,
                    "position": posicao,
                    "overall": overall,
                    "potential": max(overall, potencial),
                    "age": idade,
                    "game_version": "FC26",
                    "photo_url": photo_url,
                    "club_logo_url": club_logo_url,
                    "flag_url": ""
                })

        print(f"✅ Sucesso absoluto! {len(jogadores)} jogadores processados com links de fotos e emblemas.")

    except Exception as e:
        print(f"⚠️ Erro ao aceder à fonte externa: {e}")
        print("A carregar contingência de alta precisão com fotos...")
        # Contingência completa com IDs oficiais para fotos reais imediatas
        jogadores = [
            # Manchester City
            {"name": "Erling Haaland", "club": "Manchester City", "league": "Premier League", "position": "PL", "overall": 91, "potential": 94, "age": 24, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/239/053/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},
            {"name": "Kevin De Bruyne", "club": "Manchester City", "league": "Premier League", "position": "MC", "overall": 90, "potential": 90, "age": 33, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/192/985/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},
            {"name": "Rodri", "club": "Manchester City", "league": "Premier League", "position": "MDC", "overall": 91, "potential": 92, "age": 28, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/231/866/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},
            {"name": "Phil Foden", "club": "Manchester City", "league": "Premier League", "position": "ED", "overall": 88, "potential": 92, "age": 24, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/237/692/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},
            {"name": "Bernardo Silva", "club": "Manchester City", "league": "Premier League", "position": "MC", "overall": 88, "potential": 88, "age": 30, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/218/667/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},
            {"name": "Rúben Dias", "club": "Manchester City", "league": "Premier League", "position": "DC", "overall": 88, "potential": 90, "age": 27, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/239/818/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/10/120.png", "flag_url": ""},

            # Sporting CP
            {"name": "Viktor Gyökeres", "club": "Sporting CP", "league": "Liga Portugal", "position": "PL", "overall": 84, "potential": 87, "age": 26, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/241/096/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},
            {"name": "Morten Hjulmand", "club": "Sporting CP", "league": "Liga Portugal", "position": "MDC", "overall": 80, "potential": 85, "age": 25, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/244/260/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},
            {"name": "Pedro Gonçalves", "club": "Sporting CP", "league": "Liga Portugal", "position": "MO", "overall": 82, "potential": 84, "age": 26, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/242/444/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},
            {"name": "Francisco Trincão", "club": "Sporting CP", "league": "Liga Portugal", "position": "ED", "overall": 79, "potential": 83, "age": 25, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/240/017/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},
            {"name": "Gonçalo Inácio", "club": "Sporting CP", "league": "Liga Portugal", "position": "DC", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/258/831/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},
            {"name": "Geovany Quenda", "club": "Sporting CP", "league": "Liga Portugal", "position": "ED", "overall": 72, "potential": 88, "age": 17, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/279/118/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/237/120.png", "flag_url": ""},

            # FC Porto
            {"name": "Diogo Costa", "club": "FC Porto", "league": "Liga Portugal", "position": "GR", "overall": 82, "potential": 88, "age": 25, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/236/583/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/236/120.png", "flag_url": ""},
            {"name": "Samu Omorodion", "club": "FC Porto", "league": "Liga Portugal", "position": "PL", "overall": 78, "potential": 86, "age": 20, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/277/111/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/236/120.png", "flag_url": ""},
            {"name": "Alan Varela", "club": "FC Porto", "league": "Liga Portugal", "position": "MDC", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/258/119/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/236/120.png", "flag_url": ""},
            {"name": "Rodrigo Mora", "club": "FC Porto", "league": "Liga Portugal", "position": "MO", "overall": 72, "potential": 88, "age": 17, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/278/877/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/236/120.png", "flag_url": ""},

            # SL Benfica
            {"name": "Ángel Di María", "club": "SL Benfica", "league": "Liga Portugal", "position": "ED", "overall": 83, "potential": 83, "age": 36, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/183/898/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/234/120.png", "flag_url": ""},
            {"name": "António Silva", "club": "SL Benfica", "league": "Liga Portugal", "position": "DC", "overall": 79, "potential": 86, "age": 21, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/269/414/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/234/120.png", "flag_url": ""},
            {"name": "Orkun Kökçü", "club": "SL Benfica", "league": "Liga Portugal", "position": "MC", "overall": 80, "potential": 84, "age": 23, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/241/810/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/234/120.png", "flag_url": ""},
            {"name": "Anatoliy Trubin", "club": "SL Benfica", "league": "Liga Portugal", "position": "GR", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/254/544/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/234/120.png", "flag_url": ""},

            # Real Madrid
            {"name": "Kylian Mbappé", "club": "Real Madrid", "league": "La Liga", "position": "PL", "overall": 91, "potential": 94, "age": 25, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/231/747/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/243/120.png", "flag_url": ""},
            {"name": "Vinícius Júnior", "club": "Real Madrid", "league": "La Liga", "position": "EE", "overall": 90, "potential": 94, "age": 24, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/238/794/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/243/120.png", "flag_url": ""},
            {"name": "Jude Bellingham", "club": "Real Madrid", "league": "La Liga", "position": "MO", "overall": 90, "potential": 95, "age": 21, "game_version": "FC26", "photo_url": "https://cdn.sofifa.net/players/252/371/25_120.png", "club_logo_url": "https://cdn.sofifa.net/meta/team/243/120.png", "flag_url": ""}
        ]

    # 1. Gravar ficheiro squads.json comprimido
    print("💾 A compactar squads.json...")
    with open("squads.json", "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, separators=(',', ':'))

    # 2. Ler e incrementar a versão no version.json
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            v_data = json.load(f)
            nova_versao = v_data.get("version", 1) + 1
    except Exception:
        nova_versao = 5

    clubes_unicos = len(set(j['club'] for j in jogadores))
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    versao_info = {
        "version": nova_versao,
        "game_version": "FC26/FC27",
        "updated_at": hoje,
        "total_players": len(jogadores),
        "total_clubs": clubes_unicos,
        "changelog": f"Base de dados com Fotos e Emblemas CDN ({len(jogadores)} jogadores)"
    }

    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(versao_info, f, ensure_ascii=False, indent=2)

    print(f"🚀 Base de dados gerada com sucesso! Nova Versão: {nova_versao}")

if __name__ == "__main__":
    extrair_todos_jogadores_fc()
