import json
from pathlib import Path

import pygame


SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"
LEGACY_SETTINGS_FILE = Path(__file__).resolve().parent.parent / "preferences.json"
SUPPORTED_LANGUAGES = ("en", "vi")

LANGUAGE_NAMES = {
    "en": "English",
    "vi": "Tieng Viet",
}

TRANSLATIONS = {
    "en": {
        "app_title": "CONNECT 4",
        "one_player": "1 PLAYER",
        "two_players": "2 PLAYERS",
        "rules": "RULES",
        "quit": "QUIT",
        "team_name": "TEAM 5",
        "home_1player": "1 PLAYER",
        "home_2players": "2 PLAYERS",
        "home_rules": "RULES",
        "home_quit": "QUIT",
        "settings_title": "SETTINGS",
        "settings_volume": "VOLUME",
        "settings_language": "LANGUAGE",
        "settings_save": "SAVE",
        "settings_close": "EXIT",
        "settings_saved": "Changes are applied when you press Save.",
        "about_title": "ABOUT",
        "donate_title": "DONATE",
        "save": "SAVE",
        "exit": "EXIT",
        "play_again": "PLAY AGAIN",
        "yes": "YES",
        "no": "NO",
        "quit_prompt": "ARE YOU SURE YOU WANT TO QUIT ?",
        "language_en": "English",
        "language_vi": "Vietnamese",
        "rules_title": "HOW TO PLAY",
        "rules_close": "EXIT",
        "rules_lines": [
            "Players take turns dropping a piece into one of the columns.",
            "On each turn, choose a column.",
            "The piece falls to the lowest empty slot in that column.",
            "You cannot place a piece in a full column.",
            "Connect four matching pieces in a row, column, or diagonal to win.",
            "If the board fills up and nobody connects four, the game is a draw.",
        ],
        "about_intro": "Project Team 5, Artificial Intelligence, UTC.",
        "about_highlight": "This game was first developed by",
        "about_creator": "Howard Wexler",
        "about_names": [
            "Ta Bach Dat",
            "Le Nhat Long",
            "Nguyen Dieu Linh",
        ],
        "levels": "LEVELS",
        "back_home": "BACK",
        "easy": "EASY",
        "medium": "MEDIUM",
        "hard": "HARD",
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
        "winner_reason_connect4": "4 discs connected",
        "winner_reason_timeout": "Win by time out",
        "winner_reason_draw": "No more valid moves",
    },
    "vi": {
        "app_title": "CONNECT 4",
        "one_player": "1 NGƯỜI CHƠI",
        "two_players": "2 NGƯỜI CHƠI",
        "rules": "LUẬT CHƠI",
        "quit": "THOÁT",
        "team_name": "NHÓM 5",
        "home_1player": "1 NGƯỜI CHƠI",
        "home_2players": "2 NGƯỜI CHƠI",
        "home_rules": "LUẬT CHƠI",
        "home_quit": "THOÁT",
        "settings_title": "CÀI ĐẶT",
        "settings_volume": "ÂM THANH",
        "settings_language": "NGÔN NGỮ",
        "settings_save": "LƯU",
        "settings_close": "THOÁT",
        "settings_saved": "Nhấn Lưu để áp dụng.",
        "about_title": "GIỚI THIỆU",
        "donate_title": "ỦNG HỘ",
        "save": "LƯU",
        "exit": "THOÁT",
        "play_again": "CHƠI LẠI",
        "yes": "CÓ",
        "no": "KHÔNG",
        "quit_prompt": "BẠN CÓ CHẮC CHẮN MUỐN THOÁT KHÔNG?",
        "language_en": "Tiếng Anh",
        "language_vi": "Tiếng Việt",
        "rules_title": "LUẬT CHƠI",
        "rules_close": "THOÁT",
        "rules_lines": [
            "Hai người lần lượt thay phiên nhau thả quân cờ vào các cột.",
            "Mỗi lượt, bạn chọn một cột.",
            "Quân cờ sẽ rơi xuống vị trí thấp nhất còn trống trong cột đó.",
            "Bạn không thể đặt quân vào cột đã đầy.",
            "Ai tạo được 4 quân cùng màu liên tiếp theo hàng ngang, dọc hoặc chéo trước sẽ thắng.",
            "Bảng đầy và không có 4 quân liên tiếp thì hòa.",
        ],
        "about_intro": "Project team 5 môn Trí tuệ nhân tạo, UTC.",
        "about_highlight": "Trò chơi được phát triển lần đầu bởi",
        "about_creator": "Howard Wexler",
        "about_names": [
            "Tạ Bách Đạt",
            "Lê Nhật Long",
            "Nguyễn Diệu Linh",
        ],
        "levels": "CẤP ĐỘ",
        "back_home": "QUAY LẠI",
        "easy": "DỄ",
        "medium": "TRUNG BÌNH",
        "hard": "KHÓ",
        "turn_blue": "LƯỢT XANH",
        "turn_yellow": "LƯỢT VÀNG",
        "turn_blue_wins": "XANH THẮNG",
        "turn_yellow_wins": "VÀNG THẮNG",
        "turn_draw": "HÒA",
        "footer_depth": "ĐỘ SÂU {depth}",
        "footer_timeout": "HẾT GIỜ",
        "footer_connect4": "NỐI 4",
        "footer_draw": "HÒA",
        "footer_two_players": "2 NGƯỜI CHƠI",
        "player_you": "BẮN",
        "player_ai": "AI",
        "player_one": "N1",
        "player_two": "N2",
        "reset_title": "Chơi lại ván hiện tại?",
        "reset_body": "Bàn cờ sẽ được xóa và đồng hồ sẽ được đặt lại.",
        "reset_keep": "CHƠI TIẾP",
        "reset_confirm": "RESET",
        "settings_button": "CÀI ĐẶT",
        "winner_blue": "XANH",
        "winner_yellow": "VÀNG",
        "winner_draw": "HÒA",
        "winner_popup_win": "WIN",
        "winner_popup_draw": "DRAW",
        "winner_reason_connect4": "Nối đủ 4 quân",
        "winner_reason_timeout": "Thắng do hết giờ",
        "winner_reason_draw": "Không còn nước đi hợp lệ",
    },
}


class GamePreferences:
    def __init__(self, storage_path=None):
        self.storage_path = Path(storage_path) if storage_path else SETTINGS_FILE
        self.legacy_storage_path = LEGACY_SETTINGS_FILE
        self.language = "en"
        self.volume_on = True
        self.load()

    def load(self):
        source = self.storage_path if self.storage_path.exists() else self.legacy_storage_path
        if not source.exists():
            return

        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        language = payload.get("language", "en")
        if language in SUPPORTED_LANGUAGES:
            self.language = language
        self.volume_on = bool(payload.get("volume_on", True))

    def save(self):
        payload = {
            "language": self.language,
            "volume_on": self.volume_on,
        }
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def set_language(self, language):
        if language in SUPPORTED_LANGUAGES:
            self.language = language

    def set_volume(self, volume_on):
        self.volume_on = bool(volume_on)
        self.apply_audio()

    def toggle_volume(self):
        self.set_volume(not self.volume_on)

    def apply_audio(self):
        if not pygame.mixer.get_init():
            return

        volume = 1.0 if self.volume_on else 0.0
        try:
            pygame.mixer.music.set_volume(volume)
        except pygame.error:
            pass

    def text(self, key):
        current = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        fallback = TRANSLATIONS["en"]
        return current.get(key, fallback.get(key, key))

    def format(self, key, **kwargs):
        return self.text(key).format(**kwargs)

    def lines(self, key):
        value = self.text(key)
        if isinstance(value, list):
            return list(value)
        return [str(value)]

    def rules_lines(self):
        return self.lines("rules_lines")

    def language_label(self, language_code):
        return LANGUAGE_NAMES.get(language_code, language_code.upper())
