import random
import time
import shutil
import os
import sys
from collections import Counter
from itertools import combinations
from .sprites import Warna
from .characters import get_card_dialog
from .enemies import check_boss_phase

def _tw():
    """Terminal width saat ini."""
    return max(40, shutil.get_terminal_size(fallback=(80, 24)).columns)

try:
    from .utils import clear_screen, get_stat
except ImportError:
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_stat(obj, stat_name, default=None):
        """Fallback get_stat if utils not available"""
        return obj.get(stat_name) or obj.get('stats', {}).get(stat_name, default) or default

# Import unicode detection dari sprites
try:
    from .sprites import UNICODE_SUPPORTED
except ImportError:
    UNICODE_SUPPORTED = True

# Simbol suit kartu
if UNICODE_SUPPORTED:
    SUITS = ['♠', '♥', '♦', '♣']
    _SUIT_ASCII = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
else:
    SUITS = ['S', 'H', 'D', 'C']
    _SUIT_ASCII = {}

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}
RANK_VALUES['A'] = 14

# Kelas kartu
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __str__(self):
        # Warna berdasarkan suit — bekerja baik di Unicode maupun ASCII mode
        is_red = self.suit in ('♥', '♦', 'H', 'D')
        color  = Warna.MERAH if is_red else Warna.PUTIH
        return f"{color}{self.rank}{self.suit}{Warna.RESET}"

    def __repr__(self):
        return f"{self.rank}{self.suit}"

# Buat deck standar 52 kartu
def create_deck():
    """Create standard 52-card deck"""
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]

def refill_deck_if_needed(deck, discard_pile=None, min_cards=10):
    
    if len(deck) < min_cards:
        if discard_pile:
            random.shuffle(discard_pile)
            deck.extend(discard_pile)
            discard_pile.clear()
        else:
            new_deck = create_deck()
            random.shuffle(new_deck)
            deck.extend(new_deck)

def ensure_hand_size(hand, deck, discard_pile=None, target_size=5):
    
    refill_deck_if_needed(deck, discard_pile, min_cards=target_size * 2)
    while len(hand) < target_size:
        if deck:
            hand.append(deck.pop())
        else:
            break

# Evaluasi kombinasi kartu poker
def evaluate_hand(cards, allow_four_straight=False):
    
    if not cards:
        return ("Nothing", 0)

    if len(cards) <= 5:
        return _evaluate_five_card_hand(cards, allow_four_straight=allow_four_straight)
    
    # Find best 5-card combination if more than 5 cards
    best_hand = None
    best_score = -1
    
    for combo in combinations(cards, 5):
        hand_type, score = _evaluate_five_card_hand(list(combo))
        if score > best_score:
            best_score = score
            best_hand = (hand_type, score)
    
    # Juga cek 4-card combo jika allow_four_straight
    if allow_four_straight:
        for combo in combinations(cards, 4):
            hand_type, score = _evaluate_five_card_hand(list(combo), allow_four_straight=True)
            if score > best_score:
                best_score = score
                best_hand = (hand_type, score)
    
    return best_hand or ("Nothing", 0)

def _evaluate_five_card_hand(cards, allow_four_straight=False):
    
    if not cards:
        return ("Nothing", 0)
    
    # Validasi: semua kartu harus unik (tidak boleh kartu duplikat dari posisi yang sama)
    # Cek dengan membandingkan identitas objek kartu
    card_ids = [id(c) for c in cards]
    if len(card_ids) != len(set(card_ids)):
        # Ada kartu duplikat! Reject hand ini
        return ("Invalid Hand (Duplicate Cards)", 0)

    sorted_cards = sorted(cards, key=lambda c: c.value, reverse=True)
    values = [c.value for c in sorted_cards]

    rank_counter = Counter(c.rank for c in sorted_cards)
    counts = sorted(rank_counter.values(), reverse=True)

    unique_suits = set(c.suit for c in sorted_cards)
    is_flush = len(sorted_cards) >= 5 and len(unique_suits) == 1

    is_straight = False
    straight_high_value = 0
    
    # Validasi: harus kartu unik, tidak boleh duplikat
    unique_vals = sorted(set(values), reverse=True)
    
    min_straight_len = 4 if allow_four_straight and len(cards) == 4 else 5

    if len(unique_vals) >= min_straight_len:
        top_n = unique_vals[:min_straight_len]
        
        # Cek straight normal (n kartu berurutan)
        if top_n[0] - top_n[-1] == min_straight_len - 1:
            is_straight = True
            straight_high_value = top_n[0]
        # Cek Ace-low straight (A-2-3-4-5 atau A-2-3-4 untuk 4-card)
        elif min_straight_len == 5 and set(top_n) >= {14, 5, 4, 3, 2}:
            is_straight = True
            straight_high_value = 5
        elif min_straight_len == 4 and set(top_n) >= {14, 4, 3, 2}:
            is_straight = True
            straight_high_value = 4

    top_value = values[0] if values else 0

    if not counts:
        return ("High Card", top_value)

    if is_straight and is_flush:
        return ("Straight Flush", 800 + straight_high_value)
    elif counts[0] == 4:
        return ("Four of a Kind", 700 + top_value)
    elif len(counts) >= 2 and counts[0] == 3 and counts[1] == 2:
        return ("Full House", 600 + top_value)
    elif is_flush:
        return ("Flush", 500 + top_value)
    elif is_straight:
        return ("Straight", 400 + straight_high_value)
    elif counts[0] == 3:
        return ("Three of a Kind", 300 + top_value)
    elif len(counts) >= 2 and counts[0] == 2 and counts[1] == 2:
        return ("Two Pair", 200 + top_value)
    elif counts[0] == 2:
        return ("One Pair", 100 + top_value)
    else:
        return ("High Card", top_value)

# Hitung damage berdasarkan kombinasi kartu
def calculate_kerusakan(hand_type, hand_score, base_attack, level=1, is_enemy=False, defense=0):
    
    hand_multipliers = {
        "Straight Flush": 5.0,
        "Four of a Kind": 4.5,
        "Full House": 4.0,
        "Flush": 3.5,
        "Straight": 3.0,
        "Three of a Kind": 2.5,
        "Two Pair": 2.0,
        "One Pair": 1.5,
        "High Card": 1.2,
        "Nothing": 0.5,
    }
    multiplier = hand_multipliers.get(hand_type, 1.0)

    if is_enemy:
        # Musuh: damage dikunci supaya tidak terlalu brutal di awal
        level_factor = 1 + (level - 1) * 0.08
        raw = base_attack * multiplier * level_factor
        kerusakan = int(raw)
        kerusakan = max(8, min(kerusakan, 40))
    else:
        # Player: level scaling kuat — level 10 = ~3x, level 20 = ~5x
        level_factor = 1 + (level - 1) * 0.22
        kerusakan = int(base_attack * multiplier * level_factor)

    # Varians ±12%
    variance = max(1, int(kerusakan * 0.12))
    kerusakan = random.randint(max(4, kerusakan - variance), kerusakan + variance)

    # Defense % reduction: tiap 1 DEF = 1.8% pengurangan, max 70% reduction
    if defense > 0:
        reduction = min(0.70, defense * 0.018)
        kerusakan = int(kerusakan * (1.0 - reduction))

    min_dmg = 5 if is_enemy else 8
    return max(min_dmg, kerusakan)

def _strip_ansi_vis(s):
    """Hapus ANSI untuk hitung panjang teks yang terlihat."""
    import re as _re2
    return _re2.sub(r'\x1b\[[0-9;]*[mA-Za-z]', '', s)

def _vis_len(s):
    return len(_strip_ansi_vis(s))

def _pad_col(s, width):
    """Pad string s ke kanan sampai visible-width = width."""
    return s + ' ' * max(0, width - _vis_len(s))

# Tampilkan UI combat side-by-side
def show_combat_ui(player, enemy, overtime_progress=0, overtime_required=10, overtime_active=False, overtime_available=False):
    """Display combat UI SIDE-BY-SIDE: kolom MUSUH | kolom KAMU."""
    clear_screen()
    tw = _tw()

    # HEADER
    border = Warna.MERAH + '═' * (tw - 1) + Warna.RESET
    print(f"\n{border}")
    print(f"{Warna.MERAH + Warna.TERANG}{'  ⚔  PERTARUNGAN  ⚔'.center(tw - 1)}{Warna.RESET}")
    print(f"{border}\n")

    # Lebar tiap kolom
    col  = max(30, (tw - 3) // 2)
    bar  = max(10, col - 18)       # panjang HP/EN bar

    # KOLOM KIRI: MUSUH
    boss_tag  = f" {Warna.KUNING}[BOSS]{Warna.RESET}"  if enemy.get('boss')             else ""
    stun_tag  = f" {Warna.CYAN}[STUN]{Warna.RESET}"    if enemy.get('_stunned', 0) > 0  else ""
    e_debuffs = []
    if enemy.get('_def_debuff_turns', 0) > 0:
        e_debuffs.append(f"{Warna.KUNING}DEF↓{enemy['_def_debuff_turns']}t{Warna.RESET}")
    if enemy.get('_atk_debuff_turns', 0) > 0:
        e_debuffs.append(f"{Warna.KUNING}ATK↓{enemy['_atk_debuff_turns']}t{Warna.RESET}")
    deb = (" " + " ".join(e_debuffs)) if e_debuffs else ""

    left_lines = [
        f"{Warna.MERAH + Warna.TERANG}▶ MUSUH{Warna.RESET}{boss_tag}",
        f"  {Warna.TERANG}{enemy['name']}{Warna.RESET}{stun_tag}",
        f"  HP : {make_hp_bar(enemy['hp'], enemy['max_hp'], bar)} "
        f"{enemy['hp']}/{enemy['max_hp']}",
        f"  ATK:{enemy.get('attack','?')} DEF:{enemy.get('defense','?')}{deb}",
        "",
    ]

    # KOLOM KANAN: KAMU
    energy     = player.get('energy', 0)
    max_energy = player.get('max_energy', 30)
    p_atk      = get_stat(player, 'attack',  '?')
    p_def      = get_stat(player, 'defense', '?')
    p_spd      = get_stat(player, 'speed',   '?')

    # Buff tags
    buffs = player.get('_buffs', {})
    btags = []
    if buffs.get('atk_up', 0)         > 0: btags.append(f"{Warna.HIJAU}ATK↑{buffs['atk_up']}t{Warna.RESET}")
    if buffs.get('def_up', 0)         > 0: btags.append(f"{Warna.HIJAU}DEF↑{buffs['def_up']}t{Warna.RESET}")
    if buffs.get('evade', 0)          > 0: btags.append(f"{Warna.CYAN}DODGE{Warna.RESET}")
    if buffs.get('card_power_mult',0) > 0: btags.append(f"{Warna.UNGU}×{buffs['card_power_mult']}PWR{Warna.RESET}")
    if buffs.get('four_straight', 0)  > 0: btags.append(f"{Warna.CYAN}4STR{Warna.RESET}")
    if buffs.get('ambush_stun', 0)    > 0: btags.append(f"{Warna.UNGU}AMBUSH{Warna.RESET}")
    buff_str = " ".join(btags)

    # Overtime bar
    ot_fill = min(overtime_progress, overtime_required)
    ot_bar  = '▰' * ot_fill + '▱' * (overtime_required - ot_fill)
    if overtime_active:
        ot_label = f"{Warna.MERAH + Warna.TERANG}⚡AKTIF!{Warna.RESET}"
    elif overtime_available:
        ot_label = f"{Warna.KUNING}SIAP → ketik OT{Warna.RESET}"
    else:
        ot_label = f"{Warna.ABU_GELAP}{ot_fill}/{overtime_required}{Warna.RESET}"

    # Cooldowns (max 3 ditampilkan)
    cooldowns = player.get('_skill_cooldowns', {})
    active_cd = [(sk, cd) for sk, cd in cooldowns.items() if cd > 0]

    right_lines = [
        f"{Warna.HIJAU + Warna.TERANG}▶ KAMU{Warna.RESET}",
        f"  {Warna.TERANG}{player['name']}{Warna.RESET} (Lv.{player.get('level',1)})",
        f"  HP  : {make_hp_bar(player['hp'], player['max_hp'], bar)} "
        f"{player['hp']}/{player['max_hp']}",
        f"  {Warna.CYAN}EN  : {make_energy_bar(energy, max_energy, bar)} "
        f"{energy}/{max_energy}{Warna.RESET}",
        f"  ATK:{p_atk} DEF:{p_def} SPD:{p_spd}" + (f"  {buff_str}" if buff_str else ""),
        f"  {Warna.CYAN}OT:[{ot_bar}]{Warna.RESET} {ot_label}",
    ]
    if active_cd:
        cd_str = "  ".join(f"{Warna.ABU_GELAP}{sk[:8]}:{cd}t{Warna.RESET}"
                           for sk, cd in active_cd[:3])
        right_lines.append(f"  {Warna.ABU_GELAP}CD:{Warna.RESET} {cd_str}")

    # Render side-by-side
    div = f"{Warna.ABU_GELAP}│{Warna.RESET}"
    n   = max(len(left_lines), len(right_lines))
    for i in range(n):
        L = left_lines[i]  if i < len(left_lines)  else ""
        R = right_lines[i] if i < len(right_lines) else ""
        print(f"{_pad_col(L, col)} {div} {R}")

    print(f"\n{Warna.ABU_GELAP}{'─' * (tw - 1)}{Warna.RESET}")

def make_energy_bar(current, maximum, length=20):
    """Create energy bar untuk skill display — warna teal kalem."""
    if maximum <= 0:
        return f"{Warna.ABU_GELAP}{'░' * length}{Warna.RESET}"
    filled = max(0, min(int((current / maximum) * length), length))
    # Warna berdasarkan level energi
    if current >= maximum * 0.6:
        color = Warna.CYAN
    elif current >= maximum * 0.3:
        color = Warna.ABU_GELAP
    else:
        color = Warna.MERAH
    return f"{color}{'▪' * filled}{Warna.ABU_GELAP}{'░' * (length - filled)}{Warna.RESET}"

def _tick_buffs(player):
    """Kurangi durasi buff time-based tiap turn.
    Buff consume-on-use (card_power_mult, ambush_stun, four_straight, evade)
    tidak didecremen di sini — dikonsumsi saat kartu dimainkan."""
    CONSUME_ON_USE = {'card_power_mult', 'ambush_stun', 'four_straight', 'evade'}
    buffs = player.get('_buffs', {})
    for key in list(buffs.keys()):
        if key in CONSUME_ON_USE:
            continue
        if isinstance(buffs[key], int):
            buffs[key] -= 1
            if buffs[key] <= 0:
                del buffs[key]
    player['_buffs'] = buffs

def make_hp_bar(current, maximum, length=30):
    """Create HP bar"""
    filled = int((current / maximum) * length) if maximum else 0
    filled = max(0, min(length, filled))
    empty = length - filled
    
    if current > maximum * 0.6:
        color = Warna.HIJAU
    elif current > maximum * 0.3:
        color = Warna.KUNING
    else:
        color = Warna.MERAH
    
    bar = f"{color}{'█' * filled}{'░' * empty}{Warna.RESET}"
    return f"[{bar}]"

def _run_qte(timeout=1.8):
    """Quick Time Event saat musuh menyerang.
    Returns: 'a'=Blok, 'd'=Counter, None=gagal/timeout
    (Dodge 'S' dihapus — hanya Blok dan Counter tersedia)
    """
    bar_chars = int(timeout * 10)
    print(f"\n  {Warna.MERAH + Warna.TERANG}⚡ QTE! ▶ A=Blok(-75% dmg)  D=Counter(balik 40% serangan){Warna.RESET}")
    print(f"  {Warna.KUNING}Waktu: [{' ' * bar_chars}] ketik + Enter{Warna.RESET}", flush=True)

    try:
        if os.name == 'nt':
            import msvcrt
            deadline = time.time() + timeout
            buf = ''
            while time.time() < deadline:
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    try:
                        ch = ch.decode('utf-8').lower()
                    except Exception:
                        continue
                    if ch in ('\r', '\n'):
                        key = buf.strip().lower()
                        if key in ('a', 'd'):
                            return key
                        buf = ''
                    else:
                        buf += ch
                time.sleep(0.05)
        else:
            import select, termios, tty
            fd = sys.stdin.fileno()
            try:
                old = termios.tcgetattr(fd)
            except Exception:
                ans = input(f"  {Warna.CYAN}> {Warna.RESET}").strip().lower()
                return ans if ans in ('a', 'd') else None

            try:
                tty.setcbreak(fd)
                buf = ''
                deadline = time.time() + timeout
                while time.time() < deadline:
                    remaining = deadline - time.time()
                    r, _, _ = select.select([sys.stdin], [], [], min(0.1, remaining))
                    if r:
                        ch = sys.stdin.read(1)
                        if ch in ('\n', '\r'):
                            key = buf.strip().lower()
                            if key in ('a', 'd'):
                                termios.tcsetattr(fd, termios.TCSADRAIN, old)
                                return key
                            buf = ''
                        elif ch.lower() in ('a', 'd'):
                            buf = ch.lower()
            finally:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    pass
    except Exception:
        try:
            import signal
            def _alarm(*_): raise TimeoutError()
            old_handler = signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(int(timeout) + 1)
            try:
                ans = input(f"  {Warna.CYAN}> {Warna.RESET}").strip().lower()
                return ans if ans in ('a', 'd') else None
            except TimeoutError:
                return None
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        except Exception:
            return None
    return None


def _apply_qte_result(qte_key, enemy_kerusakan, player, enemy, combat_log, Warna=Warna):
    """Terapkan hasil QTE — kembalikan (damage_final, message, counter_dmg)."""
    counter_dmg = 0
    if qte_key == 'a':
        # Blok: kurangi 75% damage
        reduced = max(1, enemy_kerusakan // 4)
        msg = (f"{Warna.CYAN}⚡ QTE BLOK! Damage dikurangi 75%: "
               f"{enemy_kerusakan} → {reduced}{Warna.RESET}")
        combat_log.append(msg)
        return reduced, msg, 0
    elif qte_key == 'd':
        # Counter: balik 40% serangan musuh
        counter_dmg = max(5, int(enemy_kerusakan * 0.40))
        enemy['hp'] = max(0, enemy['hp'] - counter_dmg)
        msg = (f"{Warna.MERAH}⚡ QTE COUNTER! Kamu membalas {counter_dmg} damage!"
               f" Damage masuk: {enemy_kerusakan}{Warna.RESET}")
        combat_log.append(msg)
        return enemy_kerusakan, msg, counter_dmg
    else:
        msg = f"{Warna.MERAH}⚡ QTE MISS! Kena damage penuh!{Warna.RESET}"
        combat_log.append(msg)
        return enemy_kerusakan, msg, 0


def show_hand(hand, selectable=True):
    """Display hand with selection"""
    if not hand:
        print(f"  {Warna.ABU_GELAP}Tidak ada kartu{Warna.RESET}")
        return
    
    print(f"\n  {Warna.KUNING}KARTU ANDA:{Warna.RESET}")
    print("  ", end="")
    for i, card in enumerate(hand):
        if selectable:
            print(f"[{i}]{card} ", end="")
        else:
            print(f"{card} ", end="")
    print()

# Loop utama combat
def _show_boss_retry_menu(retries_left, boss_name, Warna=Warna):
    """Tampilkan menu retry/give up saat player kalah lawan boss."""
    print(f"\n{Warna.MERAH + Warna.TERANG}")
    print(f"  ╔══════════════════════════════════════════╗")
    print(f"  ║          ⚠  KALAH DARI BOSS...          ║")
    print(f"  ╚══════════════════════════════════════════╝")
    print(f"{Warna.RESET}")
    print(f"  {Warna.MERAH}Kamu dikalahkan oleh {boss_name}.{Warna.RESET}")
    print(f"  {Warna.KUNING}Retry tersisa: {retries_left}/3{Warna.RESET}\n")
    print(f"  {Warna.HIJAU}[1] RETRY{Warna.RESET}  — Ulang pertarungan (HP dipulihkan 70%)")
    print(f"  {Warna.MERAH}[2] GIVE UP{Warna.RESET} — Mundur ke Checkpoint terakhir\n")
    while True:
        try:
            ch = input(f"  {Warna.PUTIH}Pilihan (1/2): {Warna.RESET}").strip()
            if ch == '1':
                return 'retry'
            elif ch == '2':
                return 'give_up'
        except (KeyboardInterrupt, EOFError):
            return 'give_up'

def run_combat(player_stats, enemy_data, inventory):
    """Card-based combat system dengan Boss Retry (max 3x) dan Checkpoint support."""
    import copy

    is_boss = enemy_data.get('boss', False)
    MAX_RETRIES = 3
    retries_left = MAX_RETRIES

    # SNAPSHOT sebelum boss untuk retry / checkpoint
    # Snapshot menyimpan: HP, energy, dan salinan inventory
    # Retry     → restore HP saja (partial)
    # Give Up / retries habis → full restore (HP + inventory) → return 'checkpoint'
    if is_boss:
        snap_hp        = player_stats.get('hp', player_stats.get('max_hp', 100))
        snap_energy    = player_stats.get('energy', 30)
        snap_inventory = list(inventory)

    # OUTER RETRY LOOP
    while True:
        result = _run_single_combat(player_stats, enemy_data, inventory)

        if result != 'player_dead' or not is_boss:
            return result

        # Player mati lawan boss
        boss_name = enemy_data.get('name', 'Boss')

        if retries_left > 0:
            retries_left -= 1
            choice = _show_boss_retry_menu(retries_left, boss_name)

            if choice == 'retry':
                # Partial restore: HP ke 70% max (bukan full, ada konsekuensi)
                max_hp = player_stats.get('max_hp', 100)
                player_stats['hp']     = max(1, int(max_hp * 0.70))
                player_stats['energy'] = snap_energy
                # Bersihkan buff/debuff sisa
                player_stats['_buffs'] = {}
                player_stats['_skill_cooldowns'] = {}
                print(f"\n  {Warna.HIJAU}HP dipulihkan ke {player_stats['hp']}/{max_hp}. "
                      f"Bersiap ulang!{Warna.RESET}")
                time.sleep(1.5)
                continue   # ulang combat loop
            else:
                # Give Up → full checkpoint restore
                player_stats['hp']     = max(1, snap_hp)
                player_stats['energy'] = snap_energy
                player_stats['_buffs'] = {}
                player_stats['_skill_cooldowns'] = {}
                inventory.clear()
                inventory.extend(snap_inventory)
                print(f"\n  {Warna.KUNING}Mundur ke Checkpoint terakhir...{Warna.RESET}")
                time.sleep(1.5)
                return 'checkpoint'
        else:
            # Retries habis → paksa checkpoint
            player_stats['hp']     = max(1, snap_hp)
            player_stats['energy'] = snap_energy
            player_stats['_buffs'] = {}
            player_stats['_skill_cooldowns'] = {}
            inventory.clear()
            inventory.extend(snap_inventory)
            print(f"\n{Warna.MERAH + Warna.TERANG}")
            print(f"  ╔══════════════════════════════════════════╗")
            print(f"  ║   ❌ RETRY HABIS — KEMBALI KE CHECKPOINT ║")
            print(f"  ╚══════════════════════════════════════════╝")
            print(f"{Warna.RESET}")
            print(f"  {Warna.KUNING}Inventory dipulihkan ke kondisi sebelum battle.{Warna.RESET}")
            time.sleep(2)
            return 'checkpoint'


def _trigger_boss_phase_if_needed(enemy, combat_log):
    """Check for boss phase transitions and display the cinematic sequence if
    a new phase just triggered.  Mutates enemy in-place.  Safe to call on any
    enemy — check_boss_phase() returns None for non-bosses."""
    phase_info = check_boss_phase(enemy)
    if phase_info is None:
        return

    new_phase = phase_info['new_phase']
    dialog    = phase_info['dialog']
    heal      = phase_info['heal']
    atk_mult  = phase_info['atk_mult']
    def_mult  = phase_info['def_mult']

    border = Warna.MERAH + ('=' * 46) + Warna.RESET
    print(f"\n{border}")
    if new_phase == 2:
        print(f"{Warna.KUNING + Warna.TERANG}  ⚠  PHASE 2 — ENRAGED  ⚠{Warna.RESET}")
    else:
        print(f"{Warna.MERAH + Warna.TERANG}  !! PHASE {new_phase} — DESPERATE !!{Warna.RESET}")
    print(border)

    for line in dialog:
        if line:
            print(f"\n  {Warna.KUNING + Warna.TERANG}{line}{Warna.RESET}")
            time.sleep(0.9)
        else:
            print()

    print(f"\n  {Warna.MERAH}[PHASE {new_phase}] ATK x{atk_mult:.2f}  DEF x{def_mult:.2f}{Warna.RESET}")
    if heal > 0:
        print(f"  {Warna.HIJAU}[PHASE {new_phase}] Boss memulihkan {heal} HP!{Warna.RESET}")

    log_msg = (f"{Warna.MERAH}★ {enemy['name']} masuk PHASE {new_phase}! "
               f"ATK dan DEF meningkat!{Warna.RESET}")
    combat_log.append(log_msg)
    print(f"\n{border}\n")
    time.sleep(1.5)


def _run_single_combat(player_stats, enemy_data, inventory):
    """Internal: satu sesi combat (dipanggil oleh run_combat dengan retry wrapper)."""
    import copy
    
    # Gunakan player_stats langsung (BUKAN deepcopy) supaya HP
    # otomatis ter-sync balik ke caller setelah combat selesai.
    player = player_stats
    enemy = copy.deepcopy(enemy_data)
    
    # Initialize buffs at start
    player['_buffs'] = {}
    if enemy:
        enemy['_buffs'] = {}

    if 'hp' not in player:
        player['hp'] = player['max_hp']
    if 'hp' not in enemy:
        enemy['hp'] = enemy.get('max_hp', 100)
    


    deck = create_deck()
    random.shuffle(deck)
    discard_pile = []  # Tumpukan kartu yang sudah dibuang

    # Sistem Discard Slot
    # Tiap combat ada 3 slot discard. 1 aksi discard = 1 slot habis.
    # Per aksi bisa buang 1-5 kartu sekaligus.
    # Bonus token bisa dibeli dari toko Bran Edwards.
    MAX_DISCARD_SLOTS  = 3
    bonus_tokens       = player_stats.get('bonus_discard_tokens', 0)
    discard_remaining  = MAX_DISCARD_SLOTS + bonus_tokens

    # Hitung speed DULU sebelum deal kartu
    player_speed = get_stat(player, 'speed', 10)
    enemy_speed  = get_stat(enemy,  'speed', 10)
    player_turn_first = player_speed >= enemy_speed

    speed_ratio        = player_speed / max(enemy_speed, 1)
    player_extra_cards = 0
    if speed_ratio >= 2.0:
        player_extra_cards = 2
    elif speed_ratio >= 1.5:
        player_extra_cards = 1

    player_dodge_base = min(0.35, 0.10 + (player_speed - 10) * 0.01)
    if player_dodge_base < 0.05:
        player_dodge_base = 0.05

    player_hand = []
    enemy_hand  = []

    ensure_hand_size(player_hand, deck, target_size=8)
    ensure_hand_size(enemy_hand,  deck, target_size=8)

    if player_extra_cards > 0:
        for _ in range(player_extra_cards):
            if deck:
                player_hand.append(deck.pop())
        print(f"\n  {Warna.CYAN}⚡ Kecepatan lebih tinggi! +{player_extra_cards} kartu awal!{Warna.RESET}")
        time.sleep(1)

    turn = 1
    combat_log = []

    # Bar overtime terisi setiap player mainkan kartu (bukan skill/discard/pass)
    # Setelah 10 turn attack → bar penuh → player bisa aktifkan OVERTIME mode
    # OVERTIME: 2 turn kebal serangan + damage ×1.75 + bisa main 2 combo hand sekaligus
    OVERTIME_REQUIRED   = 10     # Turn attack yang dibutuhkan (naik dari 8)
    overtime_progress   = 0      # Current attack turns
    overtime_active     = False  # Mode overtime sedang aktif
    overtime_turns_left = 0      # Sisa turn overtime
    overtime_available  = False  # Bar penuh, siap diaktifkan

    player['hp'] = player.get('hp', player.get('max_hp', 100))
    player['max_hp'] = player.get('max_hp', 100)

    # Main combat loop
    MAX_TURNS = 100

    while player['hp'] > 0 and enemy['hp'] > 0 and turn <= MAX_TURNS:

        # Pastikan kedua tangan punya kartu cukup
        ensure_hand_size(player_hand, deck, target_size=5)
        ensure_hand_size(enemy_hand, deck, target_size=5)
        
        show_combat_ui(player, enemy,
                       overtime_progress=overtime_progress,
                       overtime_required=OVERTIME_REQUIRED,
                       overtime_active=overtime_active,
                       overtime_available=overtime_available)
        
        # Tampilkan history 3 aksi terbaru
        if combat_log:
            print(f"\n  {Warna.ABU_GELAP}Baru-baru ini:{Warna.RESET}")
            for log_entry in combat_log[-3:]:
                print(f"  {log_entry}")
        
        print(f"\n{Warna.KUNING}═══════════════════════════════════════{Warna.RESET}")
        print(f"  {Warna.KUNING + Warna.TERANG}TURN {turn}{Warna.RESET}")
        print(f"{Warna.KUNING}═══════════════════════════════════════{Warna.RESET}")
        
        show_hand(player_hand)
        
        # Hitung warna slot discard
        slot_color = Warna.HIJAU if discard_remaining > 1 else (Warna.KUNING if discard_remaining == 1 else Warna.MERAH)
        slot_bar   = f"{'■' * discard_remaining}{'□' * (MAX_DISCARD_SLOTS - discard_remaining)}"

        print(f"\n  {Warna.PUTIH}═══ AKSI TERSEDIA ═══{Warna.RESET}")
        print(f"  {Warna.HIJAU}[0,1,2,...]{Warna.RESET} Mainkan kartu  {Warna.ABU_GELAP}(contoh: '0,2,4' = 3 kartu sekaligus){Warna.RESET}")
        print(f"  {slot_color}[D 0,1,2]{Warna.RESET} Buang & ganti kartu  "
              f"{slot_color}[{slot_bar}] {discard_remaining} discard tersisa{Warna.RESET}")
        print(f"  {Warna.CYAN}[S]{Warna.RESET} Skill  {Warna.KUNING}[I]{Warna.RESET} Barang  "
              f"{Warna.ABU_GELAP}[P]{Warna.RESET} Skip (+4 EN)  {Warna.MERAH}[F]{Warna.RESET} Kabur")
        if overtime_available and not overtime_active:
            print(f"  {Warna.KUNING + Warna.TERANG}[OT] ⚡ AKTIFKAN OVERTIME! {Warna.RESET}"
                  f"{Warna.ABU_GELAP}(Kebal 2t + Damage ×1.75 + 2 Combo Hand){Warna.RESET}")
        
        action = input(f"\n  {Warna.PUTIH}> {Warna.RESET}").strip().upper()
        
        kerusakan_dealt = 0
        action_taken = ""
        skip_enemy_turn = False  # Skill & Discard tidak trigger giliran musuh
        
        if action == 'F':
            is_boss_fight = enemy.get('boss', False)
            
            if is_boss_fight:
                print(f"\n  {Warna.MERAH + Warna.TERANG}⚠ Musuh adalah BOSS!{Warna.RESET}")
                print(f"  {Warna.MERAH}Peluang kabur: 5% berhasil, 95% GAGAL!{Warna.RESET}")
            else:
                print(f"\n  {Warna.KUNING}Mencoba kabur...{Warna.RESET}")
            
            time.sleep(1)
            
            flee_success_rate = 0.05 if is_boss_fight else 0.25
            
            if random.random() < flee_success_rate:
                print(f"  {Warna.HIJAU}✓ Berhasil kabur{Warna.RESET}")
                time.sleep(1.5)
                return 'fled'
            else:
                # Gagal kabur, ambil damage
                flee_kerusakan = 15
                player['hp'] -= flee_kerusakan
                print(f"  {Warna.MERAH}✗ Gagal kabur! Kena {flee_kerusakan} kerusakan{Warna.RESET}")
                combat_log.append(f"{Warna.MERAH}Gagal kabur: -{flee_kerusakan} HP{Warna.RESET}")
                time.sleep(1.5)
                
                if player['hp'] <= 0:
                    break
                continue
        
        if action == 'P':
            # Skip giliran — regen energy
            en_gain = 4
            player['energy'] = min(player.get('max_energy', 30), player.get('energy', 0) + en_gain)
            action_taken = f"{Warna.ABU_GELAP}Lewati giliran (+{en_gain} EN){Warna.RESET}"
            combat_log.append(action_taken)

        elif action == 'OT':
            # AKTIFKAN OVERTIME
            if not overtime_available:
                print(f"\n  {Warna.MERAH}Overtime bar belum penuh! ({overtime_progress}/{OVERTIME_REQUIRED} attack turn){Warna.RESET}")
                time.sleep(1.5)
                continue
            if overtime_active:
                print(f"\n  {Warna.KUNING}Overtime sudah aktif! ({overtime_turns_left} turn tersisa){Warna.RESET}")
                time.sleep(1.2)
                continue
            # Aktifkan overtime
            overtime_active     = True
            overtime_available  = False
            overtime_progress   = 0
            overtime_turns_left = 2
            skip_enemy_turn     = True  # Aktivasi overtime tidak memicu giliran musuh
            action_taken = (f"{Warna.MERAH + Warna.TERANG}⚡ OVERTIME AKTIF! "
                            f"Kebal 2t + Damage ×1.75 + Bisa main 2 combo hand!{Warna.RESET}")
            combat_log.append(action_taken)
            print(f"\n  {action_taken}")
            time.sleep(1.5)
        
        elif action.startswith('D '):
            # Cek sisa slot discard
            if discard_remaining <= 0:
                print(f"\n  {Warna.MERAH}Slot discard habis! ({MAX_DISCARD_SLOTS}/{MAX_DISCARD_SLOTS} sudah terpakai){Warna.RESET}")
                time.sleep(1.5)
                continue

            try:
                indices_str = action[2:].strip()
                indices = [int(x.strip()) for x in indices_str.split(',')]
                indices = list(dict.fromkeys(indices))           # hapus duplikat
                indices = [i for i in indices if 0 <= i < len(player_hand)]
                indices = indices[:5]                            # max 5 kartu per aksi

                if not indices:
                    print(f"\n  {Warna.MERAH}Pilihan kartu salah (masukkan indeks 0-{len(player_hand)-1}){Warna.RESET}")
                    time.sleep(1)
                    continue

                discarded_count = 0
                for i in sorted(indices, reverse=True):
                    if i < len(player_hand):
                        player_hand.pop(i)
                        discarded_count += 1

                refill_deck_if_needed(deck, discard_pile)
                for _ in range(discarded_count):
                    if deck:
                        player_hand.append(deck.pop())
                ensure_hand_size(player_hand, deck, discard_pile, target_size=3)

                discard_remaining -= 1           # ← pakai 1 slot
                sisa = discard_remaining
                slot_info = (f"{Warna.HIJAU}{sisa} slot tersisa{Warna.RESET}" if sisa > 0
                             else f"{Warna.MERAH}slot habis!{Warna.RESET}")
                action_taken = (f"{Warna.KUNING}Buang {discarded_count} kartu, ambil baru "
                                f"[{slot_info}]{Warna.RESET}")
                combat_log.append(action_taken)
                skip_enemy_turn = True  # Discard tidak melanjutkan giliran musuh

            except (ValueError, IndexError):
                print(f"\n  {Warna.MERAH}Input salah (contoh: D 0,1,2){Warna.RESET}")
                time.sleep(1)
                continue
        
        elif action == 'S':
            # SKILL — pakai ENERGI + COOLDOWN system
            skills = list(player.get('skills', {}).values())
            if not skills:
                print(f"\n  {Warna.MERAH}Tidak ada skill tersedia!{Warna.RESET}")
                time.sleep(1.8)
                continue

            clear_screen()
            energy     = player.get('energy', 30)
            max_energy = player.get('max_energy', 30)
            energy_bar = make_energy_bar(energy, max_energy, 28)
            cooldowns  = player.setdefault('_skill_cooldowns', {})

            print(f"\n{Warna.CYAN}{'═'*62}{Warna.RESET}")
            print(f"  {Warna.CYAN + Warna.TERANG}⚡  SKILL  —  {player['name']}{Warna.RESET}")
            print(f"  ENERGI: [{energy_bar}] {energy}/{max_energy}")
            print(f"{Warna.CYAN}{'═'*62}{Warna.RESET}\n")

            for i, skill in enumerate(skills, 1):
                e_cost   = skill.get('energy_cost', skill.get('cost', 10))
                sk_cd    = skill.get('cooldown', 0)
                cur_cd   = cooldowns.get(skill['name'], 0)
                can_use  = energy >= e_cost and cur_cd <= 0

                sk_type  = skill.get('type', 'support')
                type_col = {
                    'heal': Warna.HIJAU, 'buff': Warna.CYAN,
                    'debuff': Warna.KUNING, 'special': Warna.UNGU,
                }.get(sk_type, Warna.PUTIH)

                cost_col = Warna.HIJAU if energy >= e_cost else Warna.MERAH
                cd_str   = (f"{Warna.MERAH}[CD: {cur_cd} turn]{Warna.RESET}" if cur_cd > 0
                            else f"{Warna.HIJAU}[Siap]{Warna.RESET}")

                print(f"  {Warna.CYAN}[{i}]{Warna.RESET} {Warna.TERANG}{skill['name']}{Warna.RESET}"
                      f"  {type_col}[{sk_type.upper()}]{Warna.RESET}"
                      f"  EN:{cost_col}{e_cost}{Warna.RESET}"
                      f"  CD:{sk_cd} turn  {cd_str}")
                desc_full = skill['desc']
                print(f"      {Warna.ABU_GELAP}{desc_full}{Warna.RESET}")
                print()

            print(f"  {Warna.ABU_GELAP}[0] Kembali{Warna.RESET}")
            choice = input(f"\n  {Warna.PUTIH}Pilih skill (atau 0 batal): {Warna.RESET}").strip()

            try:
                idx = int(choice)
                if idx == 0:
                    continue
                if not (1 <= idx <= len(skills)):
                    print(f"\n  {Warna.MERAH}Pilihan tidak valid.{Warna.RESET}")
                    time.sleep(1)
                    continue

                skill   = skills[idx - 1]
                e_cost  = skill.get('energy_cost', skill.get('cost', 10))
                cur_cd  = cooldowns.get(skill['name'], 0)
                effect  = skill.get('effect', 'heal_self')
                power   = skill.get('power', 0)
                p_atk   = get_stat(player, 'attack', 10)

                # Cek cooldown
                if cur_cd > 0:
                    print(f"\n  {Warna.MERAH}Skill masih cooldown! Tunggu {cur_cd} giliran lagi.{Warna.RESET}")
                    time.sleep(1.8)
                    continue

                # Cek energi
                if player.get('energy', 0) < e_cost:
                    print(f"\n  {Warna.MERAH}Energi tidak cukup! "
                          f"Butuh {e_cost} EN, punya {player.get('energy', 0)} EN.{Warna.RESET}")
                    time.sleep(2)
                    continue

                # Kurangi energi & set cooldown
                player['energy'] = max(0, player.get('energy', 0) - e_cost)
                cooldowns[skill['name']] = skill.get('cooldown', 0)

                # Implementasi efek skill
                buffs = player.setdefault('_buffs', {})

                # HEAL
                if effect in ('heal', 'heal_self'):
                    lv_bonus = skill.get('level_bonus', 5)
                    heal = max(20, power + lv_bonus)
                    player['hp'] = min(player['max_hp'], player['hp'] + heal)
                    action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                    f"+{heal} HP dipulihkan!{Warna.RESET}")

                # HEAL + ENERGY regen (Arganta survival)
                elif effect == 'heal_energy':
                    heal = max(15, power + skill.get('level_bonus', 4))
                    en_gain = max(15, 25)
                    player['hp'] = min(player['max_hp'], player['hp'] + heal)
                    player['energy'] = min(max_energy, player.get('energy', 0) + en_gain)
                    action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                    f"+{heal} HP + "
                                    f"{Warna.CYAN}+{en_gain} EN!{Warna.RESET}")

                # HEAL + CLEANSE debuff (Ignatius repair)
                elif effect == 'heal_cleanse':
                    heal = max(20, power + skill.get('level_bonus', 8))
                    player['hp'] = min(player['max_hp'], player['hp'] + heal)
                    # Bersihkan debuff
                    for bad_key in ['_poisoned', '_stunned_self']:
                        buffs.pop(bad_key, None)
                    action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                    f"+{heal} HP + {Warna.CYAN}debuff dibersihkan!{Warna.RESET}")

                # ATK BUFF (Haikaru focus mind, Ignatius overclock base)
                elif effect == 'buff_attack':
                    buffs['atk_up'] = 2
                    action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                    f"ATK +50% selama 2 giliran!{Warna.RESET}")

                # ATK BUFF + ENERGY (Ignatius overclock)
                # en_gain dibatasi +12 (flat recovery) agar tidak infinite loop:
                # Overclock biaya 6 EN, regen 12 EN → net +6 EN max, bukan full restore
                elif effect == 'buff_atk_energy':
                    buffs['atk_up'] = 2
                    en_gain = 12   # FIX: dikurangi dari 20 → 12 (cegah spam loop)
                    player['energy'] = min(max_energy, player.get('energy', 0) + en_gain)
                    action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                    f"ATK +50% 2t + "
                                    f"{Warna.CYAN}+{en_gain} EN!{Warna.RESET}")

                # ATK BUFF + small HEAL (Aolinh rhythm boost)
                elif effect == 'buff_atk_heal':
                    buffs['atk_up'] = 3
                    heal = 20
                    player['hp'] = min(player['max_hp'], player['hp'] + heal)
                    action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                    f"ATK +50% 3t + {Warna.HIJAU}+{heal} HP!{Warna.RESET}")

                # DEF BUFF (Aolinh shield)
                elif effect == 'buff_defense':
                    buffs['def_up'] = 3
                    action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                    f"DEF +50% selama 3 giliran!{Warna.RESET}")

                # EVASION BUFF (Arganta shadow step)
                elif effect == 'buff_evade':
                    buffs['evade'] = 1
                    action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                    f"Dodge 20% → 70% selama 1 giliran!{Warna.RESET}")

                # DEF DEBUFF enemy (Vio exploit_code: power damage + DEF debuff)
                elif effect == 'debuff_defense':
                    enemy.setdefault('_orig_def', enemy.get('defense', 5))
                    old_def = enemy.get('defense', 5)
                    # Exploit Code: 60% DEF reduction. System Hack (legacy): 50%
                    reduction = 0.40 if power > 0 else 0.50
                    pct_str   = "60" if power > 0 else "50"
                    enemy['defense'] = max(0, int(old_def * reduction))
                    enemy['_def_debuff_turns'] = 3
                    action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                    f"DEF musuh -{pct_str}% selama 3 giliran!{Warna.RESET}")
                    # Bonus direct damage jika power > 0 (Exploit Code)
                    if power > 0:
                        enemy_def = max(0, enemy.get('defense', 5))  # Already reduced
                        direct_dmg = max(1, power - enemy_def)
                        enemy['hp'] -= direct_dmg
                        action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                        f"{Warna.MERAH}-{direct_dmg} DMG{Warna.KUNING} + "
                                        f"DEF musuh -{pct_str}% selama 3 giliran!{Warna.RESET}")

                # ATK DEBUFF enemy (Vio signal jam, Arganta scout mark)
                elif effect == 'debuff_attack':
                    enemy.setdefault('_orig_atk', enemy.get('attack', 15))
                    old_atk = enemy.get('attack', 15)
                    pct = 0.55 if 'scout' in skill['name'].lower() else 0.60
                    pct_str = "45" if 'scout' in skill['name'].lower() else "40"
                    enemy['attack'] = max(1, int(old_atk * pct))
                    enemy['_atk_debuff_turns'] = 3
                    action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                    f"ATK musuh -{pct_str}% selama 3 giliran!{Warna.RESET}")

                # DEF + ATK DEBUFF combined (Haikaru pattern analysis)
                elif effect == 'debuff_def_atk':
                    enemy.setdefault('_orig_def', enemy.get('defense', 5))
                    enemy.setdefault('_orig_atk', enemy.get('attack', 15))
                    old_def = enemy.get('defense', 5)
                    old_atk = enemy.get('attack', 15)
                    enemy['defense'] = max(0, int(old_def * 0.65))
                    enemy['attack']  = max(1, int(old_atk * 0.80))
                    enemy['_def_debuff_turns'] = 2
                    enemy['_atk_debuff_turns'] = 2
                    action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                    f"DEF musuh -35% + ATK musuh -20% selama 2 giliran!{Warna.RESET}")

                # STUN enemy (Ignatius EMP, Vio zero_day_strike)
                elif effect == 'stun_enemy':
                    enemy['_stunned'] = 1
                    action_taken = (f"{Warna.UNGU}⚡ {skill['name']}: "
                                    f"STUN! Musuh skip serangan 1 giliran!{Warna.RESET}")
                    # Bonus direct damage jika power > 0 (Zero-Day Strike)
                    if power > 0:
                        enemy_def = max(0, enemy.get('defense', 5))
                        direct_dmg = max(1, power - enemy_def)
                        enemy['hp'] -= direct_dmg
                        action_taken = (f"{Warna.UNGU}⚡ {skill['name']}: "
                                        f"{Warna.MERAH}-{direct_dmg} DMG{Warna.UNGU} + "
                                        f"STUN! Musuh skip 1 giliran!{Warna.RESET}")

                # RISK/REWARD (Haikaru gambit)
                elif effect == 'power_up':
                    hp_cost = 20
                    en_gain = 30
                    player['hp'] = max(1, player['hp'] - hp_cost)
                    buffs['atk_up'] = 2
                    player['energy'] = min(max_energy, player.get('energy', 0) + en_gain)
                    action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                    f"-{hp_cost} HP → ATK +50% 2t + "
                                    f"{Warna.CYAN}+{en_gain} EN!{Warna.RESET}")

                # ATK + DEF BUFF (Vio ssr_pity_break)
                elif effect == 'buff_atk_def':
                    buffs['atk_up'] = 3   # 3 turns (duration_turns dari skill)
                    buffs['def_up'] = 3
                    action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                    f"SSR PULL! {Warna.CYAN}ATK +60%{Warna.KUNING} + "
                                    f"{Warna.HIJAU}DEF +40%{Warna.KUNING} selama 3 giliran!{Warna.RESET}")

                # RANDOM BUFF (Vio gacha — legacy, digantikan SSR Pity Break)
                elif effect == 'gacha_buff':
                    roll = random.random()
                    if roll < 0.25:
                        buffs['atk_up'] = 3
                        action_taken = (f"{Warna.KUNING}⚡ {skill['name']}: "
                                        f"ATK PULL! ATK +45% 3 giliran!{Warna.RESET}")
                    elif roll < 0.50:
                        buffs['def_up'] = 3
                        action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                        f"DEF PULL! DEF +45% 3 giliran!{Warna.RESET}")
                    elif roll < 0.75:
                        heal = 40
                        player['hp'] = min(player['max_hp'], player['hp'] + heal)
                        action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                        f"HEAL PULL! +{heal} HP!{Warna.RESET}")
                    else:
                        en_gain = 35
                        player['energy'] = min(max_energy, player.get('energy', 0) + en_gain)
                        action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                        f"ENERGY PULL! +{en_gain} EN!{Warna.RESET}")

                # Skill berbasis KARTU (baru)

                # DOUBLE CARD DAMAGE — hand berikutnya 2× damage (Vio: Data Overload)
                elif effect == 'buff_card_power':
                    buffs['card_power_mult'] = 2  # Dikonsumsi saat main kartu
                    action_taken = (f"{Warna.UNGU}⚡ {skill['name']}: "
                                    f"KRITIS KARTU! Damage hand berikutnya ×2!{Warna.RESET}")

                # AMBUSH — next card 2× damage + stun musuh (Arganta: Ambush Strike)
                elif effect == 'buff_ambush':
                    buffs['card_power_mult'] = 2
                    buffs['ambush_stun'] = 1   # Jika hand berikutnya mengenai, musuh stun
                    action_taken = (f"{Warna.UNGU}⚡ {skill['name']}: "
                                    f"AMBUSH! Kartu berikutnya ×2 + STUN musuh!{Warna.RESET}")

                # OVERLOAD — next card 2× damage tapi bayar HP (Ignatius: Power Surge)
                # Data Bomb (Vio) pakai ×3 multiplier dengan HP cost 10
                elif effect == 'buff_overload':
                    skill_name_lower = skill.get('name', '').lower()
                    if 'data bomb' in skill_name_lower or 'data_bomb' in skill_name_lower:
                        hp_cost = 10
                        mult = 3
                    else:
                        hp_cost = 15
                        mult = 2
                    player['hp'] = max(1, player['hp'] - hp_cost)
                    buffs['card_power_mult'] = mult
                    action_taken = (f"{Warna.MERAH}⚡ {skill['name']}: "
                                    f"-{hp_cost} HP → Kartu berikutnya ×{mult} damage!{Warna.RESET}")

                # FOUR-CARD STRAIGHT — hand berikutnya bisa Straight dengan 4 kartu (Haikaru)
                elif effect == 'buff_four_straight':
                    buffs['four_straight'] = 1
                    action_taken = (f"{Warna.CYAN}⚡ {skill['name']}: "
                                    f"ANALISIS POLA! Hand berikutnya: Straight bisa 4 kartu!{Warna.RESET}")

                # REFRESH DISCARD — pulihkan 1 slot discard + draw 2 kartu ekstra (Aolinh)
                elif effect == 'refresh_discard':
                    slots_recovered = min(1, MAX_DISCARD_SLOTS - discard_remaining)
                    discard_remaining = min(MAX_DISCARD_SLOTS, discard_remaining + 1)
                    # Draw 2 kartu ekstra
                    extra_drawn = 0
                    refill_deck_if_needed(deck, discard_pile)
                    for _ in range(2):
                        if deck:
                            player_hand.append(deck.pop())
                            extra_drawn += 1
                    action_taken = (f"{Warna.HIJAU}⚡ {skill['name']}: "
                                    f"+1 slot discard + draw {extra_drawn} kartu ekstra!{Warna.RESET}")

                else:
                    # Fallback: heal kecil
                    heal = max(10, power)
                    player['hp'] = min(player['max_hp'], player['hp'] + heal)
                    action_taken = f"{Warna.HIJAU}⚡ {skill['name']}: +{heal} HP{Warna.RESET}"

                combat_log.append(action_taken)
                print(f"\n  {action_taken}")
                time.sleep(1.2)
                skip_enemy_turn = True  # Skill tidak melanjutkan giliran musuh

            except (ValueError, IndexError, KeyError) as err:
                print(f"\n  {Warna.MERAH}Input salah: {err}{Warna.RESET}")
                time.sleep(1)
                continue
        
        elif action == 'I':
            clear_screen()
            print(f"\n{Warna.KUNING}═══════════════════════════════════════{Warna.RESET}")
            print(f"  {Warna.KUNING + Warna.TERANG}ITEMS{Warna.RESET}")
            print(f"{Warna.KUNING}═══════════════════════════════════════{Warna.RESET}\n")

            # Fix: HUD Update — hanya tampilkan item biasa (bukan quest items) di combat
            from .constants import QUEST_ITEM_NAMES
            usable_items = [it for it in inventory if it not in QUEST_ITEM_NAMES]

            if not usable_items:
                print(f"  {Warna.ABU_GELAP}Tidak ada barang yang bisa dipakai{Warna.RESET}")
                time.sleep(1)
                continue

            for i, item in enumerate(usable_items, 1):
                print(f"  {Warna.KUNING}[{i}]{Warna.RESET} {item}")

            print(f"\n  {Warna.ABU_GELAP}[0] Kembali{Warna.RESET}")

            item_choice = input(f"\n  {Warna.PUTIH}Pilih barang: {Warna.RESET}").strip()

            try:
                idx = int(item_choice)
                if idx == 0:
                    continue
                if 1 <= idx <= len(usable_items):
                    item = usable_items[idx - 1]
                    inventory.remove(item)

                    if "Health" in item or "Healing" in item:
                        heal = 50
                        player['hp'] = min(player['max_hp'], player['hp'] + heal)
                        action_taken = f"{Warna.HIJAU}Pakai {item}: +{heal} HP{Warna.RESET}"
                    elif "Explosive" in item:
                        kerusakan_dealt = 40
                        enemy['hp'] -= kerusakan_dealt
                        action_taken = f"{Warna.MERAH}💥 Pakai {item}: {kerusakan_dealt} damage langsung!{Warna.RESET}"
                    elif "Energy Drink" in item:
                        buffs['atk_up'] = 2
                        action_taken = f"{Warna.CYAN}⚡ Pakai {item}: ATK +50% selama 2 turn!{Warna.RESET}"
                    elif "Armor Padding" in item:
                        buffs['def_up'] = 2
                        action_taken = f"{Warna.HIJAU}🛡 Pakai {item}: DEF +50% selama 2 turn!{Warna.RESET}"
                    elif "Bomb" in item or "Molotov" in item:
                        kerusakan_dealt = 40
                        enemy['hp'] -= kerusakan_dealt
                        action_taken = f"{Warna.MERAH}Pakai {item}: {kerusakan_dealt} kerusakan{Warna.RESET}"
                    elif "Med Kit" in item:
                        heal = 80
                        player['hp'] = min(player['max_hp'], player['hp'] + heal)
                        action_taken = f"{Warna.HIJAU}Pakai {item}: +{heal} HP{Warna.RESET}"
                    elif "Bandage" in item:
                        heal = 30
                        player['hp'] = min(player['max_hp'], player['hp'] + heal)
                        action_taken = f"{Warna.HIJAU}Pakai {item}: +{heal} HP{Warna.RESET}"
                    else:
                        action_taken = f"Pakai {item}"

                    combat_log.append(action_taken)
            except (ValueError, IndexError, KeyError):
                print(f"\n  {Warna.MERAH}Input salah!{Warna.RESET}")
                time.sleep(1)
                continue
        
        else:
            try:
                original_input = action
                indices = [int(x.strip()) for x in action.split(',')]
                
                # Check for duplicates — reject if any found
                if len(indices) != len(set(indices)):
                    print(f"\n  {Warna.MERAH}Input salah! (tidak boleh ada duplikat indeks){Warna.RESET}")
                    time.sleep(1)
                    continue
                
                indices = [i for i in indices if 0 <= i < len(player_hand)]
                indices = indices[:5]                            # max 5 kartu per aksi
                
                if not indices:
                    print(f"\n  {Warna.MERAH}Pilihan kartu salah (indeks tidak valid atau di luar range)!{Warna.RESET}")
                    time.sleep(1)
                    continue
                
                played_cards = [player_hand[i] for i in sorted(indices, reverse=True)]
                for i in sorted(indices, reverse=True):
                    player_hand.pop(i)
                
                # Cek buff four_straight (Haikaru) — consume setelah dipakai
                allow_4s = player.get('_buffs', {}).get('four_straight', 0) > 0
                if allow_4s:
                    player['_buffs']['four_straight'] = 0
                hand_type, hand_score = evaluate_hand(played_cards, allow_four_straight=allow_4s)
                
                # Validasi: reject invalid hands
                if hand_type == "Invalid Hand (Duplicate Cards)" or hand_type == "Nothing":
                    print(f"\n  {Warna.MERAH}Kombinasi kartu tidak valid!{Warna.RESET}")
                    # Return cards ke hand
                    for card in played_cards:
                        player_hand.append(card)
                    time.sleep(1)
                    continue
                
                dialog = get_card_dialog(player.get('character_id', 'vio'), hand_type)
                if dialog:
                    print(f"\n  {Warna.KUNING}💬 {dialog}{Warna.RESET}")
                    time.sleep(1.2)

                player_attack = get_stat(player, 'attack', 10)
                # Terapkan ATK buff jika aktif (50% bonus)
                if player.get('_buffs', {}).get('atk_up', 0) > 0:
                    player_attack = int(player_attack * 1.50)
                defense_reduction = enemy.get('defense', 5)
                kerusakan_dealt = calculate_kerusakan(
                    hand_type, hand_score,
                    player_attack,
                    player.get('level', 1),
                    is_enemy=False,
                    defense=defense_reduction
                )

                # Cek buff card_power_mult (skill Vio/Arganta/Ignatius) — damage ×N
                card_mult = player.get('_buffs', {}).get('card_power_mult', 0)
                mult_tag = ""
                if card_mult > 0:
                    kerusakan_dealt = kerusakan_dealt * card_mult
                    mult_tag = f" {Warna.UNGU}[×{card_mult} POWER!]{Warna.RESET}"
                    player['_buffs']['card_power_mult'] = 0  # consume

                # Cek ambush_stun buff (Arganta Ambush) — stun musuh setelah hit
                ambush_stun = player.get('_buffs', {}).get('ambush_stun', 0)
                if ambush_stun > 0 and kerusakan_dealt > 0:
                    enemy['_stunned'] = 1
                    player['_buffs']['ambush_stun'] = 0
                    mult_tag += f" {Warna.CYAN}[STUN!]{Warna.RESET}"

                # OVERTIME DAMAGE BOOST
                if overtime_active:
                    kerusakan_dealt = int(kerusakan_dealt * 1.75)
                    mult_tag += f" {Warna.MERAH + Warna.TERANG}[OVERTIME ×1.75!]{Warna.RESET}"
                
                enemy['hp'] -= kerusakan_dealt
                
                action_taken = (f"{Warna.HIJAU}Main {hand_type}: {kerusakan_dealt} kerusakan"
                                f"{mult_tag}{Warna.RESET}")
                combat_log.append(action_taken)

                # Boss phase transition check (Epstein 3-phase etc)
                _trigger_boss_phase_if_needed(enemy, combat_log)

                # Refill kartu yang sudah dimainkan
                refill_deck_if_needed(deck)
                for _ in played_cards:
                    if deck:
                        player_hand.append(deck.pop())
                ensure_hand_size(player_hand, deck, target_size=3)

                # Track overtime progress (hanya dari mainkan kartu, bukan skill/discard)
                if not overtime_active and not overtime_available:
                    overtime_progress += 1
                    if overtime_progress >= OVERTIME_REQUIRED:
                        overtime_available = True
                        overtime_progress  = OVERTIME_REQUIRED
                        print(f"\n  {Warna.KUNING + Warna.TERANG}⚡ OVERTIME BAR PENUH! Ketik 'OT' untuk aktifkan!{Warna.RESET}")
                        time.sleep(1)

                # OVERTIME: 2 COMBO HAND
                # Jika overtime aktif, player bisa langsung main combo kedua
                if overtime_active and enemy['hp'] > 0:
                    print(f"\n  {Warna.MERAH + Warna.TERANG}⚡ OVERTIME: Main combo ke-2! (atau Enter untuk skip){Warna.RESET}")
                    show_hand(player_hand)
                    action2 = input(f"  {Warna.PUTIH}Combo-2 (indeks kartu / Enter skip): {Warna.RESET}").strip().upper()
                    if action2 and action2 != '':
                        try:
                            idx2 = [int(x.strip()) for x in action2.split(',')]
                            
                            # Check for duplicates — reject if any found
                            if len(idx2) != len(set(idx2)):
                                print(f"\n  {Warna.MERAH}Input salah! (tidak boleh ada duplikat indeks){Warna.RESET}")
                                time.sleep(1)
                            else:
                                idx2 = [i for i in idx2 if 0 <= i < len(player_hand)]
                                idx2 = idx2[:5]                            # max 5 kartu per aksi
                                if idx2:
                                    played2 = [player_hand[i] for i in sorted(idx2, reverse=True)]
                                    for i in sorted(idx2, reverse=True):
                                        player_hand.pop(i)
                                    ht2, hs2 = evaluate_hand(played2)
                                    
                                    # Validasi: reject invalid hands
                                    if ht2 == "Invalid Hand (Duplicate Cards)":
                                        print(f"\n  {Warna.MERAH}Kombinasi kartu tidak valid!{Warna.RESET}")
                                        # Return cards ke hand
                                        for card in played2:
                                            player_hand.append(card)
                                        time.sleep(1)
                                    else:
                                        p_atk2  = int(player_attack * 1.75)  # Overtime boost tetap aktif
                                        dmg2    = calculate_kerusakan(ht2, hs2, p_atk2,
                                                                      player.get('level', 1),
                                                                      defense=defense_reduction)
                                        enemy['hp'] -= dmg2
                                        combo_msg = (f"{Warna.MERAH}⚡ OVERTIME Combo-2: {ht2}: "
                                                     f"{dmg2} kerusakan!{Warna.RESET}")
                                        combat_log.append(combo_msg)
                                        print(f"  {combo_msg}")
                                        _trigger_boss_phase_if_needed(enemy, combat_log)
                                        time.sleep(1)
                                        for _ in played2:
                                            if deck:
                                                player_hand.append(deck.pop())
                        except (ValueError, IndexError):
                            pass

                # Combo ke-2 overtime sudah selesai
            
            except (ValueError, IndexError):
                print(f"\n  {Warna.MERAH}Input salah!{Warna.RESET}")
                time.sleep(1)
                continue
        
        if action_taken and not skip_enemy_turn:
            print(f"\n  {action_taken}")
            time.sleep(1.5)
        elif action_taken and skip_enemy_turn:
            # Sudah di-print di dalam blok skill/discard — tidak perlu ulang
            time.sleep(0.5)
        
        if enemy['hp'] <= 0:
            break
        
        if skip_enemy_turn:
            # Player gunakan Skill atau Discard → musuh tidak menyerang
            print(f"\n  {Warna.ABU_GELAP}(Giliran musuh dilewati — kamu menggunakan skill/discard){Warna.RESET}")
            time.sleep(0.8)
        elif enemy.get('_stunned', 0) > 0:
            # Musuh terkena STUN → skip serangan mereka
            enemy['_stunned'] -= 1
            print(f"\n  {Warna.KUNING}Musuh terstun! Skip giliran musuh.{Warna.RESET}")
            time.sleep(1)
        else:
            # Giliran Musuh Normal
            print(f"\n  {Warna.MERAH}Giliran musuh...{Warna.RESET}")
            time.sleep(1)

            if len(enemy_hand) >= 5:
                played = random.sample(enemy_hand, 5)
                for card in played:
                    enemy_hand.remove(card)
            elif len(enemy_hand) >= 3:
                num_to_play = random.randint(3, min(len(enemy_hand), 5))
                played = random.sample(enemy_hand, num_to_play)
                for card in played:
                    enemy_hand.remove(card)
            else:
                played, enemy_hand = enemy_hand, []
            
            hand_type, hand_score = evaluate_hand(played)

            # Dodge system:
            # - Base 20% chance setiap giliran (pasif, tanpa skill)
            # - Shadow Step (buff_evade) boost ke 70% selama 1 giliran
            evade_buffed = player.get('_buffs', {}).get('evade', 0) > 0
            dodge_chance  = 0.70 if evade_buffed else player_dodge_base
            player_dodges = random.random() < dodge_chance
            if evade_buffed:
                player['_buffs']['evade'] = 0  # consume buff
            if player_dodges:
                tag = f"{Warna.KUNING}[SHADOW STEP] {Warna.RESET}" if evade_buffed else ""
                enemy_action = (f"{Warna.CYAN}Musuh mainkan {hand_type} — "
                                f"{tag}{Warna.HIJAU}DODGE! Serangan dihindari!{Warna.RESET}")
                combat_log.append(enemy_action)
                print(f"  {enemy_action}")
            elif overtime_active:
                enemy_action = (f"{Warna.MERAH}Musuh mainkan {hand_type} — "
                                f"{Warna.MERAH + Warna.TERANG}[OVERTIME SHIELD! Serangan diabaikan!]{Warna.RESET}")
                combat_log.append(enemy_action)
                print(f"  {enemy_action}")
            else:
                player_defense = get_stat(player, 'defense', 5)
                if player.get('_buffs', {}).get('def_up', 0) > 0:
                    player_defense = int(player_defense * 1.50)
                base_enemy_dmg = calculate_kerusakan(
                    hand_type, hand_score,
                    enemy.get('attack', 15),
                    enemy.get('level', 1),
                    is_enemy=True,
                    defense=player_defense
                )

                enemy_action_pre = (f"{Warna.MERAH}Musuh mainkan {hand_type}: "
                                    f"{base_enemy_dmg} damage {Warna.KUNING}[QTE!]{Warna.RESET}")
                combat_log.append(enemy_action_pre)
                print(f"  {enemy_action_pre}")

                qte_key = _run_qte(timeout=1.8)
                final_dmg, qte_msg, _ = _apply_qte_result(
                    qte_key, base_enemy_dmg, player, enemy, combat_log
                )
                print(f"  {qte_msg}")

                player['hp'] -= final_dmg
                enemy_action = (f"{Warna.MERAH}Damage diterima: {final_dmg}{Warna.RESET}")
                combat_log.append(enemy_action)
                print(f"  {enemy_action}")
            
            time.sleep(1.5)

            refill_deck_if_needed(deck)
            for _ in played:
                if deck:
                    enemy_hand.append(deck.pop())
            ensure_hand_size(enemy_hand, deck, target_size=5)

        if player['hp'] <= 0:
            break
        
        # INDEPENDENT COOLDOWN & ENERGY REGEN
        # FIX: Cooldown dan energy regen HANYA berjalan saat player menyerang (main kartu)
        # atau Pass. Saat player pakai Skill / Discard, cooldown skill LAIN tidak boleh
        # berkurang — mencegah efek "EMP Stun mengurangi CD Overclock" dan infinite loop.
        if not skip_enemy_turn:
            regen_per_turn = 2
            player['energy'] = min(player.get('max_energy', 30),
                                   player.get('energy', 0) + regen_per_turn)
            # Tick cooldown skill player — HANYA pada turn serangan/pass
            cooldowns = player.get('_skill_cooldowns', {})
            for sk_name in list(cooldowns.keys()):
                if cooldowns[sk_name] > 0:
                    cooldowns[sk_name] -= 1

        # Tick buff durasi player (setiap turn, termasuk skill/discard)
        _tick_buffs(player)

        # Tick overtime — kurangi turns jika sedang aktif (time-based, bukan attack-based)
        if overtime_active:
            overtime_turns_left -= 1
            if overtime_turns_left <= 0:
                overtime_active = False
                overtime_turns_left = 0
                print(f"\n  {Warna.ABU_GELAP}Overtime berakhir.{Warna.RESET}")
                time.sleep(0.8)

        # Tick debuff musuh (DEF & ATK) — kembalikan nilai setelah habis
        if enemy.get('_def_debuff_turns', 0) > 0:
            enemy['_def_debuff_turns'] -= 1
            if enemy['_def_debuff_turns'] == 0:
                # Restore DEF ke nilai asli
                enemy['defense'] = enemy.get('_orig_def', enemy.get('defense', 5))
        if enemy.get('_atk_debuff_turns', 0) > 0:
            enemy['_atk_debuff_turns'] -= 1
            if enemy['_atk_debuff_turns'] == 0:
                # Restore ATK ke nilai asli
                enemy['attack'] = enemy.get('_orig_atk', enemy.get('attack', 15))

        turn += 1
    
    clear_screen()
    
    # Clean up all buff effects after combat ends
    player['_buffs'] = {}
    
    if enemy['hp'] <= 0:
        print(f"\n{Warna.HIJAU + Warna.TERANG}")
        print(f"  ╔══════════════════════════════════════╗")
        print(f"  ║            MENANG!                  ║")
        print(f"  ╚══════════════════════════════════════╝")
        print(f"{Warna.RESET}\n")
        print(f"  {Warna.HIJAU}Kamu mengalahkan {enemy['name']}!{Warna.RESET}")
        
        xp = enemy.get('xp', 10)
        print(f"  {Warna.KUNING}+{xp} XP{Warna.RESET}")
        
        if enemy.get('loot'):
            loot = random.choice(enemy['loot'])
            inventory.append(loot)
            print(f"  {Warna.CYAN}Dapat: {loot}{Warna.RESET}")
        
        time.sleep(2)
        return 'victory'
    
    else:
        print(f"\n{Warna.MERAH + Warna.TERANG}")
        print(f"  ╔══════════════════════════════════════╗")
        print(f"  ║            KALAH...                 ║")
        print(f"  ╚══════════════════════════════════════╝")
        print(f"{Warna.RESET}\n")
        print(f"  {Warna.MERAH}Kamu dikalahkan oleh {enemy['name']}...{Warna.RESET}")
        time.sleep(2)
        return 'player_dead'
    