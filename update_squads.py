import json
import urllib.request
import csv
import datetime
import re

def extrair_todos_jogadores_fc():
    print("🌍 A iniciar download da Base Mundial do EA Sports FC...")

    # URL oficial codificado com %20 no espaço do caminho
    DATASET_URL = "https://raw.githubusercontent.com/LakshmiKanth11/EA_FC_ANALYSIS/main/EA_FC_PLAYERS_DATASET_AND_%20DASHBOARD/data/players.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    req = urllib.request.Request(DATASET_URL, headers=headers)

    # Dicionário de tradução para as posições em Português
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
                # 1. Nome do Jogador
                display_name = (row.get('display_name') or '').strip()
                if not display_name:
                    first = (row.get('first_name') or '').strip()
                    last = (row.get('last_name') or '').strip()
                    display_name = f"{first} {last}".strip() if (first or last) else "Jogador"

                # 2. Clube e Liga
                clube = (row.get('club') or '').strip() or "Sem Clube"
                liga = (row.get('league') or '').strip() or "Outras Ligas"

                # 3. Posição
                pos_original = (row.get('position') or 'CM').strip().upper()
                posicao = posicoes_pt.get(pos_original, pos_original)

                # 4. Overall Rating
                try:
                    overall = int(row.get('overall_rating') or row.get('overall') or 65)
                except Exception:
                    overall = 65

                # 5. Cálculo Inteligente da Idade Real
                idade = None

                # Tentativa A: Coluna direta de idade
                col_age = row.get('age')
                if col_age:
                    try:
                        val = int(col_age)
                        if 15 <= val <= 43:
                            idade = val
                    except Exception:
                        pass

                # Tentativa B: Extração a partir da data de nascimento (ex: 2001-04-20 ou 20/04/2001)
                if idade is None:
                    birthdate = str(row.get('birthdate') or '')
                    anos_encontrados = re.findall(r'\b(19\d{2}|20\d{2})\b', birthdate)
                    if anos_encontrados:
                        ano_nasc = int(anos_encontrados[0])
                        calc = ano_referencia - ano_nasc
                        if 15 <= calc <= 44:
                            idade = calc

                # Se não encontrar nada, atribui idade média realista baseada no overall
                if idade is None:
                    idade = 24

                # 6. Cálculo do Potencial
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

                jogadores.append({
                    "name": display_name,
                    "club": clube,
                    "league": liga,
                    "position": posicao,
                    "overall": overall,
                    "potential": max(overall, potencial),
                    "age": idade,
                    "game_version": "FC26"
                })

        print(f"✅ Download concluído! {len(jogadores)} jogadores processados.")

    except Exception as e:
        print(f"⚠️ Erro ao aceder à fonte externa: {e}")
        print("A carregar contingência estruturada...")
        jogadores = [
            # Manchester City
            {"name": "Erling Haaland", "club": "Manchester City", "league": "Premier League", "position": "PL", "overall": 91, "potential": 94, "age": 24, "game_version": "FC26"},
            {"name": "Kevin De Bruyne", "club": "Manchester City", "league": "Premier League", "position": "MC", "overall": 90, "potential": 90, "age": 33, "game_version": "FC26"},
            {"name": "Rodri", "club": "Manchester City", "league": "Premier League", "position": "MDC", "overall": 91, "potential": 92, "age": 28, "game_version": "FC26"},
            {"name": "Phil Foden", "club": "Manchester City", "league": "Premier League", "position": "ED", "overall": 88, "potential": 92, "age": 24, "game_version": "FC26"},
            {"name": "Bernardo Silva", "club": "Manchester City", "league": "Premier League", "position": "MC", "overall": 88, "potential": 88, "age": 30, "game_version": "FC26"},
            {"name": "Rúben Dias", "club": "Manchester City", "league": "Premier League", "position": "DC", "overall": 88, "potential": 90, "age": 27, "game_version": "FC26"},
            {"name": "Ederson", "club": "Manchester City", "league": "Premier League", "position": "GR", "overall": 88, "potential": 89, "age": 31, "game_version": "FC26"},
            {"name": "Jérémy Doku", "club": "Manchester City", "league": "Premier League", "position": "EE", "overall": 81, "potential": 87, "age": 22, "game_version": "FC26"},
            {"name": "Joško Gvardiol", "club": "Manchester City", "league": "Premier League", "position": "DE", "overall": 83, "potential": 88, "age": 22, "game_version": "FC26"},

            # Sporting CP
            {"name": "Viktor Gyökeres", "club": "Sporting CP", "league": "Liga Portugal", "position": "PL", "overall": 84, "potential": 87, "age": 26, "game_version": "FC26"},
            {"name": "Morten Hjulmand", "club": "Sporting CP", "league": "Liga Portugal", "position": "MDC", "overall": 80, "potential": 85, "age": 25, "game_version": "FC26"},
            {"name": "Pedro Gonçalves", "club": "Sporting CP", "league": "Liga Portugal", "position": "MO", "overall": 82, "potential": 84, "age": 26, "game_version": "FC26"},
            {"name": "Francisco Trincão", "club": "Sporting CP", "league": "Liga Portugal", "position": "ED", "overall": 79, "potential": 83, "age": 25, "game_version": "FC26"},
            {"name": "Gonçalo Inácio", "club": "Sporting CP", "league": "Liga Portugal", "position": "DC", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26"},
            {"name": "Ousmane Diomande", "club": "Sporting CP", "league": "Liga Portugal", "position": "DC", "overall": 79, "potential": 86, "age": 21, "game_version": "FC26"},
            {"name": "Geovany Quenda", "club": "Sporting CP", "league": "Liga Portugal", "position": "ED", "overall": 72, "potential": 88, "age": 17, "game_version": "FC26"},
            {"name": "Geny Catamo", "club": "Sporting CP", "league": "Liga Portugal", "position": "ED", "overall": 77, "potential": 82, "age": 23, "game_version": "FC26"},
            {"name": "Franco Israel", "club": "Sporting CP", "league": "Liga Portugal", "position": "GR", "overall": 76, "potential": 82, "age": 24, "game_version": "FC26"},

            # FC Porto
            {"name": "Diogo Costa", "club": "FC Porto", "league": "Liga Portugal", "position": "GR", "overall": 82, "potential": 88, "age": 25, "game_version": "FC26"},
            {"name": "Samu Omorodion", "club": "FC Porto", "league": "Liga Portugal", "position": "PL", "overall": 78, "potential": 86, "age": 20, "game_version": "FC26"},
            {"name": "Alan Varela", "club": "FC Porto", "league": "Liga Portugal", "position": "MDC", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26"},
            {"name": "Pepê", "club": "FC Porto", "league": "Liga Portugal", "position": "ED", "overall": 80, "potential": 81, "age": 27, "game_version": "FC26"},
            {"name": "Galeno", "club": "FC Porto", "league": "Liga Portugal", "position": "EE", "overall": 80, "potential": 80, "age": 27, "game_version": "FC26"},
            {"name": "Nico González", "club": "FC Porto", "league": "Liga Portugal", "position": "MC", "overall": 78, "potential": 84, "age": 22, "game_version": "FC26"},
            {"name": "Rodrigo Mora", "club": "FC Porto", "league": "Liga Portugal", "position": "MO", "overall": 72, "potential": 88, "age": 17, "game_version": "FC26"},
            {"name": "Nehuén Pérez", "club": "FC Porto", "league": "Liga Portugal", "position": "DC", "overall": 78, "potential": 82, "age": 24, "game_version": "FC26"},

            # SL Benfica
            {"name": "Ángel Di María", "club": "SL Benfica", "league": "Liga Portugal", "position": "ED", "overall": 83, "potential": 83, "age": 36, "game_version": "FC26"},
            {"name": "Orkun Kökçü", "club": "SL Benfica", "league": "Liga Portugal", "position": "MC", "overall": 80, "potential": 84, "age": 23, "game_version": "FC26"},
            {"name": "Kerem Aktürkoğlu", "club": "SL Benfica", "league": "Liga Portugal", "position": "EE", "overall": 80, "potential": 82, "age": 26, "game_version": "FC26"},
            {"name": "Vangelis Pavlidis", "club": "SL Benfica", "league": "Liga Portugal", "position": "PL", "overall": 80, "potential": 82, "age": 26, "game_version": "FC26"},
            {"name": "António Silva", "club": "SL Benfica", "league": "Liga Portugal", "position": "DC", "overall": 79, "potential": 86, "age": 21, "game_version": "FC26"},
            {"name": "Tomás Araújo", "club": "SL Benfica", "league": "Liga Portugal", "position": "DC", "overall": 77, "potential": 85, "age": 22, "game_version": "FC26"},
            {"name": "Florentino Luís", "club": "SL Benfica", "league": "Liga Portugal", "position": "MDC", "overall": 79, "potential": 84, "age": 25, "game_version": "FC26"},
            {"name": "Anatoliy Trubin", "club": "SL Benfica", "league": "Liga Portugal", "position": "GR", "overall": 80, "potential": 86, "age": 23, "game_version": "FC26"},

            # Real Madrid
            {"name": "Kylian Mbappé", "club": "Real Madrid", "league": "La Liga", "position": "PL", "overall": 91, "potential": 94, "age": 25, "game_version": "FC26"},
            {"name": "Vinícius Júnior", "club": "Real Madrid", "league": "La Liga", "position": "EE", "overall": 90, "potential": 94, "age": 24, "game_version": "FC26"},
            {"name": "Jude Bellingham", "club": "Real Madrid", "league": "La Liga", "position": "MO", "overall": 90, "potential": 95, "age": 21, "game_version": "FC26"},
            {"name": "Federico Valverde", "club": "Real Madrid", "league": "La Liga", "position": "MC", "overall": 88, "potential": 90, "age": 26, "game_version": "FC26"},
            {"name": "Thibaut Courtois", "club": "Real Madrid", "league": "La Liga", "position": "GR", "overall": 89, "potential": 89, "age": 32, "game_version": "FC26"}
        ]

    # 1. Gravar ficheiro squads.json comprimido
    print("💾 A compactar e gravar squads.json...")
    with open("squads.json", "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, separators=(',', ':'))

    # 2. Ler e incrementar a versão no version.json
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            v_data = json.load(f)
            nova_versao = v_data.get("version", 1) + 1
    except Exception:
        nova_versao = 4

    clubes_unicos = len(set(j['club'] for j in jogadores))
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    versao_info = {
        "version": nova_versao,
        "game_version": "FC26/FC27",
        "updated_at": hoje,
        "total_players": len(jogadores),
        "total_clubs": clubes_unicos,
        "changelog": f"Base de dados calibrada ({len(jogadores)} jogadores, {clubes_unicos} clubes)"
    }

    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(versao_info, f, ensure_ascii=False, indent=2)

    print(f"🚀 Concluído com Sucesso! Versão {nova_versao} pronta a sincronizar.")

if __name__ == "__main__":
    extrair_todos_jogadores_fc()
