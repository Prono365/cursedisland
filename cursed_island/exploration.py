import random
import os
import sys
import time
import shutil
import re as _re
from itertools import product
from .sprites import Warna, SPRITES
from .characters import get_character_intro, get_character_data
from .constants import (LEVEL_UP_HP_GAIN, LEVEL_UP_ATTACK_GAIN,
                       LEVEL_UP_DEFENSE_GAIN, LEVEL_UP_SPEED_GAIN)

def _tw():
    """Terminal width — dipanggil tiap render agar otomatis fit saat resize."""
    return max(40, shutil.get_terminal_size(fallback=(80, 24)).columns)

def _strip_ansi(s):
    """Hapus ANSI escape codes untuk hitung panjang teks asli."""
    return _re.sub(r'\x1b\[[0-9;]*[mA-Za-z]', '', s)

def _trunc(text, maxlen, suffix='…'):
    """Potong teks agar tidak wrap ke baris berikutnya."""
    clean = _strip_ansi(text)
    if len(clean) <= maxlen:
        return text
    # Potong teks asli (tanpa ANSI) agar tepat
    return text[:maxlen - len(suffix)] + suffix + Warna.RESET

# Quest items vs regular items — quest items show [!] in inventory
QUEST_ITEMS = {
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
}

def is_quest_item(item_name):
    return item_name in QUEST_ITEMS

# Exploration system - map navigation, enemy encounters, location tracking

try:
    from .utils import clear_screen, flush_input
except ImportError:
    from contextlib import suppress
    
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def flush_input():
        with suppress(Exception):
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)

def _direction_arrow(px, py, tx, ty):
    """Kembalikan simbol panah 8-arah dari posisi player ke target."""
    dx = tx - px
    dy = ty - py
    if dx == 0 and dy == 0:
        return "●"
    ax, ay = abs(dx), abs(dy)
    if ax > ay * 2:
        return "→" if dx > 0 else "←"
    if ay > ax * 2:
        return "↓" if dy > 0 else "↑"
    if dx > 0 and dy < 0:
        return "↗"
    if dx > 0 and dy > 0:
        return "↘"
    return "↖" if dx < 0 and dy < 0 else "↙"

def _manhattan(px, py, tx, ty):
    return abs(tx - px) + abs(ty - py)

def _distance_label(dist):
    if dist <= 3:
        return "sangat dekat!"
    if dist <= 7:
        return f"~{dist} langkah"
    return f"~{dist} langkah" if dist <= 12 else f"~{dist} langkah (jauh)"

class MapTile:
    def __init__(self, tile_type, walkable=True, description=""):
        self.type = tile_type
        self.walkable = walkable
        self.description = description

class GameMap:
    def __init__(self, map_id, width=25, height=18, current_player_char=None):
        self.map_id = map_id
        self.width = width
        self.height = height
        self.current_player_char = current_player_char
        self.tiles = [[MapTile(0, True, "Floor") for _ in range(width)] for _ in range(height)]
        self.player_x = width // 2
        self.player_y = height // 2
        self.enemies    = []
        self.npcs       = []
        self.items      = []
        self.exits      = []
        self.boss_doors = []
        self.discovered = {(self.player_x, self.player_y)}
        self.enemy_counter = 0

    def _validate_spawn_point(self, x, y):
        
        MAX_SEARCH_RADIUS = 8  # Cukup untuk semua map 25x18
        if 0 <= x < self.width and 0 <= y < self.height and self.tiles[y][x].walkable:
            return x, y
        for radius in range(1, MAX_SEARCH_RADIUS + 1):
            for dx, dy in product(range(-radius, radius + 1), repeat=2):
                if abs(dx) != radius and abs(dy) != radius:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.tiles[ny][nx].walkable:
                    return nx, ny
        # Fallback mutlak: tengah peta
        return self.width // 2, self.height // 2

    def generate_island(self):
        for y in range(self.height):
            for x in range(self.width):
                if x < 2 or x >= self.width - 2 or y < 2 or y >= self.height - 2:
                    self.tiles[y][x] = MapTile(7, False, "Ocean")
                elif x < 3 or x >= self.width - 3 or y < 3 or y >= self.height - 3:
                    self.tiles[y][x] = MapTile(0, True, "Beach")
                else:
                    self.tiles[y][x] = MapTile(8 if random.random() < 0.25 else 0, True, "Path")

        self.create_path(self.width // 2, 3, self.width // 2, self.height - 3)
        self.create_path(3, self.height // 2, self.width - 3, self.height // 2)

        self.place_exit(7,  7,  "prison_north", "Penjara")
        self.place_exit(7,  13, "mansion",       "Mansion")
        self.place_exit(18, 13, "dock",          "Dermaga")
        self.place_exit(12, 5,  "command_center","Pusat Kontrol [Ch.2+]")
        self.place_exit(12, 15, "theater",       "Teater")
        self.place_exit(3,  9,  "beach",         "Pantai")
        self.place_exit(22, 5,  "laboratory",    "Laboratorium [Ch.4+]")
        self.place_exit(22, 13, "mansion_east",  "Mansion Timur - Area Final [Ch.5+]")

        self.add_enemy_patrol(6,  6,  "guard_novice",  [(6,6),  (9,6),  (9,9),  (6,9)])
        self.add_enemy_patrol(19, 6,  "guard_veteran", [(19,6), (22,6), (22,9), (19,9)])
        self.add_enemy_patrol(12, 11, "guard_elite",   [(12,11),(18,11)])
        self.add_enemy_patrol(4,  14, "mercenary_thug",[(4,14), (8,14)])
        self.add_enemy_patrol(20, 14, "scientist",     [(20,14),(20,10)])

        # Di island hub (chapter 2), karakter lain mungkin terlihat
        # Haikaru di penjara utara, Aolinh di teater — jangan spawn di island
        # Dynamic: potions/bandages respawn every 7 minutes; key items permanent
        self.place_item(10, 8,  "Health Potion",    respawn_delay=420)
        self.place_item(15, 8,  "Keycard Level 1")
        self.place_item(5,  12, "Bandage",           respawn_delay=420)
        self.place_item(20, 11, "Med Kit",           respawn_delay=600)
        self.place_item(12, 6,  "Health Potion",     respawn_delay=420)

        self.player_x, self.player_y = self._validate_spawn_point(12, 12)

    def generate_prison(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Wall")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Floor")

        for x in range(5, self.width - 5, 5):
            for y in range(5, self.height - 5, 5):
                if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                    self.tiles[y][x] = MapTile(6, False, "Pillar")

        for x in range(8, 17):
            if 0 < x < self.width - 1:
                self.tiles[9][x] = MapTile(1, False, "Cell")

        self.place_exit(12, 1, "island", "Keluar")
        self.add_enemy_patrol(8,  8,  "guard_novice",   [(8,8),  (16,8), (16,10), (8,10)])
        self.add_enemy_patrol(5,  5,  "guard_veteran",  [(5,5),  (10,5)])
        self.add_enemy_patrol(19, 12, "mercenary_thug", [(19,12),(19,15)])
        self.add_enemy_patrol(14, 4,  "guard_novice",   [(14,4), (20,4)])
        # Haikaru ada di prison_north sebagai NPC untuk karakter lain
        # (place_npc() sudah otomatis skip jika npc_id == current_player_char)
        self.place_npc(10, 9, "haikaru")
        self.place_item(15, 9,  "Med Kit")           # blind spot #1 — Haikaru
        self.place_item(5,  4,  "Keycard Level 1")   # blind spot #2 — Haikaru
        self.place_item(10, 13, "Info Pulau")         # blind spot #3 — Haikaru (FIX: 3 harus ada)
        self.place_item(20, 9,  "Health Potion")
        self.place_item(8,  13, "Bandage")
        self.place_item(20, 13, "Kunci Wing-C")

        self.player_x, self.player_y = self._validate_spawn_point(12, 3)

    def generate_mansion(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Wall")
                elif x % 4 == 0 and y % 3 == 0:
                    if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                        self.tiles[y][x] = MapTile(6, False, "Column")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Floor")

        self.place_exit(12, 1, "island", "Keluar")
        self.place_exit(12, 16, "basement", "Turun ke Basement")
        # FIX: Kolom di (12,15) menghalangi akses ke pintu basement.
        # Paksa tile (12,15) menjadi floor agar pemain bisa melewatinya.
        self.tiles[15][12] = MapTile(0, True, "Floor")
        # Boss akan di-spawn setelah main quest chapter selesai (bukan saat map generate)

        self.add_enemy_patrol(8,  10, "guard_elite",      [(8,10),  (16,10)])
        self.add_enemy_patrol(16, 6,  "mercenary_sniper", [(16,6),  (16,10)])
        self.add_enemy_patrol(5,  5,  "guard_novice",     [(5,5),   (10,5)])
        self.add_enemy_patrol(20, 12, "mansion_guard",    [(20,12), (16,12)])
        self.add_enemy_patrol(12, 7,  "tech_guard",       [(12,7),  (18,7)])

        self.place_item(18, 8, "Armor Vest")
        self.place_item(8,  6, "Keycard Level 1")
        self.place_item(18, 12, "Access Card")

        self.player_x, self.player_y = self._validate_spawn_point(12, 3)

    def generate_command_center(self):
        """Pusat Kontrol — server room / ruang operasi pulau.
        Tersedia Ch.2+. Digunakan sebagai hub sidequest dan boss Ch.3.
        """
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Dinding Beton")
                elif (x % 5 == 0 and 0 < x < self.width - 1
                      and 0 < y < self.height - 1):
                    self.tiles[y][x] = MapTile(6, False, "Server Rack")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Lantai Kontrol")

        for x in range(3, self.width - 3):
            if 0 < x < self.width - 1:
                self.tiles[4][x] = MapTile(11, False, "Konsol Utama")
        for x in range(6, self.width - 6):
            self.tiles[4][x] = MapTile(0, True, "Ruang Operator")

        self.place_exit(12, self.height - 2, "island", "Kembali ke Pulau")

        self.add_enemy_patrol(8,  8,  "tech_guard",    [(8,8),   (16,8)])
        self.add_enemy_patrol(5,  12, "guard_elite",   [(5,12),  (10,12)])
        self.add_enemy_patrol(18, 12, "mansion_guard", [(18,12), (22,12)])

        self.place_item(5,  8,  "Health Potion",  respawn_delay=420)
        self.place_item(19, 8,  "Med Kit",         respawn_delay=600)
        self.place_item(10, 6,  "Keycard Level 2")
        self.place_item(15, 6,  "Info Pulau")
        self.place_item(12, 10, "Bandage",         respawn_delay=420)

        self.player_x, self.player_y = self._validate_spawn_point(12, self.height - 4)

    def generate_dock(self):
        
        for y in range(self.height):
            for x in range(self.width):
                if x < 10:
                    self.tiles[y][x] = MapTile(0, True, "Dock")
                    if y in (0, self.height - 1):
                        self.tiles[y][x] = MapTile(1, False, "Fence")
                else:
                    self.tiles[y][x] = MapTile(7, False, "Water")

        self.place_exit(1, self.height // 2, "island", "Keluar")

        self.place_item(4,  8,  "Health Potion")
        self.place_item(4,  10, "Med Kit")
        self.place_item(18, 8,  "Bandage")
        self.place_item(12, 12, "Keycard Level 2")

        self.player_x, self.player_y = self._validate_spawn_point(3, self.height // 2)

    def generate_theater(self):
        """Teater — lokasi Ao Lin. Berbeda dari penjara."""
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Dinding Teater")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Lantai")

        # Panggung di bagian atas
        for x in range(4, self.width - 4):
            for y in range(2, 6):
                if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                    self.tiles[y][x] = MapTile(0, True, "Panggung")
        # Tepi Panggung — dinding pemisah. Gap di x=7, x=12, x=17 agar pemain bisa naik ke panggung
        for x in range(4, self.width - 4):
            if 0 < x < self.width - 1 and x not in (7, 12, 17):
                self.tiles[6][x] = MapTile(6, False, "Tepi Panggung")

        # Kursi penonton
        for row_y in (8, 10, 12):
            for x in range(3, self.width - 3, 3):
                if 0 < x < self.width - 1 and row_y < self.height - 1:
                    self.tiles[row_y][x] = MapTile(6, False, "Kursi")

        self.place_exit(12, self.height - 2, "island", "Keluar Teater")
        # Aolinh berada di panggung teater — NPC bagi karakter non-Aolinh
        self.place_npc(12, 4, "aolinh")
        self.add_enemy_patrol(8,  13, "guard_novice",    [(8,13),  (16,13), (16,15), (8,15)])
        self.add_enemy_patrol(5,  8,  "mansion_guard",  [(5,8),   (12,8)])
        self.add_enemy_patrol(19, 9,  "mercenary_thug", [(19,9),  (19,13)])
        self.place_item(3,  4,  "Health Potion")          # clue Jiejie #1 — Aolinh
        self.place_item(7,  4,  "Gantungan Kunci Musik")  # clue Jiejie #2 — Aolinh (FIX: QUEST_ITEMS)
        self.place_item(21, 4,  "Bandage")
        self.place_item(12, 14, "Med Kit")
        self.player_x, self.player_y = self._validate_spawn_point(12, 9)

    def generate_beach(self):
        """Pantai — lokasi Arganta."""
        for y in range(self.height):
            for x in range(self.width):
                if y >= self.height - 4:
                    self.tiles[y][x] = MapTile(7, False, "Laut")
                elif y >= self.height - 6:
                    self.tiles[y][x] = MapTile(0, True, "Pantai Pasir")
                elif x == 0 or x == self.width - 1 or y == 0:
                    self.tiles[y][x] = MapTile(1, False, "Tebing")
                else:
                    self.tiles[y][x] = MapTile(8 if random.random() < 0.15 else 0, True, "Hutan Pantai")

        for px, py in [(2, 10), (3, 10), (2, 11), (3, 11)]:
            if 0 < px < self.width - 1 and 0 < py < self.height - 4:
                self.tiles[py][px] = MapTile(6, False, "Reruntuhan Perahu")

        self.place_exit(12, 1, "island", "Masuk Pulau")
        # Arganta di pantai — NPC bagi karakter non-Arganta
        self.place_npc(6, 10, "arganta")
        self.place_item(6,  9,  "Health Potion")       # survival #1 — Arganta
        self.place_item(15, 6,  "Bandage")             # survival #2 — Arganta
        self.place_item(8,  4,  "Kompas Nonno Arganta") # survival bonus / QUEST item — Arganta
        self.place_item(20, 9,  "Med Kit")
        self.add_enemy_patrol(10, 5,  "guard_novice",   [(10,5),  (18,5), (18,8), (10,8)])
        self.add_enemy_patrol(5,  8,  "mercenary_thug", [(5,8),   (10,8)])
        self.add_enemy_patrol(18, 10, "guard_veteran",  [(18,10), (22,10)])
        self.player_x, self.player_y = self._validate_spawn_point(3, self.height - 6)

    def generate_basement(self):
        """Ruang elektrik bawah tanah — lokasi Ignatius."""
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Beton")
                elif (x % 6 == 0 and y % 5 == 0 and
                      0 < x < self.width - 1 and 0 < y < self.height - 1):
                    self.tiles[y][x] = MapTile(6, False, "Panel Listrik")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Lantai Beton")

        self.create_path(1, self.height // 2, self.width - 2, self.height // 2)
        self.create_path(self.width // 2, 1, self.width // 2, self.height - 2)

        self.place_exit(12, 1, "mansion", "Naik ke Mansion")
        self.place_npc(4, 4, "ignatius")
        self.add_enemy_patrol(10, 8,  "guard_novice",  [(10,8),  (14,8)])
        self.add_enemy_patrol(6,  10, "tech_guard",    [(6,10),  (6,14)])
        self.add_enemy_patrol(18, 5,  "scientist",     [(18,5),  (18,10)])
        # EMP komponen — static spawn agar tracker bisa tunjukkan panah (FIX: sebelumnya tidak ada)
        self.place_item(18, 12, "Kapasitor Besar")   # collect_emp_parts_ch1 #1
        self.place_item(14, 8,  "Copper Coil")       # collect_emp_parts_ch1 #2
        self.place_item(6,  14, "Relay Switch")      # collect_emp_parts_ch1 #3
        # Item biasa basement
        self.place_item(5,  8,  "Health Potion",  respawn_delay=420)
        self.place_item(19, 13, "Med Kit",         respawn_delay=600)
        self.player_x, self.player_y = self._validate_spawn_point(12, 3)

    def generate_laboratory(self):
        """Laboratorium Maxwell — area Ch.4 dengan Maxwell's Agent boss."""
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Dinding Lab")
                elif (x % 5 == 0 and y % 4 == 0 and
                      0 < x < self.width - 1 and 0 < y < self.height - 1):
                    self.tiles[y][x] = MapTile(6, False, "Meja Lab")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Lantai Lab")

        self.create_path(1, self.height // 2, self.width - 2, self.height // 2)
        self.create_path(self.width // 2, 1, self.width // 2, self.height - 2)

        self.place_exit(12, 1, "island", "Keluar Laboratorium")
        self.add_enemy_patrol(8,   6,  "tech_guard",        [(8,6),   (16,6)])
        self.add_enemy_patrol(6,   12, "scientist",         [(6,12),  (12,12)])
        self.add_enemy_patrol(18,  8,  "guard_elite",       [(18,8),  (18,14)])
        self.add_enemy_patrol(20,  5,  "mercenary_sniper",  [(20,5),  (20,12)])
        self.place_item(19,  4,  "Med Kit",              respawn_delay=600)
        self.place_item(5,   14, "Health Potion",        respawn_delay=420)
        self.place_item(19,  14, "Encrypted Files")
        self.place_npc(15, 9, "vio")
        self.place_item(14, 12, "USB Security Drive")
        self.player_x, self.player_y = self._validate_spawn_point(12, 3)

    def generate_mansion_east(self):
        """Mansion Timur — area final Ch.6, Epstein's lair."""
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[y][x] = MapTile(1, False, "Tembok Mansion")
                elif x % 3 == 0 and y % 4 == 0 and 0 < x < self.width - 1 and 0 < y < self.height - 1:
                    self.tiles[y][x] = MapTile(6, False, "Pilar")
                else:
                    self.tiles[y][x] = MapTile(0, True, "Lantai Mewah")

        self.create_path(1, self.height // 2, self.width - 2, self.height // 2)
        self.create_path(self.width // 2, 1, self.width // 2, self.height - 2)

        self.place_exit(12, 1, "island", "Keluar dari Mansion Timur")
        self.add_enemy_patrol(6,   6,  "guard_elite",      [(6,6),   (12,6)])
        self.add_enemy_patrol(18,  6,  "mercenary_thug",   [(18,6),  (22,6)])
        self.add_enemy_patrol(6,   13, "guard_veteran",    [(6,13),  (12,13)])
        self.add_enemy_patrol(18,  13, "mercenary_sniper", [(18,13), (22,13)])
        self.place_item(4,   4,  "Health Potion",   respawn_delay=420)
        self.place_item(20,  4,  "Med Kit",         respawn_delay=600)
        self.place_item(4,   14, "Bandage",         respawn_delay=420)
        # USB Evidence Drive TIDAK di-spawn bebas — hanya dari sidequest Vio
        self.place_item(20,  14, "Dokumen Rahasia")  # Hint item, bukan quest reward
        self.player_x, self.player_y = self._validate_spawn_point(12, 3)

    def create_path(self, x1, y1, x2, y2):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= y < self.height and 0 <= x1 < self.width:
                    self.tiles[y][x1] = MapTile(0, True, "Path")
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= y1 < self.height and 0 <= x < self.width:
                    self.tiles[y1][x] = MapTile(0, True, "Path")

    def place_exit(self, x, y, dest, desc):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = MapTile(2, True, desc)
            self.exits.append({
                'x': x, 'y': y,
                'destination': dest,
                'locked': False, 'key': None,
                'description': desc
            })

    def place_boss_door(self, x, y, boss_id, desc):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = MapTile(9, True, desc)
            self.boss_doors.append({
                'x': x, 'y': y,
                'boss_id': boss_id,
                'locked': False,
                'description': desc
            })

    def _spawn_boss_for_chapter(self, chapter, char_id, gs):
        
        CH1_BOSSES = {
            "vio":      ("maxwell_agent",     8,  self.height // 2, "Maxwell's Agent"),
            "haikaru":  ("warden_elite",      12, self.height - 3,  "Warden Elite"),
            "aolinh":   ("theater_master",    12, 4,                "Theater Master"),
            "arganta":  ("harbor_captain",    8,  self.height // 2,  "Harbor Captain"),
            "ignatius": ("security_bot",      12, self.height - 3,  "AmBOTukam Mk II"),
        }
        CHAR_START_MAP = {
            "vio": "mansion", "haikaru": "prison_north",
            "aolinh": "theater", "arganta": "beach", "ignatius": "basement",
        }

        if chapter == 1:
            if char_id in CH1_BOSSES and self.map_id == CHAR_START_MAP.get(char_id):
                boss_id, boss_x, boss_y, boss_desc = CH1_BOSSES[char_id]
                if not any(d['boss_id'] == boss_id for d in self.boss_doors):
                    self.place_boss_door(boss_x, boss_y, boss_id, boss_desc)

        elif chapter == 2:
            # Ch2: tiap karakter hadapi boss berbeda di lokasi berbeda
            CH2_BOSSES = {
                # Tiap karakter punya boss unik di area berbeda — tidak ada yang sama
                "vio":      ("network_overseer",    "command_center", self.width // 2, self.height // 2, "Network Overseer"),
                "haikaru":  ("kepala_penjaga",      "prison_north",   self.width // 2, self.height - 3,  "Kepala Penjaga"),
                "aolinh":   ("doctor_rousseau",     "theater",        self.width // 2, self.height // 2, "Dr. Rousseau"),
                "arganta":  ("mercenary_commander", "dock",           self.width // 2, self.height // 2, "Mercenary Commander"),
                "ignatius": ("security_bot",        "basement",       self.width // 2, self.height - 3,  "AmBOTukam Mk III"),
            }
            if char_id in CH2_BOSSES:
                boss_id, boss_map, boss_x, boss_y, boss_desc = CH2_BOSSES[char_id]
                if self.map_id == boss_map:
                    if not any(d['boss_id'] == boss_id for d in self.boss_doors):
                        self.place_boss_door(boss_x, boss_y, boss_id, boss_desc)

        elif chapter == 4:
            # Ch4: Ghislaine Maxwell di pusat kendali (command_center)
            if self.map_id == 'command_center':
                if not any(d['boss_id'] == 'ghislaine_maxwell' for d in self.boss_doors):
                    self.place_boss_door(
                        self.width // 2, self.height // 2,
                        'ghislaine_maxwell', "Ghislaine Maxwell — Pusat Kendali"
                    )
            # Agen Maxwell tetap tersedia di laboratorium sebagai optional fight
            elif self.map_id == 'laboratory':
                # Maxwell's Agent di lab adalah optional fight, tersedia Ch4+
                if not any(d['boss_id'] == 'agen_maxwell' for d in self.boss_doors):
                    self.place_boss_door(
                        self.width // 2, self.height - 3,
                        'agen_maxwell', "Maxwell's Agent — Lab (Optional)"
                    )

        elif chapter == 6:
            if self.map_id == 'mansion_east':
                if not any(d['boss_id'] == 'epstein_boss' for d in self.boss_doors):
                    self.place_boss_door(
                        self.width // 2, self.height // 2,
                        'epstein_boss', "FINAL BOSS — Jeffrey Epstein"
                    )

    def check_and_spawn_bosses(self, gs):
        # Public: check and spawn bosses based on chapter and character.
        char_id = gs.player_character
        chapter = int(gs.story_flags.get('current_chapter', 1))
        self._spawn_boss_for_chapter(chapter, char_id, gs)

        # Strict spawn: remove boss_doors whose boss_id is already in defeated flags
        defeated_ids = set(gs.story_flags.get('defeated_boss_ids', []))
        self.boss_doors = [
            d for d in self.boss_doors
            if d['boss_id'] not in defeated_ids
        ]

    def add_enemy_patrol(self, x, y, enemy_id, path=None):
        """Tambahkan enemy yang DIAM di tempat (stay). Path diabaikan untuk cegah bug render."""
        sx, sy = self._validate_spawn_point(x, y)
        self.enemies.append({
            'x': sx, 'y': sy,
            'id': enemy_id,
            'path': [],       # Selalu kosong — musuh STAY, tidak patrol
            'path_index': 0,
            'counter': 0
        })

    def place_npc(self, x, y, npc_id):
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.current_player_char and npc_id == self.current_player_char:
                return
            # Validate that NPC is not placed on unwalkable tile
            if self.tiles[y][x].walkable:
                self.npcs.append({'x': x, 'y': y, 'id': npc_id})
            else:
                # If placement invalid, find nearest valid spot
                valid_spot = self._validate_spawn_point(x, y)
                if valid_spot:
                    self.npcs.append({'x': valid_spot[0], 'y': valid_spot[1], 'id': npc_id})

    def place_item(self, x, y, item, respawn_delay=0):
        # respawn_delay: seconds until item reappears (0 = permanent pickup)
        if 0 <= x < self.width and 0 <= y < self.height:
            if not self.tiles[y][x].walkable:
                spot = self._validate_spawn_point(x, y)
                if spot:
                    x, y = spot
                else:
                    return
            if any((n['x'] == x and n['y'] == y) for n in self.npcs):
                x = min(x + 1, self.width - 2)
            if any((e['x'] == x and e['y'] == y) for e in self.enemies):
                x = max(x - 1, 1)
            self.items.append({'x': x, 'y': y, 'item': item, 'respawn_delay': respawn_delay})

    def attempt_move(self, dx, dy, gs):
        nx = self.player_x + dx
        ny = self.player_y + dy

        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return None

        if not self.tiles[ny][nx].walkable:
            return None

        for exit_data in self.exits:
            if (nx, ny) == (exit_data['x'], exit_data['y']):
                self.player_x, self.player_y = nx, ny
                self.discovered.add((nx, ny))
                # Event: Door Checkpoint — save state before map transition
                if hasattr(gs, 'save_checkpoint'):
                    gs.save_checkpoint(location=gs.current_location)
                    gs.story_flags['_checkpoint_door_pos'] = (nx, ny)
                    gs.story_flags['_checkpoint_door_map'] = self.map_id
                return {
                    'type': 'exit',
                    'destination': exit_data['destination'],
                    'locked': exit_data['locked'],
                    'key': exit_data['key']
                }

        for door in self.boss_doors:
            if (nx, ny) == (door['x'], door['y']):
                self.player_x, self.player_y = nx, ny
                self.discovered.add((nx, ny))
                return {'type': 'boss', 'boss_id': door['boss_id'], 'locked': door['locked']}

        for npc in self.npcs:
            if (nx, ny) == (npc['x'], npc['y']):
                self.player_x, self.player_y = nx, ny
                self.discovered.add((nx, ny))
                return {'type': 'npc', 'npc_id': npc['id']}

        for item in list(self.items):
            if (nx, ny) == (item['x'], item['y']):
                self.items.remove(item)
                self.player_x, self.player_y = nx, ny
                self.discovered.add((nx, ny))
                return {'type': 'item', 'item': item['item']}

        for enemy in self.enemies:
            if (nx, ny) == (enemy['x'], enemy['y']):
                from .enemies import create_enemy_instance
                _chapter = int(gs.story_flags.get('current_chapter', 1)) if gs else 1
                _plvl = getattr(gs, 'player_level', 1) if gs else 1
                if ei := create_enemy_instance(enemy['id'], chapter=_chapter, player_level=_plvl):
                    self.player_x, self.player_y = nx, ny
                    self.discovered.add((nx, ny))
                    return {'type': 'enemy', 'enemy': ei}

        self.player_x, self.player_y = nx, ny
        self.discovered.add((nx, ny))

        return {'type': 'move'}

    def add_boss_enemy(self, x, y, enemy_id):
        """Tambahkan boss enemy yang diam (stay) — tidak patrol, tidak chase."""
        self.enemies.append({
            'x': x, 'y': y,
            'id': enemy_id,
            'path': [],         # kosong = tidak patrol
            'path_index': 0,
            'counter': 0,
            'is_boss': True,    # boss: stay only, tidak chase
        })

    def update_enemies(self):
        """AI musuh: STAY sistem."""
        # Musuh sepenuhnya statis — tidak ada gerakan, tidak ada chase
        # Ini mencegah bug render posisi ganda dan memudahkan tracking no-respawn
        return None

    def _build_main_quest_lines(self, main_quests, gs=None):
        if not main_quests:
            return []
        mq = main_quests[0]
        lines = [("quest", f"[M] {mq['title']}")]
        _current_chapter = int(gs.story_flags.get('current_chapter', 1)) if gs else 1

        if _current_chapter == 1 and gs is not None:
            try:
                from .characters import get_ch1_objective_status, get_ch1_next_incomplete_objective
                obj_statuses = get_ch1_objective_status(gs)
                if obj_statuses:
                    total_objs = len(obj_statuses)
                    for step_num, (obj_id, desc, cur, tot, done, obj_type) in enumerate(obj_statuses, 1):
                        bar = '■' * cur + '□' * max(0, tot - cur)
                        if done:
                            prefix = '✓'
                            tag = "done"
                        elif obj_type == 'boss':
                            prefix = '⚔'
                            tag = "prog"
                        else:
                            prefix = '◐'
                            tag = "prog"
                        lines.append((tag, f"  └ Langkah {step_num}/{total_objs}: {prefix} {desc}"))
                        if tot > 1:
                            lines.append((tag, f"      [{bar}] {cur}/{tot}"))
                    next_id, _ = get_ch1_next_incomplete_objective(gs)
                    if next_id:
                        # Tampilkan panah ke item yang bisa complete objective berikutnya
                        # Cek QUEST_ITEMS DAN CH1_ITEM_OBJECTIVE_MAP agar non-quest items juga tampil
                        try:
                            from .characters import get_ch1_item_objective, CH1_ITEM_OBJECTIVE_MAP
                            char_id_hint = gs.player_character
                            ch1_obj_items = set(CH1_ITEM_OBJECTIVE_MAP.get(char_id_hint, {}).keys())
                        except Exception:
                            ch1_obj_items = set()
                        shown_hint = False
                        for it in self.items:
                            item_triggers_obj = (
                                is_quest_item(it['item']) or
                                it['item'] in ch1_obj_items
                            )
                            if item_triggers_obj:
                                arrow = _direction_arrow(self.player_x, self.player_y, it['x'], it['y'])
                                dist  = _manhattan(self.player_x, self.player_y, it['x'], it['y'])
                                lines.append(("prog", f"  ★ Petunjuk: {arrow} Cari {it['item']} ({_distance_label(dist)})"))
                                shown_hint = True
                                break
                        # Fallback ke item terdekat apapun kalau tidak ada yang match
                        if not shown_hint and self.items:
                            it = min(self.items, key=lambda i: _manhattan(self.player_x, self.player_y, i['x'], i['y']))
                            arrow = _direction_arrow(self.player_x, self.player_y, it['x'], it['y'])
                            dist  = _manhattan(self.player_x, self.player_y, it['x'], it['y'])
                            lines.append(("prog", f"  ★ Petunjuk: {arrow} Cari {it['item']} ({_distance_label(dist)})"))
                    return lines
            except Exception:
                pass

        try:
            from .characters import CHARACTER_MAIN_QUESTS, CHAPTER_QUEST_TEMPLATES
            char_id = gs.player_character if gs else ''
            char_quests = CHARACTER_MAIN_QUESTS.get(char_id, {})
            quest_data = char_quests.get(_current_chapter) or CHAPTER_QUEST_TEMPLATES.get(_current_chapter, {})
            steps = quest_data.get('steps', [])
            if steps and gs is not None:
                total_steps = len(steps)
                done_flag = quest_data.get('completion_flag', '')
                quest_done = gs.story_flags.get(done_flag, False) if done_flag else False
                completed_steps = self._get_completed_steps(_current_chapter, gs, total_steps, quest_done)
                for i, step_text in enumerate(steps):
                    step_num = i + 1
                    is_done = i < completed_steps
                    is_current = i == completed_steps and not quest_done
                    if is_done:
                        prefix = '✓'
                        tag = "done"
                    elif is_current:
                        prefix = '◐'
                        tag = "prog"
                    else:
                        prefix = '○'
                        tag = "side"
                    lines.append((tag, f"  └ Langkah {step_num}/{total_steps}: {prefix} {step_text}"))
                if not quest_done and completed_steps < total_steps:
                    next_step = steps[completed_steps]
                    lines.append(("prog", f"  → Aktif: {next_step}"))
                return lines
        except Exception:
            pass

        prog = mq.get("progress", 0)
        total = mq.get("total", 1)
        bar = "■" * prog + "□" * (total - prog)
        targets_list = mq.get("targets", [])
        total_t = len(targets_list)
        for i, step_text in enumerate(targets_list):
            step_num = i + 1
            is_done = i < prog
            is_current = i == prog
            if is_done:
                prefix = '✓'
                tag = "done"
            elif is_current:
                prefix = '◐'
                tag = "prog"
            else:
                prefix = '○'
                tag = "side"
            lines.append((tag, f"  └ Langkah {step_num}/{total_t}: {prefix} {step_text}"))
        if not targets_list:
            current_step = mq.get("objective", "")
            lines.append(("prog", f"  └ {current_step}"))
            lines.append(("prog", f"    [{bar}] {prog}/{total}"))
        return lines

    def _get_completed_steps(self, chapter, gs, total_steps, quest_done):
        if quest_done:
            return total_steps
        flags = gs.story_flags if gs else {}
        char_id = gs.player_character if gs else ''

        if chapter == 2:
            # Ch2: 3 steps — step1=jelajahi island, step2=lacak area boss karakter, step3=kalahkan boss
            boss_done = flags.get('boss_ch2_defeated', False)
            if boss_done:
                return total_steps
            # Lokasi boss Ch2 unik per karakter
            ch2_boss_locations = {
                'vio':      'command_center',   # Network Overseer
                'haikaru':  'prison_north',     # Kepala Penjaga
                'aolinh':   'theater',          # Dr. Rousseau
                'arganta':  'dock',             # Mercenary Commander
                'ignatius': 'basement',         # AmBOTukam Mk III
            }
            visited = gs.visited_locations if gs else set()
            boss_loc = ch2_boss_locations.get(char_id, 'island')
            been_to_island   = 'island' in visited
            at_boss_location = boss_loc in visited
            if at_boss_location and total_steps >= 2:
                return 2   # Step 1+2 selesai: sudah di area boss
            if been_to_island and total_steps >= 2:
                return 1   # Step 1 selesai: sudah jelajahi island
            return 0

        if chapter == 3:
            sq = gs.get_sidequest_progress() if gs else 0
            if flags.get('ch3_sidequests_done'):
                return total_steps
            # Step 1 done if at least 1 NPC intro shown
            npc_met = any(flags.get(f"{n}_intro_shown") for n in ['haikaru','aolinh','arganta','ignatius','vio'])
            completed = 0
            if npc_met:
                completed = 1
            if sq >= 1:
                completed = min(sq + 1, total_steps - 1)
            return completed

        if chapter == 4:
            boss_done = flags.get('boss_ch4_defeated', False)
            if boss_done:
                return total_steps
            # Step 1: arrived at command_center
            at_cc = 'command_center' in (gs.visited_locations if gs else set())
            # Step 2: used item/skill (emp, recording, peta, network key) OR has relevant item
            used_item = (flags.get('emp_device_used') or flags.get('distraksi_played') or
                         flags.get('jalur_rahasia_used') or flags.get('network_key_used') or
                         any(itm in (gs.quest_items if gs else []) for itm in
                             ['EMP Device', 'Rekaman Distraksi Aolinh', 'Peta Jalur Rahasia', 'Network Master Key']))
            if at_cc:
                return 2 if used_item else 1
            return 0

        if chapter == 5:
            sq = gs.get_sidequest_progress() if gs else 0
            has_usb = ('USB Evidence Drive' in (gs.quest_items if gs else []) or
                       flags.get('vio_sidequest_done', False))
            if has_usb:
                return total_steps
            if sq >= 4:
                return 2   # Step 2: sudah cukup SQ, tinggal ke Vio
            return min(sq, 1)

        if chapter == 6:
            boss_done = flags.get('boss_ch6_defeated', False)
            if boss_done:
                return total_steps
            at_mansion_east = 'mansion_east' in (gs.visited_locations if gs else set())
            return 1 if at_mansion_east else 0

        return 0

    def _build_tracker_lines(self, gs):
        """Quest Tracker HUD lines — uses real-time GameState properties."""
        lines = []
        chapter  = int(gs.story_flags.get('current_chapter', 1))
        sq_done  = gs.get_sidequest_progress()
        sq_ready = gs.get_sidequest_ready_count()

        # ── CHAPTER INFO ──────────────────────────────────────────────────
        sq_ready_str = f" {Warna.KUNING}★LAPOR!{Warna.RESET}" if sq_ready > 0 else ""
        sq_suffix = f" [{sq_ready}★ SIAP LAPOR]{sq_ready_str}" if sq_ready > 0 else f" (SQ:{sq_done}/5)"
        chapter_obj = gs.main_quest_status
        lines.append(("obj", f"Ch.{chapter}: {chapter_obj}{sq_suffix}"))

        # ── MAIN QUEST OBJECTIVES ─────────────────────────────────────────
        main_quests = [q for q in gs.active_quests if q.get("quest_type") != "side"]
        side_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]

        lines.extend(self._build_main_quest_lines(main_quests, gs=gs))

        # ── CHAPTER HINT (kalau belum ada quest aktif) — char-specific ───
        if not main_quests:
            try:
                from .characters import CHAPTER_OBJECTIVES, CHAPTER_OBJECTIVES_BY_CHAR
                char_id_hint = gs.player_character if gs else ''
                hint = (CHAPTER_OBJECTIVES_BY_CHAR.get(char_id_hint, {}).get(chapter, '')
                        or CHAPTER_OBJECTIVES.get(chapter, ''))
            except Exception:
                from .characters import CHAPTER_OBJECTIVES
                hint = CHAPTER_OBJECTIVES.get(chapter, '')
            if hint:
                lines.append(("prog", f"  ▶ {hint}"))

        # ── SIDE QUESTS ───────────────────────────────────────────────────
        for sq in side_quests[:2]:
            sq_prog  = sq.get("progress", 0)
            sq_total = sq.get("total", 1)
            sq_bar   = "■" * sq_prog + "□" * (sq_total - sq_prog)
            pct = int((sq_prog / max(sq_total, 1)) * 100)
            lines.extend([
                ("side", f"[SQ] {sq['title']}  [{sq_bar}] {pct}%"),
                ("prog", f"  └ {sq['objective']}")
            ])
            # Sidequest directional tracker — arah ke item/enemy yang dibutuhkan
            try:
                from .npc_interactions import NPC_SIDEQUEST_DATA
                sq_npc_id = sq.get('id', '').replace('recruit_', '')
                npc_sq = NPC_SIDEQUEST_DATA.get(sq_npc_id, {})
                req_items = list(npc_sq.get('required_items', []))
                if not req_items and npc_sq.get('required_item'):
                    req_items = [npc_sq['required_item']]
                req_action = npc_sq.get('required_action')

                for req_item in req_items:
                    if req_item in (gs.inventory or []):
                        lines.append(("done", f"  ✓ [{req_item}] sudah di inventori"))
                    else:
                        found_on_map = False
                        for it in self.items:
                            if it['item'] == req_item:
                                d = _manhattan(self.player_x, self.player_y, it['x'], it['y'])
                                arr = _direction_arrow(self.player_x, self.player_y, it['x'], it['y'])
                                lines.append(("side", f"  ★ {arr} Cari [{req_item}] ({_distance_label(d)})"))
                                found_on_map = True
                                break
                        if not found_on_map:
                            sq_loc = npc_sq.get('location', '???').upper().replace('_', ' ')
                            lines.append(("side", f"  ★ [{req_item}] → pergi ke {sq_loc}"))

                if req_action and not gs.story_flags.get(req_action):
                    if self.enemies:
                        enemy = min(self.enemies,
                                    key=lambda e: _manhattan(self.player_x, self.player_y, e['x'], e['y']))
                        d = _manhattan(self.player_x, self.player_y, enemy['x'], enemy['y'])
                        arr = _direction_arrow(self.player_x, self.player_y, enemy['x'], enemy['y'])
                        lines.append(("side", f"  ⚔ {arr} Kalahkan penjaga ({_distance_label(d)})"))
                    else:
                        sq_loc = npc_sq.get('location', '???').upper().replace('_', ' ')
                        lines.append(("side", f"  ⚔ Kalahkan musuh di {sq_loc}"))
            except Exception:
                pass

        # ── NEARBY TARGETS (sorted by distance) ──────────────────────────
        targets = []

        # Boss doors — prioritas tinggi
        for door in self.boss_doors:
            dist  = _manhattan(self.player_x, self.player_y, door['x'], door['y'])
            arrow = _direction_arrow(self.player_x, self.player_y, door['x'], door['y'])
            targets.append((dist, "boss", f"  ⚡ {arrow} BOSS: {door.get('description','?')} ({_distance_label(dist)})"))

        # NPC yang belum direkrut
        for npc in self.npcs:
            if npc['id'] not in gs.npcs_recruited:
                dist = _manhattan(self.player_x, self.player_y, npc['x'], npc['y'])
                arrow = _direction_arrow(self.player_x, self.player_y, npc['x'], npc['y'])
                try:
                    from .characters import get_character_name
                    name = get_character_name(npc['id'])
                except Exception:
                    name = npc['id'].capitalize()
                targets.append((dist, "npc", f"  👤 {arrow} NPC: {name} ({_distance_label(dist)})"))

        # Quest items — prioritas. Juga include Ch1 objective items jika di Ch1
        _ch1_obj_items: set = set()
        _cur_ch = int(gs.story_flags.get('current_chapter', 1)) if gs else 1
        if _cur_ch == 1 and gs:
            try:
                from .characters import CH1_ITEM_OBJECTIVE_MAP
                _ch1_obj_items = set(CH1_ITEM_OBJECTIVE_MAP.get(gs.player_character, {}).keys())
            except Exception:
                pass
        for item in self.items:
            dist  = _manhattan(self.player_x, self.player_y, item['x'], item['y'])
            arrow = _direction_arrow(self.player_x, self.player_y, item['x'], item['y'])
            if is_quest_item(item['item']) or item['item'] in _ch1_obj_items:
                targets.append((dist, "item", f"  ★ {arrow} [QUEST] {item['item']} ({_distance_label(dist)})"))
            elif dist <= 5:
                targets.append((dist, "item", f"  · {arrow} {item['item']} ({_distance_label(dist)})"))

        # Exit doors — selalu tampilkan
        for exit_d in self.exits:
            dist  = _manhattan(self.player_x, self.player_y, exit_d['x'], exit_d['y'])
            arrow = _direction_arrow(self.player_x, self.player_y, exit_d['x'], exit_d['y'])
            targets.append((dist, "exit", f"  ▶ {arrow} Pintu: {exit_d['description']} ({_distance_label(dist)})"))

        targets.sort(key=lambda t: t[0])
        lines.extend((kind, label) for _, kind, label in targets[:5])

        # ── QUICK STATS ───────────────────────────────────────────────────
        lines.append(("obj", f"  📍 {self.map_id.upper().replace('_',' ')}"))
        lines.append(("prog", f"  ATK:{gs.attack} DEF:{gs.defense} SPD:{gs.speed} | Lv:{gs.level} ${gs.dollars}"))

        return lines

    def render(self, gs):
        """Render peta + Quest Tracker HUD — auto-fit, side-by-side saat layar lebar."""
        # Real-time HUD: reconcile quest state on every render frame
        gs.reconcile_state()
        self.check_and_spawn_bosses(gs)
        clear_screen()

        tw = _tw()
        SIDE_BY_SIDE = tw >= 110

        vw, vh = 23, 15
        cx = max(0, min(self.player_x - vw // 2, self.width  - vw))
        cy = max(0, min(self.player_y - vh // 2, self.height - vh))

        bar_len    = max(8, min(14, (tw - 55) // 2))
        map_name   = self.map_id.upper().replace('_', ' ')

        hp_filled  = max(0, int((gs.hp / max(gs.max_hp, 1)) * bar_len))
        hp_bar     = f"{Warna.HIJAU}{'█' * hp_filled}{Warna.MERAH}{'░' * (bar_len - hp_filled)}{Warna.RESET}"

        energy     = getattr(gs, 'energy', 0)
        max_energy = getattr(gs, 'max_energy', 20)
        en_filled  = max(0, int((energy / max(max_energy, 1)) * bar_len))
        en_bar     = f"{Warna.CYAN}{'█' * en_filled}{Warna.ABU_GELAP}{'░' * (bar_len - en_filled)}{Warna.RESET}"

        chapter    = int(gs.story_flags.get('current_chapter', 1))
        dollars    = getattr(gs, 'dollars', 0)

        # Real-time sidequest counts from GameState
        sq_done    = gs.get_sidequest_progress()
        sq_ready   = gs.get_sidequest_ready_count()

        # Build SQ display with "Siap Lapor!" indicator if any quests ready
        sq_color  = Warna.HIJAU if sq_done > 0 else Warna.ABU_GELAP
        sq_str    = f"{sq_color}{sq_done}/5{Warna.RESET}"
        if sq_ready > 0:
            sq_str += f" {Warna.KUNING + Warna.TERANG}[{sq_ready}★Lapor!]{Warna.RESET}"

        print(f"\n{Warna.CYAN + Warna.TERANG}{map_name}{Warna.RESET}  "
              f"HP:[{hp_bar}]{gs.hp}/{gs.max_hp}  "
              f"{Warna.CYAN}EN:[{en_bar}]{energy}/{max_energy}{Warna.RESET}  "
              f"Lv:{Warna.KUNING}{gs.level}{Warna.RESET}  "
              f"Ch:{Warna.KUNING}{chapter}{Warna.RESET}  "
              f"${Warna.KUNING}{dollars}{Warna.RESET}  "
              f"SQ:{sq_str}")
        print(f"{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")


        map_rows = []
        for y in range(cy, min(cy + vh, self.height)):
            row = "  "
            for x in range(cx, min(cx + vw, self.width)):
                if x == self.player_x and y == self.player_y:
                    row += f"{Warna.UNGU + Warna.TERANG}P {Warna.RESET}"
                    continue
                rendered = False
                for enemy in self.enemies:
                    if x == enemy['x'] and y == enemy['y']:
                        row += f"{Warna.MERAH}E {Warna.RESET}"
                        rendered = True; break
                if not rendered:
                    for npc in self.npcs:
                        if x == npc['x'] and y == npc['y']:
                            row += f"{Warna.CYAN}N {Warna.RESET}"
                            rendered = True; break
                if not rendered:
                    for item in self.items:
                        if x == item['x'] and y == item['y']:
                            row += (f"{Warna.KUNING + Warna.TERANG}★ {Warna.RESET}"
                                    if is_quest_item(item['item'])
                                    else f"{Warna.KUNING}I {Warna.RESET}")
                            rendered = True; break
                if not rendered:
                    for exit_d in self.exits:
                        if x == exit_d['x'] and y == exit_d['y']:
                            row += f"{Warna.HIJAU}> {Warna.RESET}"
                            rendered = True; break
                if not rendered:
                    for door in self.boss_doors:
                        if x == door['x'] and y == door['y']:
                            # Logic: Boss Memory — dim color if boss was defeated before
                            defeated_ids = (gs.story_flags.get('defeated_boss_ids', [])
                                            if gs else [])
                            if door['boss_id'] in defeated_ids:
                                row += f"{Warna.ABU_GELAP}B {Warna.RESET}"  # Memory Boss
                            else:
                                row += f"{Warna.MERAH + Warna.TERANG}B {Warna.RESET}"
                            rendered = True; break
                if not rendered:
                    tile = self.tiles[y][x]
                    if tile.type in SPRITES:
                        char, color, _ = SPRITES[tile.type]
                        row += f"{color}{char[0]} {Warna.RESET}"
                    else:
                        row += "  "
            map_rows.append(row)


        tracker_lines = self._build_tracker_lines(gs)
        COLOR_MAP = {
            "obj":       Warna.KUNING + Warna.TERANG,
            "quest":     Warna.PUTIH,
            "prog":      Warna.ABU_GELAP,
            "done":      Warna.HIJAU,
            "side":      Warna.HIJAU + Warna.TERANG,
            "side_prog": Warna.ABU_GELAP,
            "npc":       Warna.CYAN,
            "boss":      Warna.MERAH + Warna.TERANG,
            "item":      Warna.KUNING,
            "exit":      Warna.HIJAU,
        }
        PROXIMITY_KINDS = {"npc", "boss", "item", "exit"}
        quest_lines     = [(k, v) for k, v in tracker_lines if k not in PROXIMITY_KINDS]
        proximity_lines = [(k, v) for k, v in tracker_lines if k in PROXIMITY_KINDS]

        def _tracker_rows(max_w):
            rows = [f"{Warna.KUNING + Warna.TERANG}◈ QUEST TRACKER{Warna.RESET}"]
            for kind, label in quest_lines:
                col = COLOR_MAP.get(kind, Warna.PUTIH)
                prefix = "✦ " if kind == "obj" else ("└ " if kind in ("quest", "side") else "  ")
                rows.append(f"{col}{_trunc(prefix + label, max_w - 1)}{Warna.RESET}")
            if proximity_lines:
                rows.append(f"{Warna.ABU_GELAP}Terdekat:{Warna.RESET}")
                for kind, label in proximity_lines[:5]:
                    col = COLOR_MAP.get(kind, Warna.PUTIH)
                    rows.append(f"  {col}{_trunc(label, max_w - 3)}{Warna.RESET}")
            return rows

        legend = (f"{Warna.UNGU}P{Warna.RESET}=Kamu "
                  f"{Warna.CYAN}N{Warna.RESET}=NPC "
                  f"{Warna.KUNING}I{Warna.RESET}=Item "
                  f"{Warna.MERAH}E{Warna.RESET}=Musuh "
                  f"{Warna.MERAH}B{Warna.RESET}=Boss "
                  f"{Warna.HIJAU}>{Warna.RESET}=Pintu")


        if SIDE_BY_SIDE:
            map_col_w    = 50
            tracker_w    = tw - map_col_w - 3
            sep          = f"{Warna.ABU_GELAP}│{Warna.RESET}"
            tracker_rows = _tracker_rows(tracker_w)

            def _pad(row, width):
                vis = len(_strip_ansi(row))
                return row + ' ' * max(0, width - vis)

            n = max(len(map_rows), len(tracker_rows))
            for i in range(n):
                left  = _pad(map_rows[i],    map_col_w) if i < len(map_rows)    else ' ' * map_col_w
                right = tracker_rows[i]                  if i < len(tracker_rows) else ''
                print(f"{left}{sep} {right}")

            print(f"{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")
            ctrl = "W/A/S/D=Gerak  I=Barang  Q=NPC Quest  B=Bran  X=Save  E=Keluar"
            print(f"  {legend}  {Warna.ABU_GELAP}|{Warna.RESET}  {Warna.ABU_GELAP}{ctrl}{Warna.RESET}")
            print(f"{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")
        else:
            for row in map_rows:
                print(row)
            print(f"\n{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")
            for line in _tracker_rows(tw - 3):
                print(f"  {line}")
            print(f"{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")
            print(f"  {legend}")
            print(f"{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")

def validate_access(target_location, gs):
    """Check if player can enter target_location based on chapter and key items.
    Returns (allowed: bool, reason: str).
    """
    try:
        from .characters import can_access_location, CHAPTER_REQUIREMENTS, CHAPTER_LOCATIONS
    except ImportError:
        return True, "OK"

    chapter = int(gs.story_flags.get('current_chapter', 1))
    char_id = gs.player_character
    inv = set(gs.inventory) | set(gs.quest_items)

    # Basic chapter gatekeeping
    if not can_access_location(char_id, target_location, chapter):
        # Find which chapter unlocks this area
        for ch in range(1, 7):
            ch_data = CHAPTER_LOCATIONS.get(ch, {})
            all_locs = ch_data.get('all', ch_data.get(char_id, []))
            if target_location in all_locs:
                if ch > chapter:
                    return False, f"Selesaikan Chapter {ch - 1} dulu untuk membuka area ini"
                break
        return False, f"Area '{target_location}' belum terbuka di Chapter {chapter}"

    # Specific item gates for high-security areas
    area_gates = {
        'command_center': {
            'chapter': 2,
            'reason': "Pusat Kontrol terbuka setelah Chapter 2 dimulai",
        },
        'laboratory': {
            'chapter': 4,
            'reason': "Butuh minimal 2 sidequest selesai dan akses Ch.4",
        },
        'mansion_east': {
            'chapter': 5,
            'reason': "Butuh USB Evidence Drive untuk masuk mansion timur",
        },
    }
    if target_location in area_gates:
        gate = area_gates[target_location]
        if chapter < gate['chapter']:
            return False, gate['reason']

    return True, "OK"


def create_game_map(map_id, gs=None):
    """Buat map berdasarkan ID."""
    current_char = gs.player_character if gs else None
    gm = GameMap(map_id, current_player_char=current_char)

    if map_id == "island":
        gm.generate_island()
    elif map_id in ("prison_north", "prison_south", "prison"):
        gm.generate_prison()
    elif map_id == "mansion":
        gm.generate_mansion()
    elif map_id == "dock":
        gm.generate_dock()
    elif map_id in ("safe_zone", "command_center"):
        gm.generate_command_center()
    elif map_id == "theater":
        gm.generate_theater()
    elif map_id == "beach":
        gm.generate_beach()
    elif map_id == "basement":
        gm.generate_basement()
    elif map_id == "laboratory":
        gm.generate_laboratory()
    elif map_id in ("mansion_east", "mansion_west"):
        gm.generate_mansion_east()
    else:
        gm.generate_island()

    if gs and gs.story_flags.get('start_x') is not None:
        sx = gs.story_flags['start_x']
        sy = gs.story_flags['start_y']
        if (0 <= sx < gm.width and 0 <= sy < gm.height
                and gm.tiles[sy][sx].walkable):
            gm.player_x = sx
            gm.player_y = sy
        del gs.story_flags['start_x']
        del gs.story_flags['start_y']

    # Filter musuh yang sudah dikalahkan agar tidak respawn
    if gs:
        defeated_set = set(gs.defeated_enemies) if isinstance(gs.defeated_enemies, list) else gs.defeated_enemies
        gm.enemies = [
            e for e in gm.enemies
            if f"{map_id}:{e['x']}:{e['y']}" not in defeated_set
        ]

        # Filter items that were already taken (persisted in story_flags) so they
        # don't reappear when the map is regenerated. Also respect respawn_delay.
        try:
            taken_key = f"items_taken_{map_id}"
            taken_items = set(gs.story_flags.get(taken_key, []))
            respawn_log = gs.story_flags.get(f"item_respawn_{map_id}", {}) or {}
            now = time.time()
            
            player_inventory_items = set(gs.inventory) if hasattr(gs, 'inventory') else set()
            player_quest_items = set(gs.quest_items) if hasattr(gs, 'quest_items') else set()
            player_items = player_inventory_items | player_quest_items

            def _item_visible(it):
                item_name = it.get('item', '')
                coord = f"{it['x']},{it['y']}"
                
                if item_name in player_items:
                    return False
                
                if coord not in taken_items:
                    return True
                delay = it.get('respawn_delay', 0)
                if not delay or delay <= 0:
                    return False
                ts = respawn_log.get(coord, 0)
                return (now - ts) >= delay

            gm.items = [it for it in gm.items if _item_visible(it)]
        except Exception:
            pass

    return gm

def loop_eksplorasi(gs, gm):
    # Core: Main exploration loop

    taken_key   = f"items_taken_{gm.map_id}"
    taken_items = set(gs.story_flags.get(taken_key, []))
    respawn_log = gs.story_flags.get(f"item_respawn_{gm.map_id}", {}) or {}
    now = time.time()
    
    # Ensure the taken_items key is initialized in story_flags to track items across map changes
    if taken_key not in gs.story_flags:
        gs.story_flags[taken_key] = []

    # Logic: Timed item respawn — filter only items not yet due for respawn
    def _item_visible(it):
        coord = f"{it['x']},{it['y']}"
        if coord not in taken_items:
            return True
        delay = it.get('respawn_delay', 0)
        return delay > 0 and (now - respawn_log.get(coord, 0)) >= delay

    gm.items = [it for it in gm.items if _item_visible(it)]
    _init_location_quests(gs, gm.map_id)

    FRAME_TIME = 0.05
    last_frame_time = time.time()
    _checkpoint_flash = 0  # HUD flash timestamp for checkpoint indicator

    while True:
        try:
            cur = time.time()
            if (cur - last_frame_time) < FRAME_TIME:
                time.sleep(FRAME_TIME - (cur - last_frame_time))
            last_frame_time = time.time()

            gm.render(gs)

            if triggered := gm.update_enemies():
                from .enemies import create_enemy_instance
                _chapter = int(gs.story_flags.get('current_chapter', 1)) if gs else 1
                _plvl = getattr(gs, 'player_level', 1) if gs else 1
                if ei := create_enemy_instance(triggered['id'], chapter=_chapter, player_level=_plvl):
                    if ret := handle_hasil({'type': 'enemy', 'enemy': ei}, gs, gm):
                        return ret
                    continue

            # HUD: slot indicator + checkpoint saved flash (3 second duration)
            slot_label = f"Slot {gs.current_slot + 1}"
            cp_hint = (f" {Warna.HIJAU}[✓ Checkpoint Saved]{Warna.RESET}"
                       if time.time() - _checkpoint_flash < 3 else "")
            print(f"\n{Warna.ABU_GELAP}W/A/S/D=Gerak | I=Barang | Q=Quest NPC | B=Bran Radio | "
                  f"X=Simpan({slot_label}) | E=Keluar{Warna.RESET}{cp_hint}")

            flush_input()
            cmd = input(f"{Warna.CYAN}> {Warna.RESET}").strip().lower()
            if not cmd:
                continue
            
            hasil = None
            if cmd == 'w':
                hasil = gm.attempt_move(0, -1, gs)
            elif cmd == 's':
                hasil = gm.attempt_move(0,  1, gs)
            elif cmd == 'a':
                hasil = gm.attempt_move(-1, 0, gs)
            elif cmd == 'd':
                hasil = gm.attempt_move(1,  0, gs)

            # Logic: item pickup with respawn timer + pre-pickup quest credit
            if hasil and hasil.get('type') == 'item':
                coord_key  = f"{gm.player_x},{gm.player_y}"
                item_name  = hasil.get('item', '')
                taken_items.add(coord_key)
                gs.story_flags[taken_key] = list(taken_items)
                # Record pickup time for timed respawn items
                item_obj = next((it for it in gm.items
                                 if f"{it['x']},{it['y']}" == coord_key), None)
                if item_obj and item_obj.get('respawn_delay', 0) > 0:
                    respawn_log[coord_key] = time.time()
                    gs.story_flags[f"item_respawn_{gm.map_id}"] = respawn_log
                # Quest: credit item even if quest wasn't active yet when picked up
                for q in list(gs.active_quests):
                    if item_name in q.get('targets', []):
                        gs.update_quest_progress(q['id'])
                if gs.update_quest_progress("collect_items"):
                    gs.complete_quest("collect_items")

            # Event: Door Checkpoint flash
            if hasil and hasil.get('type') == 'exit':
                _checkpoint_flash = time.time()

            if hasil:
                if ret := handle_hasil(hasil, gs, gm):
                    return ret

            if cmd == 'i':
                tampilkan_inventory(gs)
            elif cmd == 'q':
                tampilkan_npc_quests(gs)
            elif cmd == 'b':
                _buka_toko_bran_remote(gs)
            elif cmd == 'x':
                save_menu(gs)
            elif cmd in ('esc', 'e'):
                if konfirmasi_quit():
                    return 'quit'

        except KeyboardInterrupt:
            if konfirmasi_quit():
                return 'quit'
        except Exception as e:
            print(f"{Warna.MERAH}Error: {e}{Warna.RESET}")
            time.sleep(1)

def _init_location_quests(gs, gm_map_id):
    # Core: Init quests for current map/chapter — add_quest() deduplicates internally
    try:
        from .characters import CHARACTER_MAIN_QUESTS, NPC_QUESTS, CHAPTER_QUEST_TEMPLATES
    except ImportError:
        CHARACTER_MAIN_QUESTS = {}
        NPC_QUESTS = {}
        CHAPTER_QUEST_TEMPLATES = {}

    chapter = gs.story_flags.get("current_chapter", 1)
    try:
        chapter = int(chapter)
    except (ValueError, TypeError):
        chapter = 1

    char_id = gs.player_character

    if chapter == 1:
        # Ch1: karakter-spesifik — gunakan CHARACTER_MAIN_QUESTS
        char_quests = CHARACTER_MAIN_QUESTS.get(char_id, {})
        quest_data = char_quests.get(1)
        if quest_data:
            steps = quest_data.get("steps", [quest_data["objective"]])
            gs.add_quest(
                quest_data["id"], quest_data["title"], quest_data["objective"],
                targets=steps, location=gm_map_id, quest_type="main",
            )
    else:
        # Ch2+: prioritas CHARACTER_MAIN_QUESTS (per-karakter), fallback ke CHAPTER_QUEST_TEMPLATES
        char_quests = CHARACTER_MAIN_QUESTS.get(char_id, {})
        quest_data = char_quests.get(chapter) or CHAPTER_QUEST_TEMPLATES.get(chapter)
        if quest_data:
            steps = quest_data.get("steps", [quest_data["objective"]])
            gs.add_quest(
                quest_data["id"], quest_data["title"], quest_data["objective"],
                targets=steps, location=gm_map_id, quest_type="main",
            )
        else:
            gs.add_quest(
                f"ch{chapter}_main",
                f"Chapter {chapter}: Lanjutkan perjalanan",
                "Selesaikan objektif chapter ini untuk lanjut",
                targets=["Selesaikan chapter ini"],
                location=gm_map_id, quest_type="main",
            )

    # Sync HUD progress untuk Ch1 agar akurat bahkan setelah load game
    if chapter == 1:
        try:
            from .characters import sync_ch1_quest_hud
            sync_ch1_quest_hud(gs)
        except Exception:
            pass

    # Recruit Side Quest — TIDAK auto-add di sini.
    # Quest rekrut hanya ditambahkan saat player pertama kali berinteraksi
    # dengan NPC yang bersangkutan (di interaksi_npc()).
    # Ini mencegah quest rekrut muncul di HUD sebelum player bertemu NPC.

def _add_recruit_quest_on_meet(gs, npc_id):
    # Core: Add recruit quest to HUD on first NPC contact
    try:
        from .characters import NPC_QUESTS
    except ImportError:
        return

    char_id = gs.player_character
    if npc_id == char_id:
        return
    if npc_id in gs.npcs_recruited:
        return
    if any(q.get("id") == f"recruit_{npc_id}" for q in gs.active_quests):
        return
    if any(q.get("id") == f"recruit_{npc_id}" for q in gs.completed_quests):
        return

    npc_name_map = {
        "haikaru": "Haikaru Fumika",
        "aolinh":  "Ao Lin",
        "arganta": "Amerigo Arganta",
        "ignatius":"Ignatius",
        "vio":     "Vio",
    }
    npc_name = npc_name_map.get(npc_id, npc_id.capitalize())
    npc_quest = NPC_QUESTS.get(npc_id, {})

    gs.add_quest(
        f"recruit_{npc_id}",
        f"Rekrut: {npc_name}",
        npc_quest.get("objective", f"Bantu {npc_name} dan rekrut dia ke party"),
        targets=[npc_quest.get("required_item") or npc_quest.get("required_action") or "bantu_npc"],
        location=npc_quest.get("unlock_location", ""),
        quest_type="side",
    )

def handle_hasil(hasil, gs, gm):
    """Handle hasil dari movement dan interaksi."""
    if not hasil:
        return None

    try:
        if hasil['type'] == 'enemy':
            from .combat import run_combat
            from .characters import get_character_name, get_character_data


            try:
                from .npc_interactions import show_enemy_encounter_dialog
                enemy_id = hasil['enemy'].get('id', '')
                enemy_name = hasil['enemy'].get('name', '')
                is_boss = hasil['enemy'].get('boss', False)
                show_enemy_encounter_dialog(enemy_id, gs.player_character,
                                            enemy_name=enemy_name, is_boss=is_boss)
            except Exception:
                pass

            char_data = get_character_data(gs.player_character) or {}
            player_stats = {
                'name':         get_character_name(gs.player_character),
                'hp':           gs.hp,
                'max_hp':       gs.max_hp,
                'attack':       gs.attack,
                'defense':      gs.defense,
                'speed':        gs.speed,
                'level':        gs.level,
                'character_id': gs.player_character,
                # FIX: skill dari karakter, bukan story_flags yang selalu kosong
                'skills':       char_data.get('skills', {}),
                'energy':       getattr(gs, 'energy', 30),
                'max_energy':   getattr(gs, 'max_energy', 30),
                'bonus_discard_tokens': gs.story_flags.get('bonus_discard_tokens', 0),
                'stats': {
                    'hp':       gs.hp,
                    'max_hp':   gs.max_hp,
                    'attack':   gs.attack,
                    'defense':  gs.defense,
                    'speed':    gs.speed
                }
            }

            ret = run_combat(player_stats, hasil['enemy'], gs.inventory)

            # HP dan energy di-sync balik setelah combat
            gs.hp = max(0, player_stats.get('hp', gs.hp))
            if hasattr(gs, 'energy'):
                gs.energy = max(0, player_stats.get('energy', gs.energy))

            if ret == 'victory':
                gs.battles_won += 1

                QUEST_DROP_MAP = {
                    ('prison_north', 'guard_veteran'):    ('Buku Catatan Haikaru', None),
                    ('prison_north', 'guard_elite'):      ('Buku Catatan Haikaru', None),
                    ('beach',        'guard_veteran'):    ('Kompas Nonno Arganta', 'defeat_harbor_patrol'),
                    ('beach',        'mercenary_thug'):   ('Kompas Nonno Arganta', 'defeat_harbor_patrol'),
                    ('beach',        'guard_elite'):      ('Kompas Nonno Arganta', 'defeat_harbor_patrol'),
                    ('dock',         'guard_veteran'):    ('Kompas Nonno Arganta', 'defeat_harbor_patrol'),
                    ('laboratory',   'scientist'):        ('USB Security Drive',   'defeat_lab_scientist'),
                    ('laboratory',   'tech_guard'):       ('USB Security Drive',   'defeat_lab_scientist'),
                    ('mansion',      'guard_elite'):      ('Kapasitor Besar',      None),
                    ('mansion',      'tech_guard'):       ('Kapasitor Besar',      None),
                    ('basement',     'tech_guard'):       ('Kapasitor Besar',      None),
                    ('basement',     'scientist'):        ('Relay Switch',         None),
                    ('command_center','tech_guard'):      ('Relay Switch',         None),
                    ('command_center','guard_elite'):     ('Relay Switch',         None),
                    ('theater',      'mansion_guard'):    ('Copper Coil',          None),
                    ('theater',      'mercenary_thug'):   ('Copper Coil',          None),
                    ('theater',      'guard_veteran'):    ('Copper Coil',          None),
                    ('island',       'guard_veteran'):    ('Copper Coil',          None),
                    # Copper Coil juga tersedia di mansion/basement agar Ignatius bisa kumpulkan
                    # tanpa harus pergi ke theater saat Ch.1 (basement is starting area)
                    ('mansion',      'mansion_guard'):    ('Copper Coil',          None),
                    ('mansion',      'guard_novice'):     ('Copper Coil',          None),
                    ('basement',     'mansion_guard'):    ('Copper Coil',          None),
                    ('basement',     'guard_novice'):     ('Copper Coil',          None),
                }
                enemy_id_drop = hasil['enemy'].get('id', '')
                drop_key = (gm.map_id, enemy_id_drop)
                if drop_key in QUEST_DROP_MAP:
                    drop_item, drop_flag = QUEST_DROP_MAP[drop_key]
                    if drop_item not in gs.quest_items and drop_item not in gs.inventory:
                        gs.add_quest_item(drop_item)
                        print(f"\n  {Warna.KUNING}★ Quest Drop: {drop_item} didapat!{Warna.RESET}")
                        time.sleep(0.8)
                        if drop_flag:
                            gs.story_flags[drop_flag] = True
                EMP_PARTS = {'Kapasitor Besar', 'Relay Switch', 'Copper Coil'}
                has_all_emp = all(
                    p in gs.quest_items or p in gs.inventory
                    for p in EMP_PARTS
                )
                if has_all_emp and 'EMP Prototype' not in gs.quest_items and 'EMP Prototype' not in gs.inventory:
                    gs.add_quest_item('EMP Prototype')
                    print(f"\n  {Warna.KUNING + Warna.TERANG}★ EMP Prototype berhasil dirakit dari komponen!{Warna.RESET}")
                    time.sleep(1.2)
                    # Auto-credit sabotage_alarm_panel untuk Ignatius Ch.1
                    # Blueprint/EMP Prototype pickup trigger tidak cukup — auto-credit saat rakitan jadi
                    if gs.player_character == 'ignatius' and int(gs.story_flags.get('current_chapter', 1)) == 1:
                        try:
                            from .characters import update_ch1_objective as _upd_ch1
                            _upd_ch1(gs, 'sabotage_alarm_panel', 1)
                            print(f"  {Warna.CYAN}◐ Sabotase panel alarm: SIAP — gunakan EMP Prototype!{Warna.RESET}")
                        except Exception:
                            pass

                # Hapus enemy yang sudah kalah dari peta supaya tidak bisa fight lagi
                px, py = gm.player_x, gm.player_y
                gm.enemies = [
                    e for e in gm.enemies
                    if (e['x'] != px or e['y'] != py)
                ]
                # Simpan key agar tidak respawn saat map dibuat ulang
                defeat_key = f"{gm.map_id}:{px}:{py}"
                if defeat_key not in gs.defeated_enemies:
                    gs.defeated_enemies.append(defeat_key)

                # Update kill counter untuk quest "kalahkan musuh"
                enemy_id = hasil['enemy'].get('id', '')
                gs.story_flags[f'kill_{enemy_id}'] = gs.story_flags.get(f'kill_{enemy_id}', 0) + 1
                gs.story_flags['total_kills'] = gs.story_flags.get('total_kills', 0) + 1
                # Aolinh sidequest: kalahkan penjaga theater (enemy apapun di map theater)
                if gm.map_id == 'theater' or 'theater' in gm.map_id.lower():
                    gs.story_flags['defeat_theater_guard'] = True
                # Update quest progress jika ada quest kill aktif
                if gs.update_quest_progress("defeat_enemies"):
                    gs.complete_quest("defeat_enemies")
                if gs.update_quest_progress(f"defeat_{enemy_id}"):
                    gs.complete_quest(f"defeat_{enemy_id}")

                # Ch1 combat objective tracking
                if int(gs.story_flags.get('current_chapter', 1)) == 1:
                    try:
                        from .characters import (
                            get_ch1_quest, update_ch1_objective,
                            check_ch1_objective_progress, display_ch1_completion,
                            sync_ch1_quest_hud,
                            get_ch1_objective_complete_dialog,
                            get_ch1_next_objective_dialog,
                            get_ch1_next_incomplete_objective,
                        )
                        q_data = get_ch1_quest(gs.player_character)
                        if q_data:
                            for obj in q_data['objectives']:
                                if obj.get('type') == 'combat':
                                    pre_cur, tot = check_ch1_objective_progress(gs, obj['id'])
                                    if pre_cur < tot:
                                        update_ch1_objective(gs, obj['id'], 1)
                                        cur2, tot2 = check_ch1_objective_progress(gs, obj['id'])
                                        bar = '■' * cur2 + '□' * max(0, tot2 - cur2)

                                        # Dialog progres per karakter
                                        _win_dialogs = {
                                            'vio':      f"Vio: Penjaga dinetralisir. {cur2}/{tot2}.",
                                            'haikaru':  f"Haikaru: {cur2}/{tot2} penjaga dinetralkan. Sesuai kalkulasi.",
                                            'aolinh':   f"Aolinh: Aku bisa melakukan ini! {cur2}/{tot2} ✓",
                                            'arganta':  f"Arganta: Per Nonno. {cur2}/{tot2} patroli dilumpuhkan.",
                                            'ignatius': f"Ignatius: {cur2}/{tot2} down.",
                                        }
                                        msg = _win_dialogs.get(gs.player_character, f"{cur2}/{tot2} dikalahkan")
                                        icon = '✓' if cur2 >= tot2 else '◐'
                                        print(f"\n  {Warna.KUNING}{msg}{Warna.RESET}")
                                        print(f"  {Warna.CYAN}{icon} {obj['desc']}: [{bar}] {cur2}/{tot2}{Warna.RESET}")
                                        time.sleep(1.2)

                                        # Objective baru selesai?
                                        if cur2 >= tot2:
                                            comp_dialogs = get_ch1_objective_complete_dialog(
                                                gs.player_character, obj['id'])
                                            if comp_dialogs:
                                                print()
                                                for line in comp_dialogs:
                                                    print(f"  {Warna.HIJAU}{line}{Warna.RESET}")
                                                time.sleep(1.5)

                                            from .characters import check_ch1_complete
                                            if check_ch1_complete(gs):
                                                display_ch1_completion(gs)
                                            else:
                                                next_obj_id, _ = get_ch1_next_incomplete_objective(gs)
                                                if next_obj_id:
                                                    next_dialogs = get_ch1_next_objective_dialog(
                                                        gs.player_character, next_obj_id)
                                                    if next_dialogs:
                                                        print()
                                                        for line in next_dialogs:
                                                            print(f"  {Warna.KUNING}{line}{Warna.RESET}")
                                                        time.sleep(1.5)
                                        break
                    except Exception:
                        pass

                xp_gain = hasil['enemy'].get('xp', 10)
                if leveled := gs.gain_xp(xp_gain):
                    # Tampilkan gains per-karakter (bukan flat constants)
                    gains = getattr(gs, 'level_up_gains', {})
                    hp_g  = gains.get('hp',      LEVEL_UP_HP_GAIN)
                    atk_g = gains.get('attack',  LEVEL_UP_ATTACK_GAIN)
                    def_g = gains.get('defense', LEVEL_UP_DEFENSE_GAIN)
                    spd_g = gains.get('speed',   LEVEL_UP_SPEED_GAIN)
                    print(f"\n{Warna.KUNING}{'═' * 50}{Warna.RESET}")
                    print(f"{Warna.KUNING + Warna.TERANG}  ⭐ LEVEL UP! ⭐  Sekarang Level {gs.level}{Warna.RESET}")
                    print(f"{Warna.HIJAU}  HP Maks: +{hp_g}  ATK: +{atk_g}  DEF: +{def_g}  SPD: +{spd_g}{Warna.RESET}")
                    print(f"{Warna.CYAN}  Stats baru: HP {gs.max_hp} | ATK {gs.attack} | DEF {gs.defense} | SPD {gs.speed}{Warna.RESET}")
                    print(f"{Warna.KUNING}{'═' * 50}{Warna.RESET}")
                    time.sleep(2.5)

                # Reward Dollar
                dollar_drop = hasil['enemy'].get('dollars', 0)
                if dollar_drop > 0:
                    bonus = random.randint(0, dollar_drop // 3)  # sedikit random bonus
                    earned = dollar_drop + bonus
                    # Cek lucky charm aktif
                    if gs.story_flags.pop('luck_boost_active', False):
                        earned = int(earned * 1.25)
                        print(f"  {Warna.KUNING}🍀 Lucky Charm aktif! Bonus dollar!{Warna.RESET}")
                    gs.dollars += earned
                    print(f"  {Warna.KUNING}💵 +${earned} (Total: ${gs.dollars}){Warna.RESET}")
                    time.sleep(1)

            elif ret == 'player_dead':
                return 'game_over'
            elif ret == 'checkpoint':
                # Boss retry habis atau Give Up — load checkpoint
                if hasattr(gs, 'load_checkpoint'):
                    gs.load_checkpoint()
                    # Sync player_stats ke GameState setelah checkpoint load
                    player_stats['hp']     = gs.hp
                    player_stats['energy'] = gs.energy
                print(f"\n  {Warna.KUNING}Kembali ke checkpoint terakhir...{Warna.RESET}")
                time.sleep(1)
                # Kembalikan ke eksplorasi (bukan game_over)
                return 'checkpoint'

            try:
                from .characters import check_candala_encounter
                check_candala_encounter(gs)
            except Exception:
                pass

        elif hasil['type'] == 'npc':
            interaksi_npc(hasil['npc_id'], gs, gm)

        elif hasil['type'] == 'item':
            item_name = hasil['item']

            if is_quest_item(item_name):
                gs.add_quest_item(item_name)
            else:
                gs.add_item(item_name)
            print(f"\n{Warna.HIJAU}✓ Dapat: {item_name}!{Warna.RESET}")
            time.sleep(0.5)

            # Cek sidequest chapter advance jika USB Evidence Drive didapat
            if item_name == 'USB Evidence Drive':
                try:
                    from .npc_interactions import _check_sidequest_chapter_advance
                    _check_sidequest_chapter_advance(gs)
                except Exception:
                    pass

            # Ch1: cek apakah item ini trigger objective progress
            if int(gs.story_flags.get('current_chapter', 1)) == 1:
                try:
                    from .characters import (
                        get_ch1_item_objective, update_ch1_objective,
                        check_ch1_objective_progress, get_ch1_quest,
                        display_ch1_completion, sync_ch1_quest_hud,
                        get_ch1_objective_complete_dialog,
                        get_ch1_next_objective_dialog,
                        get_ch1_next_incomplete_objective,
                    )
                    result = get_ch1_item_objective(gs.player_character, item_name)
                    if result:
                        obj_id, obj_dialog = result

                        # Baca progress SEBELUM update untuk deteksi "baru selesai"
                        q_data = get_ch1_quest(gs.player_character)
                        obj_def = next(
                            (o for o in q_data['objectives'] if o['id'] == obj_id), None
                        ) if q_data else None
                        pre_cur = gs.story_flags.get(f"ch1_obj_{obj_id}", 0)
                        pre_done = obj_def and pre_cur >= obj_def['target']

                        # Dialog karakter saat ambil item
                        print(f"\n  {Warna.KUNING}{obj_dialog}{Warna.RESET}")
                        time.sleep(1.2)

                        # Update progress + sync HUD
                        quest_done = update_ch1_objective(gs, obj_id, 1)

                        # Tampilkan progress bar objective ini
                        if obj_def:
                            cur, tot = check_ch1_objective_progress(gs, obj_id)
                            bar = '■' * cur + '□' * max(0, tot - cur)
                            icon = '✓' if cur >= tot else '◐'
                            print(f"  {Warna.CYAN}{icon} {obj_def['desc']}: "
                                  f"[{bar}] {cur}/{tot}{Warna.RESET}")
                            time.sleep(0.8)

                        # Cek apakah objective ini BARU SAJA selesai
                        post_cur = gs.story_flags.get(f"ch1_obj_{obj_id}", 0)
                        just_done = (not pre_done) and obj_def and (post_cur >= obj_def['target'])

                        if just_done:
                            # Dialog completion objective
                            comp_dialogs = get_ch1_objective_complete_dialog(
                                gs.player_character, obj_id)
                            if comp_dialogs:
                                print()
                                for line in comp_dialogs:
                                    print(f"  {Warna.HIJAU}{line}{Warna.RESET}")
                                time.sleep(1.5)

                            # Jika seluruh quest belum selesai, tampilkan intro objective berikut
                            if not quest_done:
                                next_obj_id, _ = get_ch1_next_incomplete_objective(gs)
                                if next_obj_id:
                                    next_dialogs = get_ch1_next_objective_dialog(
                                        gs.player_character, next_obj_id)
                                    if next_dialogs:
                                        print()
                                        for line in next_dialogs:
                                            print(f"  {Warna.KUNING}{line}{Warna.RESET}")
                                        time.sleep(1.5)

                        if quest_done:
                            display_ch1_completion(gs)
                except Exception:
                    pass

        elif hasil['type'] == 'exit':
            if hasil['locked']:
                print(f"\n{Warna.MERAH}Terkunci! Perlu: {hasil['key']}{Warna.RESET}")
                time.sleep(1)
            else:
                dest = hasil['destination']
                allowed, reason = validate_access(dest, gs)
                if not allowed:
                    print(f"\n{Warna.MERAH}✗ Akses terkunci!{Warna.RESET}")
                    print(f"  {Warna.KUNING}{reason}{Warna.RESET}")
                    time.sleep(2)
                else:
                    gs.current_location = dest
                    gs.visited_locations.add(dest)

                    try:
                        from .npc_interactions import show_map_entry_dialog
                        show_map_entry_dialog(dest, gs.player_character, gs)
                    except Exception:
                        pass
                    if gs.update_quest_progress("escape_start"):
                        gs.complete_quest("escape_start")

                    # Saat masuk safe_zone, cek sidequest chapter advance
                    if dest in ('safe_zone', 'command_center'):
                        try:
                            from .npc_interactions import _check_sidequest_chapter_advance
                            _check_sidequest_chapter_advance(gs)
                        except Exception:
                            pass

                    return 'map_change'

        elif hasil['type'] == 'boss':
            if hasil['locked']:
                print(f"\n{Warna.MERAH}Pintu boss terkunci!{Warna.RESET}")
                time.sleep(1)
            else:
                from .enemies import create_boss_instance
                from contextlib import suppress
                if boss := create_boss_instance(hasil['boss_id']):
                    boss_id_key  = hasil['boss_id']
                    preboss_flag = f'preboss_shown_{boss_id_key}'
                    chapter      = int(gs.story_flags.get('current_chapter', 1))

                    # Logic: Boss Memory — if already defeated, show [Memory] variant
                    defeated_ids = gs.story_flags.get('defeated_boss_ids', [])
                    is_memory_boss = boss_id_key in defeated_ids
                    if is_memory_boss:
                        boss['name'] = f"[Memory] {boss.get('name', boss_id_key)}"
                        boss['_memory'] = True   # Flag: no story progression on kill


                    try:
                        from .npc_interactions import show_enemy_encounter_dialog
                        show_enemy_encounter_dialog(boss_id_key, gs.player_character,
                                                    enemy_name=boss.get('name', ''),
                                                    is_boss=True)
                    except Exception:
                        pass
                    if chapter == 1 and not gs.story_flags.get(preboss_flag):
                        try:
                            from .characters import get_ch1_pre_boss_dialog
                            from .utils import clear_screen
                            pre_lines = get_ch1_pre_boss_dialog(gs.player_character, boss_id_key)
                            if pre_lines:
                                clear_screen()
                                CHAR_THEME = {
                                    'vio':      Warna.MERAH + Warna.TERANG,
                                    'haikaru':  Warna.CYAN + Warna.TERANG,
                                    'aolinh':   Warna.UNGU + Warna.TERANG,
                                    'arganta':  Warna.PUTIH + Warna.TERANG,
                                    'ignatius': Warna.KUNING + Warna.TERANG,
                                }
                                tc = CHAR_THEME.get(gs.player_character, Warna.KUNING + Warna.TERANG)
                                print(f"\n{tc}{'─' * 58}{Warna.RESET}")
                                print(f"{tc}  ⚔  BOSS ENCOUNTER{Warna.RESET}")
                                print(f"{tc}{'─' * 58}{Warna.RESET}\n")
                                time.sleep(0.4)
                                for kind, text in pre_lines:
                                    if kind == 'narasi':
                                        print(f"  {Warna.ABU_GELAP}{text}{Warna.RESET}")
                                        time.sleep(0.38)
                                    elif kind == 'dialog':
                                        print(f"  {tc}{text}{Warna.RESET}")
                                        time.sleep(0.45)
                                    elif kind == 'inner':
                                        print(f"  {Warna.DIM}{Warna.CYAN}{text}{Warna.RESET}")
                                        time.sleep(0.32)
                                    elif kind == 'system':
                                        print(f"  {Warna.HIJAU + Warna.TERANG}{text}{Warna.RESET}")
                                        time.sleep(0.3)
                                print(f"\n{tc}{'─' * 58}{Warna.RESET}")
                                input(f"\n{Warna.ABU_GELAP}[ ENTER untuk mulai pertarungan ] {Warna.RESET}")
                                gs.story_flags[preboss_flag] = True
                        except Exception:
                            pass

                    with suppress(Exception):
                        from .story import play_boss_confrontation
                        play_boss_confrontation(hasil['boss_id'])

                    from .combat import run_combat
                    from .characters import get_character_name, get_character_data

                    char_data = get_character_data(gs.player_character) or {}
                    player_stats = {
                        'name':         get_character_name(gs.player_character),
                        'hp':           gs.hp,
                        'max_hp':       gs.max_hp,
                        'attack':       gs.attack,
                        'defense':      gs.defense,
                        'speed':        gs.speed,
                        'level':        gs.level,
                        'character_id': gs.player_character,
                        # FIX: skill dari karakter, bukan story_flags
                        'skills':       char_data.get('skills', {}),
                        'energy':       getattr(gs, 'energy', 20),
                        'max_energy':   getattr(gs, 'max_energy', 20),
                        'bonus_discard_tokens': gs.story_flags.get('bonus_discard_tokens', 0),
                        'stats': {
                            'hp':       gs.hp,
                            'max_hp':   gs.max_hp,
                            'attack':   gs.attack,
                            'defense':  gs.defense,
                            'speed':    gs.speed
                        }
                    }

                    if hasattr(gs, 'save_checkpoint'):
                        gs.save_checkpoint(location=gs.current_location)

                    ret = run_combat(player_stats, boss, gs.inventory)

                    # HP dan energy di-sync setelah boss combat
                    gs.hp = max(1, player_stats.get('hp', gs.hp))
                    if hasattr(gs, 'energy'):
                        gs.energy = max(0, player_stats.get('energy', gs.energy))

                    if ret == 'player_dead':
                        return 'game_over'
                    elif ret == 'checkpoint':
                        # Boss retry habis atau Give Up → load checkpoint
                        if hasattr(gs, 'load_checkpoint'):
                            gs.load_checkpoint()
                            player_stats['hp']     = gs.hp
                            player_stats['energy'] = gs.energy
                        print(f"\n  {Warna.KUNING}Kembali ke checkpoint terakhir...{Warna.RESET}")
                        time.sleep(1)
                        return 'checkpoint'
                    elif ret == 'victory':
                        boss_id = boss.get('id', '')

                        # Logic: Boss Memory — if [Memory] boss, give XP/dollars only, skip story
                        if boss.get('_memory'):
                            xp_gain  = int(boss.get('xp', 50) * 0.5)
                            dol_gain = int(boss.get('dollars', 20) * 0.5)
                            gs.gain_xp(xp_gain)
                            gs.dollars += dol_gain
                            print(f"\n  {Warna.ABU_GELAP}[Memory Boss] +{xp_gain} XP, "
                                  f"+${dol_gain} (latihan — tanpa story progress){Warna.RESET}")
                            time.sleep(2)
                            return None  # stay in exploration loop

                        # Victory Sync: record defeated boss, remove from map
                        if boss_id:
                            defeated_ids = gs.story_flags.get('defeated_boss_ids', [])
                            if boss_id not in defeated_ids:
                                defeated_ids.append(boss_id)
                            gs.story_flags['defeated_boss_ids'] = defeated_ids
                            gm.boss_doors = [d for d in gm.boss_doors if d['boss_id'] != boss_id]

                        # Check if this is a final boss
                        if boss.get('final_boss') or boss_id == 'epstein_boss':
                            gs.save_to_file()
                            return 'victory'

                        # Set special flags based on boss ID for character quests

                        if boss_id == 'theater_master' or 'theater' in boss_id.lower():
                            gs.story_flags['defeat_theater_guard'] = True
                            if 'Tiket Backstage' not in gs.quest_items:
                                gs.add_quest_item('Tiket Backstage')
                                print(f"\n  {Warna.KUNING}★ Quest Item: Tiket Backstage didapat!{Warna.RESET}")

                        gs.bosses_defeated += 1
                        # NOTE: save_to_file() dipindah ke SETELAH chapter advance
                        # supaya save file mencerminkan chapter yang sudah maju (bukan lama)

                        char_id = gs.player_character
                        chapter = int(gs.story_flags.get('current_chapter', 1))

                        # Bug Fix: Ch1 boss kill → update boss-type objective by boss_id match
                        if chapter == 1:
                            try:
                                from .characters import (
                                    get_ch1_quest, update_ch1_objective,
                                    check_ch1_objective_progress, check_ch1_complete,
                                    display_ch1_completion, sync_ch1_quest_hud,
                                    get_ch1_objective_complete_dialog,
                                )
                                q_data = get_ch1_quest(char_id)
                                if q_data:
                                    # Map boss_id → objective id (boss-type objectives)
                                    CH1_BOSS_OBJ_MAP = {
                                        'maxwell_agent':    'defeat_maxwell_agent',   # Vio Ch1
                                        'warden_elite':     'defeat_warden_elite',    # Haikaru Ch1
                                        'theater_master':   'defeat_theater_master',  # Aolinh Ch1
                                        'harbor_captain':   'defeat_harbor_captain',  # Arganta Ch1
                                        'security_bot':     'defeat_security_bot',    # Ignatius Ch1
                                    }
                                    obj_id = CH1_BOSS_OBJ_MAP.get(boss_id)
                                    if obj_id:
                                        cur, tot = check_ch1_objective_progress(gs, obj_id)
                                        if cur < tot:
                                            update_ch1_objective(gs, obj_id, 1)
                                            sync_ch1_quest_hud(gs)
                                            comp_dlg = get_ch1_objective_complete_dialog(char_id, obj_id)
                                            if comp_dlg:
                                                print()
                                                for line in comp_dlg:
                                                    print(f"  {Warna.HIJAU}{line}{Warna.RESET}")
                                                time.sleep(1.5)

                                    if check_ch1_complete(gs):
                                        xp_gain = boss.get('xp', 50)
                                        if gs.gain_xp(xp_gain):
                                            print(f"\n{Warna.KUNING}  ⭐ LEVEL UP! Level {gs.level}{Warna.RESET}")
                                        dol = boss.get('dollars', 0)
                                        if dol > 0:
                                            gs.dollars += dol
                                            print(f"  {Warna.KUNING}💵 +${dol}{Warna.RESET}")
                                        display_ch1_completion(gs)
                                        return 'map_change'
                            except Exception:
                                pass
                            # Fallback: force chapter advance even if ch1 system fails
                            gs.story_flags['current_chapter'] = 2
                            gs.story_flags['ch2_bosses_available'] = True
                            # Standardized ch1 completion flag for CHAPTER_REQUIREMENTS
                            _char_id_fb = gs.player_character
                            gs.story_flags[f'ch1_{_char_id_fb}_complete'] = True
                            gs.active_quests = [q for q in gs.active_quests if q.get('quest_type') == 'side']
                            print(f"\n{Warna.KUNING}{'═'*60}{Warna.RESET}")
                            print(f"  {Warna.KUNING + Warna.TERANG}★  CHAPTER 1 SELESAI!  ★{Warna.RESET}")
                            print(f"  {Warna.HIJAU}Chapter 2 dimulai — Eksplorasi Pulau!{Warna.RESET}")
                            print(f"{Warna.KUNING}{'═'*60}{Warna.RESET}")
                            time.sleep(3)
                            xp_gain = boss.get('xp', 50)
                            gs.gain_xp(xp_gain)
                            dol = boss.get('dollars', 0)
                            if dol > 0:
                                gs.dollars += dol
                            return 'map_change'

                        # Ambil data quest utama chapter ini
                        try:
                            from .characters import CHARACTER_MAIN_QUESTS
                            quest_data = CHARACTER_MAIN_QUESTS.get(char_id, {}).get(chapter)
                        except Exception:
                            quest_data = None

                        quest_id = (quest_data["id"]
                                    if quest_data
                                    else f"defeat_{char_id}_boss")
                        _prog_before = next((q.get('progress',0) for q in gs.active_quests if q.get('id')==quest_id), 0)

                        # Set character/boss specific extra flags before gate checks
                        _BOSS_EXTRA_FLAGS = {
                            'theater_master':  'defeat_theater_commander',  # Aolinh SQ requirement
                            'maxwell_agent':   'defeat_maxwell_agent',      # Vio Ch1 boss
                            'warden_elite':    'defeat_warden_elite',
                            'harbor_captain':  'defeat_harbor_captain',
                        }
                        if boss_id in _BOSS_EXTRA_FLAGS:
                            gs.story_flags[_BOSS_EXTRA_FLAGS[boss_id]] = True

                        # Gate bosses: chapter-aware flag setting
                        # Ch2 boss masing-masing karakter berbeda, semua set boss_ch2_defeated
                        _CH2_BOSS_IDS = {
                            'kepala_penjaga', 'network_overseer',
                            'doctor_rousseau', 'mercenary_commander',
                        }
                        # security_bot di ch2 (Ignatius) juga set flag, tapi bukan di ch1
                        _is_ch2_gate = (boss_id in _CH2_BOSS_IDS) or (boss_id == 'security_bot' and chapter == 2)
                        # Only ghislaine_maxwell is the Ch4 gate boss
                        # agen_maxwell at lab is optional - sets different flag
                        _is_ch4_gate = (boss_id == 'ghislaine_maxwell')
                        _is_lab_optional = (boss_id == 'agen_maxwell')

                        if _is_ch2_gate:
                            gs.story_flags['boss_ch2_defeated'] = True
                            for _q in gs.active_quests:
                                if _q.get('id') == quest_id:
                                    _q['progress'] = _q.get('total', 1)
                                    break
                            quest_done = True
                        elif _is_ch4_gate:
                            gs.story_flags['boss_ch4_defeated'] = True
                            for _q in gs.active_quests:
                                if _q.get('id') == quest_id:
                                    _q['progress'] = _q.get('total', 1)
                                    break
                            quest_done = True
                        elif _is_lab_optional:
                            # Agen Maxwell lab = optional fight, hanya set lab flag
                            gs.story_flags['boss_lab_agent_defeated'] = True
                            quest_done = gs.update_quest_progress(quest_id)
                        else:
                            quest_done = gs.update_quest_progress(quest_id)
                        _prog_after = next((q.get('progress',0) for q in gs.active_quests if q.get('id')==quest_id), _prog_before+1)
                        # Dialog objektif selesai
                        if quest_data and _prog_after > _prog_before:
                            _targets = quest_data.get('steps', [])
                            _step_done = _targets[_prog_before] if _prog_before < len(_targets) else ""
                            if _step_done:
                                print(f"\n{Warna.KUNING}{'★'*55}{Warna.RESET}")
                                print(f"  {Warna.HIJAU + Warna.TERANG}✓ OBJEKTIF SELESAI:{Warna.RESET} {_step_done}")
                                if not quest_done and _prog_after < len(_targets):
                                    print(f"  {Warna.CYAN}▶ Selanjutnya:{Warna.RESET} {_targets[_prog_after]}")
                                print(f"{Warna.KUNING}{'★'*55}{Warna.RESET}")
                                time.sleep(2.5)
                        if quest_done:
                            gs.complete_quest(quest_id)

                            # Tandai completion flag di story_flags
                            if quest_data:
                                gs.story_flags[quest_data["completion_flag"]] = True
                                next_msg = quest_data.get("next_chapter_msg", "")

                            # Naikan chapter — sistem 6 chapter
                            from .characters import advance_chapter, check_chapter_unlock
                            next_ch = chapter + 1
                            can_advance, reason = check_chapter_unlock(gs, next_ch)

                            if chapter == 1:
                                gs.story_flags['current_chapter'] = 2
                                gs.story_flags['ch2_bosses_available'] = True
                                # Standardized ch1 flag: ch1_{char_id}_complete (matches CHAPTER_REQUIREMENTS)
                                _ch1_char = gs.player_character
                                gs.story_flags[f'ch1_{_ch1_char}_complete'] = True
                                gs.active_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]
                                print(f"\n{Warna.KUNING}{'═'*60}{Warna.RESET}")
                                print(f"  {Warna.KUNING + Warna.TERANG}★  CHAPTER 1 SELESAI!  ★{Warna.RESET}")
                                if quest_data:
                                    print(f"  {quest_data.get('next_chapter_msg','')}")
                                print(f"  {Warna.HIJAU}Chapter 2 dimulai — Eksplorasi Pulau!{Warna.RESET}")
                                print(f"{Warna.KUNING}{'═'*60}{Warna.RESET}")
                                time.sleep(3)

                            elif chapter == 2:
                                gs.story_flags['current_chapter'] = 3
                                gs.story_flags['final_bosses_available'] = True
                                gs.active_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]
                                print(f"\n{Warna.KUNING}{'═'*60}{Warna.RESET}")
                                print(f"  {Warna.KUNING + Warna.TERANG}★  CHAPTER 2 SELESAI!  ★{Warna.RESET}")
                                _ch2_boss_names = {
                                    'network_overseer':    'Network Overseer dikalahkan! Jaringan pulau terbuka.',
                                    'kepala_penjaga':      'Kepala Penjaga dikalahkan! Penjara sepenuhnya bebas.',
                                    'doctor_rousseau':     'Dr. Rousseau dikalahkan! Jiejie aman. Pulau terbuka.',
                                    'mercenary_commander': 'Mercenary Commander roboh! Dermaga terbuka.',
                                    'security_bot':        'AmBOTukam Mk III hancur! Grid pulau terkuasai.',
                                }
                                _ch2_msg = _ch2_boss_names.get(boss_id, 'Boss Ch.2 dikalahkan! Pulau terbuka penuh.')
                                print(f"  {Warna.KUNING}{_ch2_msg}{Warna.RESET}")
                                print(f"  {Warna.CYAN}Chapter 3 — Temui NPC, selesaikan 2 sidequest untuk lanjut!{Warna.RESET}")
                                print(f"  {Warna.ABU_GELAP}Cari NPC di: Penjara Utara, Teater, Dermaga, Pantai, Basement{Warna.RESET}")
                                print(f"{Warna.KUNING}{'═'*60}{Warna.RESET}")
                                time.sleep(4)

                            elif chapter == 3:
                                # Ch3→4 butuh 2 sidequest
                                sq_done = gs.get_sidequest_progress()
                                if sq_done >= 2:
                                    gs.story_flags['current_chapter'] = 4
                                    gs.active_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]
                                    print(f"\n{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                    print(f"  {Warna.MERAH + Warna.TERANG}★  CHAPTER 3 SELESAI!  ★{Warna.RESET}")
                                    print(f"  {Warna.MERAH}Chapter 4 — Infiltrasi Pusat Kontrol, kalahkan Ghislaine Maxwell!{Warna.RESET}")
                                    print(f"{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                    time.sleep(3)
                                else:
                                    print(f"\n{Warna.KUNING}Selesaikan minimal 2 sidequest NPC untuk lanjut ke Ch.4!{Warna.RESET}")
                                    print(f"  Quest selesai: {sq_done}/2")
                                    time.sleep(3)

                            elif chapter == 4:
                                gs.story_flags['current_chapter'] = 5
                                gs.active_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]
                                print(f"\n{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                print(f"  {Warna.MERAH + Warna.TERANG}★  CHAPTER 4 SELESAI!  ★{Warna.RESET}")
                                print(f"  {Warna.KUNING}Ghislaine Maxwell dikalahkan! Little Black Book ada di tanganmu.{Warna.RESET}")
                                print(f"  {Warna.CYAN}Chapter 5 — Selesaikan 4 sidequest + dapatkan USB Evidence Drive dari Vio!{Warna.RESET}")
                                print(f"  {Warna.ABU_GELAP}Temui Vio di Laboratorium (Ch.4+) — bawa USB Security Drive ke dia{Warna.RESET}")
                                print(f"{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                time.sleep(4)

                            elif chapter == 5:
                                # Ch5→6 butuh 4 sidequest + USB
                                sq_done = gs.get_sidequest_progress()
                                has_usb = ('USB Evidence Drive' in gs.inventory
                                           or 'USB Evidence Drive' in gs.quest_items)
                                if sq_done >= 4 and has_usb:
                                    gs.story_flags['current_chapter'] = 6
                                    gs.active_quests = [q for q in gs.active_quests if q.get("quest_type") == "side"]
                                    print(f"\n{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                    print(f"  {Warna.MERAH + Warna.TERANG}★  CHAPTER 5 SELESAI!  ★{Warna.RESET}")
                                    print(f"  {Warna.MERAH}CHAPTER 6 — EPSTEIN MENUNGGU! FINAL BOSS!{Warna.RESET}")
                                    print(f"{Warna.MERAH}{'═'*60}{Warna.RESET}")
                                    time.sleep(3)
                                else:
                                    msgs = []
                                    if sq_done < 4:
                                        msgs.append(f"Quest NPC: {sq_done}/4 selesai")
                                    if not has_usb:
                                        msgs.append("USB Evidence Drive belum dimiliki!")
                                    print(f"\n{Warna.MERAH}Belum bisa lanjut ke Chapter 6!{Warna.RESET}")
                                    for m in msgs:
                                        print(f"  {Warna.KUNING}→ {m}{Warna.RESET}")
                                    time.sleep(3)

                            # Backward compat — quest generic
                            if gs.update_quest_progress("defeat_bosses"):
                                gs.complete_quest("defeat_bosses")
                            if gs.update_quest_progress("defeat_final_boss"):
                                gs.complete_quest("defeat_final_boss")

                            # Reward Dollar Boss
                            dollar_drop = boss.get('dollars', 0)
                            if dollar_drop > 0:
                                if gs.story_flags.pop('luck_boost_active', False):
                                    dollar_drop = int(dollar_drop * 1.25)
                                gs.dollars += dollar_drop
                                print(f"\n  {Warna.KUNING}💵 BOSS DEFEATED! +${dollar_drop} "
                                      f"(Total: ${gs.dollars}){Warna.RESET}")
                                time.sleep(1.5)

                            # Hapus boss door dari peta setelah dikalahkan
                            px, py = gm.player_x, gm.player_y
                            gm.boss_doors = [
                                d for d in gm.boss_doors
                                if (d['x'] != px or d['y'] != py)
                            ]

                            try:
                                from .story import get_route_chapter_at, display_route_chapter
                                # chapter_index: 0=ch1 selesai, 1=ch2 selesai, dst
                                chapter_index = chapter - 1  # 0-based sesuai chapter yang baru selesai
                                ch_id = get_route_chapter_at(gs.player_character, chapter_index)
                                if ch_id:
                                    clear_screen()
                                    displayed = display_route_chapter(ch_id)
                                    if displayed:
                                        input(f"\n{Warna.ABU_GELAP}[ENTER untuk lanjut]{Warna.RESET} ")
                            except KeyError:
                                pass  # Story chapter tidak ditemukan — skip tanpa crash
                            except Exception:
                                pass  # Abaikan error story display, jangan interrupt gameplay


                            # mencerminkan chapter terbaru (bukan chapter sebelum boss)
                            gs.save_to_file()

    except Exception as e:
        print(f"{Warna.MERAH}Error: {e}{Warna.RESET}")
        time.sleep(1)

    return None

# BRAN EDWARDS SHOP

BRAN_SHOP_ITEMS = [
    {"name": "Health Potion",     "desc": "Restore 40 HP",                   "price": 30,  "effect": "heal_40"},
    {"name": "Med Kit",           "desc": "Restore 80 HP",                   "price": 60,  "effect": "heal_80"},
    {"name": "Antidote",          "desc": "Sembuhkan status efek negatif",   "price": 45,  "effect": "cure"},
    {"name": "Energy Drink",      "desc": "ATK +50% selama 2 turn (pakai saat combat)", "price": 80,  "effect": "atk_buff_item"},
    {"name": "Armor Padding",     "desc": "DEF +50% selama 2 turn (pakai saat combat)", "price": 80,  "effect": "def_buff_item"},
    {"name": "Discard Token",     "desc": "+1 slot discard untuk 1 combat",  "price": 50,  "effect": "discard_token"},
    {"name": "Lucky Charm",       "desc": "25% bonus dollar dari musuh berikutnya", "price": 100, "effect": "luck_boost"},
    {"name": "Explosive Charge",  "desc": "Senjata sekali pakai, 40 damage", "price": 80,  "effect": "explosive"},
]

BRAN_DIALOG = [
    "Bran Edwards: *휘파람 불며* Oh hey, survivor!",
    "Bran Edwards: Name's Bran. Don't ask how I got here.",
    "Bran Edwards: I got supplies. You got dollars.",
    "Bran Edwards: Let's make a deal, yeah?",
]

def _buka_toko_bran_remote(gs):
    
    clear_screen()
    first_visit = not gs.story_flags.get('bran_shop_visited', False)

    print(f"\n{Warna.KUNING + Warna.TERANG}╔══════════════════════════════════════════════════╗{Warna.RESET}")
    print(f"{Warna.KUNING + Warna.TERANG}║          BRAN EDWARDS — RADIO SHOP               ║{Warna.RESET}")
    print(f"{Warna.KUNING + Warna.TERANG}╚══════════════════════════════════════════════════╝{Warna.RESET}")

    if first_visit:
        # Dialog dan hadiah pertama kali
        print(f"\n  {Warna.CYAN}*krssshh* Walkie-talkie berbunyi...{Warna.RESET}")
        time.sleep(1)
        print(f"\n  {Warna.KUNING + Warna.TERANG}Bran{Warna.RESET}{Warna.KUNING}: {Warna.RESET}", end="")
        for c in "Hei hei! Kamu bisa dengar aku? Bran Edwards di sini. Island Surplus Store — mobile edition.":
            print(c, end="", flush=True)
            time.sleep(0.03)
        print()
        time.sleep(0.5)
        print(f"\n  {Warna.KUNING + Warna.TERANG}Bran{Warna.RESET}{Warna.KUNING}: {Warna.RESET}", end="")
        for c in "Pertama kali hubungi aku? Ini, welcome gift dari Bran. Gratis. Jangan tanya dari mana asalnya.":
            print(c, end="", flush=True)
            time.sleep(0.03)
        print()
        time.sleep(0.5)

        # Berikan hadiah gratis
        gifts = ["Health Potion", "Bandage"]
        print(f"\n  {Warna.HIJAU + Warna.TERANG}[ HADIAH PERTAMA KALI ]{Warna.RESET}")
        for gift in gifts:
            gs.add_item(gift)
            print(f"  {Warna.HIJAU}✓ Dapat: {gift}{Warna.RESET}")
        time.sleep(0.5)

        print(f"\n  {Warna.KUNING + Warna.TERANG}Bran{Warna.RESET}{Warna.KUNING}: {Warna.RESET}", end="")
        for c in "Oke, sekarang belanja apa? Dollar kamu yang bicara.":
            print(c, end="", flush=True)
            time.sleep(0.03)
        print()
        time.sleep(1)

        gs.story_flags['bran_shop_visited'] = True
    else:
        print(f"\n  {Warna.CYAN}*krssshh*{Warna.RESET}")
        print(f"  {Warna.KUNING + Warna.TERANG}Bran{Warna.RESET}{Warna.KUNING}: {Warna.RESET}Kamu lagi. Good, berarti masih hidup. Mau beli apa?")
        time.sleep(1)


    while True:
        clear_screen()
        print(f"\n{Warna.KUNING + Warna.TERANG}╔══════════════════════════════════════════════════╗{Warna.RESET}")
        print(f"{Warna.KUNING + Warna.TERANG}║     BRAN EDWARDS — ISLAND SURPLUS STORE          ║{Warna.RESET}")
        print(f"{Warna.KUNING + Warna.TERANG}╚══════════════════════════════════════════════════╝{Warna.RESET}")
        print(f"\n  {Warna.ABU_GELAP}\"Semua barang garansi asli. Mungkin.\" — Bran{Warna.RESET}")
        print(f"\n  {Warna.KUNING}💵 Dollar kamu: ${gs.dollars}{Warna.RESET}\n")
        print(f"  {Warna.ABU_GELAP}{'─' * 52}{Warna.RESET}")

        _SHOP_MAX = {'atk_buff_item': 3, 'def_buff_item': 3}
        _SHOP_FLAG = {'atk_buff_item': 'shop_energy_drink_bought', 'def_buff_item': 'shop_armor_padding_bought'}
        for i, item in enumerate(BRAN_SHOP_ITEMS, 1):
            eff = item['effect']
            # Hitung sisa stok untuk item terbatas
            stock_str = ""
            if eff in _SHOP_MAX:
                bought = gs.story_flags.get(_SHOP_FLAG[eff], 0)
                sisa   = _SHOP_MAX[eff] - bought
                if sisa <= 0:
                    stock_str = f"  {Warna.MERAH}[HABIS]{Warna.RESET}"
                else:
                    stock_str = f"  {Warna.ABU_GELAP}[Stok: {sisa}]{Warna.RESET}"
            can_afford = gs.dollars >= item['price']
            price_color = Warna.HIJAU if can_afford else Warna.MERAH
            print(f"  {Warna.CYAN}[{i}]{Warna.RESET} {Warna.TERANG}{item['name']:<20}{Warna.RESET} "
                  f"{price_color}${item['price']:>4}{Warna.RESET}  "
                  f"{Warna.ABU_GELAP}{item['desc']}{Warna.RESET}{stock_str}")

        print(f"\n  {Warna.ABU_GELAP}[0] Keluar dari toko{Warna.RESET}")
        print(f"  {Warna.ABU_GELAP}{'─' * 52}{Warna.RESET}")

        try:
            pilihan = input(f"\n  {Warna.CYAN}Beli apa? > {Warna.RESET}").strip()
            if pilihan == '0':
                print(f"\n  {Warna.ABU_GELAP}Bran Edwards: \"Balik lagi kapanpun, friend!\"{Warna.RESET}")
                time.sleep(1.5)
                break

            idx = int(pilihan) - 1
            if not (0 <= idx < len(BRAN_SHOP_ITEMS)):
                print(f"\n  {Warna.MERAH}Pilihan tidak valid.{Warna.RESET}")
                time.sleep(1)
                continue

            item = BRAN_SHOP_ITEMS[idx]

            if gs.dollars < item['price']:
                print(f"\n  {Warna.MERAH}Dollar tidak cukup! Perlu ${item['price']}, punya ${gs.dollars}.{Warna.RESET}")
                print(f"  {Warna.ABU_GELAP}Bran: \"Come back when you have more cash, kid.\"{Warna.RESET}")
                time.sleep(2)
                continue

            # Proses pembelian
            gs.dollars -= item['price']
            effect = item['effect']

            if effect == 'heal_40':
                healed = min(40, gs.max_hp - gs.hp)
                gs.hp = min(gs.hp + 40, gs.max_hp)
                print(f"\n  {Warna.HIJAU}✓ HP +{healed} (sekarang {gs.hp}/{gs.max_hp}){Warna.RESET}")
            elif effect == 'heal_80':
                healed = min(80, gs.max_hp - gs.hp)
                gs.hp = min(gs.hp + 80, gs.max_hp)
                print(f"\n  {Warna.HIJAU}✓ HP +{healed} (sekarang {gs.hp}/{gs.max_hp}){Warna.RESET}")
            elif effect == 'cure':
                gs.story_flags.pop('poisoned', None)
                gs.story_flags.pop('debuffed', None)
                print(f"\n  {Warna.HIJAU}✓ Status efek negatif dihapus.{Warna.RESET}")
            elif effect == 'atk_buff_item':
                bought = gs.story_flags.get('shop_energy_drink_bought', 0)
                if bought >= 3:
                    gs.dollars += item['price']  # refund
                    print(f"\n  {Warna.MERAH}Stok Energy Drink habis! (Batas 3x per run){Warna.RESET}")
                    print(f"  {Warna.ABU_GELAP}Bran: \"Maaf bro, udah habis. Nanti restok.\"  {Warna.RESET}")
                else:
                    gs.story_flags['shop_energy_drink_bought'] = bought + 1
                    gs.add_item("Energy Drink")
                    sisa = 3 - (bought + 1)
                    print(f"\n  {Warna.HIJAU}✓ Energy Drink masuk ke inventory! Pakai saat combat → ATK +50% 2 turn.{Warna.RESET}")
                    print(f"  {Warna.ABU_GELAP}Stok tersisa: {sisa}{Warna.RESET}")
            elif effect == 'def_buff_item':
                bought = gs.story_flags.get('shop_armor_padding_bought', 0)
                if bought >= 3:
                    gs.dollars += item['price']  # refund
                    print(f"\n  {Warna.MERAH}Stok Armor Padding habis! (Batas 3x per run){Warna.RESET}")
                    print(f"  {Warna.ABU_GELAP}Bran: \"Maaf bro, udah habis. Nanti restok.\"  {Warna.RESET}")
                else:
                    gs.story_flags['shop_armor_padding_bought'] = bought + 1
                    gs.add_item("Armor Padding")
                    sisa = 3 - (bought + 1)
                    print(f"\n  {Warna.HIJAU}✓ Armor Padding masuk ke inventory! Pakai saat combat → DEF +50% 2 turn.{Warna.RESET}")
                    print(f"  {Warna.ABU_GELAP}Stok tersisa: {sisa}{Warna.RESET}")
            elif effect == 'atk_up':
                gs.attack += 3
                print(f"\n  {Warna.HIJAU}✓ ATK permanent +3 (sekarang {gs.attack}){Warna.RESET}")
            elif effect == 'def_up':
                gs.defense += 3
                print(f"\n  {Warna.HIJAU}✓ DEF permanent +3 (sekarang {gs.defense}){Warna.RESET}")
            elif effect == 'discard_token':
                cur = gs.story_flags.get('bonus_discard_tokens', 0)
                gs.story_flags['bonus_discard_tokens'] = cur + 1
                print(f"\n  {Warna.HIJAU}✓ +1 Discard Token! (Aktif di combat berikutnya){Warna.RESET}")
            elif effect == 'luck_boost':
                gs.story_flags['luck_boost_active'] = True
                print(f"\n  {Warna.HIJAU}✓ Lucky Charm aktif! Bonus dollar musuh berikutnya.{Warna.RESET}")
            elif effect == 'explosive':
                gs.add_item("Explosive Charge")
                print(f"\n  {Warna.HIJAU}✓ Explosive Charge masuk ke inventory!{Warna.RESET}")
            else:
                gs.add_item(item['name'])
                print(f"\n  {Warna.HIJAU}✓ {item['name']} masuk ke inventory!{Warna.RESET}")

            print(f"  {Warna.KUNING}💵 Sisa: ${gs.dollars}{Warna.RESET}")
            print(f"  {Warna.ABU_GELAP}Bran: \"Good choice. Stay alive out there.\"{Warna.RESET}")
            time.sleep(2)

        except (ValueError, IndexError):
            print(f"\n  {Warna.MERAH}Input tidak valid.{Warna.RESET}")
            time.sleep(1)
        except Exception as e:
            print(f"\n  {Warna.MERAH}Error: {e}{Warna.RESET}")
            time.sleep(1)

def interaksi_npc(npc_id, gs, gm):
    """Interaksi NPC — sidequest system (bukan party rekrutmen)."""

    # Bran Edwards — toko khusus
    if npc_id == 'bran_edwards':
        clear_screen()
        print(f"\n{Warna.KUNING + Warna.TERANG}Bran Edwards{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}Pedagang Misterius — Safe Zone{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}\n")
        for line in BRAN_DIALOG:
            print(f"  {line}")
            time.sleep(0.8)
        print()
        print(f"\n  {Warna.KUNING}[1]{Warna.RESET} Masuk ke toko")
        print(f"  {Warna.ABU_GELAP}[2] Pergi{Warna.RESET}")
        pilihan = input(f"\n{Warna.CYAN}> {Warna.RESET}").strip()
        if pilihan == '1':
            _buka_toko_bran_remote(gs)
        return

    cd = get_character_data(npc_id)
    if not cd:
        return

    # Coba gunakan npc_interactions jika tersedia
    try:
        from .npc_interactions import (
            NPC_SIDEQUEST_DATA, can_trigger_sidequest, is_sidequest_complete,
            display_npc_intro, display_npc_quest_briefing, display_npc_completion,
            display_npc_repeat_talk
        )
        npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
        use_new_system = npc_data is not None
    except ImportError:
        use_new_system = False

    clear_screen()
    chapter = int(gs.story_flags.get('current_chapter', 1))

    if use_new_system:
        npc_data = NPC_SIDEQUEST_DATA[npc_id]
        sq_flag  = npc_data.get('reward_flag', f"{npc_id}_sidequest_done")
        met_flag = f"met_{npc_id}"

        # Cek apakah sudah pernah bertemu
        already_met = gs.story_flags.get(met_flag, False)

        # Tampilkan intro pertama kali
        if not already_met:
            display_npc_intro(npc_id, gs)
            gs.story_flags[met_flag] = True

        sq_complete  = gs.story_flags.get(sq_flag, False)
        # FIX bug: urutan parameter yang benar — (npc_id, game_state)
        sq_available = can_trigger_sidequest(npc_id, gs)

        if sq_complete:
            # Quest sudah selesai — tampilkan dialog baru sesuai state
            display_npc_repeat_talk(npc_id, gs)
            return

        if not sq_available:
            min_ch = npc_data.get('available_chapter', 2)
            print(f"\n{Warna.CYAN + Warna.TERANG}{cd['name']}{Warna.RESET}")
            print(f"{Warna.ABU_GELAP}{cd.get('title', '')}{Warna.RESET}")
            print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}\n")
            print(f"  {Warna.ABU_GELAP}{cd['name']}: \"Kita bisa bicara lebih lanjut nanti...\"")
            print(f"  {Warna.KUNING}(Sidequest terbuka mulai Chapter {min_ch}){Warna.RESET}")
            time.sleep(2)
            return

        print(f"\n{Warna.CYAN + Warna.TERANG}{cd['name']}{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{cd.get('title', '')}{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}\n")

        # Cek apakah quest sudah dimulai
        sq_started_flag = f"sidequest_{npc_id}_started"
        sq_started      = gs.story_flags.get(sq_started_flag, False)

        if not sq_started:
            display_npc_quest_briefing(npc_id, gs)
            gs.story_flags[sq_started_flag] = True
            _add_recruit_quest_on_meet(gs, npc_id)
            if any(q.get('id') == f'recruit_{npc_id}' for q in gs.active_quests):
                print(f"\n  {Warna.KUNING}★ Quest ditambahkan ke HUD!{Warna.RESET}")
                time.sleep(0.8)
            # Jika pemain sudah memiliki item yang dibutuhkan sebelum menerima quest,
            # langsung selesaikan sidequest agar tidak butuh pickup ulang.
            try:
                from .npc_interactions import is_sidequest_complete, display_npc_completion
                if is_sidequest_complete(npc_id, gs):
                    # FIX: jangan set sq_flag dulu — display_npc_completion handle flag + reward + dialog
                    success, _reward = display_npc_completion(npc_id, gs)
                    if success:
                        gs.complete_quest(f"recruit_{npc_id}")
                        gs.npcs_recruited.add(npc_id)
                    time.sleep(1.2)
                    return
            except Exception:
                pass
        else:
            # Quest sudah dimulai — cek apakah sudah selesai
            # FIX bug: urutan parameter yang benar — (npc_id, game_state)
            if is_sidequest_complete(npc_id, gs):
                # FIX: jangan set sq_flag dulu — display_npc_completion handle flag + reward + dialog
                success, _reward = display_npc_completion(npc_id, gs)
                if success:
                    gs.complete_quest(f"recruit_{npc_id}")
                    gs.npcs_recruited.add(npc_id)
                time.sleep(2)
            else:
                # Quest belum selesai — tampilkan progress ringkas
                req_items   = npc_data.get('required_items') or (
                              [npc_data['required_item']] if npc_data.get('required_item') else [])
                req_action  = npc_data.get('required_action')
                print(f"\n  {Warna.KUNING}Quest: {npc_data.get('sidequest_title', 'Sidequest')}{Warna.RESET}")
                print(f"  {Warna.ABU_GELAP}Progress:{Warna.RESET}")
                if req_items:
                    for item in req_items:

                        have = (item in gs.inventory or item in gs.quest_items)
                        chk  = f"{Warna.HIJAU}✓{Warna.RESET}" if have else f"{Warna.MERAH}✗{Warna.RESET}"
                        print(f"    {chk} {item}")
                if req_action:
                    done = gs.story_flags.get(req_action, False)
                    chk  = f"{Warna.HIJAU}✓{Warna.RESET}" if done else f"{Warna.MERAH}✗{Warna.RESET}"
                    action_labels = {'defeat_theater_guard': 'Kalahkan Penjaga Theater Backstage'}
                    print(f"    {chk} {action_labels.get(req_action, req_action)}")
                print()
                input(f"\n{Warna.ABU_GELAP}[ENTER untuk kembali]{Warna.RESET} ")

    else:
        # Fallback: tampilkan backstory dan info karakter saja
        print(f"\n{Warna.CYAN + Warna.TERANG}{cd['name']}{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{cd.get('title', '')}{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}\n")
        if intro := get_character_intro(npc_id):
            for line in intro:
                print(f"  {line}")
                time.sleep(0.7)
        print()
        print(f"  {Warna.ABU_GELAP}[Sidequest akan tersedia setelah chapter yang sesuai]{Warna.RESET}")
        input(f"\n{Warna.ABU_GELAP}[ENTER untuk kembali]{Warna.RESET} ")

def tampilkan_inventory(gs):
    clear_screen()
    print(f"\n{Warna.CYAN + Warna.TERANG}BARANG{Warna.RESET}  ", end='')
    print(f"{Warna.KUNING}★=Quest Item  ·=Barang Biasa{Warna.RESET}\n")


    quest_inv   = list(gs.quest_items)  # sudah dedup via add_quest_item()
    # Juga ambil quest items yang mungkin masih tersimpan di inventory lama (backward compat)
    for it in gs.inventory:
        if is_quest_item(it) and it not in quest_inv:
            quest_inv.append(it)
    regular_inv = [it for it in gs.inventory if not is_quest_item(it)]

    if not quest_inv and not regular_inv:
        print(f"  {Warna.ABU_GELAP}Kosong{Warna.RESET}")
    else:
        if quest_inv:
            print(f"  {Warna.KUNING + Warna.TERANG}[QUEST ITEMS — Tidak bisa dijual/dibuang]{Warna.RESET}")
            for item in quest_inv:
                print(f"  {Warna.KUNING}★ {item}{Warna.RESET}")
            print()
        if regular_inv:
            print(f"  {Warna.PUTIH}[BARANG BIASA]{Warna.RESET}")
            for item in regular_inv:
                print(f"  {Warna.ABU_GELAP}·{Warna.RESET} {item}")
    print(f"\n  ${gs.dollars} tersedia | Slot {gs.current_slot + 1}")
    input(f"\n{Warna.ABU_GELAP}[ENTER]{Warna.RESET} ")

def tampilkan_npc_quests(gs):
    """Tampilkan status sidequest NPC sebagai ganti party screen."""
    clear_screen()
    chapter = int(gs.story_flags.get('current_chapter', 1))
    print(f"\n{Warna.CYAN + Warna.TERANG}STATUS SIDEQUEST NPC{Warna.RESET}")
    print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}\n")
    print(f"  Chapter saat ini: {Warna.KUNING}Ch.{chapter}{Warna.RESET}\n")

    NPC_LIST = [
        ("haikaru",  "Haikaru Fumika",  2,  "Catatan Sandi Haikaru"),
        ("aolinh",   "Ao Lin",          2,  "Rekaman Distraksi Aolinh"),
        ("arganta",  "Amerigo Arganta", 2,  "Peta Jalur Rahasia"),
        ("ignatius", "Ignatius",        2,  "EMP Device"),       # Ch.2: basement tersedia Ch.2
        ("vio",      "Vio",             4,  "USB Evidence Drive"),  # Ch.4: lab hanya tersedia Ch.4+
    ]

    REWARD_FLAGS = {
        'haikaru':  'haikaru_sidequest_done',
        'aolinh':   'aolinh_sidequest_done',
        'arganta':  'arganta_sidequest_done',
        'ignatius': 'ignatius_sidequest_done',
        'vio':      'vio_sidequest_done',
    }

    for npc_id, npc_name, min_ch, reward in NPC_LIST:
        sq_flag      = REWARD_FLAGS.get(npc_id, f"{npc_id}_sidequest_done")
        started_flag = f"sidequest_{npc_id}_started"
        met_flag     = f"met_{npc_id}"

        sq_done    = gs.story_flags.get(sq_flag, False)
        sq_started = gs.story_flags.get(started_flag, False)
        met        = gs.story_flags.get(met_flag, False)
        locked     = chapter < min_ch

        if sq_done:
            status_str = f"{Warna.HIJAU}✓ SELESAI{Warna.RESET}"
            reward_str = f"  → {Warna.HIJAU}{reward} diperoleh{Warna.RESET}"
        elif locked:
            status_str = f"{Warna.ABU_GELAP}⬜ Terbuka Ch.{min_ch}{Warna.RESET}"
            reward_str = f"  → {Warna.ABU_GELAP}Reward: {reward}{Warna.RESET}"
        elif not met:
            status_str = f"{Warna.ABU_GELAP}⬜ Belum bertemu{Warna.RESET}"
            reward_str = f"  → {Warna.ABU_GELAP}Reward: {reward}{Warna.RESET}"
        elif sq_started:
            status_str = f"{Warna.KUNING}◐ Dalam progress{Warna.RESET}"
            reward_str = f"  → {Warna.KUNING}Reward: {reward}{Warna.RESET}"
        else:
            status_str = f"{Warna.CYAN}○ Siap diterima{Warna.RESET}"
            reward_str = f"  → {Warna.CYAN}Reward: {reward}{Warna.RESET}"

        print(f"  {Warna.TERANG}{npc_name:<18}{Warna.RESET} {status_str}")
        print(f"{reward_str}")
        print()

    # Chapter unlock info
    print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}")
    print(f"  {Warna.KUNING}Syarat unlock chapter:{Warna.RESET}")
    print(f"  Ch.4: min 2 sidequest selesai")
    print(f"  Ch.6: min 4 sidequest + USB Evidence Drive")
    print()

    input(f"{Warna.ABU_GELAP}[ENTER untuk kembali]{Warna.RESET} ")

def tampilkan_party(gs):
    """Backward compat — redirect ke npc quest screen."""
    tampilkan_npc_quests(gs)

def save_menu(gs):
    # Core: Save Logic — show active slot, allow slot change before save
    clear_screen()
    try:
        from .gamestate import SLOT_FILES
        print(f"\n{Warna.CYAN}SIMPAN GAME{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}{'─' * (_tw() - 1)}{Warna.RESET}")
        print(f"  Slot aktif: {Warna.KUNING}Slot {gs.current_slot + 1} "
              f"({gs.get_slot_filename()}){Warna.RESET}\n")
        print(f"  [1] Simpan ke Slot {gs.current_slot + 1}")
        print(f"  [2] Ganti Slot Simpan")
        print(f"  [0] Batal\n")
        ch = input(f"{Warna.CYAN}Pilihan: {Warna.RESET}").strip()
        if ch == '0':
            return
        if ch == '2':
            # Inline slot picker
            for idx, fname in SLOT_FILES.items():
                try:
                    from .gamestate import GameState as _GS
                    tmp = _GS()
                    s = tmp.get_save_summary(fname)
                    label = (f"Lv.{s['level']} | {s['player']} | {s['playtime']}"
                             if s else "Kosong")
                except Exception:
                    label = "Kosong"
                mark = "◉" if idx == gs.current_slot else "○"
                print(f"  {mark} [{idx + 1}] Slot {idx + 1} — {label}")
            try:
                sel = int(input(f"\n{Warna.CYAN}Pilih slot (1-5): {Warna.RESET}").strip()) - 1
                if 0 <= sel <= 4:
                    gs.current_slot = sel
            except (ValueError, KeyboardInterrupt, EOFError):
                pass
        
        # Copy current settings to game state before saving
        try:
            from .settings import SETTINGS
            gs.settings = dict(SETTINGS)
        except (ImportError, AttributeError):
            pass
        
        sukses, msg = gs.save_to_file()
        print(f"\n{Warna.HIJAU if sukses else Warna.MERAH}{msg}{Warna.RESET}")
        if sukses:
            print(f"{Warna.ABU_GELAP}Tersimpan di Slot {gs.current_slot + 1}.{Warna.RESET}")
    except Exception as e:
        print(f"\n{Warna.MERAH}Simpan error: {e}{Warna.RESET}")
    time.sleep(2)

def konfirmasi_quit():
    try:
        print(f"\n{Warna.KUNING}Progress belum di-save akan hilang!{Warna.RESET}")
        confirm = input(f"{Warna.CYAN}Keluar? (y/n): {Warna.RESET}").strip().lower()
        return confirm == 'y'
    except (KeyboardInterrupt, EOFError):
        return True
