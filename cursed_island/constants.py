# Konstanta global game
import os

# Currency System
CURRENCY_NAME = "Dollars"
CURRENCY_SINGULAR = "Dollar"
CURRENCY_PLURAL = "Dollars"
CURRENCY_SHORT = "$"

# Monster Drops
BASE_MONEY_DROP = 10  # Base dollars dropped per enemy
BASE_XP_DROP = 25     # Base XP dropped per enemy

# Combat System
BASE_ATTACK = 10
BASE_DEFENSE = 10
BASE_SPEED = 10
BASE_HP = 100
BASE_ENERGY = 30

# Leveling System
BASE_XP_TO_LEVEL = 100
LEVEL_UP_HP_GAIN = 12
LEVEL_UP_ATTACK_GAIN = 2
LEVEL_UP_DEFENSE_GAIN = 2
LEVEL_UP_SPEED_GAIN = 1
LEVEL_UP_ENERGY_GAIN = 5
XP_SCALE_FACTOR = 1.15

# Terminal & Display
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 24
DEFAULT_TERMINAL_WIDTH = 80
DEFAULT_TERMINAL_HEIGHT = 24

# Game Settings
GAME_VERSION = "0.3.2"
SAVE_FILE = os.path.join("saves", "data.txt")
CONFIG_FILE = os.path.join("cursed_island", "data", "card_dialogs.json")

# Chapter System — 6 chapter total
MAX_CHAPTERS = 6
BOSS_CHAPTERS = [2, 4, 6]   # Chapter dengan boss battle
FINAL_CHAPTER = 6

# Boss identifiers per chapter
# Ch2: setiap karakter punya boss unik di area berbeda
# Ch4: Ghislaine Maxwell di pusat kendali (command_center)
# Ch6: Jeffrey Epstein di Mansion Timur (Final Boss)
CHAPTER_BOSSES = {
    2: "varies_by_char",      # Ch2: boss unik per karakter — lihat exploration.py CH2_BOSSES
    4: "ghislaine_maxwell",   # Ghislaine Maxwell — Pusat Kendali (Ch4)
    6: "epstein_boss",        # Jeffrey Epstein — Ch6 Final Boss
}

# NPC Sidequest System (menggantikan party system)
# NPC tidak join party — mereka kasih KEY ITEM yang dibutuhkan main quest
NPC_IDS = ['haikaru', 'aolinh', 'arganta', 'ignatius', 'vio']
SIDEQUESTS_NEEDED_FOR_CH4 = 2   # Min sidequest selesai sebelum bisa ke Ch4
SIDEQUESTS_NEEDED_FOR_CH6 = 4   # Min sidequest selesai sebelum Ch6

# Dialog & UI
# Quest Items — item objektif unik yang tidak boleh duplikat di inventory
# Dipakai oleh GameState.add_quest_item() untuk dedup guard
QUEST_ITEM_NAMES = {
    # Vio route
    'Keycard Level 1', 'Keycard Level 2', 'Keycard Level 3', 'Access Card',
    'USB Encrypted', 'Akses Level 3', 'USB Security Drive',
    # Haikaru route
    'Buku Catatan', 'Buku Catatan Haikaru', 'Peta Blind Spot Penjara', 'Info Pulau',
    'Catatan Sandi Haikaru', 'Kunci Wing-C',
    # Aolinh route
    'Tiket Backstage', 'Rekaman Distraksi Aolinh', 'Gantungan Kunci Musik',
    # Arganta route
    'Kompas Nonno Arganta', 'Kompas Aktif', 'Peta Jalur Rahasia',
    # Ignatius route
    'Kapasitor Besar', 'Relay Switch', 'Copper Coil', 'EMP Prototype',
    'Blueprint', 'EMP Device',
    # General progression
    'Epstein Phone', 'Rekaman Candala', 'USB Evidence Drive',
    'Kunci Master Penjara', 'Kartu Akses Lab',
    # New boss drops
    'Maxwell Agent Badge', 'Server Room Keycard', 'Network Master Key',
    'Dock Commander Badge', 'Mercenary Contract',
}

FALLBACK_CARD_DIALOGS = {
    "attack": "Serang!",
    "defend": "Pertahanan!",
    "heal": "Pulihkan!",
    "special": "Kekuatan khusus!",
    "flee": "Melariiiii!",
    "default": "Aksi!",
}
