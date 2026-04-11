
class Warna:
    """Konfigurasi warna ANSI untuk terminal"""
    RESET = '\033[0m'
    

    HITAM = '\033[30m'
    MERAH = '\033[31m'
    HIJAU = '\033[32m'
    KUNING = '\033[33m'
    BIRU = '\033[34m'
    UNGU = '\033[35m'
    CYAN = '\033[36m'
    PUTIH = '\033[37m'
    ABU_GELAP = '\033[90m'
    

    BG_HITAM = '\033[40m'
    BG_MERAH = '\033[41m'
    BG_HIJAU = '\033[42m'
    BG_KUNING = '\033[43m'
    BG_BIRU = '\033[44m'
    BG_UNGU = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_PUTIH = '\033[47m'
    BG_ABU_GELAP = '\033[100m'
    

    TERANG = '\033[1m'
    DIM = '\033[2m'


# Unicode Support Detection
import sys as _sys
import os as _os

def _detect_unicode_support():
    """Cek apakah terminal mendukung Unicode secara penuh."""
    if _os.environ.get('TERM_UNICODE', '').lower() == '0':
        return False
    
    enc = getattr(_sys.stdout, 'encoding', '') or ''
    if enc.lower().replace('-', '') not in ('utf8', 'utf16', 'utf32'):
        return False
    
    # Empirical test: coba encode karakter Unicode. Jika gagal, fallback ke ASCII.
    # BUG FIX: sebelumnya menulis ke stdout (sys.stdout.write('♠')) yang menyebabkan
    # karakter muncul di terminal saat import. Sekarang test lewat encode saja.
    try:
        test_char = '♠'
        enc_name = enc.lower().replace('-', '')
        test_char.encode(enc_name)
        return True
    except (UnicodeEncodeError, UnicodeDecodeError, LookupError, Exception):
        return False

UNICODE_SUPPORTED = _detect_unicode_support()


def _u(unicode_str, ascii_fallback):
    """Pilih unicode atau ASCII tergantung kemampuan terminal."""
    return unicode_str if UNICODE_SUPPORTED else ascii_fallback


PLAYER_SPRITES = {
    'normal': _u("🧍", "[O]"),
    'alt':    _u("🚶", "[>]"),
}


PLAYER_ASCII = {
    'normal': [" O ", "/|\\", "/ \\"],
    'front':  [" o ", "/|\\", "/ \\"],
    'side':   [" o ", "-|\\", "/ \\"]
}


SPRITES = {
    0:  (_u("  ",   "  "), Warna.ABU_GELAP, Warna.BG_HITAM),
    1:  (_u("▓▓",   "##"), Warna.ABU_GELAP, Warna.BG_HITAM),
    2:  (_u("▒▒",   ">>"), Warna.KUNING,    Warna.BG_HITAM),
    3:  (_u("◆◆",   "**"), Warna.KUNING + Warna.TERANG, Warna.BG_HITAM),
    4:  (_u("☺☺",   ":)"), Warna.CYAN + Warna.TERANG,   Warna.BG_HITAM),
    5:  (_u("░░",   "~~"), Warna.CYAN,      Warna.BG_BIRU),
    6:  (_u("██",   "||"), Warna.PUTIH,     Warna.BG_ABU_GELAP),
    7:  (_u("~~",   "~~"), Warna.BIRU,      Warna.BG_HITAM),
    8:  (_u("##",   "##"), Warna.HIJAU,     Warna.BG_HITAM),
    9:  (_u("[]",   "[]"), Warna.MERAH,     Warna.BG_HITAM),
    10: (_u("⇅⇅",   "^^"), Warna.CYAN + Warna.TERANG,   Warna.BG_HITAM),
    11: (_u("▣▣",   "XX"), Warna.MERAH + Warna.TERANG,  Warna.BG_HITAM),
    12: (_u("⚡⚡",  "!!"), Warna.MERAH + Warna.TERANG,  Warna.BG_HITAM),
    13: (_u("★★",   "**"), Warna.KUNING + Warna.TERANG, Warna.BG_HITAM),
}


PLAYER_SPRITE = (_u("♂♂", "P>"), Warna.UNGU + Warna.TERANG, Warna.BG_HITAM)


NPC_SPRITES = {
    'aolinh':   (_u("♀♀", "nA"), Warna.UNGU + Warna.TERANG,   Warna.BG_HITAM),
    'haikaru':  (_u("♀♀", "nH"), Warna.CYAN + Warna.TERANG,   Warna.BG_HITAM),
    'ignatius': (_u("♂♂", "nI"), Warna.KUNING + Warna.TERANG, Warna.BG_HITAM),
    'arganta':  (_u("♂♂", "nR"), Warna.PUTIH + Warna.TERANG,  Warna.BG_HITAM),
    'vio':      (_u("♂♂", "nV"), Warna.MERAH + Warna.TERANG,  Warna.BG_HITAM),
}


UI_CHARS = {
    'tl': _u('╔', '+'), 'tr': _u('╗', '+'),
    'bl': _u('╚', '+'), 'br': _u('╝', '+'),
    'h':  _u('═', '-'), 'v':  _u('║', '|'),
    'tl_light': _u('┌', '+'), 'tr_light': _u('┐', '+'),
    'bl_light': _u('└', '+'), 'br_light': _u('┘', '+'),
    'h_light':  _u('─', '-'), 'v_light':  _u('│', '|'),
}



# TITLE_ART — ASCII art dengan box-drawing Unicode.
# Terminal yang tidak support (CMD lama) otomatis pakai versi ASCII murni.
if UNICODE_SUPPORTED:
    TITLE_ART = f"""{Warna.CYAN + Warna.TERANG}
 ██████╗██╗   ██╗██████╗ ███████╗███████╗██████╗    ██╗███████╗██╗      █████╗ ███╗   ██╗██████╗     
██╔════╝██║   ██║██╔══██╗██╔════╝██╔════╝██╔══██╗   ██║██╔════╝██║     ██╔══██╗████╗  ██║██╔══██╗  
██║     ██║   ██║██████╔╝███████╗█████╗  ██║  ██║   ██║███████╗██║     ███████║██╔██╗ ██║██║  ██║  
██║     ██║   ██║██╔══██╗╚════██║██╔══╝  ██║  ██║   ██║╚════██║██║     ██╔══██║██║╚██╗██║██║  ██║  
╚██████╗╚██████╔╝██║  ██║███████║███████╗██████╔╝   ██║███████║███████╗██║  ██║██║ ╚████║██████╔╝  
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝    ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝   
                       .------..------..------..------..------..------.
                       |E.--. ||S.--. ||C.--. ||A.--. ||P.--. ||E.--. |
                       | (\/) || :/\: || :/\: || (\/) || :/\: || (\/) |
                       | :\/: || :\/: || :\/: || :\/: || (__) || :\/: |
                       | '--'E|| '--'S|| '--'C|| '--'A|| '--'P|| '--'E|
                       `------'`------'`------'`------'`------'`------'
                               
{Warna.RESET}"""
else:
    TITLE_ART = f"""{Warna.CYAN + Warna.TERANG}
  ================================================
  ||  CURSED ISLAND ESCAPE                      ||
  ||  Petualangan Melarikan Diri                ||
  ================================================
{Warna.RESET}"""


def get_title_simple(versi="0.3"):
    """Kotak judul kecil — pakai UI_CHARS agar otomatis fallback ke ASCII."""
    tl = UI_CHARS['tl']; tr = UI_CHARS['tr']
    bl = UI_CHARS['bl']; br = UI_CHARS['br']
    h  = UI_CHARS['h'];  v  = UI_CHARS['v']
    bar = h * 35
    return (
        f"\n{Warna.CYAN + Warna.TERANG}"
        f"  {tl}{bar}{tr}\n"
        f"  {v}      CURSED ISLAND ESCAPE         {v}\n"
        f"  {v}   Petualangan Melarikan Diri      {v}\n"
        f"  {v}{Warna.ABU_GELAP}          v{versi:<25}{Warna.CYAN + Warna.TERANG}{v}\n"
        f"  {bl}{bar}{br}"
        f"{Warna.RESET}\n"
    )
