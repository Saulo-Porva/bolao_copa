"""Generate correct Copa 2026 data files."""
from __future__ import annotations

import json

GROUPS = {
    "A": [
        {"code": "MEX", "name": "Mexico",              "name_pt": "México",              "confederation": "CONCACAF", "fifa_ranking": 13, "api_football_id": 16,   "football_data_id": None},
        {"code": "KOR", "name": "South Korea",         "name_pt": "Coreia do Sul",        "confederation": "AFC",      "fifa_ranking": 23, "api_football_id": 4,    "football_data_id": None},
        {"code": "CZE", "name": "Czech Republic",      "name_pt": "República Checa",      "confederation": "UEFA",     "fifa_ranking": 36, "api_football_id": None, "football_data_id": None},
        {"code": "RSA", "name": "South Africa",        "name_pt": "África do Sul",        "confederation": "CAF",      "fifa_ranking": 50, "api_football_id": None, "football_data_id": None},
    ],
    "B": [
        {"code": "CAN", "name": "Canada",              "name_pt": "Canadá",               "confederation": "CONCACAF", "fifa_ranking": 49, "api_football_id": 95,   "football_data_id": None},
        {"code": "SUI", "name": "Switzerland",         "name_pt": "Suíça",                "confederation": "UEFA",     "fifa_ranking": 19, "api_football_id": 7,    "football_data_id": None},
        {"code": "BIH", "name": "Bosnia Herzegovina", "name_pt": "Bósnia e Herzegovina", "confederation": "UEFA",     "fifa_ranking": 67, "api_football_id": None, "football_data_id": None},
        {"code": "QAT", "name": "Qatar",               "name_pt": "Catar",                "confederation": "AFC",      "fifa_ranking": 37, "api_football_id": None, "football_data_id": None},
    ],
    "C": [
        {"code": "MAR", "name": "Morocco",             "name_pt": "Marrocos",             "confederation": "CAF",      "fifa_ranking": 14, "api_football_id": None, "football_data_id": None},
        {"code": "SCO", "name": "Scotland",            "name_pt": "Escócia",              "confederation": "UEFA",     "fifa_ranking": 38, "api_football_id": None, "football_data_id": None},
        {"code": "BRA", "name": "Brazil",              "name_pt": "Brasil",               "confederation": "CONMEBOL", "fifa_ranking": 5,  "api_football_id": 6,    "football_data_id": 63},
        {"code": "HTI", "name": "Haiti",               "name_pt": "Haiti",                "confederation": "CONCACAF", "fifa_ranking": 83, "api_football_id": None, "football_data_id": None},
    ],
    "D": [
        {"code": "USA", "name": "United States",       "name_pt": "Estados Unidos",       "confederation": "CONCACAF", "fifa_ranking": 11, "api_football_id": None, "football_data_id": 762},
        {"code": "AUS", "name": "Australia",           "name_pt": "Austrália",            "confederation": "AFC",      "fifa_ranking": 23, "api_football_id": 35,   "football_data_id": None},
        {"code": "TUR", "name": "Turkey",              "name_pt": "Turquia",              "confederation": "UEFA",     "fifa_ranking": 36, "api_football_id": None, "football_data_id": None},
        {"code": "PAR", "name": "Paraguay",            "name_pt": "Paraguai",             "confederation": "CONMEBOL", "fifa_ranking": 65, "api_football_id": None, "football_data_id": None},
    ],
    "E": [
        {"code": "GER", "name": "Germany",             "name_pt": "Alemanha",             "confederation": "UEFA",     "fifa_ranking": 12, "api_football_id": 25,   "football_data_id": 759},
        {"code": "CIV", "name": "Ivory Coast",         "name_pt": "Costa do Marfim",      "confederation": "CAF",      "fifa_ranking": 50, "api_football_id": None, "football_data_id": None},
        {"code": "ECU", "name": "Ecuador",             "name_pt": "Equador",              "confederation": "CONMEBOL", "fifa_ranking": 30, "api_football_id": None, "football_data_id": None},
        {"code": "CUR", "name": "Curacao",             "name_pt": "Curaçao",              "confederation": "CONCACAF", "fifa_ranking": 90, "api_football_id": None, "football_data_id": None},
    ],
    "F": [
        {"code": "SWE", "name": "Sweden",              "name_pt": "Suécia",               "confederation": "UEFA",     "fifa_ranking": 24, "api_football_id": None, "football_data_id": None},
        {"code": "JPN", "name": "Japan",               "name_pt": "Japão",                "confederation": "AFC",      "fifa_ranking": 15, "api_football_id": 21,   "football_data_id": None},
        {"code": "NED", "name": "Netherlands",         "name_pt": "Holanda",              "confederation": "UEFA",     "fifa_ranking": 7,  "api_football_id": None, "football_data_id": 784},
        {"code": "TUN", "name": "Tunisia",             "name_pt": "Tunísia",              "confederation": "CAF",      "fifa_ranking": 28, "api_football_id": 28,   "football_data_id": None},
    ],
    "G": [
        {"code": "NZL", "name": "New Zealand",         "name_pt": "Nova Zelândia",        "confederation": "OFC",      "fifa_ranking": 95, "api_football_id": None, "football_data_id": None},
        {"code": "IRN", "name": "Iran",                "name_pt": "Irã",                  "confederation": "AFC",      "fifa_ranking": 22, "api_football_id": None, "football_data_id": None},
        {"code": "BEL", "name": "Belgium",             "name_pt": "Bélgica",              "confederation": "UEFA",     "fifa_ranking": 4,  "api_football_id": 1,    "football_data_id": 68},
        {"code": "EGY", "name": "Egypt",               "name_pt": "Egito",                "confederation": "CAF",      "fifa_ranking": 35, "api_football_id": None, "football_data_id": None},
    ],
    "H": [
        {"code": "URU", "name": "Uruguay",             "name_pt": "Uruguai",              "confederation": "CONMEBOL", "fifa_ranking": 10, "api_football_id": 34,   "football_data_id": None},
        {"code": "SAU", "name": "Saudi Arabia",        "name_pt": "Arábia Saudita",       "confederation": "AFC",      "fifa_ranking": 56, "api_football_id": None, "football_data_id": None},
        {"code": "ESP", "name": "Spain",               "name_pt": "Espanha",              "confederation": "UEFA",     "fifa_ranking": 9,  "api_football_id": 9,    "football_data_id": 760},
        {"code": "CPV", "name": "Cape Verde",          "name_pt": "Cabo Verde",           "confederation": "CAF",      "fifa_ranking": 75, "api_football_id": None, "football_data_id": None},
    ],
    "I": [
        {"code": "NOR", "name": "Norway",              "name_pt": "Noruega",              "confederation": "UEFA",     "fifa_ranking": 30, "api_football_id": None, "football_data_id": None},
        {"code": "FRA", "name": "France",              "name_pt": "França",               "confederation": "UEFA",     "fifa_ranking": 2,  "api_football_id": 2,    "football_data_id": 66},
        {"code": "SEN", "name": "Senegal",             "name_pt": "Senegal",              "confederation": "CAF",      "fifa_ranking": 20, "api_football_id": 37,   "football_data_id": None},
        {"code": "IRQ", "name": "Iraq",                "name_pt": "Iraque",               "confederation": "AFC",      "fifa_ranking": 70, "api_football_id": None, "football_data_id": None},
    ],
    "J": [
        {"code": "ARG", "name": "Argentina",           "name_pt": "Argentina",            "confederation": "CONMEBOL", "fifa_ranking": 1,  "api_football_id": 26,   "football_data_id": 64},
        {"code": "AUT", "name": "Austria",             "name_pt": "Áustria",              "confederation": "UEFA",     "fifa_ranking": 25, "api_football_id": None, "football_data_id": None},
        {"code": "JOR", "name": "Jordan",              "name_pt": "Jordânia",             "confederation": "AFC",      "fifa_ranking": 85, "api_football_id": None, "football_data_id": None},
        {"code": "ALG", "name": "Algeria",             "name_pt": "Argélia",              "confederation": "CAF",      "fifa_ranking": 34, "api_football_id": None, "football_data_id": None},
    ],
    "K": [
        {"code": "COL", "name": "Colombia",            "name_pt": "Colômbia",             "confederation": "CONMEBOL", "fifa_ranking": 8,  "api_football_id": 31,   "football_data_id": None},
        {"code": "COD", "name": "DR Congo",            "name_pt": "Congo (RD)",           "confederation": "CAF",      "fifa_ranking": 60, "api_football_id": None, "football_data_id": None},
        {"code": "POR", "name": "Portugal",            "name_pt": "Portugal",             "confederation": "UEFA",     "fifa_ranking": 6,  "api_football_id": 27,   "football_data_id": 765},
        {"code": "UZB", "name": "Uzbekistan",          "name_pt": "Uzbequistão",          "confederation": "AFC",      "fifa_ranking": 64, "api_football_id": None, "football_data_id": None},
    ],
    "L": [
        {"code": "ENG", "name": "England",             "name_pt": "Inglaterra",           "confederation": "UEFA",     "fifa_ranking": 3,  "api_football_id": 10,   "football_data_id": 66},
        {"code": "GHA", "name": "Ghana",               "name_pt": "Gana",                 "confederation": "CAF",      "fifa_ranking": 60, "api_football_id": 22,   "football_data_id": None},
        {"code": "PAN", "name": "Panama",              "name_pt": "Panamá",               "confederation": "CONCACAF", "fifa_ranking": 49, "api_football_id": None, "football_data_id": None},
        {"code": "CRO", "name": "Croatia",             "name_pt": "Croácia",              "confederation": "UEFA",     "fifa_ranking": 14, "api_football_id": 3,    "football_data_id": None},
    ],
}

STANDINGS = {
    "A": [
        {"Selecao": "México",           "J": 2, "V": 2, "E": 0, "D": 0, "GM": 3, "GS": 0, "Pts": 6, "code": "MEX"},
        {"Selecao": "Coreia do Sul",    "J": 2, "V": 1, "E": 0, "D": 1, "GM": 2, "GS": 2, "Pts": 3, "code": "KOR"},
        {"Selecao": "Rep. Checa",       "J": 2, "V": 0, "E": 1, "D": 1, "GM": 2, "GS": 3, "Pts": 1, "code": "CZE"},
        {"Selecao": "Africa do Sul",    "J": 2, "V": 0, "E": 1, "D": 1, "GM": 1, "GS": 3, "Pts": 1, "code": "RSA"},
    ],
    "B": [
        {"Selecao": "Canada",           "J": 2, "V": 1, "E": 1, "D": 0, "GM": 7, "GS": 1, "Pts": 4, "code": "CAN"},
        {"Selecao": "Suica",            "J": 2, "V": 1, "E": 1, "D": 0, "GM": 5, "GS": 2, "Pts": 4, "code": "SUI"},
        {"Selecao": "Bosnia e Herz.",   "J": 2, "V": 0, "E": 1, "D": 1, "GM": 2, "GS": 5, "Pts": 1, "code": "BIH"},
        {"Selecao": "Catar",            "J": 2, "V": 0, "E": 1, "D": 1, "GM": 1, "GS": 7, "Pts": 1, "code": "QAT"},
    ],
    "C": [
        {"Selecao": "Marrocos",         "J": 2, "V": 1, "E": 1, "D": 0, "GM": 2, "GS": 1, "Pts": 4, "code": "MAR"},
        {"Selecao": "Escocia",          "J": 2, "V": 1, "E": 0, "D": 1, "GM": 1, "GS": 1, "Pts": 3, "code": "SCO"},
        {"Selecao": "Brasil",           "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "BRA"},
        {"Selecao": "Haiti",            "J": 1, "V": 0, "E": 0, "D": 1, "GM": 0, "GS": 1, "Pts": 0, "code": "HTI"},
    ],
    "D": [
        {"Selecao": "EUA",              "J": 2, "V": 2, "E": 0, "D": 0, "GM": 6, "GS": 1, "Pts": 6, "code": "USA"},
        {"Selecao": "Australia",        "J": 2, "V": 1, "E": 0, "D": 1, "GM": 2, "GS": 2, "Pts": 3, "code": "AUS"},
        {"Selecao": "Turquia",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 0, "GS": 2, "Pts": 0, "code": "TUR"},
        {"Selecao": "Paraguai",         "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 4, "Pts": 0, "code": "PAR"},
    ],
    "E": [
        {"Selecao": "Alemanha",         "J": 1, "V": 1, "E": 0, "D": 0, "GM": 7, "GS": 1, "Pts": 3, "code": "GER"},
        {"Selecao": "Costa do Marfim",  "J": 1, "V": 1, "E": 0, "D": 0, "GM": 1, "GS": 0, "Pts": 3, "code": "CIV"},
        {"Selecao": "Equador",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 0, "GS": 1, "Pts": 0, "code": "ECU"},
        {"Selecao": "Curacao",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 7, "Pts": 0, "code": "CUR"},
    ],
    "F": [
        {"Selecao": "Suecia",           "J": 1, "V": 1, "E": 0, "D": 0, "GM": 5, "GS": 1, "Pts": 3, "code": "SWE"},
        {"Selecao": "Japao",            "J": 1, "V": 0, "E": 1, "D": 0, "GM": 2, "GS": 2, "Pts": 1, "code": "JPN"},
        {"Selecao": "Holanda",          "J": 1, "V": 0, "E": 1, "D": 0, "GM": 2, "GS": 2, "Pts": 1, "code": "NED"},
        {"Selecao": "Tunisia",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 5, "Pts": 0, "code": "TUN"},
    ],
    "G": [
        {"Selecao": "Nova Zelandia",    "J": 1, "V": 0, "E": 1, "D": 0, "GM": 2, "GS": 2, "Pts": 1, "code": "NZL"},
        {"Selecao": "Ira",              "J": 1, "V": 0, "E": 1, "D": 0, "GM": 2, "GS": 2, "Pts": 1, "code": "IRN"},
        {"Selecao": "Belgica",          "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "BEL"},
        {"Selecao": "Egito",            "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "EGY"},
    ],
    "H": [
        {"Selecao": "Uruguai",          "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "URU"},
        {"Selecao": "Arabia Saudita",   "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "SAU"},
        {"Selecao": "Espanha",          "J": 1, "V": 0, "E": 1, "D": 0, "GM": 0, "GS": 0, "Pts": 1, "code": "ESP"},
        {"Selecao": "Cabo Verde",       "J": 1, "V": 0, "E": 1, "D": 0, "GM": 0, "GS": 0, "Pts": 1, "code": "CPV"},
    ],
    "I": [
        {"Selecao": "Noruega",          "J": 1, "V": 1, "E": 0, "D": 0, "GM": 4, "GS": 1, "Pts": 3, "code": "NOR"},
        {"Selecao": "Franca",           "J": 1, "V": 1, "E": 0, "D": 0, "GM": 3, "GS": 1, "Pts": 3, "code": "FRA"},
        {"Selecao": "Senegal",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 3, "Pts": 0, "code": "SEN"},
        {"Selecao": "Iraque",           "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 4, "Pts": 0, "code": "IRQ"},
    ],
    "J": [
        {"Selecao": "Argentina",        "J": 1, "V": 1, "E": 0, "D": 0, "GM": 3, "GS": 0, "Pts": 3, "code": "ARG"},
        {"Selecao": "Austria",          "J": 1, "V": 1, "E": 0, "D": 0, "GM": 3, "GS": 1, "Pts": 3, "code": "AUT"},
        {"Selecao": "Jordania",         "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 3, "Pts": 0, "code": "JOR"},
        {"Selecao": "Algeria",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 0, "GS": 3, "Pts": 0, "code": "ALG"},
    ],
    "K": [
        {"Selecao": "Colombia",         "J": 1, "V": 1, "E": 0, "D": 0, "GM": 3, "GS": 1, "Pts": 3, "code": "COL"},
        {"Selecao": "Congo RD",         "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "COD"},
        {"Selecao": "Portugal",         "J": 1, "V": 0, "E": 1, "D": 0, "GM": 1, "GS": 1, "Pts": 1, "code": "POR"},
        {"Selecao": "Uzbequistao",      "J": 1, "V": 0, "E": 0, "D": 1, "GM": 1, "GS": 3, "Pts": 0, "code": "UZB"},
    ],
    "L": [
        {"Selecao": "Inglaterra",       "J": 1, "V": 1, "E": 0, "D": 0, "GM": 4, "GS": 2, "Pts": 3, "code": "ENG"},
        {"Selecao": "Gana",             "J": 1, "V": 1, "E": 0, "D": 0, "GM": 1, "GS": 0, "Pts": 3, "code": "GHA"},
        {"Selecao": "Panama",           "J": 1, "V": 0, "E": 0, "D": 1, "GM": 0, "GS": 1, "Pts": 0, "code": "PAN"},
        {"Selecao": "Croacia",          "J": 1, "V": 0, "E": 0, "D": 1, "GM": 2, "GS": 4, "Pts": 0, "code": "CRO"},
    ],
}


def main() -> None:
    # teams_48.json
    teams = []
    for group, team_list in GROUPS.items():
        for t in team_list:
            teams.append({
                "code": t["code"],
                "name": t["name"],
                "name_pt": t["name_pt"],
                "confederation": t["confederation"],
                "fifa_ranking": t["fifa_ranking"],
                "group": group,
                "api_football_id": t["api_football_id"],
                "football_data_id": t["football_data_id"],
            })
    with open("data/teams_48.json", "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print(f"teams_48.json: {len(teams)} teams across {len(GROUPS)} groups")

    # copa2026_fixtures.json
    fixtures = []
    for group, team_list in GROUPS.items():
        codes = [t["code"] for t in team_list]
        names = {t["code"]: t["name_pt"] for t in team_list}
        matches = []
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                matches.append({
                    "home": codes[i],
                    "away": codes[j],
                    "label": f"{names[codes[i]]} x {names[codes[j]]}",
                })
        fixtures.append({"group": group, "teams": codes, "matches": matches})
    with open("data/copa2026_fixtures.json", "w", encoding="utf-8") as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    total_matches = sum(len(g["matches"]) for g in fixtures)
    print(f"copa2026_fixtures.json: {len(fixtures)} groups, {total_matches} matches")

    # copa2026_standings.json
    with open("data/copa2026_standings.json", "w", encoding="utf-8") as f:
        json.dump(STANDINGS, f, ensure_ascii=False, indent=2)
    print(f"copa2026_standings.json: {len(STANDINGS)} groups")

    print("Done.")


if __name__ == "__main__":
    main()
