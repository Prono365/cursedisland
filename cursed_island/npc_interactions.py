# Interaksi NPC dan sidequest

from .sprites import Warna
import time
from contextlib import suppress
from .utils import clear_screen, wait_input, separator, flush_input

#  NPC sidequest data - available_chapter, reward_item, chapter_unlock tracking
#  DATA SIDEQUEST NPC
#  Setiap NPC punya:
#    available_chapter   : minimum chapter agar bisa ditemui
#    location            : lokasi di mana NPC bisa ditemui
#    reward_item         : item kunci yang diberikan setelah sidequest selesai
#    reward_flag         : story flag yang di-set setelah reward diberikan
#    required_item / required_action : syarat penyelesaian sidequest
#    main_quest_impact   : kalimat singkat dampak ke main quest
#    chapter_unlock      : sidequest ini membuka akses ke chapter ini
NPC_SIDEQUEST_DATA = {
    'haikaru': {
        'name':             'Haikaru Fumika',
        'title':            'Analis Strategis',
        'available_chapter': 2,
        'location':          'prison_north',
        'sidequest_id':      'sq_haikaru',
        'sidequest_title':   'Kode yang Terlupakan',
        'required_item':     'Buku Catatan Haikaru',
        'required_action':   None,
        'reward_item':       'Catatan Sandi Haikaru',
        'reward_flag':       'haikaru_sidequest_done',
        'main_quest_impact': 'Decode dokumen rahasia mansion — kunci untuk maju ke Ch.4',
        'chapter_unlock':    4,

        # Dialog pertama kali ketemu
        'intro_dialog': [
            ("Haikaru", "..."),
            ("Haikaru", "Kamu... bukan penjaga."),
            ("Haikaru", "47 detik untuk sampai ke sini dari koridor barat. Kamu tidak berlari. Menarik."),
            (None,      "Gadis itu berdiri tegak meskipun dalam seragam penjara. Matanya menganalisa setiap gerakan kamu."),
            ("Haikaru", "Haikaru Fumika. 12 tahun. IQ 178. Dijebloskan ke sini karena 'terlalu tahu'."),
            ("Haikaru", "Tapi mereka melakukan kesalahan. Mereka pikir mengambil kebebasanku akan menghentikanku berpikir."),
            ("Haikaru", "Salah. Setiap detik di sini — aku hitung. Setiap pola penjaga — aku hafal."),
            ("Haikaru", "Kamu butuh bantuanku. Dan aku butuh sesuatu dari kamu."),
        ],

        'quest_dialog': [
            ("Haikaru", "Guard veteran di Wing-B menyita buku catatanku. 312 halaman. Analisis enkripsi dan peta blind spot."),
            ("Haikaru", "Mereka pikir kalau buku itu diambil, aku berhenti berpikir. Salah kalkulasi besar."),
            ("Haikaru", "Penjaga itu patroli area koridor timur laut penjara ini. Bukan target sulit kalau tahu polanya."),
            (None,      "Haikaru menyerahkan diagram rute patroli yang digambar dari ingatan."),
            ("Haikaru", "Kalahkan guard veteran itu. Buku itu pasti ada di sakunya — dia tidak akan menaruh di loker."),
            ("Haikaru", "Kembalikan buku itu padaku. Aku akan decode semua dokumen mansion yang tidak bisa kalian baca."),
            ("Haikaru", "Data di buku itu... bukan sekadar catatan. Itu kunci sistem enkripsi seluruh jaringan Epstein."),
        ],

        # Dialog saat quest selesai
        'complete_dialog': [
            ("Haikaru", "Kamu berhasil. 94% lebih cepat dari estimasiku. Kecepatanmu mengejutkan."),
            (None,      "Haikaru segera membuka buku catatan, tangannya bergerak cepat membalik halaman."),
            ("Haikaru", "...Ada. Persis di halaman 247. Cipher Vigenère, kunci 'LITTLE_SAINT_JAMES'."),
            ("Haikaru", "Ini bukan sekadar catatan keuangan. Ini jadwal 'kunjungan'. Nama-nama."),
            ("Haikaru", "Aku salin bagian terpenting. Ambil ini."),
            (None,      "Kamu menerima [Catatan Sandi Haikaru] — kunci untuk decode dokumen mansion."),
            ("Haikaru", "Jangan sampai jatuh ke tangan penjaga. Kalau itu terjadi, semua orang di pulau ini dalam bahaya."),
        ],

        # Dialog setelah quest selesai — muncul SEKALI saat kembali mengobrol
        'after_complete_dialog': [
            ("Haikaru", "...Aku masih menganalisa fragmentasi data di catatan itu. Ada anomali di halaman 89."),
            ("Haikaru", "Pola enkripsi berubah tiap tiga bulan. Artinya ada orang dalam yang update sistemnya."),
            (None,      "Haikaru menyerahkan selembar kecil kertas tambahan."),
            ("Haikaru", "Tambahan. Koordinat yang selalu dipakai untuk 'drop point'. Mungkin berguna nanti."),
            ("Haikaru", "Kalau kamu bertemu jalan buntu — lihat polanya. Setiap sistem punya celah. Cari saja."),
        ],
    },

    'aolinh': {
        'name':             'Ao Lin',
        'title':            'Violinis & Harapan',
        'available_chapter': 2,
        'location':          'theater',
        'sidequest_id':      'sq_aolinh',
        'sidequest_title':   'Suara yang Terkubur',
        'required_item':     None,
        'required_action':   'defeat_theater_commander',  # Set by combat when theater_master is defeated (Aolinh only)
        'reward_item':       'Rekaman Distraksi Aolinh',
        'reward_flag':       'aolinh_sidequest_done',
        'main_quest_impact': 'Rekaman musik mengalihkan penjaga dock (Ch4 — akses kapal)',
        'chapter_unlock':    4,

        # Dialog pertama kali ketemu
        'intro_dialog': [
            (None,      "Suara biola mengalun pelan dari balik tirai panggung. Melodi yang... terlalu indah untuk tempat seperti ini."),
            ("Aolinh",  "...Siapa di sana?"),
            (None,      "Seorang gadis muncul dari balik tirai. Biola di tangan, earphone biru menggantung di leher."),
            ("Aolinh",  "O — kamu bukan penjaga. Syukurlah. Jantungku hampir copot."),
            ("Aolinh",  "Namaku Ao Lin. Panggil Aolinh. Dari Hongkong. Dipisah dari Jiejie-ku di sini."),
            (None,      "Matanya berkaca-kaca sesaat, tapi dia tersenyum — senyum yang dipaksakan tapi tulus."),
            ("Aolinh",  "音乐给我力量 — Musik memberi kekuatan. Selama aku bisa main biola, aku tidak akan menyerah."),
            ("Aolinh",  "Kamu mau cari cara keluar? Aku mau bantu. Tapi aku butuh sesuatu darimu dulu."),
        ],

        'quest_dialog': [
            ("Aolinh",  "Theater Commander di area backstage ini — dia yang mengurung aku. Dia juga yang ambil HP-ku."),
            (None,      "Aolinh memandang ke arah pintu besi di balik panggung. Matanya berkilat tapi suaranya tenang."),
            ("Aolinh",  "Kalahkan Theater Commander itu. Bebaskan backstage. Ambil HP-ku kembali."),
            ("Aolinh",  "Di HP itu ada rekaman performance terakhirku sebelum ditangkap. Masih ada di sana — aku yakin."),
            ("Aolinh",  "Rekaman itu bisa jadi senjata. Penjaga dermaga punya titik lemah: mereka berhenti fokus kalau ada musik."),
            ("Aolinh",  "Satu rekaman loop yang tepat, dan jalur dermaga terbuka 10 menit. Cukup untuk lewat tanpa konflik."),
            ("Aolinh",  "♪ Kalahkan Theater Commander. Ambil HP-ku. Dan kita semua bisa pulang. ♪"),
        ],

        # Dialog saat quest selesai
        'complete_dialog': [
            ("Aolinh",  "Kamu berhasil! Oh, Dewa — terimakasih, terimakasih banyak!"),
            (None,      "Aolinh memeluk HP-nya erat-erat, kemudian segera memutar sesuatu."),
            ("Aolinh",  "Ini... rekaman terakhirku sebelum ditangkap. Competition di Hongkong."),
            ("Aolinh",  "Aku buat versi loop-nya. Sambungkan ke speaker dermaga, dan semua penjaga akan terpaku 10 menit."),
            (None,      "Aolinh menyerahkan USB kecil. Di labelnya tertulis: 'DISTRAKSI — JANGAN DIPUTAR SEKARANG'."),
            ("Aolinh",  "Gunakan ini saat kalian butuh jalan lewat dermaga tanpa keributan."),
            ("Aolinh",  "Dan... kalau kalian menemukan Jiejie-ku di suatu tempat — tolong beritahu aku. ♪"),
        ],

        # Dialog setelah quest selesai — muncul SEKALI saat kembali mengobrol
        'after_complete_dialog': [
            (None,      "Aolinh sedang memainkan melodi pelan di atas panggung. Senyumnya lebih tenang dari sebelumnya."),
            ("Aolinh",  "Oh, kamu lagi. Duduk, kalau mau. ♪"),
            ("Aolinh",  "Aku nulis lagu baru. Tentang pulau ini. Tentang kita semua."),
            ("Aolinh",  "Judulnya... belum ada. Mungkin 'Lari dari Kegelapan'. Mungkin 'Kita Akan Pulang'."),
            (None,      "Dia memainkan beberapa nada lembut — melodi yang entah kenapa terasa seperti harapan."),
            ("Aolinh",  "Apapun yang terjadi nanti — aku percaya kalian bisa. 音乐给我力量. ♪"),
        ],
    },

    'arganta': {
        'name':             'Amerigo Arganta',
        'title':            'Pathfinder & Navigator',
        'available_chapter': 2,
        'location':          'beach',
        'sidequest_id':      'sq_arganta',
        'sidequest_title':   'Warisan yang Direbut',
        'required_item':     'Kompas Nonno Arganta',
        'required_action':   None,
        'reward_item':       'Peta Jalur Rahasia',
        'reward_flag':       'arganta_sidequest_done',
        'main_quest_impact': 'Reveal jalur alternatif ke laboratorium bawah tanah (Ch4/Ch5)',
        'chapter_unlock':    4,

        # Dialog pertama kali ketemu
        'intro_dialog': [
            (None,      "Seseorang bersembunyi di balik batu karang pantai. Pisau lipat siap di tangan."),
            ("Arganta", "Fermo! Diam dulu — siapa kamu?!"),
            (None,      "Pemuda itu menatap tajam, tapi menurunkan pisaunya perlahan saat mengenali pakaianmu."),
            ("Arganta", "...Seragam penjara. Jadi kamu juga tahanan. Amerigo Arganta. Napoli."),
            ("Arganta", "Keluargaku dibunuh karena Papà mendokumentasikan aktivitas di pulau ini."),
            (None,      "Tangannya menggenggam kompas tua. Jarinya menelusuri ukiran di permukaannya."),
            ("Arganta", "Nonno bilang: 'La via è sempre avanti.' Jalan selalu ada di depan."),
            ("Arganta", "Aku tidak kabur dari sini tanpa bukti. Per famiglia. Kamu mau bantu?"),
        ],

        'quest_dialog': [
            ("Arganta", "Kompas Nonno-ku. Penjaga pantai mengambilnya waktu penangkapan — tapi aku lihat ke mana perginya."),
            ("Arganta", "Guard veteran di pantai barat. Dia yang mengambilnya. Aku hampir bisa merasakannya di sakunya."),
            (None,      "Arganta mengepalkan tangan. Amarah yang tertahan."),
            ("Arganta", "Di dalam kompas itu ada peta yang diukir Nonno. Jalur yang tidak ada di blueprint resmi pulau ini."),
            ("Arganta", "Kalahkan guard veteran itu. Ambil kompas dari sakunya. Ini bukan pilihan — ini keharusan."),
            ("Arganta", "Terowongan yang Nonno catat itu tembus ke laboratorium bawah tanah. Akses tersembunyi."),
            ("Arganta", "Per famiglia. Kompas itu satu-satunya warisan yang tersisa."),
        ],

        # Dialog saat quest selesai
        'complete_dialog': [
            ("Arganta", "Il compasso! Grazie mille — mille grazie!"),
            (None,      "Arganta membuka kompas dengan hati-hati, mengeluarkan lensa kecil dari sakunya."),
            ("Arganta", "Eccola — ini dia. Peta Nonno. Lihat — terowongan ini dimulai di balik batu besar pantai barat."),
            ("Arganta", "Nonno pernah bantu konstruksi awal pulau ini. Dia tahu setiap sudut yang tidak ada di blueprint."),
            (None,      "Arganta menyalin peta ke selembar kertas dengan tangan yang terlatih."),
            ("Arganta", "Ambil ini. Peta Jalur Rahasia. Terowongan ini tembus langsung ke basement laboratorium."),
            ("Arganta", "Kalau kalian butuh masuk ke lab tanpa ketahuan — ini jalannya. Per Nonno."),
        ],

        # Dialog setelah quest selesai — muncul SEKALI saat kembali mengobrol
        'after_complete_dialog': [
            (None,      "Arganta sedang mengukir sesuatu di tanah pasir dengan ranting. Peta improvisasi."),
            ("Arganta", "Ah, kamu. Duduk — aku baru ingat sesuatu dari catatan Nonno."),
            ("Arganta", "Ada menara pantai di ujung timur. Nonno catat itu sebagai 'punto di osservazione' — titik observasi."),
            ("Arganta", "Dari sana bisa lihat seluruh pulau. Kalau ada sesuatu yang perlu dipantau — itu tempatnya."),
            (None,      "Arganta menggenggam kompasnya sejenak, lalu menatap cakrawala."),
            ("Arganta", "Keluargaku meninggal untuk pulau ini. Aku tidak akan membiarkan pengorbanan mereka sia-sia. Capisci?"),
        ],
    },

    'ignatius': {
        'name':             'Ignatius Forgers',
        'title':            'Insinyur Jenius',
        'available_chapter': 2,
        'location':          'basement',
        'sidequest_id':      'sq_ignatius',
        'sidequest_title':   'Komponen EMP yang Disita',
        'required_items':    ['Kapasitor Besar', 'Relay Switch', 'Copper Coil'],
        'required_item':     None,
        'required_action':   None,
        'reward_item':       'EMP Device',
        'reward_flag':       'ignatius_sidequest_done',
        'main_quest_impact': 'EMP Device matikan sistem elektronik Ghislaine — wajib untuk Boss Ch.4 di Pusat Kontrol',
        'chapter_unlock':    4,

        # Dialog pertama kali ketemu
        'intro_dialog': [
            (None,      "Ruang basement penuh kabel dan komponen elektronik berserakan. Di tengahnya, seorang anak berumur 12 tahun bekerja tanpa henti."),
            ("Ignatius", "Oh! Ada tamu. Tunggu — jangan sentuh apapun. Serius."),
            (None,      "Dia melepas kacamata, mengusap tangan di baju, lalu mengulurkan tangan."),
            ("Ignatius", "Ignatius Forgers. Insinyur berbakat. Juara lomba sains tiga tahun berturut-turut."),
            ("Ignatius", "Mereka menangkapku karena penemuanku. Generator pulsa elektromagnetik mini. Mereka mau menggunakannya sebagai senjata."),
            ("Ignatius", "Aku tolak. Jadi mereka taruh aku di sini. Kesalahan besar dari pihak mereka."),
            (None,      "Dia tersenyum lebar dan menunjuk panel listrik besar di dinding."),
            ("Ignatius", "Mereka menaruhku di sebelah seluruh infrastruktur listrik pulau ini. Waktunya bekerja!"),
        ],

        'quest_dialog': [
            ("Ignatius", "EMP Device grade industrial. Bisa matikan semua sistem keamanan elektronik — kunci magnetis, alarm, kamera."),
            ("Ignatius", "Tapi tiga komponen kuncinya tidak ada di basement ini. Mereka sudah diambil penjaga."),
            (None,      "Ignatius menyerahkan daftar komponen dengan diagram teknis yang detail."),
            ("Ignatius", "Pertama: Kapasitor Besar. Guard elite di mansion ambil dari gudang supply-ku waktu penangkapan."),
            ("Ignatius", "Kedua: Relay Switch. Tech guard di Pusat Kontrol menyitanya. Dia pikir itu alat komunikasi biasa."),
            ("Ignatius", "Ketiga: Copper Coil. Ada di mansion guard atau mercenary yang patroli area teater — sisa instalasi lama."),
            ("Ignatius", "Kalahkan mereka, ambil komponen-komponen itu, bawa ke sini. Aku rakit dalam 20 menit."),
            ("Ignatius", "EMP ini wajib sebelum konfrontasi Ghislaine Maxwell di Pusat Kontrol. Tanpa ini, kita masuk perangkap. Logis!"),
        ],

        # Dialog saat quest selesai
        'complete_dialog': [
            ("Ignatius", "Sempurna! Semua komponen lengkap. Mundur dulu — ini butuh konsentrasi penuh."),
            (None,      "Ignatius bekerja dengan kecepatan luar biasa. Tangannya bergerak seperti sudah hafal setiap langkah."),
            ("Ignatius", "Selesai. 18 menit 43 detik. Rekor pribadi."),
            (None,      "Sebuah perangkat kecil berwarna abu-abu dengan tombol merah di tengahnya diletakkan di tanganmu."),
            ("Ignatius", "Tekan tombol merah ini dalam radius 50 meter dari target. Jangkauan efektif: 30 meter."),
            ("Ignatius", "Efek: semua sistem elektronik mati selama 4–6 menit. Termasuk senjata listrik penjaga."),
            ("Ignatius", "Gunakan tepat sebelum konfrontasi dengan Ghislaine Maxwell di Pusat Kontrol. Waktu adalah segalanya!"),
        ],

        # Dialog setelah quest selesai — muncul SEKALI saat kembali mengobrol
        'after_complete_dialog': [
            (None,      "Ignatius sedang membongkar panel listrik lain, tampaknya sedang mengerjakan sesuatu yang baru."),
            ("Ignatius", "Oh! Pas banget. Aku bikin peningkatan kecil untuk EMP itu."),
            (None,      "Dia menyerahkan sepotong kecil komponen tambahan."),
            ("Ignatius", "Perluasan jangkauan. Sekarang efektif 40 meter, bukan 30. Selesai dalam 11 menit."),
            ("Ignatius", "Satu lagi — kalau kamu pakai EMP di dekat air, interferensinya dobel. Berguna untuk situasi tertentu."),
            ("Ignatius", "Tips rekayasa gratis. Tagihannya nanti. Bercanda. ...Mungkin."),
        ],
    },

    'vio': {
        'name':             'Vio',
        'title':            'Peretas & Pakar Enkripsi',
        'available_chapter': 4,
        'location':          'laboratory',
        'sidequest_id':      'sq_vio',
        'sidequest_title':   'USB Kebenaran',
        'required_item':     'USB Security Drive',
        'required_action':   None,
        'reward_item':       'USB Evidence Drive',
        'reward_flag':       'vio_sidequest_done',
        'main_quest_impact': 'USB Evidence Drive — 47 GB bukti kejahatan untuk upload di Ch.6 (WAJIB untuk true ending)',
        'chapter_unlock':    6,

        # Dialog pertama kali ketemu
        'intro_dialog': [
            (None,      "Di ruang server mansion, layar komputer masih menyala. Seseorang sedang mengetik cepat."),
            ("Vio",     "Eh, tunggu — kamu bukan penjaga."),
            (None,      "Pemuda berambut merah dengan jaket hoodie berbalik, mata kritisnya menilaimu sekilas."),
            ("Vio",     "Vio. Umur 13. Spesialis enkripsi, dan... terpaksa jadi peretas etis sekarang."),
            ("Vio",     "Aku di sini karena ketidaksengajaan murni. Lagi mengerjakan sesuatu, tiba-tiba diculik."),
            ("Vio",     "Tapi mereka menaruhku di sebelah server farm mereka. Kesalahan terbesar yang pernah mereka buat."),
            (None,      "Dia menunjuk layar yang penuh baris kode dan enkripsi."),
            ("Vio",     "Sistem enkripsi mereka pakai AES-256. Lumayan. Tapi ada celah di implementasinya."),
            ("Vio",     "Beri aku perangkat keras yang tepat dan aku bisa ekstrak semua yang ada di server ini."),
        ],

        'quest_dialog': [
            ("Vio",     "Aku butuh USB Security Drive — chip enkripsi hardware spesifik. Tidak bisa diganti."),
            ("Vio",     "Ilmuwan di laboratorium Maxwell punya satu. Dia pakai buat transfer data riset terenkripsi."),
            (None,      "Vio mengetuk jari ke meja, suaranya datar tapi matanya fokus."),
            ("Vio",     "Scientist yang patroli area barat lab. Kalahkan dia, ambil USB dari sakunya."),
            ("Vio",     "...Aku bisa bajak kata sandi 16 karakter dalam 3 menit. Bukan masalah. Yang masalah: dapat USB-nya."),
            ("Vio",     "Dengan itu aku bisa tembus enkripsi server utama — daftar tamu, catatan transfer, rekaman pengawasan."),
            ("Vio",     "Itu bukan sekadar bukti. Itu senjata nuklir informasi. Kalau bocor ke publik... banyak orang berkuasa hancur."),
        ],

        # Dialog saat quest selesai
        'complete_dialog': [
            ("Vio",     "USB-nya ada. Oke, mulai bekerja."),
            (None,      "Vio mencolokkan USB ke port server, jarinya bergerak cepat menavigasi sistem."),
            ("Vio",     "Menembus lapisan enkripsi pertama... melewati autentikasi... mengunduh..."),
            (None,      "Layar berkedip-kedip. Bilah progres mengisi perlahan."),
            ("Vio",     "Selesai. 47 GB data. Daftar tamu dari tahun 1995 sampai sekarang. Catatan pembayaran. Rekaman pengawasan."),
            ("Vio",     "Dan... ada satu folder khusus. Labelnya 'INSURANCE'. Isinya... lebih dari yang aku bayangkan."),
            (None,      "Vio melepas USB dan memegangnya dengan hati-hati."),
            ("Vio",     "Ini bukan sekadar bukti kejahatan di pulau ini. Ini bukti siapa saja yang terlibat. Secara global."),
            ("Vio",     "Jaga ini seperti nyawa kalian. Karena secara harfiah — inilah yang akan menyelamatkan semua orang."),
            (None,      "Kamu menerima [USB Evidence Drive] — senjata paling berbahaya di pulau ini."),
        ],

        # Dialog setelah quest selesai — muncul SEKALI saat kembali mengobrol
        'after_complete_dialog': [
            (None,      "Vio sedang membaca data di layar, tapi ekspresinya jauh lebih serius dari biasanya."),
            ("Vio",     "Oh. Kamu. Aku... baru menemukan sesuatu di folder yang aku unduh tadi."),
            ("Vio",     "Ada daftar nama. Ratusan. Bukan cuma politisi atau selebriti. Ada... orang biasa juga."),
            (None,      "Dia terdiam sebentar, menatap layar dengan berat."),
            ("Vio",     "Aku tahu data adalah data. Tapi ini berbeda. Ini nyata. Ini orang-orang nyata."),
            ("Vio",     "...USB itu harus keluar dari pulau ini dengan selamat. Apapun yang terjadi pada kita."),
            ("Vio",     "Semoga kita berhasil."),
        ],
    },
}

#  FUNGSI DISPLAY DIALOG

def _print_dialog_line(speaker, line, delay=0.035):
    """Print satu baris dialog dengan format yang sesuai."""
    try:
        if speaker is None:
            # Narasi / action
            print(f"\n  {Warna.ABU_GELAP}[{line}]{Warna.RESET}")
        else:
            # Dialog karakter
            print(f"\n  {Warna.KUNING + Warna.TERANG}{speaker}{Warna.RESET}{Warna.KUNING}: {Warna.RESET}", end="")
            for char in line:
                print(char, end="", flush=True)
                time.sleep(delay)
            print()
        time.sleep(0.3)
    except (IOError, OSError, KeyboardInterrupt):
        if speaker is None:
            print(f"\n  [{line}]")
        else:
            print(f"\n  {speaker}: {line}")

def _display_npc_header(npc_data, header_text="PERTEMUAN"):
    """Tampilkan header NPC interaction."""
    separator('═')
    name  = npc_data.get('name', '???')
    title = npc_data.get('title', '')
    print(f"{Warna.CYAN + Warna.TERANG}{header_text} — {name}{Warna.RESET}".center(80))
    if title:
        print(f"{Warna.ABU_GELAP}{title.center(80)}{Warna.RESET}")
    separator('═')
    print()

def display_npc_intro(npc_id, game_state=None):
    # Menampilkan dialog pertemuan awal dengan NPC (hanya sekali)
    
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return False

    # Cek flag — jika sudah pernah ditampilkan, skip sepenuhnya
    intro_flag = f"{npc_id}_intro_shown"
    if game_state and game_state.story_flags.get(intro_flag):
        return False

    clear_screen()
    _display_npc_header(npc_data, "PERTEMUAN PERTAMA")

    for speaker, line in npc_data.get('intro_dialog', []):
        _print_dialog_line(speaker, line)

    print()
    separator()
    wait_input()

    if game_state:
        game_state.story_flags[intro_flag] = True
        # Auto-trigger sidequest jika chapter sudah cukup
        current_chapter = game_state.story_flags.get('current_chapter', 1)
        try:
            current_chapter = int(current_chapter)
        except (ValueError, TypeError):
            current_chapter = 1
        if current_chapter >= npc_data['available_chapter']:
            game_state.story_flags[f"{npc_id}_quest_available"] = True

    return True

def display_npc_quest_briefing(npc_id, game_state=None):
    # Menampilkan briefing sidequest dari NPC (hanya sekali)
    
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return False

    # Guard: jangan tampilkan ulang jika sudah pernah
    briefing_flag = f"{npc_id}_briefing_shown"
    if game_state and game_state.story_flags.get(briefing_flag):
        return False

    clear_screen()
    _display_npc_header(npc_data, "SIDEQUEST")
    print(f"  {Warna.KUNING}Quest:{Warna.RESET} {npc_data.get('sidequest_title', '')}")
    print(f"  {Warna.ABU_GELAP}Dampak: {npc_data.get('main_quest_impact', '')}{Warna.RESET}")
    separator()
    print()

    for speaker, line in npc_data.get('quest_dialog', []):
        _print_dialog_line(speaker, line)

    print()
    separator()

    # Tampilkan objective dengan [S] icon
    print(f"\n  {Warna.KUNING + Warna.TERANG}[S] SIDEQUEST OBJECTIVE{Warna.RESET}")
    if npc_data.get('required_items'):
        print(f"  {Warna.KUNING}Kumpulkan item berikut:{Warna.RESET}")
        for item in npc_data['required_items']:
            print(f"    {Warna.CYAN}◆ {item}{Warna.RESET}")
    elif npc_data.get('required_item'):
        print(f"  {Warna.KUNING}Temukan:{Warna.RESET} {Warna.CYAN}◆ {npc_data['required_item']}{Warna.RESET}")
    elif npc_data.get('required_action'):
        action_labels = {
            'defeat_theater_commander': 'Kalahkan Theater Commander di Backstage Teater',
        }
        label = action_labels.get(npc_data['required_action'], npc_data['required_action'])
        print(f"  {Warna.KUNING}Lakukan:{Warna.RESET} {Warna.CYAN}◆ {label}{Warna.RESET}")
    else:
        print(f"  {Warna.ABU_GELAP}(Tidak ada syarat khusus — bicara dengan NPC kembali){Warna.RESET}")

    print(f"\n  {Warna.HIJAU}◈ Reward: {npc_data.get('reward_item', '???')}{Warna.RESET}")
    print()
    separator()
    wait_input()

    if game_state:
        game_state.story_flags[f"{npc_id}_quest_active"] = True
        game_state.story_flags[briefing_flag] = True   # Tandai sudah tampil — tidak akan muncul lagi
    return True

def _check_sidequest_chapter_advance(game_state):
    """Cek dan trigger chapter advance untuk chapter sidequest-only (Ch3→4, Ch5→6).
    Dipanggil setelah setiap sidequest selesai dari display_npc_completion."""
    import time as _time
    try:
        chapter = int(game_state.story_flags.get('current_chapter', 1))
        sq_done = game_state.get_sidequest_progress()

        if chapter == 3 and sq_done >= 2:
            if not game_state.story_flags.get('boss_ch2_defeated'):
                return
            if not game_state.story_flags.get('ch3_sidequests_done'):
                game_state.story_flags['ch3_sidequests_done'] = True
                game_state.story_flags['current_chapter'] = 4
                game_state.active_quests = [
                    q for q in game_state.active_quests if q.get('quest_type') == 'side'
                ]
                print()
                separator()
                print(f"\n  {Warna.KUNING + Warna.TERANG}★  CHAPTER 3 SELESAI!  ★{Warna.RESET}")
                print(f"  {Warna.KUNING}2 sidequest selesai — aliansi terbentuk!{Warna.RESET}")
                print(f"  {Warna.CYAN}Chapter 4 terbuka — Infiltrasi Pusat Kontrol, kalahkan Ghislaine Maxwell!{Warna.RESET}")
                print(f"  {Warna.ABU_GELAP}Cari exit 'Command Center' di pulau — juga Laboratorium tersedia Ch.4+{Warna.RESET}")
                separator()
                _time.sleep(4)
                return

        if chapter == 5 and sq_done >= 4:
            has_usb = ('USB Evidence Drive' in game_state.inventory
                       or 'USB Evidence Drive' in game_state.quest_items
                       or game_state.story_flags.get('vio_sidequest_done', False))
            if not game_state.story_flags.get('boss_ch4_defeated'):
                return
            if has_usb and not game_state.story_flags.get('ch5_evidence_done'):
                game_state.story_flags['ch5_evidence_done'] = True
                game_state.story_flags['current_chapter'] = 6
                game_state.active_quests = [
                    q for q in game_state.active_quests if q.get('quest_type') == 'side'
                ]
                print()
                separator()
                print(f"\n  {Warna.MERAH + Warna.TERANG}★  CHAPTER 5 SELESAI!  ★{Warna.RESET}")
                print(f"  {Warna.KUNING}Semua bukti terkumpul! 47 GB data aman di USB Evidence Drive.{Warna.RESET}")
                print(f"  {Warna.MERAH}CHAPTER 6 TERBUKA — JEFFREY EPSTEIN MENUNGGU DI MANSION TIMUR! FINAL BOSS!{Warna.RESET}")
                print(f"  {Warna.ABU_GELAP}Cari exit 'Mansion Timur' di sudut kanan bawah island.{Warna.RESET}")
                separator()
                _time.sleep(4)
    except Exception:
        pass


def display_npc_completion(npc_id, game_state=None):
    """Tampilkan dialog completion NPC dan berikan reward item."""
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return False, None

    reward_flag  = npc_data.get('reward_flag', f"{npc_id}_sidequest_done")
    reward_item  = npc_data.get('reward_item')

    if game_state and game_state.story_flags.get(reward_flag):
        return False, None  # Idempoten — sudah pernah selesai

    # STEP 1: Commit state ke game_state SEBELUM dialog
    # Jika pemain Ctrl+C di tengah dialog, item sudah masuk dan flag sudah set.
    # Saat load ulang, guard `reward_flag` di atas akan skip fungsi ini → tidak duplikat.
    if game_state:
        game_state.story_flags[reward_flag]                  = True
        game_state.story_flags[f"{npc_id}_quest_active"]    = False
        game_state.story_flags[f"{npc_id}_quest_done"]      = True
        done_count = game_state.story_flags.get('sidequests_completed', 0)
        game_state.story_flags['sidequests_completed']       = done_count + 1

        # Berikan reward item (idempoten — cek dulu sebelum add)
        if reward_item and reward_item not in game_state.inventory and reward_item not in game_state.quest_items:
            game_state.add_item(reward_item)

        # Consume required items yang dipakai untuk quest ini
        req_items = npc_data.get('required_items', [])
        if not req_items and npc_data.get('required_item'):
            req_items = [npc_data['required_item']]
        for item in req_items:
            game_state.remove_item(item)


        # Ch.3 dan Ch.5 adalah sidequest-only chapters (tanpa boss).
        # Advance trigger ada di sini — dipanggil setiap kali sidequest selesai.
        _check_sidequest_chapter_advance(game_state)

    # STEP 2: Tampilkan dialog completion (state sudah aman)
    clear_screen()
    _display_npc_header(npc_data, "SIDEQUEST SELESAI \u2713")

    for speaker, line in npc_data.get('complete_dialog', []):
        _print_dialog_line(speaker, line)

    print()
    separator()
    print(f"\n  {Warna.HIJAU + Warna.TERANG}[ REWARD DITERIMA ]{Warna.RESET}")
    print(f"  {Warna.KUNING}+{Warna.RESET} {reward_item}")
    print(f"\n  {Warna.ABU_GELAP}Dampak ke main quest:{Warna.RESET}")
    print(f"  {npc_data.get('main_quest_impact', '')}")
    print()
    separator()
    wait_input()

    return True, reward_item

def display_npc_repeat_talk(npc_id, game_state=None):
    """Dialog saat player kembali berbicara dengan NPC setelah quest selesai."""
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return

    name = npc_data.get('name', npc_id.capitalize())
    after_flag = f"{npc_id}_after_complete_shown"

    # State 1: after_complete_dialog (sekali)
    if game_state and not game_state.story_flags.get(after_flag):
        after_dialog = npc_data.get('after_complete_dialog', [])
        if after_dialog:
            clear_screen()
            _display_npc_header(npc_data, "PERCAKAPAN")
            for speaker, line in after_dialog:
                _print_dialog_line(speaker, line)
            print()
            separator()
            wait_input()
            game_state.story_flags[after_flag] = True
            return

    # State 2: brief done line (setiap kunjungan setelahnya)
    brief_done_lines = {
        'haikaru': "Cari polanya. Setiap sistem punya celah. Temukan saja.",
        'aolinh':  "♪ Kita akan pulang. Aku percaya itu. ♪",
        'arganta': "La via è sempre avanti. Jalan selalu ada di depan.",
        'ignatius':"Otak insinyur tidak pernah berhenti. Kalau butuh sesuatu — tanya.",
        'vio':     "USB aman? Bagus. Kita hampir sampai.",
    }
    line = brief_done_lines.get(npc_id, f"{name}: Semoga berhasil.")

    clear_screen()
    _display_npc_header(npc_data, "PERCAKAPAN")
    print()
    _print_dialog_line(name, line)
    print()
    wait_input()

#  HELPER — CEK STATUS SIDEQUEST

def can_trigger_sidequest(npc_id, game_state):
    """Return True jika sidequest NPC bisa dimulai sekarang."""
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return False
    reward_flag = npc_data.get('reward_flag', f"{npc_id}_sidequest_done")
    if game_state.story_flags.get(reward_flag):
        return False  # Sudah selesai
    current_chapter = int(game_state.story_flags.get('current_chapter', 1))
    return current_chapter >= npc_data['available_chapter']

def is_sidequest_complete(npc_id, game_state):
    """Return True jika semua syarat sidequest NPC sudah terpenuhi (siap redeem reward).
    BUG FIX: cek inventory DAN quest_items — quest items disimpan di quest_items via add_quest_item()
    """
    npc_data = NPC_SIDEQUEST_DATA.get(npc_id)
    if not npc_data:
        return False

    def _has_item(item):
        """Cek item di inventory MAUPUN quest_items."""
        return item in game_state.inventory or item in game_state.quest_items

    # Cek syarat item
    if npc_data.get('required_items'):
        return all(_has_item(item) for item in npc_data['required_items'])
    if npc_data.get('required_item'):
        return _has_item(npc_data['required_item'])
    if npc_data.get('required_action'):
        return game_state.story_flags.get(npc_data['required_action'], False)
    return False

def get_npc_display_name(npc_id):
    """Terlebih dahulu mengecek NPC_SIDEQUEST_DATA, lalu cek game_state cache,"""
    # Priority 1: Check NPC_SIDEQUEST_DATA
    data = NPC_SIDEQUEST_DATA.get(npc_id)
    if data:
        return data.get('name', npc_id.capitalize())
    
    # Priority 2: Fallback ke capitalize() jika NPC belum terdaftar
    # (ini untuk NPC baru yang belum ditambah ke NPC_SIDEQUEST_DATA)
    return npc_id.capitalize()

def get_sidequest_summary(game_state):
    
    result = []
    
    # Safe chapter retrieval: handles both string and int values
    current_chapter_raw = game_state.story_flags.get('current_chapter', 1)
    try:
        current_chapter = int(current_chapter_raw) if current_chapter_raw else 1
    except (ValueError, TypeError):
        current_chapter = 1  # Fallback to chapter 1 if conversion fails
    
    for npc_id, data in NPC_SIDEQUEST_DATA.items():
        reward_flag = data.get('reward_flag', f"{npc_id}_sidequest_done")
        if game_state.story_flags.get(reward_flag):
            status = 'done'
        elif game_state.story_flags.get(f"{npc_id}_quest_active"):
            status = 'active'
        elif current_chapter >= data.get('available_chapter', 1):
            status = 'available'
        else:
            status = 'locked'
        result.append({
            'npc':    npc_id,
            'name':   data.get('name', npc_id),
            'title':  data.get('sidequest_title', ''),
            'status': status,
            'impact': data.get('main_quest_impact', ''),
        })
    return result

#  ENCOUNTER DIALOGS — dialog saat ketemu enemy & masuk lokasi baru
#  Terintegrasi langsung di npc_interactions.py sesuai permintaan.

import random as _random

# Dialog musuh saat encounter
_ENEMY_ENCOUNTER_LINES = {
    "guard_novice": [
        "Hei! Berhenti di situ, tahanan!",
        "Kamu pikir bisa kabur? Tidak di sini!",
        "Shift baru dimulai dan sudah ada masalah... TANGKAP!",
        "Stop! Atau aku tidak bertanggung jawab atas yang terjadi!",
        "Alarm! Ada kabur-kaburan! Kejar!",
    ],
    "guard_veteran": [
        "Sudah lihat seribu orang coba hal yang sama. Tidak ada yang berhasil.",
        "Berhenti. Sebelum kamu bikin situasi lebih buruk.",
        "Dua puluh tahun di sini. Kamu bukan yang pertama.",
        "Kalian anak zaman sekarang... selalu sok jagoan.",
        "Mau kabur? Boleh coba. Tapi aku lebih tahu pulau ini.",
    ],
    "guard_elite": [
        "Target teridentifikasi. Protokol netralisasi diaktifkan.",
        "Unit elite tidak berdialog dengan target. Menyerah atau konsekuensinya.",
        "Kamu tidak punya peluang melawan unit khusus.",
        "Backup dalam 2 menit. Mau tunggu atau menyerah?",
    ],
    "mercenary_thug": [
        "Ha! Satu lagi bocah yang sok berani.",
        "Maxwell bayar ekstra buat yang tangkap tahanan kabur. Lucky me!",
        "Mau ke mana, anak? Pantai? *Tawa kasar* Lucu sekali.",
        "Aku butuh uang tambahan bulan ini. Makasih udah jadi bonusnya.",
        "Jangan lari. Itu cuma bikin aku kesal.",
    ],
    "mercenary_sniper": [
        "Dari tadi sudah kuintai kamu. Gerak satu langkah lagi — tamat.",
        "*Suara klik senjata* Tidak ada tempat bersembunyi.",
        "Sniper tidak suka target yang bergerak. Berhentilah.",
        "Jarak 40 meter. Kamu tidak bisa lari lebih cepat dari peluru.",
    ],
    "scientist": [
        "Subjek melarikan diri! Eksperimen belum selesai! TANGKAP!",
        "Data kamu masih dibutuhkan. Kembali ke lab sekarang!",
        "Maxwell tidak akan senang kalau subjek utama kabur!",
        "Kamu tidak akan mengerti pentingnya penelitian ini.",
    ],
    "tech_guard": [
        "ALERT: Intrusi area restricted! Hentikan gerakan!",
        "Sistem keamanan mendeteksi target. Identifikasi gagal. Netralisasi!",
        "Area restricted! Apa bagian 'DILARANG MASUK' tidak kamu mengerti?",
    ],
    "mansion_guard": [
        "Area privat! Siapa yang mengizinkan kamu masuk?!",
        "Tamu tidak diundang di sayap ini. Ada konsekuensinya.",
        "Tuan Maxwell tidak menerima tamu tanpa janji.",
        "Sekuriti mansion level tertinggi. Kamu salah tempat, kawan.",
    ],
    "maxwell_enforcer": [
        "Jadi kamu yang menyebabkan semua keributan ini. Menarik.",
        "Maxwell memberi instruksi jelas tentang kamu.",
        "Sudah cukup jauh untuk anak seusia kamu. Tapi berakhir di sini.",
    ],
    "maxwell_agent": [
        "Server room ini tidak boleh ditembus siapapun.",
        "Maxwell memberi instruksi jelas — tidak ada saksi.",
        "Anak 13 tahun? ...Maxwell benar-benar tidak mau ambil risiko.",
    ],
    "network_overseer": [
        "Intrusi terdeteksi di jaringan utama. Netralisasi segera.",
        "256-bit encryption dan kamu masih coba menembus? Percuma.",
        "Firewall berlapis. AI watchdog. Kamu tidak punya peluang.",
    ],
    "mercenary_commander": [
        "Tidak ada yang lewat dermaga ini tanpa izinku.",
        "Maxwell bayar bagus. Tapi ini sudah soal profesionalisme.",
        "Bocah Italy nyasar di dermaga? Keberuntunganmu sudah habis.",
    ],
    "ghislaine_maxwell": [
        "Anak-anak kecil bermain detektif. Menggemaskan.",
        "Jeffrey akan sangat marah mendengar ini.",
        "Saya sudah mengelola jaringan ini 30 tahun. Kalian tidak bisa menghentikannya.",
        "Satu panggilan telepon dan kalian semua akan menghilang.",
    ],
    "warden_elite": [
        "Tidak satu pun yang pernah kabur selama saya bertugas.",
        "Dua puluh tahun zero escape rate. Kamu tidak akan jadi pengecualian.",
        "Warden Elite tidak kehilangan tahanan. Tidak pernah.",
    ],
    "theater_master": [
        "Pertunjukan hampir selesai. Dan kamu bukan bagian dari naskahnya.",
        "Penonton tidak boleh naik ke panggung. Aturan nomor satu.",
        "Ah, pengganggu. *Bertepuk tangan pelan* Drama entrance, tapi pihak yang salah.",
    ],
    "harbor_captain": [
        "Tidak ada kapal yang keluar tanpa izin tertulis dari saya.",
        "Dermaga restricted. Kamu punya pass? Tidak? Kita punya masalah.",
        "Kapten dermaga ini saya. Dan saya bilang: kamu tidak boleh lewat.",
    ],
    "security_bot": [
        ">> UNAUTHORIZED PERSONNEL DETECTED",
        ">> INITIATING ELIMINATION PROTOCOL",
        ">> TARGET ACQUIRED — STAND BY",
    ],
    "epstein_boss": [
        "Jadi... kalian yang menyebabkan semua ini. Anak-anak kecil bodoh.",
        "Lima anak? Ha! Aku sudah hancurkan ribuan seperti kalian.",
        "Kalian sama sekali tidak paham kekuatan yang kalian hadapi.",
        "Presiden takut padaku. Raja takut padaku. Bahkan negara takut padaku.",
        "Biarkan aku tunjukkan kenapa dunia ini berjalan sesuai keinginanku.",
        "Kalian pikir ini permainan? Ini adalah akhir dari eksplorasi kalian.",
    ],
}

# Reaksi player saat encounter musuh
_PLAYER_REACTIONS = {
    "vio": [
        "...Ini kayak random encounter di game. Annoying tapi manageable.",
        "*Tersenyum tipis* Stat musuh ini sudah aku analisa. RNG-ku tidak akan mengkhianati.",
        "Gacha player tahu: selalu ada pattern di setiap boss.",
        "*Dalam hati* Kalau kalah di sini, respawn-nya pasti jauh...",
        "Fine. Anggap ini mini-boss sebelum stage utama.",
    ],
    "haikaru": [
        "*Kalkulasi cepat* 3,7 detik sampai jarak serang. Dua skenario optimal siap.",
        "Pola gerakannya sudah aku prediksi dua langkah yang lalu.",
        "Kelemahan: reaksi lambat di sisi kiri. Ini akan efisien.",
        "*Diam sebentar, mengangguk* Data cukup. Mulai.",
        "Semakin banyak rintangan, semakin banyak data yang kukumpulkan.",
    ],
    "aolinh": [
        "E-eh?! K-kita tidak bisa... negosiasi ya? *Menarik napas* 加油, Aolinh!",
        "*Gemetar tapi bertekad* Aku tidak akan menyerah. Jiejie masih menungguku.",
        "Maaf ya... tapi aku tidak bisa berhenti di sini.",
        "音乐给我力量! Selagi aku bisa merasakannya... aku bisa!",
        "*Memejamkan mata* Ini untuk Jiejie. Aku tidak akan kalah.",
    ],
    "arganta": [
        "*Menggenggam pisau* Fermo. Aku sudah siap untuk ini.",
        "Per famiglia. Per Nonno. Aku tidak mundur.",
        "Di Napoli, kami belajar: hadapi masalah, jangan lari.",
        "*La via è sempre avanti* Jalan ada di depan. Ini cuma halangan.",
        "Anggap pemanasan sebelum menemukan jalan keluar sesungguhnya.",
    ],
    "ignatius": [
        "*Menilai situasi* Kalkulasi odds. Parameter dinilai. Proceed.",
        "Tidak ada waktu untuk teori panjang. Ini saatnya praktikum.",
        "Otak insinyur tidak pernah berhenti — bahkan dalam kondisi ini.",
        "*Menyiapkan alat* Saatnya aksi.",
        "Setiap sistem punya kelemahan. Ini juga.",
    ],
    "vio_epstein": [
        "*Mengambil napas dalam* Server pusat ini... adalah kasusnya. Aku tahu. Dan aku tahu caranya.",
        "Setiap network punya titik kritis. Dan aku akan temukannya pada dirimu.",
        "Dataku tidak pernah berbohong. Kamu — skema korupsi terbesar di planet ini.",
        "Hari ini... koneksi terakhirmu akan diputus.",
    ],
    "haikaru_epstein": [
        "*Menghitung dengan permata matanya* Probabilitas: Survival tidak mungkin jika aku ragu.",
        "Tapi aku tidak akan ragu. Setiap detail dianalisis. Setiap hasil diperhitungkan.",
        "Kamu adalah puzzle terakhir. Dan aku sudah tahu gambarnya.",
        "*Tenang tapi tajam* Mari kita selesaikan ini dengan logika murni.",
    ],
    "aolinh_epstein": [
        "*Mata memerah* Jiejie... semua orang di sini... semuanya karena dia!",
        "Musik tidak bisa mengubah apa yang kamu lakukan. Tapi aksi kami bisa.",
        "♪ Ini adalah lagu terakhirmu. ♪",
        "*Membawa biola ke hadapan* Yang menculik kakakku akan lihat apa yang bisa kami lakukan.",
    ],
    "arganta_epstein": [
        "*Pisau berkilau di tangan* Papà. Mamma. Nonno. Mereka semua.",
        "Kamu pikir orang seperti kami cukup untuk diabaikan. Kesalahan fatal.",
        "Per setiap nyawa yang kamu renggut — aku akan ambil seribu jawaban darimu.",
        "La via è sempre avanti — bahkan jika jalur itu diterangi darah.",
    ],
    "ignatius_epstein": [
        "*Melepas kacamata, membersihkannya dengan tenang* Sistem terakhirmu ada di depanku.",
        "Semua kabel, semua chip, semua data — aku tahu semuanya tentang itu.",
        "Kamu membangun kuil dari daging manusia. Saatnya meruntuhkannya.",
        "*Mengenakan kacamata kembali dengan pasti* EMP di ujung — dan kebenaran di akhir.",
    ],
}

# Dialog masuk lokasi baru (pertama kali)
_MAP_ENTRY_DIALOGS = {
    "island": {
        "vio":      [(None, "Pulau utama terbuka lebar."),
                     ("Vio", "Server pusat pasti ada di salah satu bangunan ini. Tinggal cari sinyalnya.")],
        "haikaru":  [(None, "Haikaru berdiri di tengah pulau, angin menggerakkan rambutnya."),
                     ("Haikaru", "Topografi diverifikasi. Enam zona, empat jalur patroli utama. Akurasi rencana: 91%.")],
        "aolinh":   [(None, "Angin laut menyentuh wajah Aolinh. Sebentar dia menutup mata."),
                     ("Aolinh", "Jiejie... kamu di mana? Apakah kamu melihat laut yang sama ini?"),
                     ("Aolinh", "*Menekan earphone* Selama musikku masih ada... aku tidak akan menyerah.")],
        "arganta":  [(None, "Arganta membuka kompas tuanya, mencermati arah dengan serius."),
                     ("Arganta", "La via è sempre avanti. Ayo cari jalur yang tidak ada di peta resmi.")],
        "ignatius": [(None, "Ignatius memindai infrastruktur pulau dengan mata terlatih."),
                     ("Ignatius", "Satu EMP yang tepat di junction utama... seluruh sistem keamanan mati.")],
    },
    "prison_north": {
        "vio":      [("Vio", "Keamanan 3 lapis. Tapi setiap sistem punya backdoor — kalau tahu caranya."),
                     ("Vio", "Dan aku selalu tahu caranya.")],
        "haikaru":  [(None, "Kembali ke penjara ini terasa... ironis."),
                     ("Haikaru", "Tidak ada waktu untuk nostalgia. Fokus.")],
        "aolinh":   [(None, "Koridor penjara dingin dan sempit. Aolinh menggigil."),
                     ("Aolinh", "Tempat ini gelap. Tapi mungkin ada yang butuh bantuan di dalam. Ayo masuk.")],
        "arganta":  [("Arganta", "Penjara. Hampir berakhir di sini dulu. Hampir."),
                     ("Arganta", "Per Nonno — hati-hati, tapi jangan ragu.")],
        "ignatius": [(None, "Ignatius memeriksa panel listrik di koridor pertama."),
                     ("Ignatius", "Kalau panel darurat ini dimatikan... semua sel terbuka otomatis. Berguna.")],
    },
    "mansion": {
        "vio":      [(None, "Mansion mewah. Server utama ada di sini."),
                     ("Vio", "Aku bisa rasakan sinyalnya dari luar. Tapi pertama — bypass sistem keamanan berlapis itu.")],
        "haikaru":  [("Haikaru", "Dokumen tersembunyi di sini pasti kunci segalanya."),
                     ("Haikaru", "Waspada. Penjaga di sini berbeda kelas dari yang di luar.")],
        "aolinh":   [(None, "Mansion besar yang terasa dingin meski mewah."),
                     ("Aolinh", "*Memegang biola erat* Ada perasaan tidak enak. Tapi aku harus masuk.")],
        "arganta":  [(None, "Arganta menatap mansion dengan mata menyimpan amarah."),
                     ("Arganta", "Tempat seperti ini yang menghancurkan keluargaku. Aku tidak akan takut masuk.")],
        "ignatius": [(None, "Ignatius masuk ke mansion dengan rencana yang sudah matang."),
                     ("Ignatius", "Sistem listrik mansion terhubung ke seluruh pulau. Kendali ada di sini.")],
    },
    "theater": {
        "vio":      [("Vio", "Teater di tengah pulau penjara. Absurd. Tapi kalau ada orang berguna di dalam...")],
        "haikaru":  [("Haikaru", "Suara bisa jadi distraksi yang sangat efektif jika dimanfaatkan dengan benar.")],
        "aolinh":   [(None, "Bau kayu panggung. Tirai beludru merah. Aolinh terpaku sebentar."),
                     ("Aolinh", "Panggung... *menggenggam biola* ini mengingatkanku pada rumah."),
                     ("Aolinh", "Tapi sekarang bukan waktunya bernostalgia.")],
        "arganta":  [("Arganta", "Waspada. Tempat seperti ini punya banyak sudut tersembunyi.")],
        "ignatius": [("Ignatius", "Speaker sistem teater terhubung ke seluruh gedung. Berguna untuk distraksi massal.")],
    },
    "beach": {
        "vio":      [(None, "Pantai. Vio merasakan angin laut untuk pertama kali sejak ditangkap."),
                     ("Vio", "Berapa jauh daratan? *Menghitung* ...Terlalu jauh. Butuh kapal.")],
        "haikaru":  [("Haikaru", "Sekitar 47 kilometer ke daratan. Membutuhkan kapal kecepatan minimal 25 knot."),
                     ("Haikaru", "Rencana B: cari kapal. Rencana A belum gagal, tapi data ini disimpan.")],
        "aolinh":   [(None, "Laut yang indah. Ironi yang menyakitkan."),
                     ("Aolinh", "不要放弃. Jangan menyerah. Ini bukan akhir.")],
        "arganta":  [(None, "Arganta berdiri di pantai. Angin laut seperti sapaan lama."),
                     ("Arganta", "Nonno sering cerita pantai-pantai di sini. Akhirnya aku di sini juga."),
                     ("Arganta", "*Melihat reruntuhan perahu* Ada yang bisa dipakai?")],
        "ignatius": [("Ignatius", "Arus pantai barat tidak standar. Ada jalur bawah permukaan yang tidak terpetakan.")],
    },
    "dock": {
        "vio":      [("Vio", "Kalau bisa akses sistem navigasi kapal itu... kita punya tiket keluar."),
                     ("Vio", "Enkripsi sistem dermaga pasti bisa ditembus. 10 menit.")],
        "haikaru":  [("Haikaru", "Kapal terbesar — kapasitas 20 orang. Kecepatan estimasi 35 knot. Memadai."),
                     ("Haikaru", "Tantangan: netralisasi penjaga dermaga sebelum kapal digunakan.")],
        "aolinh":   [(None, "Aolinh melihat kapal-kapal dengan mata penuh harapan."),
                     ("Aolinh", "Kapal itu... bisa membawa kita pulang? *Mata berkaca-kaca*"),
                     ("Aolinh", "Aku harus kuat. Untuk Jiejie.")],
        "arganta":  [(None, "Dermaga. Arganta mengenali jenis kapal utama dari kejauhan."),
                     ("Arganta", "Kapal itu — mirip yang Papà punya dulu. Aku tahu cara mengemudikannya."),
                     ("Arganta", "Ini jalan keluar kita. Per Nonno.")],
        "ignatius": [("Ignatius", "Semua kapal terhubung ke sistem kunci sentral. Satu override dan semua terbuka."),
                     ("Ignatius", "Butuh 8 menit. Mungkin 7 kalau kondisi optimal.")],
    },
    "safe_zone": {
        "vio":      [("Vio", "Ada toko? *Melihat konter* Menarik. Siapa yang mengelola ini?")],
        "haikaru":  [("Haikaru", "Safe zone. Kenapa Maxwell membiarkan zona ini aman? Ada maksud tersembunyi?"),
                     ("Haikaru", "Atau jebakan. Tetap waspada.")],
        "aolinh":   [(None, "Aolinh menghela napas lega."),
                     ("Aolinh", "Akhirnya... istirahat sebentar. *Melihat toko* Oh ada pedagang? ♪")],
        "arganta":  [("Arganta", "Bersih. Tidak ada jebakan terlihat. Aman untuk sekarang."),
                     ("Arganta", "Tapi tetap waspada. Pulau ini penuh kejutan tidak menyenangkan.")],
        "ignatius": [("Ignatius", "Tidak ada sistem keamanan aktif yang terdeteksi."),
                     ("Ignatius", "Entah ini keberuntungan atau strategi pihak ketiga.")],
    },
    "basement": {
        "vio":      [("Vio", "Server farm di sini? *Melihat ke sekeliling* Siapapun yang merancang ini — respect.")],
        "haikaru":  [("Haikaru", "Ada jalur kabel tersembunyi di dinding timur. Mengarah ke mana?")],
        "aolinh":   [(None, "Aolinh mengernyit. Basement pengap dan gelap."),
                     ("Aolinh", "*Menekan earphone, memutar musik pelan* Oke. Ayo masuk.")],
        "arganta":  [("Arganta", "Terowongan bawah tanah seperti ini... Nonno pernah cerita.")],
        "ignatius": [(None, "Ignatius memasuki basement. Matanya langsung mencerna setiap detail teknis."),
                     ("Ignatius", "Panel utama, kapasitor, relay, transformator... ini ruang kontrolku."),
                     ("Ignatius", "Dari sini, aku bisa matikan seluruh sistem keamanan pulau.")],
    },
}

# Fungsi publik

def show_enemy_encounter_dialog(enemy_id, player_char_id, enemy_name=None, is_boss=False, is_superboss=False):
    
    import shutil as _shutil
    tw = max(40, _shutil.get_terminal_size(fallback=(80, 24)).columns)

    CHAR_COLORS = {
        'vio':      Warna.MERAH + Warna.TERANG,
        'haikaru':  Warna.CYAN + Warna.TERANG,
        'aolinh':   Warna.UNGU + Warna.TERANG,
        'arganta':  Warna.PUTIH + Warna.TERANG,
        'ignatius': Warna.KUNING + Warna.TERANG,
    }
    CHAR_NAMES = {
        'vio': 'Vio', 'haikaru': 'Haikaru', 'aolinh': 'Aolinh',
        'arganta': 'Arganta', 'ignatius': 'Ignatius',
    }
    tc        = CHAR_COLORS.get(player_char_id, Warna.PUTIH + Warna.TERANG)
    char_name = CHAR_NAMES.get(player_char_id, player_char_id.capitalize())
    disp_enemy = enemy_name or enemy_id.replace('_', ' ').title()

    try:
        from .enemies import get_enemy_dialog_lines
        enemy_pool = get_enemy_dialog_lines(enemy_id, 'encounter')
        if not enemy_pool:
            enemy_pool = _ENEMY_ENCOUNTER_LINES.get(enemy_id, ["Berhenti! Tidak ada yang bisa lewat!"])
    except Exception:
        enemy_pool = _ENEMY_ENCOUNTER_LINES.get(enemy_id, ["Berhenti! Tidak ada yang bisa lewat!"])
    
    if enemy_id == 'epstein_boss':
        epstein_char_key = f"{player_char_id}_epstein"
        player_pool = _PLAYER_REACTIONS.get(epstein_char_key, _PLAYER_REACTIONS.get(player_char_id, ["*Bersiap untuk bertarung*"]))
    else:
        player_pool = _PLAYER_REACTIONS.get(player_char_id, ["*Bersiap untuk bertarung*"])
    
    player_line = _random.choice(player_pool)

    sep_w = min(58, tw - 2)
    if is_superboss:
        sep_outer = Warna.UNGU + '▓' * sep_w + Warna.RESET
        sep       = Warna.CYAN + '─' * sep_w + Warna.RESET
        label     = "★★  LEGENDARY SUPERBOSS  ★★"
        lc        = Warna.UNGU + Warna.TERANG
    elif is_boss:
        sep_outer = None
        sep       = '─' * sep_w
        label     = "★  BOSS ENCOUNTER  ★"
        lc        = Warna.KUNING + Warna.TERANG
    else:
        sep_outer = None
        sep       = '─' * sep_w
        label     = "!  PERTEMUAN"
        lc        = Warna.MERAH

    if is_superboss:
        print(f"\n{sep_outer}")
        print(f"{lc}{sep}{Warna.RESET}")
        print(f"  {lc}{label}{Warna.RESET}")
        print(f"{lc}{sep}{Warna.RESET}")
        print(f"{sep_outer}\n")
    else:
        print(f"\n{lc}{sep}{Warna.RESET}")
        print(f"  {lc}{label}{Warna.RESET}")
        print(f"{lc}{sep}{Warna.RESET}\n")
    time.sleep(0.12)

    # Musuh bicara — superboss plays full encounter script
    if is_superboss:
        for line in enemy_pool:
            if ':' in line:
                speaker, text = line.split(':', 1)
                print(f"  {Warna.UNGU + Warna.TERANG}{speaker.strip()}{Warna.RESET}: {Warna.CYAN + Warna.TERANG}{text.strip()}{Warna.RESET}")
            elif line.startswith('*') and line.endswith('*'):
                print(f"  {Warna.CYAN + Warna.DIM}{line}{Warna.RESET}")
            else:
                print(f"  {Warna.CYAN + Warna.TERANG}{line}{Warna.RESET}")
            time.sleep(0.75)
    else:
        enemy_line = _random.choice(enemy_pool)
        print(f"  {Warna.MERAH + Warna.TERANG}{disp_enemy}{Warna.RESET}: {enemy_line}")
        time.sleep(0.65)

    # Player bereaksi
    print(f"  {tc}{char_name}{Warna.RESET}: {player_line}")
    time.sleep(0.65)

    if is_superboss:
        print(f"\n{sep_outer}")
        print(f"  {Warna.CYAN + Warna.TERANG}⚠ Tidak ada jalan keluar dari pertarungan ini.{Warna.RESET}")
        print(f"{sep_outer}")
    else:
        print(f"\n{Warna.ABU_GELAP}{sep}{Warna.RESET}")
    time.sleep(0.25)

def show_map_entry_dialog(map_id, player_char_id, gs=None):
    
    flag = f"map_entry_{map_id}_shown"
    if gs and gs.story_flags.get(flag):
        return

    lines = _MAP_ENTRY_DIALOGS.get(map_id, {}).get(player_char_id, [])
    if not lines:
        if gs:
            gs.story_flags[flag] = True
        return

    MAP_DISPLAY = {
        'island': '🌴 PULAU UTAMA', 'prison_north': '⛓ PENJARA UTARA',
        'mansion': '🏛 MANSION',    'theater': '🎭 TEATER',
        'beach': '🌊 PANTAI',       'dock': '⚓ DERMAGA',
        'safe_zone': '🛒 SAFE ZONE', 'basement': '⚡ BASEMENT',
    }
    CHAR_COLORS = {
        'vio': Warna.MERAH + Warna.TERANG, 'haikaru': Warna.CYAN + Warna.TERANG,
        'aolinh': Warna.UNGU + Warna.TERANG, 'arganta': Warna.PUTIH + Warna.TERANG,
        'ignatius': Warna.KUNING + Warna.TERANG,
    }
    tc = CHAR_COLORS.get(player_char_id, Warna.PUTIH)
    map_name = MAP_DISPLAY.get(map_id, map_id.upper())

    print(f"\n{Warna.KUNING}── {map_name} ──{Warna.RESET}")
    time.sleep(0.2)

    for speaker, line in lines:
        if speaker is None:
            print(f"  {Warna.ABU_GELAP}[{line}]{Warna.RESET}")
        else:
            print(f"  {tc}{speaker}{Warna.RESET}: {line}")
        time.sleep(0.45)

    print(f"{Warna.ABU_GELAP}{'─' * 40}{Warna.RESET}")
    time.sleep(0.3)

    if gs:
        gs.story_flags[flag] = True
