# Konten cerita dan chapter
from .sprites import Warna
import time
import shutil
from contextlib import suppress
from .utils import print_slow

def _tw():
    """Terminal width saat ini."""
    return max(40, shutil.get_terminal_size(fallback=(80, 24)).columns)

def _get_character_gender_descriptor(player_character=''):
    """Get gender descriptor for player character — avoids circular import."""
    if not player_character:
        return 'gadis biasa'  # Default fallback
    
    try:
        from .characters import PLAYABLE_CHARACTERS
        if player_character in PLAYABLE_CHARACTERS:
            char_data = PLAYABLE_CHARACTERS[player_character]
            gender = char_data.get('gender', 'female')
            if gender.lower() == 'male':
                return 'anak laki-laki biasa'
            elif gender.lower() == 'female':
                return 'gadis biasa'
    except ImportError:
        pass  # Fallback if import fails
    
    return 'orang biasa'  # Safe fallback

def _interpolate_player_info(text, game_state=None):
    """Ganti variabel template cerita dengan data pemain."""
    if not game_state:
        return text
    
    player_name = getattr(game_state, 'player_name', 'Traveler')
    player_char = getattr(game_state, 'player_character', '')
    
    # Default pronouns for third-person narration
    pronoun_subject = "dia"
    pronoun_object = "dia"
    gender_adj = _get_character_gender_descriptor(player_char)
    
    # Replace placeholders
    text = text.replace('{player_name}', player_name)
    text = text.replace('{player_pronoun_subject}', pronoun_subject)
    text = text.replace('{player_pronoun_object}', pronoun_object)
    text = text.replace('{player_gender_adj}', gender_adj)
    
    return text

STORY_CHAPTERS = {
    "prologue_1": {
        "title": "PULAU TERKUTUK",
        "type": "narration",
        "content": [
            "Little St. James Island, tengah Laut Karibia.",
            "Dari luar: pulau tropis yang indah.",
            "Dari dalam: penjara yang mengerikan.",
            "",
            "Pulau Epstein. Pulau Dosa. Pulau Kutukan.",
            "Banyak nama untuk satu tempat terkutuk.",
            "",
            "Untukmu, ini adalah penjara.",
            "Dan kamu harus keluar. Sekarang."
        ]
    },
    "prologue_2": {
        "title": "KETAKUTAN DALAM GELAP",
        "type": "exposition",
        "content": [
            "Tiga hari yang lalu, kamu ditangkap",
            "Tiga hari di dalam sel tanpa penjelasan",
            "Tanpa pengadilan. Tanpa hak",
            "",
            "Hanya pertanyaan brutal dari penjaga",
            "Pertanyaan yang tidak masuk akal",
            "'Siapa yang mengirim mu?'",
            "'Apa yang kamu tahu?'",
            "'SIAPA YANG BEKERJA DENGAN MU?'",
            "",
            "Tapi kamu tidak tahu apa-apa",
            "Kamu hanya {player_gender_adj} yang salah tempat",
            "Di tempat yang salah pada waktu yang salah",
            "",
            "Sekarang pintu terbuka",
            "Dan satu-satunya jalan adalah maju",
            "Atau mati di sini"
        ]
    },
    "prologue_3": {
        "title": "SENDIRIAN",
        "type": "exposition",
        "content": [
            "Kamu tidak tahu dimana kamu",
            "Tidak tahu siapa yang membawamu",
            "Tidak tahu apa yang akan terjadi",
            "",
            "Sel dingin. Gelap. Sunyi",
            "Hanya kamu dan ketakutan",
            "",
            "Tapi kamu tidak menyerah",
            "Tidak akan menyerah",
            "",
            "Ada cara keluar",
            "Harus ada",
            "Dan kamu akan menemukannya"
        ]
    },
    "prologue_4": {
        "title": "KESEMPATAN",
        "type": "action",
        "content": [
            "Malam ini berbeda",
            "Alarm kebakaran tiba-tiba berbunyi",
            "Penjaga berlarian, panik, kacau",
            "",
            "Di tengah kekacauan itu,",
            "Pintu selmu terbuka",
            "",
            "Seseorang di luar berbisik cepat:",
            "'Ini kesempatanmu. Lari. SEKARANG!'",
            "",
            "Kamu tidak tahu siapa dia",
            "Tapi kamu tahu ini mungkin satu-satunya kesempatan",
            "",
            "Kamu melangkah keluar dari sel",
            "Koridor panjang membentang di depanmu",
            "",
            "Petualanganmu dimulai sekarang"
        ]
    },
    
    "chapter_1_intro": {
        "title": "CHAPTER 1: FIRST STEPS",
        "type": "gameplay_intro",
        "content": [
            "Kaki telanjangmu menyentuh lantai dingin",
            "Seragam penjara yang kusam",
            "Tidak ada sepatu. Tidak ada senjata",
            "",
            "Tapi kamu bebas",
            "Untuk pertama kalinya dalam tiga hari,",
            "pintu sel terbuka dan kamu bisa berlari",
            "",
            "Koridor penjara membentang",
            "Cahaya lampu darurat berkedip merah",
            "Alarm terus berbunyi",
            "",
            "Kamu harus keluar dari sini",
            "Cari jalan. Cari bantuan",
            "Setiap detik berharga"
        ]
    },
    
    "chapter_1_meet": {
        "title": "PERTEMUAN PERTAMA",
        "type": "character_arc",
        "content": [
            "Suara langkah di koridor",
            "Kamu berhenti, siap untuk lari",
            "",
            "Tapi yang muncul... anak kecil juga",
            "Umur sekitar sama denganmu",
            "Seragam penjara yang sama",
            "",
            "'K-kamu juga melarikan diri?'",
            "",
            "Mata kalian bertemu",
            "Tidak ada kata-kata",
            "Tapi kalian tahu",
            "",
            "Sendiri, kalian lemah",
            "Bersama?",
            "Mungkin ada kesempatan",
            "",
            "'Ayo. Kita keluar bersama.'"
        ]
    },
    
    "chapter_2_intro": {
        "title": "CHAPTER 2: MEMPERLUAS SAYAP",
        "type": "progression",
        "content": [
            "Kalian berhasil keluar dari area pertama.",
            "Tapi pulau masih besar.",
            "Masih banyak bahaya.",
            "",
            "Di seberang, lampu mansion menyala.",
            "Di timur, dermaga dengan kapal.",
            "Di selatan, gedung lain yang gelap.",
            "",
            "'Ada orang lain yang terjebak di sini,' bisikmu.",
            "'Kita harus mencari mereka.'",
            "'Semakin banyak yang tahu kebenaran ini, semakin kuat posisi kita.'",
            "",
            "Misi baru: jelajahi pulau.",
            "Temukan semua yang bisa ditemukan.",
            "Bersama, ada kesempatan untuk kabur."
        ]
    },
    
    "chapter_2_growing": {
        "title": "LINGKARAN YANG MELUAS",
        "type": "character_arc",
        "content": [
            "Satu per satu kamu menemukannya.",
            "Orang-orang lain yang terjebak di pulau ini.",
            "Masing-masing dengan kisah sendiri.",
            "Masing-masing dengan kemampuan sendiri.",
            "",
            "Ada yang ahli teknologi.",
            "Ada yang pintar membaca situasi.",
            "Ada yang kuat dan tak kenal menyerah.",
            "Ada yang bisa membawa ketenangan di saat paling gelap.",
            "",
            "Sendiri, masing-masing tidak ada apa-apanya.",
            "Tapi saat saling berbagi informasi?",
            "",
            "Kekuatan itu berlipat ganda.",
            "Kesempatan itu nyata.",
            "Dan pulau ini mulai terasa tidak seperkasa sebelumnya."
        ]
    },
    
    "chapter_3_intro": {
        "title": "CHAPTER 3: THE TRUTH",
        "type": "revelation",
        "content": [
            "Semakin kalian eksplorasi pulau,",
            "Semakin kalian mengerti",
            "",
            "Ini bukan penjara biasa",
            "Ini bukan penculikan biasa",
            "",
            "Pulau ini adalah bagian dari sesuatu",
            "Jaringan besar. Network kekuasaan",
            "Orang-orang berkuasa yang melindungi monster",
            "",
            "Jeffrey Epstein",
            "Ghislaine Maxwell",
            "Dan mereka yang berkunjung ke pulau ini",
            "",
            "Politisi. Bangsawan. Miliarder",
            "Semua terlibat. Semua tahu",
            "Semua bersalah"
        ]
    },
    
    "chapter_3_decision": {
        "title": "PILIHAN BERAT",
        "type": "choice",
        "content": [
            "Tim berkumpul untuk meeting",
            "Sudah cukup kuat untuk kabur",
            "Speedboat di dermaga bisa membawa kalian pergi",
            "",
            "Tapi...",
            "",
            "'Kalau kita pergi sekarang,' kata salah satu",
            "'Tidak ada yang akan percaya kita'",
            "'Tidak ada bukti'",
            "",
            "'Kita butuh bukti,' kata yang lain",
            "'Files. Dokumen. Rekaman'",
            "'Agar dunia tahu apa yang terjadi di sini'",
            "",
            "Kalian terdiam",
            "Kabur sekarang = aman",
            "Ambil bukti = risiko tinggi",
            "",
            "'Apa yang kita lakukan?'"
        ]
    },
    
    "chapter_final_intro": {
        "title": "FINAL CHAPTER: NO TURNING BACK",
        "type": "commitment",
        "content": [
            "Keputusan sudah dibuat",
            "Kalian akan mengambil bukti",
            "Kalian akan expose mereka semua",
            "",
            "Tidak peduli risikonya",
            "Tidak peduli betapa berbahayanya",
            "",
            "Ini bukan lagi tentang kabur",
            "Ini tentang keadilan",
            "Ini tentang kebenaran",
            "",
            "Untuk semua anak yang menderita di sini",
            "Untuk semua korban yang tidak pernah bebas",
            "Untuk masa depan yang lebih baik",
            "",
            "Kalian akan menang",
            "Atau kalian mati berusaha"
        ]
    },
    
    "epilogue_good": {
        "title": "KEBEBASAN",
        "type": "ending",
        "content": [
            "Monster jatuh",
            "Epstein dikalahkan",
            "",
            "Speedboat menjauhimu dari pulau",
            "Bukti aman di tanganmu",
            "Tim-mu selamat",
            "",
            "Di belakang: pulau terkutuk mengecil",
            "Di depan: cakrawala baru",
            "",
            "Dunia akan tahu",
            "Media akan expose",
            "Keadilan akan ditegakkan",
            "",
            "Kalian bukan lagi korban",
            "Kalian adalah penyintas",
            "Kalian adalah pahlawan",
            "",
            "Dan pulau ini?",
            "Tidak akan pernah menyakiti siapapun lagi"
        ]
    },

    "vio_route_1": {
        "title": "VIO: PERETAS DARI EDINBURGH",
        "type": "route_chapter",
        "content": [
            "Ruang server. Tersembunyi di balik dinding mansion.",
            "Di sini kamu terbangun.",
            "",
            "Mereka meremehkanmu.",
            "Menaruhmu di ruang komputer seperti menaruh tikus di gudang keju.",
            "Mereka pikir kamu tidak bisa berbuat apa-apa.",
            "",
            "Tapi mereka salah.",
            "Kamu Vio. Peretas kelas atas dari Edinburgh.",
            "Di kota kastil dan hujan itulah kemampuanmu diasah.",
            "",
            "File terenkripsi? Kamu bisa pecahkan.",
            "Sistem keamanan? Kamu bisa tembus.",
            "Jaringan internal? Kamu bisa kuasai.",
            "",
            "Edinburgh tidak pernah mencetak orang yang menyerah.",
            "Saatnya tunjukkan bahwa keputusan menaruhmu di sini",
            "adalah kesalahan terbesar yang pernah mereka buat."
        ]
    },
    
    "vio_route_2": {
        "title": "VIO: PERANG DIGITAL",
        "type": "route_chapter",
        "content": [
            "Laptop menyala.",
            "Terminal terbuka.",
            "Baris kode mulai mengalir.",
            "",
            "Kamu masuk ke jaringan internal pulau.",
            "Server demi server, komputer demi komputer.",
            "Semua terhubung. Semua bisa kamu akses.",
            "",
            "Daftar tamu — terenkripsi.",
            "Di dalamnya ada nama-nama besar.",
            "Politisi. Selebriti. Bangsawan kerajaan.",
            "",
            "Log penerbangan.",
            "Puluhan perjalanan ke pulau ini.",
            "Semua tercatat. Semua ada buktinya.",
            "",
            "Kamu unduh semuanya.",
            "Ini tambang emas informasi.",
            "Inilah yang akan menghancurkan mereka semua."
        ]
    },
    
    "vio_route_3": {
        "title": "VIO: PEMBOBOLAN SISTEM",
        "type": "route_chapter",
        "content": [
            "Alarm menyala.",
            "Mereka tahu kamu sudah masuk ke sistem.",
            "",
            "Tapi sudah terlambat.",
            "Kamu sudah dapat semuanya.",
            "Data sudah dienkripsi dan dicadangkan.",
            "",
            "Pintu keamanan? Sudah terbuka.",
            "Sistem kamera? Sudah diputar ulang ke rekaman lama.",
            "Komunikasi penjaga? Sudah dijamming.",
            "",
            "Kamu bukan sekadar peretas.",
            "Kamu adalah senjata digital.",
            "",
            "Dan sekarang, saatnya keluar.",
            "Bersama data yang akan meruntuhkan kekaisaran mereka."
        ]
    },

    "haikaru_route_1": {
        "title": "HAIKARU FUMIKA: THE STRATEGIST",
        "type": "route_chapter",
        "content": [
            "Sel penjara. Dingin dan gelap",
            "Sudah dua minggu kamu di sini",
            "",
            "Putri akademisi Kyoto tidak akan panik",
            "Kamu observe. Analyze. Plan",
            "Seperti yang Ayah ajarkan sejak kecil",
            "",
            "Guard shift: jam 6 pagi, 6 sore",
            "Patrol pattern: setiap 20 menit",
            "Blind spot kamera: 3 lokasi — tercatat semua",
            "",
            "Kamu Haikaru Fumika",
            "Juara olimpiade matematik. IQ 162",
            "Photographic memory yang tidak pernah gagal",
            "",
            "2 minggu. 47 halaman catatan",
            "Dan sekarang kamu tahu:",
            "Exactly kapan. Exactly bagaimana. Exactly kemana"
        ]
    },
    
    "haikaru_route_2": {
        "title": "HAIKARU FUMIKA: PERFECT TIMING",
        "type": "route_chapter",
        "content": [
            "T-minus 3 menit",
            "Pergantian shift penjaga",
            "",
            "Kamu menunggu",
            "Setiap detik terkalkulasi. Setiap langkah sudah direncanakan",
            "",
            "2 menit...",
            "Guard A meninggalkan pos — tepat 6 langkah ke kiri",
            "Guard B belum muncul dari belokan koridor",
            "",
            "1 menit...",
            "Window terbuka: 47 detik",
            "Cukup untuk mencapai tangga besi di ujung sayap utara",
            "",
            "NOW",
            "",
            "Fumika bergerak",
            "Persis seperti yang sudah diulang 38 kali dalam kepala",
            "Setiap langkah, setiap tikungan",
            "Sempurna. Presisi. Calculated",
            "",
            "Ini bukan keberuntungan",
            "Ini bukan keajaiban",
            "Ini adalah dua minggu kerja keras seorang Fumika"
        ]
    },
    
    "haikaru_route_3": {
        "title": "HAIKARU FUMIKA: MASTER STRATEGI",
        "type": "route_chapter",
        "content": [
            "Kamu sudah di luar sel.",
            "Tapi ini baru langkah pertama dari 47 langkah.",
            "",
            "Pulau ini seperti papan catur.",
            "Setiap bidak punya aturan geraknya.",
            "Setiap lawan punya kelemahan yang bisa dibaca.",
            "",
            "Fumika sudah memetakan papan ini dengan sempurna.",
            "Tujuh belas posisi penjaga — jam dan rotasinya tercatat.",
            "Delapan titik buta kamera — sudah diverifikasi langsung.",
            "Tiga jalur pelarian — sudah diurutkan berdasarkan risiko.",
            "Lima anak yang terjebak — lokasi terakhir yang diketahui.",
            "",
            "Informasi adalah segalanya.",
            "Dan Fumika punya semuanya tersimpan di satu tempat.",
            "*mengetuk kepala* Ingatan fotografis. Tidak pernah gagal.",
            "",
            "Saatnya bermain catur.",
            "Dan Fumika tidak pernah kalah."
        ]
    },

    "aolinh_route_1": {
        "title": "AO LIN: MELODI DI PANGGUNG GELAP",
        "type": "route_chapter",
        "content": [
            "Panggung teater. Gelap dan sunyi",
            "Kamu terbangun di sini, biola masih di tangan",
            "",
            "Mereka tidak mengambil biolamu",
            "Mungkin mereka pikir itu tidak berbahaya",
            "Mereka salah",
            "",
            "Ibu selalu berkata:",
            "'音乐是灵魂的语言 — musik adalah bahasa jiwa'",
            "'Dan jiwa yang kuat tidak bisa dipenjarakan'",
            "",
            "Jiejie... dimana kamu?",
            "Kalian diculik bersama dari Hongkong",
            "Tapi sejak kapal itu... terpisah",
            "",
            "Ao Lin tidak akan menyerah",
            "Tidak. Pernah",
            "",
            "Pegang biola. Tarik napas",
            "音乐给我力量",
            "Musik memberiku kekuatan"
        ]
    },
    
    "aolinh_route_2": {
        "title": "AO LIN: SIMFONI HARAPAN",
        "type": "route_chapter",
        "content": [
            "Kamu main biola",
            "Pelan. Lembut. Seperti ibu ajarkan",
            "",
            "Lagu tua dari Sichuan",
            "Melodi yang mengalir lewat koridor gelap",
            "Menembus tembok. Menembus ketakutan",
            "",
            "Anak-anak lain mendengar",
            "Mereka berhenti. Mereka keluar dari persembunyian",
            "",
            "'Aku tahu lagu itu...'",
            "'Nenekku dari Chengdu. Dia selalu nyanyikan itu'",
            "",
            "音乐连接我们 — musik menyatukan kita",
            "Di tengah kegelapan terdalam,",
            "Satu melodi membawa cahaya",
            "",
            "Satu per satu mereka mendekat.",
            "Ditarik oleh harmoni.",
            "Disatukan oleh musik yang melampaui semua batas.",
            "",
            "Ini bukan lagi solo.",
            "Ini simfoni",
            "Simfoni harapan dari gadis Chengdu"
        ]
    },
    
    "aolinh_route_3": {
        "title": "AO LIN: MENEMUKAN JIEJIE",
        "type": "route_chapter",
        "content": [
            "Kamu mendengar suara",
            "Lemah. Hampir tidak terdengar",
            "Tapi kamu kenal suara itu",
            "",
            "JIEJIE!",
            "",
            "Kamu berlari",
            "Biola di tangan, earphone biru bergetar di leher",
            "Musik memandu langkahmu",
            "",
            "Di basement, di balik pintu besi berkarat",
            "Dia ada. Lemah. Tapi hidup",
            "",
            "'Ao Lin... 妹妹... kamu... datang...'",
            "",
            "Air mata jatuh. Hangat di pipi yang dingin",
            "Tapi ini bukan saatnya menangis",
            "",
            "Kamu angkat biola",
            "Mainkan melodi ibu — yang paling kamu kenal",
            "Yang paling Jiejie kenal",
            "",
            "Frekuensi biola bergetar di engsel pintu tua...",
            "Bergetar... retak... TERBUKA",
            "",
            "音乐是魔法 — musik adalah keajaiban",
            "Dan kamu akan membawa Jiejie pulang"
        ]
    },

    "arganta_route_1": {
        "title": "AMERIGO ARGANTA: IL NAVIGATORE RISORGE",
        "type": "route_chapter",
        "content": [
            "Spiaggia. Pantai pulau terkutuk",
            "Reruntuhan perahu keluargamu di kejauhan",
            "Kayu-kayu yang dulu kamu kenal, kini serpihan di lautan",
            "",
            "'Rescue operation' katanya",
            "Bugiardi. Assassini palsu yang berkhianat",
            "Orang-orang Epstein membunuh keluargamu",
            "",
            "Kamu duduk di atas batu karang",
            "Menggenggam il compasso di Nonno",
            "Dan teringat malam-malam di geladak kapal",
            "Nonno bercerita tentang seorang pemuda legendaris dari Firenze,",
            "",
            "'Ayahnya digantung di depan matanya,' kata Nonno",
            "'Saudara-saudaranya dieksekusi'",
            "'Tapi Ezio tidak mati bersama mereka'",
            "'Dia berlari. Dia bertahan. Dia belajar'",
            "'Dan suatu hari dia kembali — bukan sebagai korban'",
            "'Tapi sebagai badai'",
            "",
            "Amerigo, kamu bukan Ezio",
            "Tapi kamu putra Napoli",
            "Dan Napoli tidak pernah menghasilkan pecundang",
            "",
            "Berdiri. Pegang kompas",
            "Jarum menunjuk barat laut: dermaga",
            "La via è sempre avanti",
            "",
            "Mulai sekarang, kamu bukan korban",
            "Kamu adalah badai yang sedang bangkit"
        ]
    },
    
    "arganta_route_2": {
        "title": "AMERIGO ARGANTA: PANDANGAN SANG NAVIGATOR",
        "type": "route_chapter",
        "content": [
            "Nonno mengajarimu membaca bintang sebelum bisa membaca huruf",
            "Di geladak kapal yang bergoyang, jari tua beliau menunjuk langit:",
            "'Utara selalu ada, Amerigo. Yang berubah hanya sudut pandangmu.'",
            "",
            "Il compasso non mente mai — kompas tidak pernah bohong",
            "",
            "Tapi kompas hanya berguna bagi mereka yang mau naik lebih tinggi",
            "Mau melihat lebih luas dari posisi mereka sekarang",
            "",
            "Kamu memanjat menara air di sudut pulau",
            "Tangan dan kaki menemukan pegangan seperti di tiang kapal dulu",
            "Otot ingat. Tubuh ingat",
            "",
            "Di atas sana, kamu lihat segalanya",
            "Utara: kompleks penjara — dijaga ketat",
            "Timur: mansion dan taman — lampu menyala malam",
            "Selatan: laboratorium — bau kimia, jauhi",
            "Barat: dermaga — target utama",
            "",
            "Jalur tersembunyi di balik hutan bakau",
            "Kanal irigasi yang guard tidak pernah patrol",
            "Shortcut dari mansion ke dermaga — 4 menit jalan cepat",
            "",
            "Peta mental terbentuk di kepala",
            "Lebih tajam dari peta kertas manapun",
            "",
            "Insting navigator yang diasah di lautan Mediterania",
            "Sekarang menemukan gunanya di pulau terkutuk ini",
            "",
            "Nonno benar:",
            "Yang berubah hanya sudut pandang",
            "Kamu sudah menemukan milikmu",
            "E tu lo farai — dan kamu akan melakukannya"
        ]
    },
    
    "arganta_route_3": {
        "title": "AMERIGO ARGANTA: IL CAMMINO DEL NAVIGATORE",
        "type": "route_chapter",
        "content": [
            "Nonno selalu berkata: orang yang mencari keadilan",
            "tidak pergi kepada mereka yang berkuasa",
            "Karena terlalu sering, merekalah bagian dari masalahnya",
            "",
            "Orang yang mencari keadilan belajar bergerak sendiri",
            "Di bayang-bayang. Tanpa suara. Tanpa jejak",
            "Dan menjangkau mereka yang seharusnya tidak bisa dijangkau",
            "",
            "Kamu Amerigo Arganta",
            "Bukan pejuang terlatih dengan senjata mahal",
            "Tapi kamu punya pisau lipat warisan Papà",
            "Dan gang-gang Napoli mengajarimu bergerak seperti bayangan",
            "",
            "Kamu tahu siapa yang bertanggung jawab:",
            "Epstein. Maxwell. Orang-orang berkuasa yang terlindungi",
            "Sistem yang melindungi monster karena monster itu berguna bagi mereka",
            "",
            "Semua fasad kekuasaan bisa ditembus",
            "Semua benteng punya pintu belakang",
            "Semua tirani punya celah",
            "Selama ada yang berani mencarinya",
            "",
            "Kamu akan survive",
            "Kamu akan kabur bersama timmu",
            "Tapi sebelum itu...",
            "",
            "Kamu akan pastikan pulau ini tidak lagi menjadi senjata",
            "Kamu akan pastikan nama-nama yang terlibat diketahui dunia",
            "Kamu akan pastikan keadilan ditegakkan",
            "",
            "Ini bukan sekadar dendam",
            "Ini tanggung jawab",
            "Bagi mereka yang melihat kebenaran dan punya kemampuan untuk bertindak",
            "",
            "Per Nonno. Per Papà. Per Mamma.",
            "Requiescat in pace — istirahatlah dengan tenang",
            "",
            "Il tuo erede porta avanti il tuo lavoro",
            "Pewarismu akan melanjutkan pekerjaan kalian"
        ]
    },

    "ignatius_route_1": {
        "title": "IGNATIUS: SANG INSINYUR",
        "type": "route_chapter",
        "content": [
            "Basement. Ruang kelistrikan.",
            "Generator cadangan berdengung pelan — suara yang justru menenangkan.",
            "",
            "Mereka menaruhmu di sini.",
            "Berpikir ini hanya gudang penyimpanan.",
            "Berpikir seorang anak dua belas tahun tidak akan bisa berbuat apa-apa.",
            "",
            "Tapi ini bukan gudang biasa.",
            "Ini pusat saraf seluruh pulau.",
            "Semua sistem keamanan, semua lampu, semua komunikasi —",
            "semuanya terhubung ke sini.",
            "",
            "Kamu Ignatius Forgers.",
            "Juara lomba sains tiga tahun berturut-turut.",
            "Yang membangun robot pertamamu di usia sepuluh tahun.",
            "Yang menciptakan sesuatu yang begitu berbahaya sehingga mereka memilih",
            "untuk menculikmu daripada membelimu.",
            "",
            "Kesalahan mereka.",
            "",
            "Papà selalu bilang: 'Otak yang tenang lebih tajam dari pisau manapun.'",
            "Dan otakmu sekarang sangat, sangat tenang.",
            "",
            "Satu pulsa elektromagnetik...",
            "Dan seluruh sistem mereka akan mati.",
            "",
            "Waktunya bekerja."
        ]
    },
    
    "ignatius_route_2": {
        "title": "IGNATIUS: SABOTASE SISTEM",
        "type": "route_chapter",
        "content": [
            "Multitool di tangan.",
            "Cetak biru terhampar di lantai.",
            "",
            "Kamu telusuri setiap sirkuit.",
            "Setiap kabel. Setiap sambungan. Setiap titik lemah.",
            "",
            "Jaringan daya utama: sudah dipetakan.",
            "Generator cadangan: sudah ditemukan.",
            "Protokol keamanan: sudah dianalisis.",
            "",
            "Sekarang kamu membangun sesuatu.",
            "Dari komponen-komponen sisa dan bagian bekas.",
            "Generator pulsa elektromagnetik buatan tangan.",
            "",
            "Tidak sempurna.",
            "Tapi cukup kuat.",
            "",
            "Aktifkan ini, dan...",
            "Seluruh sistem listrik di pulau ini akan mati.",
            "",
            "Kekacauan total.",
            "Distraksi sempurna untuk melarikan diri.",
            "",
            "Papà benar — otak insinyur sejati bekerja paling tajam",
            "justru saat situasi paling berbahaya."
        ]
    },
    
    "ignatius_route_3": {
        "title": "IGNATIUS: PERANG TEKNOLOGI",
        "type": "route_chapter",
        "content": [
            "Alat siap.",
            "Timer diatur: 5 menit.",
            "",
            "Kamu beritahu tim.",
            "'Saat lampu padam — lari.'",
            "",
            "5... 4... 3... 2... 1...",
            "",
            "BOOOM.",
            "",
            "Bukan ledakan sesungguhnya.",
            "Tapi pulsa elektromagnetik yang merembet ke seluruh sistem.",
            "",
            "Semua sistem elektronik: mati.",
            "Kamera: offline.",
            "Kunci magnetis: gagal — dan otomatis terbuka.",
            "Komunikasi penjaga: terputus.",
            "",
            "Para penjaga panik. Kekacauan di mana-mana.",
            "Tapi di tengah kegelapan itu, kamu tersenyum.",
            "",
            "Kekerasan bisa dikalahkan kekerasan.",
            "Uang bisa dikalahkan uang.",
            "Tapi teknologi yang tepat, di tangan yang tepat —",
            "tidak ada yang bisa mengalahkannya.",
            "",
            "Waktunya kabur.",
            "Di dalam kegelapan yang kamu ciptakan sendiri."
        ]
    },
    
    "ending_vio": {
        "title": "ENDING: KEMENANGAN SANG PERETAS",
        "type": "route_ending",
        "content": [
            "Ruang server. Untuk terakhir kalinya.",
            "Tapi kali ini kamu yang mengendalikan segalanya.",
            "",
            "Kamu unggah semuanya.",
            "Daftar tamu. Log penerbangan. Rekaman. Dokumen.",
            "Terabyte demi terabyte bukti.",
            "",
            "Cadangan cloud: tersimpan di beberapa lokasi.",
            "Saklar mati-otomatis: aktif.",
            "Jika kamu meninggal, semua data otomatis terkirim ke media.",
            "",
            "Epstein dikalahkan.",
            "Data diamankan.",
            "Misi selesai.",
            "",
            "Di speedboat, laptop masih terbuka di tanganmu.",
            "Kamu pantau saat data menyebar ke seluruh penjuru dunia.",
            "",
            "Situs berita meledak dengan berita ini.",
            "Media sosial terbakar.",
            "Dunia akhirnya tahu.",
            "",
            "Kamu bukan sekadar penyintas.",
            "Kamu adalah pelapor.",
            "Prajurit digital yang meruntuhkan sebuah kekaisaran.",
            "",
            "Edinburgh tidak mencetak orang yang menyerah.",
            "Dan peretasan ini mengubah segalanya."
        ]
    },
    
    "ending_haikaru": {
        "title": "ENDING: FUMIKA'S CHECKMATE",
        "type": "route_ending",
        "content": [
            "Setiap bidak sudah di posisinya",
            "Setiap variabel sudah diperhitungkan",
            "",
            "Rencana 47 langkah berjalan sempurna",
            "Zero deviasi. Zero mistakes",
            "",
            "Epstein: dikalahkan",
            "Guard: dinetralkan",
            "Tim: selamat",
            "Bukti: diamankan",
            "",
            "Checkmate",
            "",
            "Di speedboat, Fumika membuka buku catatan",
            "Terakhir kali melihatnya",
            "Lalu menutupnya dengan tenang",
            "",
            "Kesaksian akan ironclad",
            "47 halaman catatan detail",
            "Setiap nama. Setiap tanggal. Setiap fakta",
            "Tidak ada satu pun yang bisa dibantah",
            "",
            "Mereka bilang dia cuma anak perempuan dari Kyoto",
            "Tapi dia outthink mereka semua",
            "",
            "Kecerdasan mengalahkan kekuasaan",
            "Strategi mengalahkan kekuatan",
            "",
            "Sempurna. Terkalkulasi. Menang."
        ]
    },
    
    "ending_aolinh": {
        "title": "ENDING: SIMFONI AO LIN",
        "type": "route_ending",
        "content": [
            "Jiejie aman",
            "Tim diselamatkan",
            "Epstein dikalahkan",
            "",
            "Di speedboat, kamu mainkan biola",
            "Bukan lagu sedih. Bukan lagu marah",
            "Tapi lagu yang ibu ajarkan dulu",
            "Lagu dari Chengdu yang hangat",
            "",
            "Jiejie duduk di sebelahmu",
            "Tangannya menggenggam tanganmu",
            "Tidak ada kata-kata yang diperlukan",
            "",
            "Angin laut membawa melodi",
            "Anak-anak lain ikut mendengarkan",
            "Beberapa menangis. Beberapa tersenyum",
            "Semua merasakan hal yang sama",
            "",
            "Kegelapan mencoba membungkam musikmu",
            "Tapi musik terbukti lebih kuat",
            "",
            "Kanal berita menyebarkan ceritamu:",
            "'Gadis dari Chengdu yang menyelamatkan",
            "saudaranya dan teman-temannya",
            "dengan keberanian dan melodi'",
            "",
            "音乐是希望 — musik adalah harapan",
            "希望是力量 — harapan adalah kekuatan",
            "力量带来自由 — kekuatan membawa kebebasan",
            "",
            "Simfoni Ao Lin",
            "Standing ovation dari seluruh dunia"
        ]
    },
    
    "ending_arganta": {
        "title": "ENDING: IL NAVIGATORE — LA VIA È SEMPRE AVANTI",
        "type": "route_ending",
        "content": [
            "Il compasso di Nonno di tanganmu",
            "Jarum akhirnya menunjuk arah pulang",
            "",
            "Epstein dikalahkan",
            "Maxwell tidak bisa lagi bersembunyi",
            "Keadilan untuk keluarga Arganta dari Napoli",
            "La strada è libera — jalan kini bebas",
            "",
            "Di speedboat yang membelah ombak Karibia,",
            "Kamu buka kompas untuk terakhir kalinya hari ini",
            "Menelusuri ukiran tembaga tua dengan ibu jari",
            "",
            "'La via è sempre avanti, Amerigo'",
            "",
            "Suara Nonno begitu jelas terdengar",
            "Seolah beliau duduk di sebelahmu",
            "Seolah Papà dan Mamma ada di sana juga",
            "",
            "Kamu baru 13 tahun",
            "Masih jauh dari akhir perjalananmu",
            "Tapi hari ini kamu mengerti sesuatu yang penting:",
            "",
            "Dendam hanya membuatmu terus melihat ke belakang",
            "Keadilan memberimu alasan untuk terus maju",
            "La via è sempre avanti — jalan selalu ada di depan",
            "",
            "Kamu bukan hanya survivor",
            "Kamu navigatore yang memimpin tim ke keselamatan",
            "Kamu saksi yang bukti-buktinya akan mengubah dunia",
            "",
            "Setiap jalur dipetakan",
            "Setiap jalur pelarian diamankan",
            "Setiap orang selamat dan terhitung",
            "",
            "Bintang Karibia di atas kepalamu",
            "Sama seperti bintang Mediterania yang Nonno ajarkan dulu",
            "Sama indahnya. Sama setia menunjuk utara",
            "",
            "Amerigo mengangkat kompas ke langit malam",
            "",
            "'Requiescat in pace, Nonno.'",
            "'Requiescat in pace, Papà.'",
            "'Requiescat in pace, Mamma.'",
            "",
            "'Il vostro erede porta avanti il vostro lavoro.'",
            "'Pewaris kalian akan melanjutkan pekerjaan kalian.'",
            "",
            "La via è sempre avanti",
            "",
            "Il navigatore di Napoli",
            "ha riportato tutti a casa",
            "",
            "Navigator Napoli",
            "membawa semua orang pulang"
        ]
    },
    
    "ending_ignatius": {
        "title": "ENDING: CETAK BIRU SANG INSINYUR",
        "type": "route_ending",
        "content": [
            "Sistem mati total.",
            "Infrastruktur pulau: hancur.",
            "Bukti: tersimpan aman.",
            "",
            "Epstein dikalahkan.",
            "Bukan dengan kekerasan.",
            "Tapi dengan kecerdasan rekayasa.",
            "",
            "Setiap sistem elektronik disabotase.",
            "Setiap langkah keamanan ditembus.",
            "Setiap jalur pelarian dihitung dengan tepat.",
            "",
            "Di speedboat, kamu buka laptop.",
            "Memantau sistem pulau yang satu per satu padam.",
            "",
            "Generator: offline.",
            "Komunikasi: mati.",
            "Pertahanan: dinetralkan.",
            "",
            "Pembongkaran yang sempurna.",
            "Karya terbaik yang pernah kamu rancang.",
            "",
            "Media mendapat buktinya.",
            "Termasuk dokumentasi teknis.",
            "'Bagaimana seorang anak dua belas tahun meruntuhkan",
            "jaringan kriminal — satu sirkuit dalam satu waktu.'",
            "",
            "Papà selalu bilang otakmu aneh.",
            "Aneh dalam cara yang terbaik.",
            "",
            "Teknologi mengalahkan tirani.",
            "Rekayasa mengalahkan kejahatan.",
            "",
            "Cetak biru keadilan: selesai."
        ]
    },
    "ch1_solo_end": {
        "title": "CHAPTER 1 SELESAI: SENDIRIAN TAPI BEBAS",
        "type": "chapter_transition",
        "content": [
            "Kamu berhasil keluar dari starting area",
            "Seorang diri. Tanpa bantuan siapapun",
            "",
            "Tapi pulau ini masih besar",
            "Masih banyak bahaya di depan",
            "",
            "Di suatu tempat di pulau ini...",
            "Ada anak-anak lain yang terjebak",
            "Masing-masing berjuang sendirian",
            "",
            "Jika kamu bisa menemukan mereka...",
            "Jika kamu bisa membantu mereka...",
            "",
            "Kalian tidak perlu sendirian lagi"
        ]
    },

    "npc_haikaru_meet": {
        "title": "PERTEMUAN: HAIKARU FUMIKA",
        "type": "npc_encounter",
        "content": [
            "Di koridor penjara, seorang anak perempuan berdiri di sudut",
            "Tidak berlari. Tidak berteriak",
            "Hanya mengamati. Matanya seperti merekam segalanya",
            "",
            "Fumika: 'Kamu datang dari selatan. Lewat blind spot kamera ketiga.'",
            "Fumika: 'Gap antara patrol 7 menit 23 detik. Cukup untuk sampai ke sini.'",
            "Fumika: 'Baik. Kamu tahu cara bergerak.'",
            "",
            "Baru kemudian dia menoleh ke arahmu",
            "Matanya bukan ramah — tapi bukan juga bermusuhan",
            "Ini adalah tatapan orang yang sedang menghitung",
            "",
            "Fumika: 'Haikaru Fumika. Kyoto. Dua minggu di sini.'",
            "Fumika: '...Mereka mengambil buku catatanku.'",
            "Fumika: 'Semua data 47 halaman. Tanpa itu, rencanaku tidak sempurna.'"
        ]
    },
    "npc_haikaru_quest": {
        "title": "MISI: BUKU CATATAN FUMIKA",
        "type": "npc_quest",
        "content": [
            "Guard Station Wing-B",
            "Di situlah buku catatan Fumika disimpan",
            "",
            "Fumika: 'Penjaga itu ambil bukuku kemarin pagi.'",
            "Fumika: 'Guard Station Wing-B. Lantai 1. Laci ketiga dari kiri.'",
            "Fumika: 'Aku sudah verify lokasinya dari blind spot kamera di koridor C.'",
            "",
            "Dia tidak mengemis. Tidak memelas",
            "Hanya menyampaikan fakta dengan presisi seorang ahli strategi",
            "",
            "Fumika: 'Kalau kamu berhasil mengambilnya...'",
            "Fumika: 'Aku bergabung dengan timmu. Data 47 halaman ada di dalamnya.'",
            "Fumika: '17 posisi guard. 8 blind spot. 3 jalur pelarian. Semua tersimpan di sana.'"
        ]
    },
    "npc_haikaru_join": {
        "title": "HAIKARU FUMIKA BERGABUNG",
        "type": "npc_join",
        "content": [
            "Buku catatan itu kembali ke tangan yang berhak",
            "",
            "Fumika membukanya",
            "Membalik halaman demi halaman",
            "Mengecek setiap catatan masih utuh",
            "",
            "Fumika: '...Kamu benar-benar mengambilnya.'",
            "Fumika: 'Hmph. Efisien. Aku tidak menyangka.'",
            "",
            "Untuk pertama kalinya, ekspresinya berubah",
            "Bukan senyum — tapi sesuatu yang mendekatinya",
            "",
            "Fumika: 'Baik. Aku bergabung dengan timmu.'",
            "Fumika: 'Satu syarat: ikuti rencanaku. Deviasi tidak diperbolehkan.'",
            "Fumika: 'Dengan data ini... checkmate hanya tinggal masalah waktu.'"
        ]
    },

    "npc_aolinh_meet": {
        "title": "PERTEMUAN: AO LIN SI MUSISI",
        "type": "npc_encounter",
        "content": [
            "Dari dalam teater terdengar suara",
            "Bukan teriakan. Bukan tangis",
            "Melodi biola yang terhenti di tengah frase",
            "",
            "Di balik tirai panggung, seorang gadis kecil",
            "Seragam penjara. Biola di tangan. Earphone biru menggantung di leher",
            "Matanya berkaca-kaca tapi tidak menangis",
            "",
            "Ao Lin: '你是谁... Kamu siapa? Bukan penjaga?'",
            "",
            "Napasnya lega — sesaat saja, lalu cemas lagi",
            "",
            "Ao Lin: 'Ada penjaga namanya Brenin. Dia tidak mau biarkan aku pergi.'",
            "Ao Lin: 'Katanya aku harus main biola untuk boss-nya malam ini.'",
            "Ao Lin: 'Aku tidak mau. Tapi aku tidak bisa lawan dia sendiri...'"
        ]
    },
    "npc_aolinh_quest": {
        "title": "MISI: BEBASKAN AO LIN",
        "type": "npc_quest",
        "content": [
            "Theater Guard Brenin",
            "Penjaga yang menahan Ao Lin di teater",
            "",
            "Ao Lin: 'Dia besar dan galak. Aku sudah coba kabur dua kali, gagal.'",
            "Ao Lin: 'Tapi kalau kamu bisa ngalahin dia...'",
            "Ao Lin: '*menggenggam biola lebih erat* 我可以跑 — aku bisa lari!'",
            "",
            "Matanya tidak putus asa",
            "Di dalamnya ada semangat yang tidak padam",
            "Semangat anak Chengdu yang belajar bahwa musik tidak bisa dipenjarakan",
            "",
            "Ao Lin: '我相信你！ Aku percaya kamu bisa!'"
        ]
    },
    "npc_aolinh_join": {
        "title": "AO LIN BERGABUNG",
        "type": "npc_join",
        "content": [
            "Brenin jatuh",
            "Teater kembali sunyi",
            "",
            "Ao Lin berlari ke panggung",
            "Memeluk biolanya erat seperti memeluk seseorang yang dirindukan",
            "",
            "Ao Lin: '*mata berkaca-kaca* 谢谢！ Xiè xie... terima kasih...'",
            "Ao Lin: 'Jiejie-ku — kakakku — juga ada di sini di suatu tempat.'",
            "Ao Lin: 'Aku harus cari dia. Tapi sendirian... aku takut.'",
            "",
            "Dia mengangkat biola",
            "Memainkan beberapa nada — pelan, hangat",
            "Seperti salam dari jauh",
            "",
            "Ao Lin: '我们一起！ Kita bersama! 音乐给我们力量!'",
            "Ao Lin: 'Musik memberi kita kekuatan! Let's fight together! ♪'"
        ]
    },

    "npc_arganta_meet": {
        "title": "PERTEMUAN: AMERIGO ARGANTA",
        "type": "npc_encounter",
        "content": [
            "Di pantai, seorang anak lelaki berdiri di atas batu karang tinggi",
            "Memandang laut dengan pandangan yang jauh menembus cakrawala",
            "Seperti orang yang sudah terbiasa membaca lautan",
            "",
            "Postur tubuhnya mengingatkan pada sesuatu",
            "Cara berdiamnya — kewaspadaan tanpa ketegangan yang terlihat",
            "Seperti seseorang yang siap bergerak kapan pun",
            "",
            "Amerigo: 'Chi sei? Siapa kamu?'",
            "",
            "Dia turun dari batu dengan gerakan yang natural dan cepat",
            "Tidak canggung. Terlatih",
            "",
            "Amerigo: 'Ah. Bukan penjaga. Bene.'",
            "Amerigo: 'Itu perahu keluargaku di sana. Yang hancur itu.'",
            "Amerigo: 'Nonno-ku bilang, seorang navigator selalu tahu kapan harus diam'",
            "Amerigo: 'Dan kapan harus bertindak. Sekarang waktunya bertindak.'",
            "",
            "Tangannya merogoh saku — ekspresinya berubah",
            "Bukan panik. Tapi kehilangan yang dalam",
            "",
            "Amerigo: 'Il mio compasso... kompas Nonno-ku.'",
            "Amerigo: 'Penjaga dermaga mengambilnya. Satu-satunya yang tersisa dari keluargaku.'",
            "Amerigo: 'Tanpanya... aku merasa seperti kapal tanpa bintang penunjuk.'"
        ]
    },
    "npc_arganta_quest": {
        "title": "MISI: KOMPAS NONNO ARGANTA",
        "type": "npc_quest",
        "content": [
            "Gudang barat dermaga",
            "Di situlah kompas Nonno Arganta disimpan",
            "",
            "Amerigo: 'Kompas itu bertuliskan: La via è sempre avanti.'",
            "Amerigo: 'Jalan selalu ada di depan. Itu yang Nonno selalu katakan.'",
            "",
            "Dia diam sebentar. Matanya jauh",
            "",
            "Amerigo: 'Nonno sering cerita tentang para pejuang Italia yang kehilangan segalanya.'",
            "Amerigo: 'Orang-orang yang keluarganya dirampas, tapi tidak hancur oleh tragedi.'",
            "Amerigo: 'Kata Nonno: seorang yang sejati tidak hancur oleh tragedi.'",
            "Amerigo: 'Dia ditempa olehnya.'",
            "",
            "Dia berbalik menatapmu langsung",
            "",
            "Amerigo: 'Aku tidak meminta belas kasihan.'",
            "Amerigo: 'Aku menawarkan kerjasama. Bantu aku dapatkan kompas itu...'",
            "Amerigo: 'Dan aku akan tunjukkan setiap jalur di pulau ini.'",
            "Amerigo: 'Navigatore Napoli selalu menepati kata-katanya.'"
        ]
    },
    "npc_arganta_join": {
        "title": "AMERIGO ARGANTA BERGABUNG",
        "type": "npc_join",
        "content": [
            "Kompas antik itu kembali ke tangan yang berhak",
            "",
            "Amerigo menggenggamnya",
            "Menutup mata",
            "Jari-jarinya menelusuri ukiran di permukaan tembaga tua",
            "",
            "Amerigo: 'La via è sempre avanti...'",
            "Amerigo: '*membuka mata, suaranya lebih kuat* Grazie. Terima kasih.'",
            "",
            "Dia membuka kompas",
            "Jarum bergoyang sebentar lalu menunjuk mantap ke barat laut",
            "",
            "Amerigo: 'Nonno selalu bilang: seorang navigator sejati tidak berlayar sendirian.'",
            "Amerigo: 'Sendirian kamu cepat, bersama kamu bisa jauh lebih jauh.'",
            "Amerigo: 'Aku bergabung dengan timmu. Aku yang navigasi.'",
            "",
            "Dia mengantongi kompas dengan hati-hati",
            "Dan untuk pertama kalinya ada sesuatu seperti cahaya di matanya",
            "",
            "Amerigo: 'Dermaga 800 meter, jalur aman lewat hutan bakau.'",
            "Amerigo: 'Penjaga bertukar posisi tiap 20 menit. Kita punya window 4 menit.'",
            "Amerigo: 'Requiescat in pace, Nonno. Il tuo erede porta avanti il tuo lavoro.'",
            "Amerigo: 'La via è sempre avanti. Ayo — jalan kita masih panjang.'"
        ]
    },

    "npc_ignatius_meet": {
        "title": "PERTEMUAN: IGNATIUS SI INSINYUR",
        "type": "npc_encounter",
        "content": [
            "Suara ketukan logam dari balik pintu besi",
            "Bukan serangan - ritmenya terlalu teratur",
            "Seseorang sedang bekerja",
            "",
            "Di basement, seorang anak lelaki",
            "Dikelilingi kabel, papan sirkuit, dan komponen elektronik",
            "Wajahnya bersinar penuh antusias yang ganjil untuk situasi ini",
            "",
            "Ignatius: 'OH! Akhirnya ada orang! Perfect timing!'",
            "Ignatius: 'Aku Ignatius. Aku lagi bangun sesuatu yang sangat keren.'",
            "",
            "Dia menunjuk tumpukan komponen setengah jadi",
            "",
            "Ignatius: 'EMP pulse generator. Satu aktivasi, semua sistem keamanan mati.'",
            "Ignatius: 'Tapi... aku butuh 3 komponen lagi. Ada di mansion. Dan aku tidak bisa keluar basement ini.'"
        ]
    },
    "npc_ignatius_quest": {
        "title": "MISI: KOMPONEN EMP IGNATIUS",
        "type": "npc_quest",
        "content": [
            "Tiga komponen. Tersebar di mansion",
            "",
            "Ignatius: 'Kapasitor Besar - di gudang supply lantai 1.'",
            "Ignatius: 'Relay Switch - di ruang komunikasi lantai 2.'",
            "Ignatius: 'Copper Coil - di ruang generator timur.'",
            "",
            "Dia menggambar peta cepat di secarik kertas",
            "Tangan kecilnya ternyata sangat presisi",
            "",
            "Ignatius: 'Kalau semua komponen terkumpul...'",
            "Ignatius: '*mata berbinar* EMP ini akan matiin SEMUA sistem di pulau.'",
            "Ignatius: 'Percaya saja padaku. Ini akan berhasil!'"
        ]
    },
    "npc_ignatius_join": {
        "title": "IGNATIUS BERGABUNG",
        "type": "npc_join",
        "content": [
            "Semua komponen terkumpul",
            "Ignatius melompat kegirangan",
            "",
            "Ignatius: 'YES! SEMUA ADA! Ini yang aku butuhkan!'",
            "Ignatius: '*langsung mulai merakit dengan cepat* Kasih aku 10 menit!'",
            "",
            "Tangannya bergerak cepat. Terampil",
            "Jari-jarinya hafal setiap komponen",
            "",
            "Ignatius: 'Oke. Alat ini butuh diaktifkan di dekat panel listrik utama.'",
            "Ignatius: 'Aku ikut. Aku yang handle semua urusan teknis.'",
            "Ignatius: 'Kalau alatnya pakai listrik, aku bisa retas atau hancurkan!'"
        ]
    },

    "npc_vio_meet": {
        "title": "PERTEMUAN: VIO SI HACKER EDINBURGH",
        "type": "npc_encounter",
        "content": [
            "Di server room mansion, layar komputer menyala dalam gelap",
            "Seseorang sudah ada di sana - sedang mengetik cepat",
            "",
            "Vio: '...Shhh. Aku lagi decrypt.'",
            "",
            "Tanpa menoleh. Matanya tidak meninggalkan layar",
            "Jari-jarinya tidak berhenti",
            "",
            "Vio: 'Sistem keamanan pulau ini payah. Backdoor di mana-mana.'",
            "Vio: 'Tapi ada satu file yang menarik. Guest list dan flight log.'",
            "Vio: '...Tapi enkripsinya butuh USB drive khusus dari security room.'",
            "",
            "Baru sekarang dia menoleh",
            "Mengukurmu sebentar",
            "",
            "Vio: 'Kamu lihat-ku gimana. Aku lihat kamu bisa bergerak.'",
            "Vio: 'Deal? Kamu ambil USB-nya, aku buka semua file mereka.'"
        ]
    },
    "npc_vio_quest": {
        "title": "MISI: USB DRIVE TERENKRIPSI",
        "type": "npc_quest",
        "content": [
            "Security Room. Mansion lantai 2",
            "Di situlah USB Security Drive disimpan",
            "",
            "Vio: 'Ruangan itu dijaga. Tapi lock-nya model lama.'",
            "Vio: 'Security patch terakhir 2017. Seriously? These people.'",
            "",
            "Dia kembali ke layar - tapi sekarang ada sedikit nada menunggu",
            "",
            "Vio: 'File ini kalau berhasil di-crack...'",
            "Vio: 'Nama-nama besar. Semua tamu pulau ini. Bukti yang mengubah segalanya.'",
            "Vio: '...Edinburgh trained me for exactly this moment.'"
        ]
    },
    "npc_vio_join": {
        "title": "VIO BERGABUNG",
        "type": "npc_join",
        "content": [
            "USB drive berpindah tangan",
            "Vio langsung mencolokkannya",
            "Jari-jarinya menari di keyboard",
            "",
            "Vio: '...Nice. Enkripsi 256-bit? Cracked dalam 3 menit.'",
            "Vio: 'Guest list. Flight log. Offshore accounts. Semuanya ada.'",
            "",
            "Dia menyandarkan punggung",
            "Ekspresi puas yang tenang",
            "",
            "Vio: 'Peretas Edinburgh menghargai kerja sama yang baik.'",
            "Vio: 'Aku gabung. Data ini sudah aku cadangkan ke cloud — saklar mati-otomatis.'",
            "Vio: 'Kalau kita kenapa-napa, data ini otomatis terkirim ke media seluruh dunia.'"
        ]
    },

    "chapter_1_crisis": {
        "title": "CHAPTER 1: SAAT DUNIA RUNTUH",
        "type": "chapter_beat",
        "content": [
            "Alarm masih meraung di lorong-lorong",
            "Tapi sesuatu berubah — suara tembakan di luar",
            "",
            "Para penjaga tidak lagi panik",
            "Mereka mendapat perintah baru:",
            "Bunuh semua yang kabur",
            "",
            "Langkahmu melambat",
            "Kakimu gemetar untuk pertama kalinya",
            "",
            "Ini bukan sekadar kabur dari sel lagi",
            "Ini adalah pertarungan untuk tetap hidup",
            "",
            "Tapi di dalam ketakutan itu,",
            "Ada sesuatu yang muncul:",
            "",
            "Kemarahan",
            "Bersih dan dingin",
            "Seperti pisau yang baru diasah",
            "",
            "Mereka tidak berhak atas nyawamu",
            "Mereka tidak berhak atas siapapun di sini",
            "",
            "Mundur bukan pilihan"
        ]
    },

    "chapter_2_trust": {
        "title": "CHAPTER 2: KETIKA ORANG ASING MENJADI TIM",
        "type": "chapter_beat",
        "content": [
            "Kalian baru saja bertemu beberapa jam lalu",
            "Anak-anak dari negara berbeda",
            "Bahasa berbeda. Latar belakang berbeda",
            "",
            "Namun di ruang gelap ini,",
            "Kalian makan dari satu kaleng yang sama",
            "Berbagi selimut yang sudah compang-camping",
            "Bergantian berjaga sementara yang lain istirahat",
            "",
            "Tidak ada kontrak. Tidak ada janji palsu",
            "Hanya satu pemahaman yang tidak perlu diucapkan:",
            "",
            "Kamu tidak akan kutinggalkan",
            "Dan aku tidak akan meninggalkanmu",
            "",
            "Di dunia yang penuh pengkhianatan ini,",
            "Kepercayaan kecil itu terasa seperti harta paling berharga",
            "",
            "Kalian bukan lagi orang asing",
            "Kalian adalah tim"
        ]
    },

    "chapter_3_revelation": {
        "title": "CHAPTER 3: KEBENARAN YANG MEMBAKAR",
        "type": "chapter_beat",
        "content": [
            "File itu terbuka di depan kalian",
            "Nama-nama. Foto-foto. Tanggal. Rekaman",
            "",
            "Tangan kalian gemetar membacanya",
            "",
            "Politisi yang kalian kenal dari berita",
            "Tokoh agama yang dipuja jutaan orang",
            "CEO yang dipuji majalah bisnis dunia",
            "Bangsawan dengan gelar kuno dan reputasi bersih",
            "",
            "Semua ada di sini",
            "Semua pernah ke pulau ini",
            "Semua tahu",
            "",
            "Ada yang menangis",
            "Ada yang tidak bisa bicara",
            "Ada yang hanya menatap layar dalam diam",
            "",
            "Kalian masih anak-anak",
            "Kalian seharusnya tidak tahu hal-hal ini",
            "Kalian seharusnya masih di rumah",
            "",
            "Tapi sekarang kalian tahu",
            "Dan tidak ada jalan untuk tidak tahu lagi",
            "",
            "Yang tersisa hanya satu pertanyaan:",
            "Apa yang akan kalian lakukan dengan kebenaran ini?"
        ]
    },

    "chapter_final_confrontation": {
        "title": "FINAL: TIDAK ADA YANG BISA BERHENTI SEKARANG",
        "type": "chapter_beat",
        "content": [
            "Dermaga sudah terlihat",
            "Speedboat menunggu",
            "Tapi jalan ke sana diblokir",
            "",
            "Epstein berdiri di sana",
            "Tidak sendirian",
            "Dengan semuanya yang dimilikinya:",
            "Uang. Kuasa. Penjaga bersenjata",
            "",
            "Dia menatap kalian",
            "Anak-anak yang seharusnya sudah hancur",
            "Anak-anak yang seharusnya sudah menyerah",
            "",
            "'Apa yang kalian pikir akan kalian lakukan?'",
            "Suaranya meremehkan",
            "'Aku punya koneksi di semua tempat.'",
            "'Tidak ada yang akan percaya kalian.'",
            "",
            "Tapi kemudian seseorang di tim kalian melangkah maju",
            "Dan berkata dengan suara yang stabil:",
            "",
            "'Kami tidak perlu siapapun yang percaya kami.'",
            "'Data sudah ter-upload. Deadman switch aktif.'",
            "'Seluruh dunia sudah tahu namamu.'",
            "",
            "Untuk pertama kalinya,",
            "Epstein-lah yang terlihat takut"
        ]
    },

    "vio_route_4": {
        "title": "VIO: BOBOT DARI NAMA-NAMA ITU",
        "type": "route_chapter",
        "content": [
            "Layar penuh teks terenkripsi yang sudah kamu crack",
            "Guest list. Satu per satu nama terungkap",
            "",
            "Kamu berhenti",
            "",
            "Nama pertama: Senator dari negara demokrasi terbesar di dunia",
            "Nama kedua: Bangsawan dengan gelar Kerajaan yang kuno",
            "Nama ketiga: Tokoh filantropi yang namanya ada di gedung-gedung amal",
            "Nama keempat: CEO yang wajahnya ada di sampul majalah 'Pemimpin Masa Depan'",
            "",
            "Tanganmu berhenti mengetik",
            "",
            "Kamu bukan hacker yang mudah shock",
            "Kamu sudah lihat banyak hal dari balik layar",
            "Tapi ini berbeda",
            "",
            "Ini bukan data",
            "Ini wajah-wajah orang sungguhan",
            "Yang dengan sadar memilih untuk datang ke sini",
            "Yang dengan sadar memilih untuk tutup mata",
            "Yang dengan sadar memilih untuk melindungi monster",
            "",
            "Matamu memanas",
            "Kamu berkedip cepat",
            "",
            "Edinburgh trained you to be cold under pressure",
            "Tapi ada hal-hal yang bahkan Edinburgh tidak bisa",
            "membuat kamu kebal darinya",
            "",
            "Kamu simpan semuanya",
            "Setiap nama. Setiap tanggal. Setiap foto",
            "Ini bukan lagi soal kabur",
            "Ini soal memastikan dunia tidak bisa pura-pura tidak tahu"
        ]
    },

    "vio_route_5": {
        "title": "VIO: DEADMAN SWITCH",
        "type": "route_chapter",
        "content": [
            "Terakhir kali di server room ini",
            "Semua data sudah dikompilasi",
            "3.7 terabyte bukti. Encrypted. Backed up",
            "Di tujuh server berbeda di empat benua",
            "",
            "Kamu atur saklar mati-otomatis terakhir",
            "Script kecil yang elegannya membuatmu hampir bangga:",
            "Jika sinyal check-in 24 jam tidak diterima,",
            "Semua data auto-release ke 300 jurnalis terpilih",
            "Plus Wikileaks. Plus The Guardian. Plus tiga investigative desk lainnya",
            "",
            "Kamu menekan ENTER untuk terakhir kalinya",
            "",
            "UPLOAD INITIATED",
            "DEADMAN SWITCH: ARMED",
            "DISTRIBUTION LIST: LOCKED",
            "",
            "Kamu tutup laptop",
            "Berdiri",
            "",
            "Di luar, tim sudah menunggu",
            "Suara tembakan semakin dekat",
            "Tapi dalam dadamu ada sesuatu yang tidak ada sebelumnya:",
            "",
            "Keyakinan.",
            "",
            "Apapun yang terjadi padamu hari ini,",
            "mereka tidak bisa lagi menyembunyikan ini.",
            "Dunia sudah diberitahu.",
            "",
            "Edinburgh tidak pernah mencetak orang yang menyerah.",
            "Dan hari ini, peretas dari Edinburgh itu",
            "baru saja memenangkan pertarungan paling penting dalam hidupnya."
        ]
    },

    "haikaru_route_4": {
        "title": "HAIKARU FUMIKA: VARIABEL YANG TIDAK DIPERHITUNGKAN",
        "type": "route_chapter",
        "content": [
            "Langkah ke-23 dari rencana 47 langkah",
            "Seharusnya berjalan mulus",
            "",
            "Tapi kemudian dia muncul",
            "Anak kecil. Tidak ada dalam catatanmu",
            "Umur mungkin 8 tahun. Tersembunyi di balik pipa di koridor",
            "Matanya menatapmu",
            "Ketakutan yang murni dan tak tersembunyikan",
            "",
            "Rencana 47 langkah tidak memasukkan variabel ini",
            "",
            "Ambil dia: kecepatan turun 40%, risiko naik signifikan",
            "Tinggalkan dia: rencana tetap optimal",
            "",
            "Fumika berdiri di sana",
            "Untuk pertama kalinya dalam dua minggu,",
            "Kalkulasinya berhenti",
            "",
            "Bukan karena data tidak ada",
            "Tapi karena ada sesuatu di dalam dirinya",
            "yang menolak untuk mengolah pertanyaan itu sebagai kalkulasi",
            "",
            "Di Kyoto, Ibu pernah berkata:",
            "'Fumika-chan, kecerdasan yang sejati'",
            "'bukan soal berapa banyak yang bisa kamu hitung'",
            "'Tapi soal apa yang kamu pilih untuk diperhitungkan'",
            "",
            "Fumika jongkok",
            "Uluran tangan",
            "'Namamu siapa?'",
            "",
            "Rencana akan diadaptasi",
            "Fumika tidak pernah tidak bisa beradaptasi"
        ]
    },

    "haikaru_route_5": {
        "title": "HAIKARU FUMIKA: PROTOKOL ADAPTASI",
        "type": "route_chapter",
        "content": [
            "Rencana 47 langkah kini menjadi rencana 61 langkah",
            "Dengan satu variabel baru yang tidak ada dalam buku catatan:",
            "Seorang anak kecil bernama Jun yang tidak mau lepaskan tanganmu",
            "",
            "Fumika menghitung ulang semua probabilitas dalam 30 detik",
            "Rute dimodifikasi. Timing disesuaikan",
            "Formasi tim diubah untuk melindungi yang paling rentan",
            "",
            "Ada sesuatu yang berbeda dalam kepalamu sekarang",
            "Kalkulasi masih ada — tidak pernah berhenti",
            "Tapi di balik angka-angka itu ada sesuatu yang lebih hangat",
            "",
            "Photographic memory-mu menyimpan wajah Jun",
            "Cara dia akhirnya tersenyum saat kamu bilang dia aman",
            "Seperti beban yang terlalu besar untuk bahu sekecil itu",
            "akhirnya bisa diletakkan",
            "",
            "Langkah ke-59: formasi tim diubah untuk melindungi yang paling rentan.",
            "Langkah ke-60: jalur keluar dialihkan lewat koridor yang lebih aman.",
            "Langkah ke-61: semua orang naik ke speedboat — tidak ada yang tertinggal.",
            "",
            "Fumika menutup buku catatan",
            "47 halaman data tentang penjara yang sudah tidak relevan lagi",
            "Dan satu halaman baru, kosong, menunggu",
            "",
            "Ini bukan kemenangan yang ada dalam rencananya",
            "Ini lebih baik dari itu",
            "",
            "Karena ini nyata"
        ]
    },

    "aolinh_route_4": {
        "title": "AO LIN: JIEJIE DI UJUNG BAHAYA",
        "type": "route_chapter",
        "content": [
            "Jiejie ditemukan",
            "Tapi belum bebas",
            "",
            "Pintu besi itu terkunci dari luar dengan gembok baru",
            "Seseorang tahu kalian sudah di sini",
            "Langkah kaki berat terdengar di koridor sebelah",
            "",
            "Jiejie menggenggam tanganmu lewat celah kecil di pintu",
            "Tangannya dingin tapi cengkeramannya kuat",
            "'Ao Lin — ada dua penjaga. Mereka akan kembali dalam 5 menit.'",
            "'Pergi. Tinggalkan aku. Selamatkan dirimu sendiri.'",
            "",
            "Kamu tarik tangannya lebih erat",
            "'Tidak.'",
            "",
            "Satu kata. Tapi beratnya seperti batu karang",
            "",
            "Kamu angkat biola",
            "Ibu mengajarimu tentang resonansi",
            "Tentang frekuensi yang bisa membuat gelas pecah",
            "Tentang getaran yang bisa menembus yang tampaknya tidak bisa ditembus",
            "",
            "Kamu ingat kunci nada yang tepat:",
            "Gembok tua. Engsel berkarat. Logam yang lelah",
            "",
            "'Tutup telingamu, Jiejie'",
            "",
            "Busur naik ke atas senar",
            "Dan Ao Lin memainkan not paling keras",
            "yang pernah dia mainkan dalam hidupnya"
        ]
    },

    "aolinh_route_5": {
        "title": "AO LIN: SIMFONI TERAKHIR",
        "type": "route_chapter",
        "content": [
            "Jiejie bebas",
            "Tanganmu masih gemetar",
            "Tapi ada sesuatu yang telah berubah",
            "",
            "Penjaga muncul dari tikungan",
            "Mereka melihat kalian",
            "Mereka bergerak",
            "",
            "Tapi sebelum mereka bisa berteriak,",
            "kamu mainkan sesuatu",
            "",
            "Bukan serangan",
            "Bukan ancaman",
            "",
            "Kamu mainkan lagu dari Chengdu",
            "Lagu yang Ibu ajarkan saat kamu berumur empat tahun",
            "Lagu yang selalu membuat Jiejie menangis dengan senyum di wajahnya",
            "Lagu yang katanya bisa membuat awan berhenti dan mendengarkan",
            "",
            "Dan sesuatu yang aneh terjadi",
            "",
            "Satu penjaga berhenti",
            "Tangannya turun",
            "Di matanya ada sesuatu yang tidak bisa disembunyikan:",
            "Kerinduan. Rumah. Ibu yang menunggunya suatu tempat",
            "",
            "Itu cukup",
            "Tim bergerak. Kalian berlari",
            "",
            "Di belakangmu melodi masih mengambang di udara",
            "Seperti obat yang tidak pernah diminta",
            "Seperti cahaya yang menyusup lewat retak di dinding terkuat sekalipun",
            "",
            "音乐是希望",
            "Musik adalah harapan",
            "Dan harapan selalu menemukan jalannya"
        ]
    },

    "arganta_route_4": {
        "title": "AMERIGO ARGANTA: MEMIMPIN DI BAYANG-BAYANG",
        "type": "route_chapter",
        "content": [
            "Tim bergantung padamu",
            "Kamu yang memegang kompas",
            "Kamu yang tahu jalan",
            "",
            "Tapi malam ini kabut turun tebal",
            "Jalur hutan bakau yang kamu hafal",
            "tiba-tiba terlihat berbeda dalam kegelapan",
            "",
            "Di belakangmu: enam orang",
            "Semuanya mengikuti langkahmu",
            "Semuanya percaya pada kompasmu",
            "Semuanya percaya padamu",
            "",
            "Nonno pernah bilang:",
            "'Seorang navigator yang sejati tidak hanya tahu arah'",
            "'Dia tahu cara membuat orang lain percaya pada arah itu'",
            "'Bahkan saat dia sendiri tidak 100% yakin'",
            "",
            "Tanganmu mencengkeram kompas lebih erat",
            "Jarum bergoyang — lalu mantap menunjuk barat laut",
            "",
            "Kamu naik ke pohon bakau tertinggi",
            "Di kejauhan: lampu dermaga",
            "Samar. Tapi ada",
            "",
            "Kamu turun",
            "Matamu menatap tim",
            "",
            "'Ikut aku. Tiga ratus meter lagi.'",
            "Suaramu tidak gemetar",
            "Meski tanganmu iya",
            "",
            "Begitulah cara Nonno memimpin",
            "Kamu melakukannya juga"
        ]
    },

    "arganta_route_5": {
        "title": "AMERIGO ARGANTA: IL VENTO DEL SUD",
        "type": "route_chapter",
        "content": [
            "Dermaga akhirnya di depan mata",
            "Bukan mimpi. Bukan halusinasi dari rasa lelah",
            "Nyata",
            "",
            "Speedboat tertambat di ujung dermaga",
            "Gelap. Tidak dijaga",
            "Persis seperti yang kamu prediksi berdasarkan pola patrol",
            "",
            "Tapi sebelum kalian mencapai tangga dermaga,",
            "kamu berhenti",
            "",
            "Tim bertanya dengan mata mereka",
            "",
            "Kamu keluarkan il compasso",
            "Membukanya di bawah cahaya bintang",
            "Jarum bergoyang",
            "Dan untuk pertama kali sejak Nonno pergi,",
            "kamu biarkan air mata jatuh",
            "",
            "Tidak ada yang berkomentar",
            "Ao Lin menyentuh bahumu pelan",
            "Fumika menundukkan kepala singkat",
            "",
            "Kamu menutup kompas",
            "Mengantonginya dengan hati-hati",
            "",
            "'Per Nonno. Per Papà. Per Mamma.'",
            "'Requiescat in pace.'",
            "",
            "Lalu kamu membalik badan",
            "Menatap dermaga",
            "Menatap kebebasan yang sudah kalian perjuangkan",
            "",
            "Il vento del sud — angin selatan",
            "selalu membawa pelaut Napoli pulang ke rumah",
            "",
            "Hari ini, kamu membawa semua orang bersamamu"
        ]
    },

    "ignatius_route_4": {
        "title": "IGNATIUS: MERAKIT HARAPAN",
        "type": "route_chapter",
        "content": [
            "Semua komponen di depanmu",
            "Kapasitor besar. Relay switch. Copper coil",
            "",
            "Tangan kecilmu mulai bekerja",
            "",
            "Ini bukan robot yang pernah kamu build di rumah",
            "Ini bukan project sains yang pernah kamu bawa ke kompetisi",
            "",
            "Ini berbeda",
            "Karena jika ini gagal,",
            "Bukan nilai nol yang kamu dapat",
            "",
            "Tapi tanganmu tidak gemetar",
            "Aneh",
            "",
            "Papà selalu bilang kamu aneh",
            "Di saat orang lain panik, justru otakmu jernih",
            "Di saat tekanan naik, justru fokusmu bertambah",
            "",
            "'Itu bukan kelemahan, Iggy,' kata Papà",
            "'Itu adalah cara kerja otak insinyur sejati'",
            "",
            "Senar demi senar disambungkan",
            "Komponen demi komponen dipasangkan",
            "Blueprint di kepalamu — jauh lebih akurat dari kertas",
            "",
            "30 menit",
            "20 menit",
            "10 menit",
            "",
            "Dan kemudian kamu mendengar klik yang kamu tunggu",
            "Indikator hijau menyala",
            "",
            "EMP generator: READY",
            "",
            "Kamu menatap alat kecil di tanganmu",
            "Terbuat dari sampah elektronik dan kepercayaan diri",
            "Cukup untuk mematikan sebuah pulau",
            "",
            "Waktunya bekerja."
        ]
    },

    "ignatius_route_5": {
        "title": "IGNATIUS: BLACKOUT",
        "type": "route_chapter",
        "content": [
            "Panel listrik utama",
            "Jantung dari semua sistem keamanan pulau ini",
            "",
            "Kamu berdiri di depannya",
            "EMP generator di tangan",
            "Tim menunggu di balik pintu",
            "",
            "Kamu set timer: 3 menit",
            "Cukup untuk semua orang mencapai dermaga",
            "Cukup untuk blackout berlangsung sebelum penjaga bisa koordinasi",
            "",
            "Timer berputar",
            "2:59",
            "2:58",
            "2:57...",
            "",
            "Di tiga menit itu kamu berdiri sendiri",
            "Di ruang yang paling berbahaya di pulau ini",
            "Menunggu",
            "",
            "Aneh — bukan ketakutan yang kamu rasakan",
            "Tapi sesuatu seperti ketenangan",
            "",
            "Problem sudah di-analyze",
            "Solution sudah di-engineer",
            "Variables sudah di-account for",
            "",
            "0:03",
            "0:02",
            "0:01",
            "",
            "PULSE",
            "",
            "Semua lampu padam",
            "Semua layar mati",
            "Semua kamera buta",
            "Semua pintu terkunci elektronik: terbuka",
            "",
            "Dalam kegelapan total itu,",
            "Ignatius tersenyum",
            "",
            "Rekayasa mengalahkan segalanya.",
            "Setiap. Saat."
        ]
    },

}

CHARACTER_BACKSTORIES = {
    "vio": {
        "title": "VIO — Peretas Kelas Atas dari Edinburgh",
        "content": [
            "Namamu: Vincenzo Alastair",
            "Umur: 13 tahun",
            "Asal: Edinburgh, Skotlandia",
            "",
            "Kamu bukan peretas sembarangan.",
            "Kamu kelas atas. Terbaik.",
            "Juara kompetisi keamanan siber sejak usia 11 tahun.",
            "Pemburu celah keamanan dengan rekam jejak bersih.",
            "",
            "Di Edinburgh yang dingin,",
            "kamu tumbuh di antara batu kastil dan hujan.",
            "Tapi pikiranmu selalu ada di dunia digital.",
            "",
            "Suatu hari kamu salah pilih target.",
            "Tantangan yang terlihat biasa.",
            "Tanpa sengaja kamu menembus jaringan keuangan Epstein.",
            "Melihat hal-hal yang tidak seharusnya kamu lihat.",
            "",
            "Mereka menemukanmu.",
            "Mereka membawamu pergi.",
            "",
            "Dari Edinburgh ke pulau terkutuk.",
            "Jauh dari tanah yang kamu cintai.",
            "",
            "Tapi mereka salah.",
            "Mereka meremehkanmu.",
            "",
            "Sistem mereka akan menjadi senjatamu.",
            "Kode akan menjadi jalan keluarmu.",
            "",
            "Edinburgh tidak mencetak orang yang menyerah.",
            "Waktunya tunjukkan apa yang peretas dari Edinburgh bisa lakukan."
        ]
    },
    
    "haikaru": {
        "title": "HAIKARU FUMIKA - Ahli Strategi dari Kyoto",
        "content": [
            "Namamu: Haikaru Fumika",
            "Umur: 12 tahun",
            "Asal: Kyoto, Jepang",
            "",
            "Juara olimpiade matematika nasional",
            "IQ 162. Photographic memory",
            "Catur: sudah 1400+ Elo meski baru 12 tahun",
            "",
            "Kamu lihat pola di mana-mana",
            "Menghitung probabilitas dalam hitungan detik",
            "Selalu 10 langkah di depan siapa pun",
            "",
            "Mereka menculikmu karena kamu menyaksikan",
            "Transaksi mencurigakan di airport Kansai",
            "Jaringan Epstein. Pejabat tinggi",
            "Wajahmu terekam CCTV mereka",
            "",
            "Tapi kamu sempat rekam balik",
            "Photographic memory-mu sudah simpan segalanya",
            "Setiap wajah. Setiap detail",
            "",
            "Sekarang di pulau terkutuk ini",
            "Tapi kamu tidak panik",
            "Seorang Fumika tidak pernah panik",
            "",
            "Kamu observe. Analyze. Plan",
            "",
            "2 minggu penuh pengamatan",
            "Buku catatan penuh data",
            "17 posisi guard. 8 blind spot. 3 jalur keluar",
            "",
            "Ini bukan penjara",
            "Ini adalah teka-teki paling kompleks yang pernah ada",
            "",
            "Dan kamu tidak pernah kalah dalam teka-teki"
        ]
    },
    
    "aolinh": {
        "title": "AO LIN - Melodi dari Chengdu",
        "content": [
            "Namamu: Ao Lin (敖琳)",
            "Umur: 10 tahun",
            "Asal: Chengdu, Sichuan, China",
            "",
            "Belajar biola sejak usia 4 tahun",
            "Di bawah tangan Jiejie — kakak perempuanmu",
            "Dua jiwa, satu melodi",
            "",
            "Turnamen musik internasional di Hongkong",
            "Kalian berdua berangkat bersama",
            "Tidak pernah pulang",
            "",
            "Mereka menculik kalian berdua",
            "Memisahkan kalian",
            "",
            "Jiejie di suatu tempat di pulau ini",
            "Sendirian. Ketakutan. Menunggu",
            "",
            "音乐给我力量",
            "Musik memberimu kekuatan",
            "",
            "Ibu selalu berkata:",
            "'Ao Lin, selama kamu bisa memainkan satu nada,'",
            "'dunia tidak sepenuhnya gelap.'",
            "",
            "Biola masih di tanganmu",
            "Earphone biru masih di lehermu",
            "Jiejie masih menunggumu",
            "",
            "我们一起 — kita bersama",
            "Mainkan simfonimu",
            "Dan bawa Jiejie pulang"
        ]
    },
    
    "arganta": {
        "title": "AMERIGO ARGANTA - Il Navigatore di Napoli",
        "content": [
            "Namamu: Amerigo Arganta",
            "Umur: 13 tahun",
            "Asal: Napoli, Italia",
            "",
            "Keluargamu adalah pelaut Napoli",
            "Turun-temurun mengarungi Mediterania",
            "Nonno-mu navigator legendaris yang pernah berlayar",
            "dari Napoli hingga Alexandria dan kembali tanpa peta",
            "",
            "Il compasso di Nonno",
            "Tembaga tua. Ukiran tangan",
            "Bertuliskan: 'La via è sempre avanti'",
            "'Jalan selalu ada di depan, Amerigo'",
            "",
            "Sejak kecil, Nonno bercerita.",
            "Tentang kota-kota besar Italia yang penuh sejarah.",
            "Tentang Firenze yang megah di bawah Medici.",
            "Tentang bayang-bayang para pembela keadilan yang menjaga keseimbangan dunia.",
            "",
            "'Ada seorang pemuda dari Firenze,' kata Nonno suatu malam",
            "di atas geladak kapal yang bergoyang pelan.",
            "'Ayahnya digantung. Saudara-saudaranya dieksekusi'",
            "'Hidupnya dirampas oleh orang-orang berkuasa yang korup'",
            "'Tapi dia tidak hancur. Dia tidak melarikan diri ke sudut gelap'",
            "",
            "'Dia bangkit. Dia belajar bergerak dari bayang-bayang'",
            "'Dia bergerak seperti angin di atap-atap kota tua'",
            "'Dan dia temukan siapa yang benar-benar bersalah'",
            "'Tidak hanya algojo — tapi dalangnya'",
            "",
            "Kamu dengarkan cerita itu ratusan kali",
            "Di Napoli, di lautan, di bawah bintang Mediterania",
            "Dan setiap kali, satu kalimat selalu bergema:",
            "",
            "'Keadilan tidak mengenal batas, Amerigo'",
            "'Yang membedakan pejuang dengan penjahat'",
            "'Adalah tujuan yang mereka pilih'",
            "",
            "Kamu bukan Assassino",
            "Kamu hanya anak pelaut dari Napoli",
            "Tapi darah Italia mengalir di nadimu",
            "Dan dendam yang sah membakar dadamu",
            "",
            "Keluargamu berlayar ke Karibia",
            "'Rescue operation' katanya",
            "Semuanya kebohongan. Perangkap",
            "",
            "Kapal keluargamu dihancurkan",
            "Orang-orang Epstein, atas perintah Maxwell",
            "Papà. Mamma. Nonno. Semua hilang di laut Karibia",
            "Hanya kamu yang terdampar di pulau ini",
            "",
            "Dan dalam diam di pantai itu,",
            "Kamu teringat Nonno dan kisah Ezio-nya:",
            "'Requiescat in pace bukan berarti menyerah'",
            "'Tapi memberi penghormatan pada yang gugur'",
            "'Sambil kamu sendiri terus berjalan maju'",
            "",
            "Il compasso masih di sakumu",
            "Pisau lipat masih di pinggang",
            "Gang-gang Napoli yang kamu lari-lari kecil sejak umur 6 tahun",
            "Mengajarimu cara bergerak di tempat sempit, cara menghilang, cara muncul lagi",
            "",
            "Sang pemuda Firenze itu memanjat menara katedral kota lamanya",
            "Kamu memanjat karang tepi pantai pulau terkutuk ini",
            "Tidak ada bedanya — tekad mereka yang tidak bisa dihentikan",
            "",
            "La via è sempre avanti",
            "",
            "Per Nonno. Per Papà. Per Mamma.",
            "Per ogni vita che hanno preso",
            "Untuk setiap nyawa yang mereka renggut"
        ]
    },
    
    "ignatius": {
        "title": "IGNATIUS FORGERS — Insinyur Jenius dari Garasi Papà",
        "content": [
            "Namamu: Ignatius Forgers",
            "Umur: 12 tahun",
            "Asal: Bristol, Inggris",
            "",
            "Juara lomba sains tiga tahun berturut-turut.",
            "Penerima beasiswa teknik.",
            "Membangun robot pertamamu di usia sepuluh tahun",
            "dari suku cadang yang kamu pungut di pasar loak.",
            "",
            "Papà seorang montir. Mama seorang guru matematika.",
            "Mereka tidak kaya — tapi mereka paham",
            "bahwa otak yang baik lebih berharga dari harta manapun.",
            "",
            "Di garasi Papà itulah semuanya dimulai.",
            "Kabel, besi tua, komponen bekas.",
            "Tapi di tangan Ignatius, semuanya bisa menjadi sesuatu.",
            "",
            "Suatu hari kamu menciptakan sesuatu yang terlalu bagus.",
            "Generator pulsa elektromagnetik mini.",
            "Yang seharusnya untuk proyek lomba sains.",
            "Tapi mereka mau menggunakannya sebagai senjata.",
            "",
            "Kamu menolak.",
            "Jadi mereka mengambilmu sebagai gantinya.",
            "",
            "Sekarang terjebak di pulau ini.",
            "Tapi mereka membuat kesalahan besar.",
            "",
            "Mereka menaruhmu di ruang basement.",
            "Tepat di sebelah seluruh infrastruktur listrik pulau.",
            "Generator. Jaringan daya. Semua sistem keamanan.",
            "",
            "Ini bukan penjara.",
            "Ini bengkel kerja.",
            "",
            "Dan dengan cukup kabel dan waktu,",
            "Ignatius Forgers bisa membangun apa saja.",
            "",
            "Termasuk kebebasannya sendiri."
        ]
    }
}

def print_story_slow(text, delay=None):
    # Use dialog_speed from SETTINGS if available, otherwise use provided delay or default
    if delay is None:
        try:
            from .settings import SETTINGS
            delay = SETTINGS.get('dialog_speed', 0.03)
        except (ImportError, AttributeError):
            delay = 0.03
    
    print_slow(text, delay=delay, allow_skip=True)

def display_chapter(chapter_id, skip_delays=False, game_state=None):
    # Menampilkan chapter cerita dengan interpolasi nama pemain
    """Args:"""
    if chapter_id not in STORY_CHAPTERS:
        return False

    chapter = STORY_CHAPTERS[chapter_id]

    print(f"\n{Warna.CYAN}{'═' * (_tw() - 1)}{Warna.RESET}")
    print(f"{Warna.KUNING + Warna.TERANG}{chapter['title'].center(_tw())}{Warna.RESET}")
    print(f"{Warna.CYAN}{'═' * (_tw() - 1)}{Warna.RESET}\n")

    for line in chapter['content']:
        # Interpolate player info before displaying
        display_line = _interpolate_player_info(line, game_state)
        
        if display_line:
            if skip_delays:
                print(f"  {display_line}")
            else:
                print_story_slow(f"  {display_line}")
        else:
            print()

    return True

def display_backstory(character_id, skip_delays=False):
    # Menampilkan backstory karakter yang dipilih
    """Display character backstory"""
    if character_id not in CHARACTER_BACKSTORIES:
        return False

    backstory = CHARACTER_BACKSTORIES[character_id]

    print(f"\n{Warna.CYAN}{'═' * (_tw() - 1)}{Warna.RESET}")
    print(f"{Warna.KUNING + Warna.TERANG}{backstory['title'].center(_tw())}{Warna.RESET}")
    print(f"{Warna.CYAN}{'═' * (_tw() - 1)}{Warna.RESET}\n")

    for line in backstory['content']:
        if line:
            if skip_delays:
                print(f"  {line}")
            else:
                print_story_slow(f"  {line}")
        else:
            print()
    return True

def display_route_chapter(chapter_id, skip_delays=False):
    """Display a route-specific chapter"""
    if chapter_id not in STORY_CHAPTERS:
        return False

    chapter = STORY_CHAPTERS[chapter_id]
    chapter_type = chapter.get('type', '')

    if chapter_type in ('route_chapter', 'route_ending'):
        border_color = Warna.UNGU
        title_color = Warna.CYAN + Warna.TERANG
    else:
        border_color = Warna.CYAN
        title_color = Warna.KUNING + Warna.TERANG

    print(f"\n{border_color}{'═' * (_tw() - 1)}{Warna.RESET}")
    print(f"{title_color}{chapter['title'].center(_tw())}{Warna.RESET}")
    print(f"{border_color}{'═' * (_tw() - 1)}{Warna.RESET}\n")

    for line in chapter['content']:
        if line:
            if skip_delays:
                print(f"  {line}")
            else:
                print_story_slow(f"  {line}")
        else:
            print()
    return True

def play_route_story(char_id, gs=None, skip_delays=False):
    """Mainkan semua chapter untuk rute karakter tertentu"""
    route_map = {
        'vio':      ['vio_route_1', 'vio_route_2', 'vio_route_3', 'vio_route_4', 'vio_route_5'],
        'haikaru':  ['haikaru_route_1', 'haikaru_route_2', 'haikaru_route_3', 'haikaru_route_4', 'haikaru_route_5'],
        'aolinh':   ['aolinh_route_1', 'aolinh_route_2', 'aolinh_route_3', 'aolinh_route_4', 'aolinh_route_5'],
        'arganta':  ['arganta_route_1', 'arganta_route_2', 'arganta_route_3', 'arganta_route_4', 'arganta_route_5'],
        'ignatius': ['ignatius_route_1', 'ignatius_route_2', 'ignatius_route_3', 'ignatius_route_4', 'ignatius_route_5'],
    }

    chapters = route_map.get(char_id, [])
    for ch_id in chapters:
        display_route_chapter(ch_id, skip_delays=skip_delays)
        if not skip_delays:
            with suppress(Exception):
                input(f"\n{Warna.ABU_GELAP}[ENTER untuk lanjut]{Warna.RESET} ")

def play_route_ending(char_id, skip_delays=False):
    """Mainkan ending khusus untuk karakter yang dipilih"""
    ending_map = {
        'vio':      'ending_vio',
        'haikaru':  'ending_haikaru',
        'aolinh':   'ending_aolinh',
        'arganta':  'ending_arganta',
        'ignatius': 'ending_ignatius',
    }

    ending_id = ending_map.get(char_id, 'epilogue_good')
    display_route_chapter(ending_id, skip_delays=skip_delays)

def get_route_chapter_at(char_id, chapter_index):
    """Ambil satu chapter rute berdasarkan index"""
    route_map = {
        'vio':      ['vio_route_1', 'vio_route_2', 'vio_route_3', 'vio_route_4', 'vio_route_5'],
        'haikaru':  ['haikaru_route_1', 'haikaru_route_2', 'haikaru_route_3', 'haikaru_route_4', 'haikaru_route_5'],
        'aolinh':   ['aolinh_route_1', 'aolinh_route_2', 'aolinh_route_3', 'aolinh_route_4', 'aolinh_route_5'],
        'arganta':  ['arganta_route_1', 'arganta_route_2', 'arganta_route_3', 'arganta_route_4', 'arganta_route_5'],
        'ignatius': ['ignatius_route_1', 'ignatius_route_2', 'ignatius_route_3', 'ignatius_route_4', 'ignatius_route_5'],
    }

    chapters = route_map.get(char_id, [])
    return chapters[chapter_index] if 0 <= chapter_index < len(chapters) else None

def get_prologue_chapters():
    """Get list of prologue chapters"""
    return ["prologue_1", "prologue_2", "prologue_3", "prologue_4"]

def get_chapter_1():
    return ["chapter_1_intro", "chapter_1_meet", "chapter_1_crisis"]

def get_chapter_2():
    return ["chapter_2_intro", "chapter_2_growing", "chapter_2_trust"]

def get_chapter_3():
    return ["chapter_3_intro", "chapter_3_revelation", "chapter_3_decision"]

def get_chapter_final():
    return ["chapter_final_intro", "chapter_final_confrontation"]

def get_all_chapters():
    return list(STORY_CHAPTERS.keys())

def get_route_chapters(char_id):
    """Get list of chapter IDs for a specific character route"""
    route_map = {
        'vio':      ['vio_route_1', 'vio_route_2', 'vio_route_3', 'vio_route_4', 'vio_route_5'],
        'haikaru':  ['haikaru_route_1', 'haikaru_route_2', 'haikaru_route_3', 'haikaru_route_4', 'haikaru_route_5'],
        'aolinh':   ['aolinh_route_1', 'aolinh_route_2', 'aolinh_route_3', 'aolinh_route_4', 'aolinh_route_5'],
        'arganta':  ['arganta_route_1', 'arganta_route_2', 'arganta_route_3', 'arganta_route_4', 'arganta_route_5'],
        'ignatius': ['ignatius_route_1', 'ignatius_route_2', 'ignatius_route_3', 'ignatius_route_4', 'ignatius_route_5'],
    }
    return route_map.get(char_id, [])
