from __future__ import annotations

import json
from pathlib import Path


TRANSLATIONS = {
    "en": {
        "app_title": "CONNECT 4",
        "one_player": "1 PLAYER",
        "two_players": "2 PLAYERS",
        "rules": "RULES",
        "quit": "QUIT",
        "team_name": "TEAM 5",
        "settings_title": "SETTINGS",
        "settings_language": "Language",
        "settings_close": "CLOSE",
        "settings_saved": "Changes apply immediately.",
        "language_en": "English",
        "language_vi": "Vietnamese",
        "rules_title": "HOW TO PLAY",
        "rules_lines": [
            "Players take turns dropping one disc into any non-full column.",
            "The first side that connects 4 discs in a row wins.",
            "A winning line can be horizontal, vertical, or diagonal.",
            "In 1 Player mode you control Blue and the AI controls Yellow.",
            "In 2 Players mode Blue moves first, then Yellow.",
        ],
        "rules_close": "BACK",
        "levels": "LEVELS",
        "back_home": "BACK",
        "easy": "EASY",
        "medium": "MEDIUM",
        "hard": "HARD",
        "exit": "EXIT",
        "turn_blue": "BLUE'S TURN",
        "turn_yellow": "YELLOW'S TURN",
        "turn_blue_wins": "BLUE WINS",
        "turn_yellow_wins": "YELLOW WINS",
        "turn_draw": "DRAW",
        "footer_depth": "DEPTH {depth}",
        "footer_timeout": "TIME OUT",
        "footer_connect4": "CONNECT 4",
        "footer_draw": "DRAW",
        "footer_two_players": "2 PLAYERS",
        "player_you": "YOU",
        "player_ai": "AI",
        "player_one": "P1",
        "player_two": "P2",
        "reset_title": "Reset current match?",
        "reset_body": "The board will be cleared and both timers restart.",
        "reset_keep": "KEEP PLAYING",
        "reset_confirm": "RESET",
        "settings_button": "SETTINGS",
        "winner_blue": "BLUE",
        "winner_yellow": "YELLOW",
        "winner_draw": "DRAW",
        "winner_popup_win": "WIN",
        "winner_popup_draw": "DRAW",
        "play_again": "PLAY AGAIN",
        "winner_reason_connect4": "4 discs connected",
        "winner_reason_timeout": "Win by time out",
        "winner_reason_draw": "No more valid moves",
    },
    "vi": {
        "app_title": "CONNECT 4",
        "one_player": "1 NGUOI CHOI",
        "two_players": "2 NGUOI CHOI",
        "rules": "LUAT CHOI",
        "quit": "THOAT",
        "team_name": "NHOM 5",
        "settings_title": "CAI DAT",
        "settings_language": "Ngon ngu",
        "settings_close": "DONG",
        "settings_saved": "Ap dung ngay lap tuc.",
        "language_en": "Tieng Anh",
        "language_vi": "Tieng Viet",
        "rules_title": "CACH CHOI",
        "rules_lines": [
            "Moi luot, nguoi choi tha 1 quan vao cot con trong.",
            "Ben nao noi duoc 4 quan lien tiep se gianh chien thang.",
            "4 quan co the nam ngang, doc hoac cheo.",
            "Che do 1 nguoi choi: ban danh quan Xanh, AI danh quan Vang.",
            "Che do 2 nguoi choi: quan Xanh di truoc, sau do den quan Vang.",
        ],
        "rules_close": "QUAY LAI",
        "levels": "CAP DO",
        "back_home": "QUAY LAI",
        "easy": "DE",
        "medium": "TRUNG BINH",
        "hard": "KHO",
        "exit": "THOAT",
        "turn_blue": "LUOT XANH",
        "turn_yellow": "LUOT VANG",
        "turn_blue_wins": "XANH THANG",
        "turn_yellow_wins": "VANG THANG",
        "turn_draw": "HOA",
        "footer_depth": "DO SAU {depth}",
        "footer_timeout": "HET GIO",
        "footer_connect4": "CONNECT 4",
        "footer_draw": "HOA",
        "footer_two_players": "2 NGUOI CHOI",
        "player_you": "BAN",
        "player_ai": "AI",
        "player_one": "N1",
        "player_two": "N2",
        "reset_title": "Choi lai van hien tai?",
        "reset_body": "Ban co se duoc xoa va dong ho tinh lai tu dau.",
        "reset_keep": "CHOI TIEP",
        "reset_confirm": "RESET",
        "settings_button": "CAI DAT",
        "winner_blue": "XANH",
        "winner_yellow": "VANG",
        "winner_draw": "HOA",
        "winner_popup_win": "WIN",
        "winner_popup_draw": "DRAW",
        "play_again": "CHOI LAI",
        "winner_reason_connect4": "Noi du 4 quan",
        "winner_reason_timeout": "Thang do het gio",
        "winner_reason_draw": "Khong con nuoc di hop le",
    },
}


class GamePreferences:
    def __init__(self, storage_path=None):
        project_root = Path(__file__).resolve().parents[1]
        self.storage_path = Path(storage_path) if storage_path else project_root / "preferences.json"
        self.language = "en"
        self.load()

    def load(self):
        if not self.storage_path.exists():
            return

        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        language = payload.get("language", "en")
        if language in TRANSLATIONS:
            self.language = language

    def save(self):
        payload = {"language": self.language}
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def set_language(self, language):
        if language not in TRANSLATIONS:
            return
        self.language = language

    def text(self, key):
        current = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        fallback = TRANSLATIONS["en"]
        return current.get(key, fallback.get(key, key))

    def format(self, key, **kwargs):
        return self.text(key).format(**kwargs)

    def rules_lines(self):
        return list(self.text("rules_lines"))
