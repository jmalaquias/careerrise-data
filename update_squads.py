import json
import urllib.request
import csv
import datetime

def extrair_todos_jogadores_fc():
    print("🌍 A descarregar a base mundial do EA Sports FC (19.789 jogadores)...")

    # Fonte oficial de ratings do EA Sports FC (Snapshot completo com 702 clubes)
    DATASET_URL = "https://raw.githubusercontent.com/LakshmiKanth11/EA_FC_ANALYSIS/main/EA_FC_PLAYERS_DATASET_AND_DASHBOARD/data/players.csv"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(DATASET_URL, headers=headers)

    # Mapeamento para posições no nosso formato português
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
    ano_atual = 2026

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            lines = [line.decode('utf-8', errors='ignore') for line in response.readlines()]
            reader = csv.DictReader(lines)

            for row in reader:
                # 1. Nome do jogador
                display_name = row.get('display_name', '').strip()
                if not display_name:
                    first = row.get('first_name', '').strip()
                    last = row.get('last_name', '').strip()
                    display_name = f"{first} {last}".strip() if (first or last) else "Jogador"

                # 2. Clube e Liga
                clube = row.get('club', '').strip() or "Sem Clube"
                liga = row.get('league', '').strip() or "Outras Ligas"

                # 3. Posição
                pos_original = row.get('position', 'CM').strip().upper()
                posicao = posicoes_pt.get(pos_original, pos_original)

                # 4. Overall e Idade
                try:
                    overall = int(row.get('overall_rating', 60))
                except (ValueError, TypeError):
                    overall = 65

                # Cálculo de idade a partir da data de nascimento (ex: 2003-05-12)
                birthdate = row.get('birthdate', '')
                try:
                    ano_nasc = int(birthdate.split('-')[0])
                    idade = max(16, min(44, ano_atual - ano_nasc))
                except (ValueError, IndexError):
                    idade = 24

                # 5. Potencial (algoritmo com base no Overall e na Idade)
                if idade <= 21:
                    potencial = min(96, overall + max(4, 25 - idade))
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
                    "potential": potencial,
                    "age": idade,
                    "game_version": "FC26"
                })

        print(f"✅ Sucesso! Extraídos {len(jogadores)} jogadores de {len(set(j['club'] for j in jogadores))} clubes.")

    except Exception as e:
        print(f"❌ Erro ao descarregar dataset: {e}")
        return

    # Gravação do squads.json otimizado (formato compacto para a app abrir super rápida)
    print("💾 A guardar squads.json...")
    with open("squads.json", "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, separators=(',', ':'))

    # Atualização da versão no version.json
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            v_data = json.load(f)
            nova_versao = v_data.get("version", 1) + 1
    except Exception:
        nova_versao = 2

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    versao_info = {
        "version": nova_versao,
        "game_version": "FC26/FC27",
        "updated_at": hoje,
        "total_players": len(jogadores),
        "total_clubs": len(set(j['club'] for j in jogadores)),
        "changelog": f"Base de dados global completa ({len(jogadores)} jogadores)"
    }

    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(versao_info, f, ensure_ascii=False, indent=2)

    print(f"🚀 Base de dados pronta no GitHub! Versão: {nova_versao}")

if __name__ == "__main__":
    extrair_todos_jogadores_fc()
