# Utilitas terminal dan I/O
import os
import sys
import time
import shutil
from contextlib import suppress
from .sprites import Warna

def _setup_encoding():
    encoding_success = False
    with suppress(Exception):
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            encoding_success = True
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    return encoding_success

def get_term_width(default=80):
    """Terminal width — re-queried each call so it auto-updates on resize."""
    return max(40, shutil.get_terminal_size(fallback=(default, 24)).columns)

def check_terminal_compatibility():
    try:
        cols, rows = shutil.get_terminal_size(fallback=(80, 24))
        if cols < 80 or rows < 24:
            return False, cols, rows
        return True, cols, rows
    except Exception:
        return True, 80, 24

def get_terminal_info():
    try:
        cols, rows = shutil.get_terminal_size(fallback=(80, 24))
        return {'width': cols, 'height': rows,
                'encoding': sys.stdout.encoding or 'unknown',
                'platform': os.name}
    except Exception as e:
        return {'error': str(e)}

_encoding_ok = _setup_encoding()

def clear_screen():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except OSError:
        print('\n' * 50)

def flush_input():
    try:
        if os.name == 'nt':
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass


def print_slow(text, delay=0.03, allow_skip=True):
    if delay <= 0:
        print(text)
        return
    try:
        skip_mode = False
        for char in text:
            if allow_skip and not skip_mode:
                try:
                    if os.name == 'nt':
                        import msvcrt
                        if msvcrt.kbhit():
                            key = msvcrt.getch()
                            if key in (b'\r', b' ', b'\n'):
                                skip_mode = True
                    else:
                        import select
                        rlist, _, _ = select.select([sys.stdin], [], [], 0)
                        if rlist:
                            sys.stdin.readline()
                            skip_mode = True
                except Exception:
                    pass
            sys.stdout.write(char)
            if not skip_mode:
                sys.stdout.flush()
                time.sleep(delay)
        sys.stdout.flush()
        print()
    except (IOError, OSError, UnicodeEncodeError):
        try:
            print(text)
        except Exception:
            pass

def wait_input(prompt="[ENTER untuk lanjut] "):
    try:
        flush_input()
        time.sleep(0.02)
        input(f"{Warna.ABU_GELAP}{prompt}{Warna.RESET}")
    except (KeyboardInterrupt, EOFError):
        pass

def separator(char=None, length=None):
    # Public: auto-fit separator to current terminal width
    if char is None:
        char = '─'
    if length is None:
        length = max(40, get_term_width() - 2)
    try:
        print(f"{Warna.ABU_GELAP}{char * length}{Warna.RESET}")
    except UnicodeEncodeError:
        print('-' * length)

def header(text):
    # Public: section header with separators
    separator()
    print(f"{Warna.CYAN}{text}{Warna.RESET}")
    separator()

def center(text, width=None):
    # Public: center text in terminal width
    w = width or get_term_width()
    return text.center(w)

def confirm_action(prompt="Yakin? (y/n): "):
    while True:
        response = input(f"{Warna.KUNING}{prompt}{Warna.RESET}").strip().lower()
        if response in ['y', 'ya', 'yes']:
            return True
        elif response in ['n', 'no', 'tidak']:
            return False
        else:
            print(f"{Warna.MERAH}Masukkan 'y' atau 'n'{Warna.RESET}")

def get_stat(obj, stat_name, default=None):
    return obj.get(stat_name) or obj.get('stats', {}).get(stat_name, default) or default

def trunc(text, maxlen, suffix='…'):
    """Potong teks agar tidak melebihi maxlen karakter."""
    if len(text) <= maxlen:
        return text
    return text[:maxlen - len(suffix)] + suffix
