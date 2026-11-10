import json
import urllib.request
import csv
import datetime
import re

def gerar_url_foto(player_id):
    try:
        pid = int(player_id)
        if pid <= 0:
            return ""
        pid_str = str(pid).zfill(6)
        p1 = pid_str[:3]
        p2 = pid_str[3:]
        return f"https://cdn.sofifa.net/players/{p1}/{p2}/25_120.png"
    except Exception:
        return ""

def gerar_url_clube(clube_nome):
    clubes_ids = {
        "Sporting CP": "237", "SL Benfica": "234", "FC Porto": "236",
        "SC Braga": "1896", "Vitória SC": "1887", "Boavista": "1898",
        "Famalicão": "113007", "Rio Ave": "744", "Gil Vicente": "110940",
        "Moreirense": "1900", "Santa Clara": "110946", "Arouca": "112512",
        "Estoril Praia": "10020", "Casa Pia": "114385", "Farense": "110955",
        "Nacional": "1891", "AVS": "116335", "Estrela da Amadora": "116315",
        "1. FC Köln": "31", "Bayern München": "21", "Borussia Dortmund": "22",
        "Bayer 04 Leverkusen": "32", "RB Leipzig": "112172",
        "Manchester City": "10", "Arsenal": "1", "Liverpool": "9",
        "Manchester United": "11", "Chelsea": "5", "Tottenham Hotspur": "18",
        "Real Madrid": "243", "FC Barcelona": "241", "Atlético de Madrid": "240",
        "Paris Saint-Germain": "73", "Juventus": "45", "Inter": "44", "Milan": "47"
    }
    cid = clubes_ids.get(clube_nome)
    if cid:
        return f"https://cdn.sofifa.net/teams/{cid}/60.png"
    return ""

def extrair_todos_jogadores_fc():
    print("A iniciar processamento dos jogadores masculinos do EA FC...")

    DATASET_URL = "https://raw.githubusercontent.com/LakshmiKanth11/EA_FC_ANALYSIS/main/EA_FC_PLAYERS_DATASET_AND_%20DASHBOARD/data/players.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(DATASET_URL, headers=headers)

    posicoes_pt = {
        "GK": "GR", "CB": "DC", "LB": "DE", "RB": "DD", "LWB": "ADE", "RWB": "ADD",
        "CDM": "MDC", "CM": "MC", "CAM": "MO", "LM": "ME", "RM": "MD",
        "LW": "EE", "RW": "ED", "CF": "SA", "ST": "PL"
    }

    jogadores = []
    ano_referencia = 2026

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            lines = [line.decode('utf-8', errors='ignore') for line in response.readlines()]
            reader = csv.DictReader(lines)

            for row in reader:
                # FILTRO OFICIAL DO SOFIFA: MANTÉM APENAS FUTEBOL MASCULINO
                gender = (row.get('gender') or '').strip()
                if gender and gender != "Men's Football":
                    continue

                player_id = row.get('player_id') or "0"
                display_name = (row.get('display_name') or '').strip()
                if not display_name:
                    first = (row.get('first_name') or '').strip()
                    last = (row.get('last_name') or '').strip()
                    display_name = f"{first} {last}".strip() if (first or last) else "Jogador"

                clube = (row.get('club') or '').strip() or "Sem Clube"
                pos_original = (row.get('position') or 'CM').strip().upper()
                posicao = posicoes_pt.get(pos_original, pos_original)

                try:
                    overall = int(row.get('overall_rating') or 65)
                except Exception:
                    overall = 65

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

                potencial = min(95, overall + (max(1, 26 - idade) if idade <= 24 else 0))

                photo_url = gerar_url_foto(player_id)
                club_logo_url = gerar_url_clube(clube)

                jogadores.append({
                    "name": display_name,
                    "club": clube,
                    "league": (row.get('league') or '').strip(),
                    "position": posicao,
                    "overall": overall,
                    "potential": max(overall, potencial),
                    "age": idade,
                    "game_version": "FC26",
                    "photo_url": photo_url,
                    "club_logo_url": club_logo_url,
                    "flag_url": ""
                })

        print(f"Sucesso! {len(jogadores)} jogadores masculinos processados.")

    except Exception as e:
        print(f"Erro ao descarregar: {e}")
        return

    with open("squads.json", "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, separators=(',', ':'))

    versao_info = {
        "version": 15,
        "game_version": "FC26/FC27",
        "updated_at": datetime.date.today().strftime("%d/%m/%Y"),
        "total_players": len(jogadores),
        "changelog": "Versão 15 Oficial: Futebol Masculino Puro com Fotos e Emblemas"
    }

    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(versao_info, f, ensure_ascii=False, indent=2)

    print("Versão 15 gravada com sucesso!")

if __name__ == "__main__":
    extrair_todos_jogadores_fc()
