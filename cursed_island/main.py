# Entry point dan menu utama

import os
import sys
import time
from contextlib import suppress

with suppress(Exception):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from .sprites import Warna, PLAYER_SPRITE, NPC_SPRITES, UI_CHARS, TITLE_ART, SPRITES
    from .characters import (
        PLAYABLE_CHARACTERS,
        get_card_dialog,
        get_character_name,
        display_route_intro,
        apply_route_bonuses,
        check_chapter_complete,
        advance_chapter,
    )
    from .enemies import ENEMIES, BOSSES, create_enemy_instance, create_boss_instance
    from .exploration import GameMap, create_game_map, loop_eksplorasi
    from .combat import (
        Card,
        SUITS,
        RANKS,
        run_combat,
        evaluate_hand,
        calculate_kerusakan,
        make_hp_bar,
    )
    from .gamestate import GameState, SLOT_FILES
    from .story import (
        display_chapter,
        display_backstory,
        get_prologue_chapters,
        play_route_ending,
        get_chapter_1,
        get_chapter_2,
        get_chapter_3,
    )
    from .tutorial import tutorial_lengkap
    from .utils import (
        clear_screen as clear,
        wait_input as wait,
        separator,
        header,
        check_terminal_compatibility,
        print_slow,
        flush_input,
        get_term_width,
    )
    from .constants import MIN_TERMINAL_WIDTH, MIN_TERMINAL_HEIGHT, GAME_VERSION
    from .settings import SETTINGS
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

VERSI = GAME_VERSION

def _tw():
    # Private: terminal width
    return get_term_width()

def get_title_simple(version):
    """Title box yang auto-fit ke lebar terminal."""
    import shutil
    tw = max(44, shutil.get_terminal_size(fallback=(80, 24)).columns)
    inner = tw - 4   # ruang dalam box (mengurangi '  ║' dan '║')

    def _center(text, w):
        pad = max(0, w - len(text))
        l = pad // 2
        r = pad - l
        return ' ' * l + text + ' ' * r

    top    = '  ╔' + '═' * inner + '╗'
    bot    = '  ╚' + '═' * inner + '╝'
    def row(text): return f"  ║{_center(text, inner)}║"

    lines = [
        top,
        row('CURSED ISLAND ESCAPE'),
        row('Petualangan Melarikan Diri'),
        row(f'v{version}'),
        bot,
    ]
    return f"{Warna.CYAN + Warna.TERANG}\n" + '\n'.join(lines) + f"\n{Warna.RESET}"

def check_and_enforce_terminal_size():
    # Mengecek dan memastikan ukuran terminal memenuhi standar minimal
    """Cek ukuran terminal minimal 80x24"""
    is_compatible, width, height = check_terminal_compatibility()
    
    if not is_compatible or width < MIN_TERMINAL_WIDTH or height < MIN_TERMINAL_HEIGHT:
        clear()
        print(f"{Warna.MERAH + Warna.TERANG}⚠ WARNING: UKURAN TERMINAL TIDAK SESUAI{Warna.RESET}")
        print(f"\nUkuran saat ini: {width}x{height}")
        print(f"Ukuran minimum yang direkomendasikan: {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}")
        print(f"\nPerintah untuk resize terminal:")
        
        if os.name == 'nt':
            print("  • Windows CMD: Klik judul jendela → Properties → Layout")
            print("    Set ke minimal 80 kolom × 24 baris")
        else:
            print(f"  • Linux/Mac: {Warna.CYAN}resize{Warna.RESET} atau drag jendela terminal")
            print("    Pastikan terminal berukuran minimal 80×24")
        
        print(f"\n{Warna.KUNING}Jika diabaikan, tampilan peta dan UI mungkin akan rusak!{Warna.RESET}")
        print(f"{Warna.ABU_GELAP}(Tekan ENTER untuk melanjutkan){Warna.RESET}")
        
        with suppress(Exception):
            input()
        
        clear()
    
    clear()

def mainkan_prolog():
    """Tampilkan prolog awal"""
    clear()
    header("PROLOG")
    print(f"{Warna.ABU_GELAP}[Warning: Tema dewasa]{Warna.RESET}\n")
    wait()
    
    for chapter_id in get_prologue_chapters():
        clear()
        display_chapter(chapter_id)
        print()
        wait()
    
    clear()
    separator('═')
    print(f"{Warna.PUTIH}CERITAMU DIMULAI{Warna.RESET}".center(_tw()))
    separator('═')
    wait()

def play_chapter_story(chapter_num):
    """Mainkan story chapter"""
    clear()
    
    if chapter_num == 1:
        chapters = get_chapter_1()
    elif chapter_num == 2:
        chapters = get_chapter_2()
    elif chapter_num == 3:
        chapters = get_chapter_3()
    else:
        return
    
    for chapter_id in chapters:
        clear()
        display_chapter(chapter_id)
        print()
        wait()

def pilih_karakter(gs):
    # Menampilkan pilihan karakter dan menyimpan pilihan pemain
    """Menu pilih karakter"""
    clear()
    header("PILIH KARAKTER")
    
    chars = list(PLAYABLE_CHARACTERS.keys())
    
    print()
    for i, cid in enumerate(chars, 1):
        cd = PLAYABLE_CHARACTERS[cid]
        diff = "★" * cd.get('difficulty', 2)
        print(f"{Warna.KUNING}[{i}]{Warna.RESET} {cd['name']} - {cd['title']} {diff}")
        print(f"     Nyawa:{cd['stats']['hp']} Serang:{cd['stats']['attack']} Pertahanan:{cd['stats']['defense']}")
        print()
    
    while True:
        try:
            pilihan = input(f"\n{Warna.CYAN}Pilih karakter (1-{len(chars)}, atau 0 batal): {Warna.RESET}").strip()
            if pilihan == '0':
                return False
            num = int(pilihan)
            if 1 <= num <= len(chars):
                _apply_character_stats(gs, chars[num-1])
                return True
            else:
                print(f"{Warna.MERAH}Pilihan tidak valid, masukkan 1-{len(chars)}{Warna.RESET}")
        except ValueError:
            print(f"{Warna.MERAH}Masukkan angka!{Warna.RESET}")
        except (KeyboardInterrupt, EOFError):
            return False

def _apply_character_stats(gs, char_id):
    """Terapkan stat karakter ke game state"""
    cd = PLAYABLE_CHARACTERS[char_id]
    gs.player_character = char_id
    gs.hp       = cd['stats']['hp']
    gs.max_hp   = cd['stats']['hp']
    gs.attack   = cd['stats']['attack']
    gs.defense  = cd['stats']['defense']
    gs.speed    = cd['stats']['speed']

    base_energy = 20 + cd['stats'].get('speed', 10) // 2
    gs.energy     = base_energy
    gs.max_energy = base_energy

    gs.story_flags['player_skills'] = cd.get('skills', {})
    gs.story_flags['current_chapter'] = gs.story_flags.get('current_chapter', 1)

    # Terapkan level-up gains spesifik karakter
    gs.apply_character_level_gains(char_id)

def menu_settings():
    # Public: game settings menu (difficulty locked to Hard)
    while True:
        clear()
        header("PENGATURAN")

        print(f"\n{Warna.CYAN}Kecepatan Dialog:{Warna.RESET}")
        speeds = [('Lambat', 0.05), ('Normal', 0.03), ('Cepat', 0.01), ('Instan', 0)]
        for i, (name, val) in enumerate(speeds, 1):
            mark = "◉" if abs(SETTINGS['dialog_speed'] - val) < 0.01 else "○"
            print(f"  {mark} [{i}] {name}")

        print(f"\n{Warna.MERAH}Kesulitan: Hard Mode (Terkunci — 1.2x stat musuh){Warna.RESET}")

        print(f"\n{Warna.CYAN}Lainnya:{Warna.RESET}")
        print(f"  [5] Auto-Save: {'ON' if SETTINGS['auto_save'] else 'OFF'}")
        print(f"  [6] Tutorial:  {'ON' if SETTINGS['show_tutorial'] else 'OFF'}")
        print(f"\n  [0] Kembali")

        pilihan = input(f"\n{Warna.CYAN}> {Warna.RESET}").strip()

        if pilihan == '1':
            SETTINGS['dialog_speed'] = 0.05
        elif pilihan == '2':
            SETTINGS['dialog_speed'] = 0.03
        elif pilihan == '3':
            SETTINGS['dialog_speed'] = 0.01
        elif pilihan == '4':
            SETTINGS['dialog_speed'] = 0
        elif pilihan == '5':
            SETTINGS['auto_save'] = not SETTINGS['auto_save']
        elif pilihan == '6':
            SETTINGS['show_tutorial'] = not SETTINGS['show_tutorial']
        elif pilihan == '0':
            break

def tampilkan_kredit():
    """Tampilkan credits"""
    clear()
    header("KREDIT")
    
    print(f"""
{Warna.KUNING}CURSED ISLAND ESCAPE v{VERSI}{Warna.RESET}

{Warna.CYAN}Developers:{Warna.RESET}
  - Ahmad Haikal Ramadhan
  - Alif Rizky Ramadhan Atmadja
  - M Vallerian Aprilio Gunawan
  - Ignatius Nino Jumantoro
  - Evan Arganta

{Warna.HIJAU}SMKN 2 JAKARTA Class X RPL 1{Warna.RESET}

{Warna.CYAN}Inspirasi/Referensi:{Warna.RESET}
  - Sword and Poker
  - Final Fantasy Adventure
  - Atari Adventure
  - The Legend of Zelda
  - Balatro
  - The Jeffrey Epstein Case and Files #justiceforvictim

{Warna.CYAN}Engine:{Warna.RESET}
  Python 3.6+ CLI

{Warna.ABU_GELAP}
    """)
    
    wait()

def _print_error(message):
    """Print pesan error"""
    print(f"\n{Warna.MERAH}{message}{Warna.RESET}\n")
    wait()

def pilih_slot(gs, aksi="load"):
    # Public: display 5-slot picker; return True if slot chosen
    clear()
    label = "MUAT GAME" if aksi == "load" else "SIMPAN GAME"
    header(f"SLOT SAVE — {label}")
    print()

    has_any = False
    for slot_idx, fname in SLOT_FILES.items():
        try:
            tmp_gs = GameState()
            tmp_gs.current_slot = slot_idx
            summary = tmp_gs.get_save_summary(fname)
        except Exception:
            summary = None

        if summary:
            has_any = True
            loc = summary.get('location','?').capitalize()[:8]
            print(f"  {Warna.KUNING}[{slot_idx + 1}]{Warna.RESET} "
                  f"Slot {slot_idx + 1} — {summary['player']} "
                  f"| Level: {summary['level']} | Waktu: {summary['playtime']} "
                  f"| Lokasi: {loc}")
        else:
            empty_label = f"  {Warna.ABU_GELAP}[{slot_idx + 1}]{Warna.RESET} Slot {slot_idx + 1} — Kosong"
            if aksi == "load":
                empty_label += f" {Warna.ABU_GELAP}(tidak bisa dimuat){Warna.RESET}"
            print(empty_label)

    print(f"\n  {Warna.ABU_GELAP}[0] Batal{Warna.RESET}")

    while True:
        try:
            ch = input(f"\n{Warna.CYAN}Pilih slot (1-5, 0=batal): {Warna.RESET}").strip()
            if ch == '0':
                return False
            idx = int(ch) - 1
            if 0 <= idx <= 4:
                if aksi == "load":
                    tmp_gs2 = GameState()
                    tmp_gs2.current_slot = idx
                    if not tmp_gs2.get_save_summary(SLOT_FILES[idx]):
                        print(f"{Warna.MERAH}Slot kosong!{Warna.RESET}")
                        continue
                gs.current_slot = idx
                return True
            print(f"{Warna.MERAH}Pilih 1-5.{Warna.RESET}")
        except ValueError:
            print(f"{Warna.MERAH}Masukkan angka.{Warna.RESET}")
        except (KeyboardInterrupt, EOFError):
            return False

def muat_game(gs):
    # Public: load game from selected slot
    if not pilih_slot(gs, aksi="load"):
        return False

    fname = SLOT_FILES[gs.current_slot]
    clear()
    header(f"MUAT GAME — SLOT {gs.current_slot + 1}")

    try:
        summary = gs.get_save_summary(fname)
        if not summary:
            _print_error(f"Slot {gs.current_slot + 1} kosong atau rusak!")
            return False

        print(f"\n{Warna.CYAN}Info Save:{Warna.RESET}")
        print(f"  Player: {summary['player']}")
        print(f"  Level:  {summary['level']}")
        print(f"  Lokasi: {summary['location']}")
        print(f"  Waktu:  {summary['playtime']}")

        confirm = input(f"\n{Warna.CYAN}Muat Slot {gs.current_slot + 1}? (y/n): {Warna.RESET}").strip().lower()

        if confirm == 'y':
            sukses, msg = gs.load_from_file(fname)
            print(f"\n{Warna.HIJAU if sukses else Warna.MERAH}{msg}{Warna.RESET}\n")
            if sukses:
                # Apply loaded settings to the global SETTINGS dict
                if hasattr(gs, 'settings') and isinstance(gs.settings, dict):
                    SETTINGS.update(gs.settings)
                
                if gs.player_character:
                    char_data = PLAYABLE_CHARACTERS.get(gs.player_character, {})
                    if char_data and 'player_skills' not in gs.story_flags:
                        gs.story_flags['player_skills'] = char_data.get('skills', {})
                if not hasattr(gs, 'energy') or gs.energy == 0:
                    base_energy = 20 + char_data.get('stats', {}).get('speed', 10) // 2
                    gs.energy     = base_energy
                    gs.max_energy = base_energy
                gs.apply_character_level_gains(gs.player_character)
            wait()
            return sukses
    except Exception as e:
        print(f"\n{Warna.MERAH}Error: {e}{Warna.RESET}\n")
        wait()

    return False

def wait_or_timeout(timeout_seconds=1.5):
    """Auto-advance atau skip dengan ENTER - respects dialog speed setting"""
    pass

def menu_utama():
    # Menampilkan dan mengelola menu utama permainan
    """Menu utama"""
    clear()
    print(f"{TITLE_ART}")
    wait(prompt="[ENTER untuk mulai] ")
    clear()
    print(f"\n{get_title_simple(VERSI)}")
    
    gs = GameState()
    
    while True:
        separator()
        print(f"{Warna.KUNING}[1]{Warna.RESET} Game Baru")
        print(f"{Warna.KUNING}[2]{Warna.RESET} Lanjutkan")
        print(f"{Warna.KUNING}[3]{Warna.RESET} Pengaturan")
        print(f"{Warna.KUNING}[4]{Warna.RESET} Kredit")
        print(f"{Warna.KUNING}[5]{Warna.RESET} Keluar")
        separator()
        
        pilihan = input(f"\n{Warna.CYAN}> {Warna.RESET}").strip()
        
        if pilihan == '1':
            clear()
            header("GAME BARU")

            nama = input(f"\n{Warna.CYAN}Nama: {Warna.RESET}").strip()
            if not nama:
                continue

            gs.player_name = nama

            if not pilih_karakter(gs):
                continue

            # Pilih slot untuk menyimpan game baru
            if not pilih_slot(gs, aksi="save"):
                continue

            # Store current settings in game state
            gs.settings = dict(SETTINGS)

            clear()
            display_backstory(gs.player_character)
            wait()
            
            tutorial_lengkap()
            
            display_route_intro(gs.player_character)
            gs = apply_route_bonuses(gs, gs.player_character)
            
            loop_game(gs)
            
            gs = GameState()
            clear()
            print(f"\n{get_title_simple(VERSI)}")
        
        elif pilihan == '2':
            if muat_game(gs):
                loop_game(gs)
                gs = GameState()
            clear()
            print(f"\n{get_title_simple(VERSI)}")
        
        elif pilihan == '3':
            menu_settings()
            clear()
            print(f"\n{get_title_simple(VERSI)}")
        
        elif pilihan == '4':
            tampilkan_kredit()
            clear()
            print(f"\n{get_title_simple(VERSI)}")
        
        elif pilihan == '5':
            clear()
            print(f"\n{Warna.CYAN}Terima kasih!{Warna.RESET}\n")
            sys.exit(0)

def loop_game(gs):
    # Menjalankan loop utama game (eksplorasi, pertarungan, cerita)
    """Main game loop - handle exploration, chapters, and endings"""
    berjalan = True
    
    while berjalan:
        current_chapter = gs.story_flags.get('current_chapter', 1)
        
        if check_chapter_complete(gs) and current_chapter < 3:
            clear()
            separator('═')
            print(f"{Warna.HIJAU}CHAPTER {current_chapter} SELESAI!{Warna.RESET}".center(_tw()))
            separator('═')
            wait()
            
            if advance_chapter(gs):
                new_chapter = gs.story_flags.get('current_chapter')
                play_chapter_story(new_chapter)
        
        peta = buat_peta_game(gs.current_location, gs)
        hasil = loop_eksplorasi(gs, peta)
        
        if hasil == 'quit':
            berjalan = False
        elif hasil == 'game_over':
            layar_game_over(gs)
            berjalan = False
        elif hasil == 'checkpoint':
            # Kembali dari boss (retry habis / give up) — lanjut eksplorasi dari checkpoint
            from .sprites import Warna as _W
            print(f"\n  {_W.KUNING}Kembali ke checkpoint. Siapkan dirimu untuk mencoba lagi!{_W.RESET}")
            time.sleep(1.5)
            # gs.current_location sudah di-set oleh load_checkpoint() di exploration.py
            # Game loop lanjut — tidak game over
        elif hasil == 'victory':
            layar_kemenangan(gs)
            berjalan = False

def layar_game_over(gs):
    """Display game over screen with final stats"""
    clear()
    tw = _tw()
    sep = Warna.MERAH + '═' * (tw - 1) + Warna.RESET
    print(sep)
    print(f"{Warna.MERAH + Warna.TERANG}{'💀  GAME OVER  💀'.center(tw)}{Warna.RESET}")
    print(sep)

    try:
        from .characters import get_character_name
        char_name = get_character_name(gs.player_character)
    except Exception:
        char_name = (gs.player_character or '?').upper()

    print(f"\n  {Warna.CYAN}Karakter:{Warna.RESET} {char_name}")
    print(f"  {Warna.CYAN}Level:{Warna.RESET}    {gs.level}")
    print(f"  {Warna.CYAN}Battle:{Warna.RESET}   {gs.battles_won} menang")
    print(f"  {Warna.CYAN}Chapter:{Warna.RESET}  {gs.story_flags.get('current_chapter', 1)}")
    print(f"  {Warna.CYAN}Waktu:{Warna.RESET}    {gs.get_playtime_string()}")
    print(f"\n  {Warna.ABU_GELAP}Jangan menyerah — coba lagi!{Warna.RESET}\n")
    print(sep)
    wait()

def layar_kemenangan(gs):
    """Display victory screen dan ending karakter."""
    clear()
    tw = _tw()

    try:
        from .characters import get_character_name
        char_name = get_character_name(gs.player_character)
    except Exception:
        char_name = (gs.player_character or '?').upper()

    sep_gold = Warna.KUNING + '═' * (tw - 1) + Warna.RESET
    print(sep_gold)
    print(f"{Warna.KUNING + Warna.TERANG}{'🏆  CURSED ISLAND ESCAPE — TAMAT  🏆'.center(tw)}{Warna.RESET}")
    print(f"{Warna.HIJAU + Warna.TERANG}{char_name.upper().center(tw)}{Warna.RESET}")
    print(sep_gold)

    bosses_defeated = getattr(gs, 'bosses_defeated', 0)
    score = bosses_defeated
    score += gs.level // 5
    score += gs.battles_won // 15
    
    if hasattr(gs, 'playtime_seconds') and gs.playtime_seconds < 5400:
        score += 1
    
    if score >= 13:
        grade = 'S'
    elif score >= 9:
        grade = 'A'
    elif score >= 5:
        grade = 'B'
    else:
        grade = 'C'
    
    print(f"\n  {Warna.CYAN}Statistik Akhir:{Warna.RESET}")
    print(f"  {'─' * 25}")
    print(f"  Level          : {Warna.KUNING}{gs.level}{Warna.RESET}")
    print(f"  Battle Menang  : {Warna.KUNING}{gs.battles_won}{Warna.RESET}")
    print(f"  Boss Dikalahkan: {Warna.KUNING}{getattr(gs, 'bosses_defeated', '?')}/6{Warna.RESET}")
    print(f"  Waktu          : {gs.get_playtime_string()}")
    print(f"  Grade          : {Warna.KUNING + Warna.TERANG}{grade}{Warna.RESET}")
    print(f"  {'─' * 25}")

    wait(prompt="[ENTER untuk lihat ending karakter] ")
    clear()

    # Mainkan ending karakter
    try:
        from .story import play_route_ending
        play_route_ending(gs.player_character, skip_delays=False)
    except Exception as e:
        # Fallback: tampilkan pesan ending generic
        print(sep_gold)
        print(f"{Warna.HIJAU + Warna.TERANG}{'KEBEBASAN!'.center(tw)}{Warna.RESET}")
        print(sep_gold)
        print(f"\n  {char_name} berhasil melarikan diri dari Cursed Island!")
        print(f"  Keberanian dan kecerdikan telah mengalahkan sistem yang korup.")
        print(f"\n  {Warna.ABU_GELAP}(Ending detail tidak dapat dimuat: {e}){Warna.RESET}\n")

    print(f"\n{sep_gold}")
    print(f"{Warna.KUNING + Warna.TERANG}{'TERIMA KASIH SUDAH BERMAIN!'.center(tw)}{Warna.RESET}")
    print(f"{Warna.ABU_GELAP}{'Cursed Island Escape — by Kelompok Ludo'.center(tw)}{Warna.RESET}")
    print(sep_gold)
    wait()

def dapatkan_nama_karakter(char_id):
    try:
        return get_character_name(char_id)
    except (KeyError, AttributeError):
        return char_id.upper()

def buat_peta_game(map_id, gs=None):
    return create_game_map(map_id, gs)

def main():
    """Alur utama game"""
    try:
        if sys.version_info < (3, 6):
            print("Python 3.6+ required")
            sys.exit(1)
        
        check_and_enforce_terminal_size()
        
        menu_utama()
    
    except KeyboardInterrupt:
        clear()
        print(f"\n{Warna.CYAN}Interrupted.{Warna.RESET}\n")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n{Warna.MERAH}Error: {e}{Warna.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
