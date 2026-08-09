# Tutorial game

from .sprites import Warna
import time
from .utils import clear_screen as clear, wait_input as wait, flush_input, separator as _sep
from contextlib import suppress

def separator():
    _sep('═')

def wait_for_skip():
    
    flush_input()
    time.sleep(0.02)
    with suppress(EOFError, KeyboardInterrupt):
        response = input(f"{Warna.ABU_GELAP}[ENTER lanjut / ketik 'skip' untuk lewati] {Warna.RESET}").strip().lower()
        return 'skip' if response == 'skip' else None
    return None

def tutorial_eksplorasi():
    clear()
    separator()
    print(f"{Warna.HIJAU + Warna.TERANG}  TUTORIAL: EKSPLORASI{Warna.RESET}".center(70))
    separator()

    print()
    print(f"  {Warna.ABU_GELAP}(Ketik 'skip' untuk melewati bagian ini){Warna.RESET}")
    print()
    print(f"  {Warna.KUNING}Cara Bergerak:{Warna.RESET}")
    print(f"    {Warna.CYAN}W{Warna.RESET} = Atas   {Warna.CYAN}S{Warna.RESET} = Bawah")
    print(f"    {Warna.CYAN}A{Warna.RESET} = Kiri   {Warna.CYAN}D{Warna.RESET} = Kanan")

    print()
    print(f"  {Warna.KUNING}Perintah Lain:{Warna.RESET}")
    print(f"    {Warna.CYAN}I{Warna.RESET}   = Buka Inventory")
    print(f"    {Warna.KUNING}B{Warna.RESET}   = Buka Toko Bran (dari mana saja!)")
    print(f"    {Warna.CYAN}Q{Warna.RESET}   = Status Quest & NPC")
    print(f"    {Warna.CYAN}X{Warna.RESET}   = Save Game")
    print(f"    {Warna.ABU_GELAP}E{Warna.RESET}   = Keluar")

    print()
    print(f"  {Warna.KUNING}Simbol di Peta:{Warna.RESET}")
    print(f"    {Warna.UNGU}P{Warna.RESET}  = Kamu")
    print(f"    {Warna.CYAN}N{Warna.RESET}  = NPC (punya sidequest penting!)")
    print(f"    {Warna.KUNING}I{Warna.RESET}  = Item")
    print(f"    {Warna.MERAH}E{Warna.RESET}  = Musuh biasa (bisa dicoba kabur)")
    print(f"    {Warna.MERAH}B{Warna.RESET}  = Boss (WAJIB dikalahkan, tidak bisa kabur!)")
    print(f"    {Warna.ABU_GELAP}#{Warna.RESET}  = Dinding")
    print(f"    {Warna.HIJAU}>{Warna.RESET}  = Pintu keluar ke area lain")

    print()
    print(f"  {Warna.KUNING}Perilaku Musuh:{Warna.RESET}")
    print(f"    Semua musuh {Warna.KUNING}DIAM di tempat{Warna.RESET} — mereka tidak mengejar kamu.")
    print(f"    Encounter terjadi hanya saat kamu {Warna.MERAH}bergerak menuju tile musuh{Warna.RESET}.")
    print(f"    Musuh yang sudah dikalahkan {Warna.HIJAU}tidak respawn{Warna.RESET} — peta makin aman.")
    print(f"    Boss menunggu di tempatnya — dekatinya hanya saat kamu siap!")

    print()
    print(f"  {Warna.KUNING}Quest Tracker HUD (kanan peta):{Warna.RESET}")
    print(f"    {Warna.KUNING}[O]{Warna.RESET} = Objektif chapter saat ini (Main Quest)")
    print(f"    {Warna.PUTIH}[M]{Warna.RESET} = Quest utama karakter aktif dengan progress bar")
    print(f"    {Warna.HIJAU}[S]{Warna.RESET} = Sidequest NPC aktif")
    print(f"    Di bawahnya ada daftar target terdekat: NPC, item, musuh, pintu.")
    print(f"    HUD tampil di SEBELAH KANAN peta — tidak terhalangi perintah!")
    print(f"    {Warna.CYAN}[S]:x/5{Warna.RESET} di header = jumlah sidequest selesai.")
    print()
    print(f"  {Warna.KUNING}Tips:{Warna.RESET}")
    print(f"    - Save (X) sering — terutama sebelum masuk area berbahaya")
    print(f"    - Gunakan Quest Tracker untuk navigasi")
    print(f"    - Ambil semua item — item seringkali dibutuhkan untuk sidequest")
    print(f"    - HP rendah? Hindari musuh dan cari Health Potion lebih dulu")
    print()

    resp = wait_for_skip()
    return resp != 'skip'

def tutorial_combat():
    clear()
    separator()
    print(f"{Warna.MERAH + Warna.TERANG}  TUTORIAL: PERTARUNGAN{Warna.RESET}".center(70))
    separator()

    print()
    print(f"  {Warna.ABU_GELAP}(Ketik 'skip' untuk melewati bagian ini){Warna.RESET}")
    print()
    print(f"  {Warna.KUNING}Sistem Kartu Poker:{Warna.RESET}")
    print(f"  Pertarungan pakai sistem kartu poker. Tiap giliran kamu punya beberapa kartu.")
    print(f"  Mainkan kombinasi kartu untuk menyerang musuh.")
    print(f"  Kombinasi yang lebih tinggi = damage lebih besar!")

    print()
    print(f"  {Warna.KUNING}Cara Main Kartu:{Warna.RESET}")
    print(f"  Ketik nomor kartu yang ingin dimainkan, pisah dengan koma.")
    print()
    print(f"    {Warna.CYAN}0{Warna.RESET}         → main 1 kartu (High Card)")
    print(f"    {Warna.CYAN}0,1{Warna.RESET}       → main 2 kartu (bisa Pair)")
    print(f"    {Warna.CYAN}0,1,2,3,4{Warna.RESET} → main 5 kartu (Straight/Flush/dll)")

    print()
    print(f"  {Warna.KUNING}Kombinasi Kartu (lemah → kuat):{Warna.RESET}")
    combos = [
        (Warna.ABU_GELAP,  "High Card",       "1 kartu saja",                         "×1.0"),
        (Warna.PUTIH,      "One Pair",         "2 kartu sama nilai (misal K♠ K♥)",      "×1.7"),
        (Warna.PUTIH,      "Two Pair",         "2 pasang berbeda",                      "×2.5"),
        (Warna.HIJAU,      "Three of a Kind",  "3 kartu sama nilai",                    "×3.4"),
        (Warna.HIJAU,      "Straight",         "5 kartu berurutan",                     "×4.2"),
        (Warna.CYAN,       "Flush",            "5 kartu lambang sama",                  "×4.7"),
        (Warna.CYAN,       "Full House",       "Three of a Kind + Pair",                "×5.6"),
        (Warna.UNGU,       "Four of a Kind",   "4 kartu sama nilai",                    "×6.5"),
        (Warna.MERAH,      "Straight Flush",   "5 kartu berurutan & lambang sama",      "×8.0"),
        (Warna.UNGU + Warna.TERANG, "Five of a Kind", "5 kartu sama nilai",            "×10.0"),
        (Warna.CYAN + Warna.TERANG,  "Royal Flush",    "10-J-Q-K-A lambang sama (MAHA TERKUAT!)", "×12.0"),
    ]
    for color, name, desc, mult in combos:
        print(f"    {color}{name:<20}{Warna.RESET} {Warna.ABU_GELAP}{desc:<34}{Warna.RESET} {Warna.KUNING}{mult} dmg{Warna.RESET}")

    print()
    print(f"  {Warna.KUNING}Damage Formula:{Warna.RESET}")
    print(f"  Damage = ATK × multiplier kartu × faktor level − DEF musuh")
    print(f"  Level-mu naikkan ATK secara signifikan — terus naik level!")
    print(f"  DEF musuh mengurangi damage — skill debuff bisa turunkan DEF mereka.")

    print()
    print(f"  {Warna.KUNING}Tingkat Kesulitan Musuh:{Warna.RESET}")
    print(f"  Musuh biasa memiliki HP sekitar {Warna.KUNING}80-150{Warna.RESET}, ATK {Warna.MERAH}12-22{Warna.RESET}.")
    print(f"  Boss jauh lebih kuat — persiapkan skill dan item sebelum menghadapinya.")
    print(f"  Musuh veteran dan elite bisa menyerang cukup keras; jangan anggap remeh!")

    print()
    print(f"  {Warna.KUNING}Aksi Lain di Pertarungan:{Warna.RESET}")
    print(f"    {Warna.CYAN}[S]{Warna.RESET}       = Gunakan Skill (buff/debuff/heal)")
    print(f"    {Warna.KUNING}[I]{Warna.RESET}       = Gunakan Item dari inventory")
    print(f"    {Warna.KUNING}[D 0,1]{Warna.RESET}   = Buang kartu & ambil baru (3 slot/battle)")
    print(f"    {Warna.ABU_GELAP}[P]{Warna.RESET}       = Lewati giliran (energy regen +5)")
    print(f"    {Warna.MERAH}[OT]{Warna.RESET}      = Aktifkan OVERTIME (setelah bar penuh)")
    print(f"    {Warna.MERAH}[F]{Warna.RESET}       = Coba kabur (25% sukses, GAGAL saat lawan Boss!)")

    print()
    print(f"  {Warna.KUNING + Warna.TERANG}⚡ QUICK TIME EVENT (QTE) DODGE:{Warna.RESET}")
    print(f"  Setiap kali musuh mau menyerang, muncul {Warna.KUNING}QTE Prompt{Warna.RESET}.")
    print(f"  Tekan tombol yang ditampilkan ({Warna.CYAN}Z / X / C / V{Warna.RESET}) + ENTER dalam waktu singkat.")
    print(f"  Sukses QTE → {Warna.HIJAU}~80% chance dodge{Warna.RESET} serangan musuh!")
    print(f"  Gagal QTE → {Warna.ABU_GELAP}15% chance dodge{Warna.RESET} (keberuntungan murni).")
    print(f"  Shadow Step skill + QTE = {Warna.CYAN}95% dodge chance{Warna.RESET} — hampir kebal!")

    print()
    print(f"  {Warna.KUNING + Warna.TERANG}⚡ MODE OVERTIME:{Warna.RESET}")
    print(f"  Serang terus-menerus untuk mengisi bar Overtime.")
    print(f"  Setelah {Warna.KUNING}8 turn serangan{Warna.RESET}, bar penuh → ketik {Warna.MERAH}[OT]{Warna.RESET} untuk aktifkan!")
    print(f"  {Warna.MERAH}Efek Overtime:{Warna.RESET} Kebal serangan 2 turn + Damage ×1.75 + 2 combo hand")
    print(f"  {Warna.MERAH}Trade-off:{Warna.RESET} Menghabiskan {Warna.KUNING}90% Energy{Warna.RESET} semua karakter saat diaktifkan!")
    print(f"  Pakai Overtime di waktu yang tepat — jangan saat energy dibutuhkan untuk skill!")
    print()

    resp = wait_for_skip()
    return resp != 'skip'

def tutorial_skills():
    clear()
    separator()
    print(f"{Warna.CYAN + Warna.TERANG}  TUTORIAL: SKILL & NPC SIDEQUEST{Warna.RESET}".center(70))
    separator()

    print()
    print(f"  {Warna.ABU_GELAP}(Ketik 'skip' untuk melewati bagian ini){Warna.RESET}")
    print()

    # Skill System
    print(f"  {Warna.KUNING}Sistem Skill:{Warna.RESET}")
    print(f"  Kartu = sumber damage utama. Skill = pendukung strategis.")
    print(f"  Skill TIDAK dirancang untuk spam — pakai di saat yang tepat!")
    print()
    print(f"  {Warna.KUNING}Jenis Skill:{Warna.RESET}")
    skill_types = [
        (Warna.HIJAU,   "Heal",    "Pulihkan HP sendiri. Penting saat kondisi kritis."),
        (Warna.CYAN,    "Buff",    "Naikkan ATK atau DEF beberapa giliran."),
        (Warna.KUNING,  "Debuff",  "Turunkan ATK atau DEF musuh — kartu jadi makin mematikan!"),
        (Warna.UNGU,    "Special", "Efek unik (stun musuh, regen energy, risk-reward)."),
    ]
    for color, stype, desc in skill_types:
        print(f"    {color}[{stype}]{Warna.RESET} {desc}")

    print()
    print(f"  {Warna.KUNING}Skill per Karakter:{Warna.RESET}")
    char_skills = [
        ("Vio",      "System Hack (DEF Debuff)", "Signal Jam (ATK Debuff)", "Gacha Fortune (Random Buff)"),
        ("Haikaru",  "Pattern Analysis (DEF+ATK Debuff)", "Focus Mind (ATK Buff)", "Strategic Gambit (Risk/Reward)"),
        ("Aolinh",   "Healing Melody (Heal)", "Harmonic Shield (DEF Buff)", "Rhythm Boost (ATK Buff+Heal)"),
        ("Arganta",  "Shadow Step (Dodge Buff)", "Survival Instinct (Heal+Energy)", "Scout Mark (ATK Debuff)"),
        ("Ignatius", "EMP Stun (Buat musuh skip 1 turn)", "Overclock (ATK Buff)", "Emergency Repair (Heal+Cleanse)"),
    ]
    for char, s1, s2, s3 in char_skills:
        print(f"    {Warna.TERANG}{char}:{Warna.RESET} {s1}, {s2}, {s3}")

    print()
    print(f"  {Warna.KUNING}Cooldown Skill:{Warna.RESET}")
    print(f"  Setiap skill punya cooldown (2-4 giliran) — tidak bisa spam!")
    print(f"  Cooldown tersisa ditampilkan di layar pilih skill.")

    print()
    print(f"  {Warna.KUNING}Energy (EN):{Warna.RESET}")
    print(f"  Skill butuh energy. Kamu mulai dengan {Warna.CYAN}30 EN{Warna.RESET} per pertarungan.")
    print(f"  Energy regen otomatis +{Warna.CYAN}2 EN{Warna.RESET} tiap giliran — hemat penggunaannya!")
    print(f"  Lewati giliran [P] untuk regen +5 EN lebih cepat.")
    print(f"  {Warna.MERAH}Perhatian:{Warna.RESET} Mengaktifkan OVERTIME menguras 90% energy!")
    print(f"  Pikirkan matang-matang sebelum menekan [OT] — energy susah dipulihkan.")

    print()
    separator()
    print()

    # NPC Sidequest System
    print(f"  {Warna.KUNING}Sistem NPC & Sidequest:{Warna.RESET}")
    print(f"  Ada {Warna.CYAN}5 NPC{Warna.RESET} yang bisa kamu temui selama petualangan.")
    print(f"  Mereka punya masalah masing-masing — dan bisa membantumu jika dibantu!")
    print()
    print(f"  NPC {Warna.MERAH}tidak ikut bertarung bersamamu{Warna.RESET} — tapi mereka kasih {Warna.KUNING}KEY ITEM{Warna.RESET}")
    print(f"  penting yang dibutuhkan untuk melanjutkan perjalanan.")
    print()
    print(f"  {Warna.KUNING}Cara kerja sidequest [{Warna.HIJAU}S{Warna.KUNING}]:{Warna.RESET}")
    print(f"    1. Temui NPC di lokasinya — perhatikan ikon {Warna.CYAN}N{Warna.RESET} di peta")
    print(f"    2. Dengarkan cerita mereka → terima sidequest")
    print(f"    3. Selesaikan objective {Warna.CYAN}◆{Warna.RESET} (cari item / kalahkan musuh)")
    print(f"    4. Kembali ke NPC → terima {Warna.HIJAU}Key Item{Warna.RESET} reward")
    print(f"    5. Key item ini WAJIB untuk membuka chapter berikutnya!")
    print()
    print(f"  {Warna.KUNING}Contoh manfaat sidequest:{Warna.RESET}")
    impacts = [
        ("Haikaru",  "Catatan Sandi → buka akses dokumen rahasia"),
        ("Aolinh",   "Rekaman Musik → distraksi penjaga di jalur penting"),
        ("Arganta",  "Peta Jalur → temukan rute tersembunyi"),
        ("Ignatius", "EMP Device → lemahkan sistem keamanan boss"),
        ("Vio",      "USB Evidence → kunci untuk membuka ending final"),
    ]
    for npc, impact in impacts:
        print(f"    {Warna.CYAN}{npc:<10}{Warna.RESET} → {impact}")
    print()
    print(f"  {Warna.ABU_GELAP}Tips: Tidak semua sidequest terbuka di awal — ikuti chapter progress!")
    print(f"        Pantau {Warna.CYAN}[S]:{Warna.RESET} di HUD untuk melihat berapa sidequest yang sudah selesai.{Warna.RESET}")
    print()

    resp = wait_for_skip()
    return resp != 'skip'

def tutorial_chapter():
    clear()
    separator()
    print(f"{Warna.UNGU + Warna.TERANG}  TUTORIAL: CHAPTER & PROGRESS{Warna.RESET}".center(70))
    separator()

    print()
    print(f"  {Warna.ABU_GELAP}(Ketik 'skip' untuk melewati bagian ini){Warna.RESET}")
    print()
    print(f"  {Warna.KUNING}Struktur Game — 6 Chapter:{Warna.RESET}")
    chapters = [
        (1, "Escape",           "Kabur dari area awal. Temukan jalan keluar!"),
        (2, "Exploration  [★]", "Jelajahi area baru. Kalahkan Boss Ch.2!"),
        (3, "Investigation",    "Temui NPC, selesaikan sidequest penting."),
        (4, "Confrontation [★]","Gunakan item sidequest. Kalahkan Boss Ch.4!"),
        (5, "Evidence",         "Kumpulkan bukti. Selesaikan sidequest tersisa."),
        (6, "Final        [★]", "Konfrontasi terakhir — Boss paling kuat!"),
    ]
    for num, name, desc in chapters:
        is_boss = "[★]" in name
        star_color = Warna.MERAH if is_boss else ""
        clean_name = name.replace("  [★]", " ★").replace(" [★]", " ★")
        print(f"    {star_color}Ch.{num} {clean_name:<22}{Warna.RESET} {Warna.ABU_GELAP}{desc}{Warna.RESET}")

    print()
    print(f"  {Warna.KUNING}Syarat naik chapter:{Warna.RESET}")
    print(f"    Ch.1 → 2 : Selesaikan quest awal & tinggalkan area starting")
    print(f"    Ch.2 → 3 : Kalahkan Boss Ch.2")
    print(f"    Ch.3 → 4 : Minimal {Warna.CYAN}2 sidequest NPC{Warna.RESET} selesai")
    print(f"    Ch.4 → 5 : Kalahkan Boss Ch.4")
    print(f"    Ch.5 → 6 : Minimal {Warna.CYAN}4 sidequest NPC{Warna.RESET} + item khusus dari NPC Vio")
    print()
    print(f"  {Warna.MERAH}⚠ Chapter terakhir hanya terbuka jika cukup sidequest sudah selesai!{Warna.RESET}")
    print(f"  Jangan skip sidequest — semuanya ada dampak ke jalan cerita.")
    print()
    print(f"  {Warna.KUNING}Objektif di HUD:{Warna.RESET}")
    print(f"    {Warna.KUNING}[O]{Warna.RESET} = Objektif chapter aktif (Main)")
    print(f"    {Warna.PUTIH}[M]{Warna.RESET} = Quest utama karakter dengan progress bar")
    print(f"    {Warna.HIJAU}[S]{Warna.RESET} = Sidequest NPC aktif")
    print(f"    {Warna.CYAN}[S]:x/5{Warna.RESET} = Di header HUD — berapa sidequest sudah selesai")
    print()

    resp = wait_for_skip()
    return resp != 'skip'

def tutorial_lengkap():
    clear()
    separator()
    print(f"{Warna.KUNING + Warna.TERANG}  SELAMAT DATANG DI CURSED ISLAND ESCAPE!{Warna.RESET}".center(70))
    separator()

    print()
    print(f"  Kamu terjebak di sebuah pulau terpencil yang penuh bahaya.")
    print(f"  Satu-satunya jalan: kabur, cari bantuan, dan ungkap kebenaran!")
    print()
    print(f"  Tutorial ini terdiri dari 4 bagian:")
    print(f"    1. Eksplorasi & navigasi peta")
    print(f"    2. Sistem pertarungan kartu poker + Overtime")
    print(f"    3. Skill & NPC sidequest")
    print(f"    4. Struktur chapter & cara baca HUD")
    print()
    print(f"  {Warna.ABU_GELAP}(Kamu bisa skip tiap bagian dengan mengetik 'skip'){Warna.RESET}")
    print()

    wait()

    parts_done = []

    if not tutorial_eksplorasi():
        parts_done.append(f"{Warna.ABU_GELAP}✓ Eksplorasi dilewati{Warna.RESET}")
    else:
        parts_done.append(f"{Warna.HIJAU}✓ Eksplorasi{Warna.RESET}")

    if not tutorial_combat():
        parts_done.append(f"{Warna.ABU_GELAP}✓ Combat dilewati{Warna.RESET}")
    else:
        parts_done.append(f"{Warna.HIJAU}✓ Combat{Warna.RESET}")

    if not tutorial_skills():
        parts_done.append(f"{Warna.ABU_GELAP}✓ Skill & NPC dilewati{Warna.RESET}")
    else:
        parts_done.append(f"{Warna.HIJAU}✓ Skill & NPC{Warna.RESET}")

    if not tutorial_chapter():
        parts_done.append(f"{Warna.ABU_GELAP}✓ Chapter dilewati{Warna.RESET}")
    else:
        parts_done.append(f"{Warna.HIJAU}✓ Chapter Progress{Warna.RESET}")

    clear()
    separator()
    print(f"{Warna.HIJAU + Warna.TERANG}  SIAP BERMAIN!{Warna.RESET}".center(70))
    separator()
    print()
    for p in parts_done:
        print(f"  {p}")
    print()
    print(f"  {Warna.KUNING}Ringkasan cepat:{Warna.RESET}")
    print(f"  - WASD bergerak, hindari musuh jika HP rendah")
    print(f"  - Main kartu poker untuk damage — kombinasi tinggi = damage besar")
    print(f"  - OVERTIME: damage besar tapi habiskan 90% energy — pakai bijak!")
    print(f"  - Skill = buff/debuff/heal strategis, bukan spam")
    print(f"  - Temui NPC [N] → sidequest [S] → key item → buka chapter baru")
    print(f"  - Pantau {Warna.KUNING}[O]{Warna.RESET} chapter obj, {Warna.CYAN}[S]:x/5{Warna.RESET} sidequest, {Warna.PUTIH}[M]{Warna.RESET} main quest di HUD")
    print(f"  - QTE Dodge: tekan tombol yang ditampilkan saat musuh mau serang!")
    print(f"  - {Warna.UNGU}Secret:{Warna.RESET} di Ch.6, temukan Epstein Phone → NPC rahasia bisa muncul...")
    print(f"  - {Warna.ABU_GELAP}(Psst: Joker mungkin membantumu jika nasib sedang buruk...){Warna.RESET}")
    print(f"  - Save (X) sering, terutama sebelum masuk area berbahaya!")
    print()
    print(f"  {Warna.HIJAU}Selamat berpetualangan — temukan jalan keluarmu!{Warna.RESET}")
    print()

    wait("Tekan ENTER untuk mulai petualangan... ")

if __name__ == "__main__":
    tutorial_lengkap()
