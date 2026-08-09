from .sprites import Warna
import random
import json
import os
from contextlib import suppress
from .constants import FALLBACK_CARD_DIALOGS

def _load_card_dialogs():
    """Muat CARD_PLAY_DIALOGS dari card_dialogs.json dengan validasi ketat."""

    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _candidates = [
        os.path.join(_this_dir, "data", "card_dialogs.json"),
        os.path.join(_this_dir, "card_dialogs.json"),
        os.path.join(os.getcwd(), "card_dialogs.json"),
    ]

    for _path in _candidates:
        if os.path.exists(_path):
            try:
                with open(_path, "r", encoding="utf-8") as _f:
                    _raw = json.load(_f)

                # Validate structure: should be dict with character -> hand_type -> dialogs array
                if not isinstance(_raw, dict):
                    raise TypeError(f"card_dialogs.json harus dict, bukan {type(_raw).__name__}")
                
                # Validate that we have character entries with dialog arrays
                _valid_dialogs = {}
                for char_id, hand_dialogs in _raw.items():
                    if not char_id.startswith("_") and isinstance(hand_dialogs, dict):
                        # This is a valid character entry
                        _valid_dialogs[char_id] = hand_dialogs

                if _valid_dialogs:
                    return _valid_dialogs
                # If no valid dialogs found, fall through to fallback
                print(f"⚠️  WARNING: card_dialogs.json tidak memiliki dialog valid di {_path}")
                break
                
            except json.JSONDecodeError as _e:
                print(f"⚠️  WARNING: card_dialogs.json memiliki JSON syntax error: {_e}")
                print(f"           Gunakan fallback dialogs untuk mencegah NPC bisu.")
                break
            except (OSError, TypeError, ValueError) as _e:
                print(f"⚠️  WARNING: card_dialogs.json error ({type(_e).__name__}): {_e}")
                break

    # Fallback ke FALLBACK_CARD_DIALOGS jika terjadi masalah
    print("   Menggunakan fallback dialogs.")
    return FALLBACK_CARD_DIALOGS.copy()

CARD_PLAY_DIALOGS = _load_card_dialogs()

PLAYABLE_CHARACTERS = {
    "vio": {
        "name": "Vio",
        "title": "Gacha Whale & Crypto Expert",
        "age": 13,
        "gender": "Male",
        "desc": "Whaler game mobile gacha dan ahli enkripsi sistem",
        "sprite": ("♂♂", Warna.MERAH + Warna.TERANG, ""),
        "stats": {
            "hp": 88,
            "attack": 16,
            "defense": 11,
            "speed": 21
        },
        "skills": {
            "exploit_code": {
                "name": "Exploit Code",
                "type": "debuff",
                "power": 35,
                "cost": 5,
                "energy_cost": 5,
                "cooldown": 4,
                "duration_turns": 3,
                "desc": "Eksploitasi kelemahan: 35 DMG langsung + DEF musuh -60% selama 3 turn | EN:5 CD:4t",
                "effect": "debuff_defense",
                "target": "enemy",
                "level_bonus": 5
            },
            "zero_day_strike": {
                "name": "Zero-Day Strike",
                "type": "special",
                "power": 50,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 5,
                "duration_turns": 1,
                "desc": "Critical exploit ditemukan: 50 DMG + STUN musuh 1 turn | EN:6 CD:5t",
                "effect": "stun_enemy",
                "target": "enemy",
                "level_bonus": 0
            },
            "ssr_pity_break": {
                "name": "SSR Pity Break",
                "type": "buff",
                "power": 0,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 6,
                "duration_turns": 2,
                "desc": "Guaranteed SSR pull! ATK +25% + DEF +25% selama 2 turn | EN:6 CD:6t",
                "effect": "buff_atk_def",
                "target": "self",
                "level_bonus": 5
            },
            "data_bomb": {
                "name": "Data Bomb",
                "type": "special",
                "power": 0,
                "cost": 8,
                "energy_cost": 8,
                "cooldown": 6,
                "duration_turns": 1,
                "desc": "Injeksi virus: kartu berikutnya ×1.75 DAMAGE (korbankan 10 HP sebagai biaya) | EN:8 CD:6t",
                "effect": "buff_overload",
                "target": "self",
                "level_bonus": 0
            }
        },
        "backstory": "Jenius coding dari Edinburgh, Skotlandia. Sejak usia 10 tahun sudah memenangkan berbagai kompetisi pemrograman tingkat UK. Diculik setelah secara tidak sengaja membobol jaringan keuangan Epstein saat mengikuti CTF challenge online. Meski terjebak, tetap menyembunyikan HP gaming di balik lapisan seragam penjara untuk 'daily login' gacha.",
        "passive": "Gacha Luck: 25% chance untuk double damage atau heal berkat RNG god",
        "starting_location": "mansion",
        "nationality": "Scottish",
        "hometown": "Edinburgh, Skotlandia",
        "personality": "Tenang, analitis, sedikit addict gacha, sarkastik, bangga pada asal Skotlandia",
        "hobby": "Main gacha game, collect SSR characters, CTF hacking competition, flexing pull",
        "favorite_quote": "Pity system is for casuals. True whale goes all-in!",

        "card_dialogs": CARD_PLAY_DIALOGS.get("vio", {})
    },
    
    "haikaru": {
        "name": "Haikaru Fumika",
        "title": "Strategic Observer",
        "age": 12,
        "gender": "Female",
        "desc": "Pengamat tajam dari Kyoto dengan photographic memory dan analisis sempurna",
        "sprite": ("♀♀", Warna.CYAN + Warna.TERANG, ""),
        "stats": {
            "hp": 92,
            "attack": 13,
            "defense": 16,
            "speed": 19
        },
        "skills": {
            "pattern_analysis": {
                "name": "Pattern Analysis",
                "type": "debuff",
                "power": 0,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 5,
                "duration_turns": 2,
                "desc": "Analisis kelemahan musuh: DEF -35% + ATK -20% selama 2 turn | CD: 5 turn",
                "effect": "debuff_def_atk",
                "target": "enemy",
                "level_bonus": 5
            },
            "focus_mind": {
                "name": "Focus Mind",
                "type": "buff",
                "power": 0,
                "cost": 5,
                "energy_cost": 5,
                "cooldown": 6,
                "duration_turns": 2,
                "desc": "Konsentrasi penuh: ATK diri sendiri +25% selama 2 turn | EN:5 CD:6t",
                "effect": "buff_attack",
                "target": "self",
                "level_bonus": 5
            },
            "gambit": {
                "name": "Strategic Gambit",
                "type": "special",
                "power": 0,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 6,
                "duration_turns": 2,
                "desc": "Korbankan 25 HP → ATK +25% selama 2 turn + +20 Energy | EN:6 CD:6t",
                "effect": "power_up",
                "target": "self",
                "level_bonus": 5
            },
            "four_card_read": {
                "name": "Four-Card Read",
                "type": "special",
                "power": 0,
                "cost": 3,
                "energy_cost": 3,
                "cooldown": 5,
                "duration_turns": 1,
                "desc": "Analisis pola: hand berikutnya bisa Straight dengan 4 kartu saja | EN:3 CD:5t",
                "effect": "buff_four_straight",
                "target": "self",
                "level_bonus": 5
            }
        },
        "backstory": "Putri sulung keluarga akademisi dari Kyoto, Jepang. Fumika adalah juara olimpiade matematika tingkat nasional di usia 11 tahun dengan IQ 162 dan photographic memory yang tidak pernah gagal. Diculik ketika secara tidak sengaja menyaksikan transaksi mencurigakan antara anggota jaringan Epstein dan seorang pejabat tinggi di airport Kansai. Selama 2 minggu di pulau, tidak panik — justru mengisi buku catatannya dengan pola penjaga, blind spot CCTV, dan tiga rencana pelarian berlapis.",
        "passive": "Keen Eye: Selalu tahu hand musuh & +20% crit chance",
        "starting_location": "island",
        "nationality": "Japanese",
        "hometown": "Kyoto, Jepang",
        "personality": "Serius, perfeksionis, dingin tapi protektif, sedikit tsundere pada yang dianggap 'kurang efisien'",
        "hobby": "Catur, mencatat pola, membuat strategi berlapis, puzzle logika, origami sebagai meditasi",
        "favorite_quote": "Semua sistem punya celah. Saya hanya perlu 2.7 detik untuk menemukannya.",
        "card_dialogs": CARD_PLAY_DIALOGS.get("haikaru", {})
    },
    
    "aolinh": {
        "name": "Ao Lin",
        "title": "Cheerful Healer & Music Lover",
        "age": 10,
        "gender": "Female",
        "desc": "Gadis ceria dari Chengdu yang musiknya bisa menyembuhkan jiwa",
        "sprite": ("♀♀", Warna.UNGU + Warna.TERANG, ""),
        "stats": {
            "hp": 88,
            "attack": 11,
            "defense": 13,
            "speed": 17
        },
        "skills": {
            "healing_melody": {
                "name": "Healing Melody",
                "type": "heal",
                "power": 55,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 5,
                "desc": "Melodi penyembuh: pulihkan 55-75 HP diri sendiri | EN:6 CD:5t",
                "effect": "heal_self",
                "target": "self",
                "level_bonus": 10
            },
            "harmonic_shield": {
                "name": "Harmonic Shield",
                "type": "buff",
                "power": 0,
                "cost": 4,
                "energy_cost": 4,
                "cooldown": 5,
                "duration_turns": 3,
                "desc": "Perisai harmoni: DEF diri sendiri +50% selama 3 turn | EN:4 CD:5t",
                "effect": "buff_defense",
                "target": "self",
                "level_bonus": 5
            },
            "rhythm_boost": {
                "name": "Rhythm Boost",
                "type": "buff",
                "power": 0,
                "cost": 5,
                "energy_cost": 5,
                "cooldown": 6,
                "duration_turns": 2,
                "desc": "Irama semangat: ATK +20% selama 2 turn + pulihkan 15 HP | EN:5 CD:6t",
                "effect": "buff_atk_heal",
                "target": "self",
                "level_bonus": 5
            },
            "discard_rhythm": {
                "name": "Discard Rhythm",
                "type": "special",
                "power": 0,
                "cost": 3,
                "energy_cost": 3,
                "cooldown": 5,
                "desc": "Irama baru: pulihkan 1 slot discard + langsung draw 2 kartu tambahan | CD: 5 turn",
                "effect": "refresh_discard",
                "target": "self",
                "level_bonus": 0
            }
        },
        "backstory": "Gadis berhati besar dari Chengdu, Sichuan, China. Belajar biola sejak usia 4 tahun di bawah bimbingan Jiejie (kakak perempuannya) yang juga seorang pemain biola berbakat. Keduanya diculik saat mengikuti turnamen musik internasional di Hongkong. Meski ketakutan, Ao Lin tetap memegang biola dan earphone birunya sebagai penghubung keberanian — karena musik ibunya selalu bilang adalah jembatan antara hati yang hancur dan dunia yang lebih baik.",
        "passive": "Musical Spirit: Heal +25% effectiveness & party morale boost (+10% all stats)",
        "starting_location": "prison_south",
        "nationality": "Chinese",
        "hometown": "Chengdu, Sichuan, China",
        "personality": "Ceria, optimis, penyayang, pemberani saat terdesak, sesekali bicara Mandarin saat emosional",
        "hobby": "Biola, mendengarkan musik erhu & pop Cina, memasak masakan Sichuan, membuat playlist, dance",
        "favorite_quote": "音乐能让世界变得更美好！ Musik bisa membuat dunia lebih indah!",
        "favorite_music": "Erhu klassik, C-Pop, Anime OST, EDM",
        "card_dialogs": CARD_PLAY_DIALOGS.get("aolinh", {})
    },
    
    "arganta": {
        "name": "Amerigo Arganta",
        "title": "Pathfinder Scout",
        "age": 13,
        "gender": "Male",
        "desc": "Navigator Italia dan scout dengan insting survival tajam",
        "sprite": ("♂♂", Warna.PUTIH + Warna.TERANG, ""),
        "stats": {
            "hp": 87,
            "attack": 19,
            "defense": 11,
            "speed": 24
        },
        "skills": {
            "shadow_step": {
                "name": "Shadow Step",
                "type": "buff",
                "power": 0,
                "cost": 3,
                "energy_cost": 3,
                "cooldown": 5,
                "duration_turns": 1,
                "desc": "Satu langkah ke bayangan: 70% dodge serangan musuh giliran ini | CD: 5 turn",
                "effect": "buff_evade",
                "target": "self",
                "level_bonus": 5
            },
            "survival_instinct": {
                "name": "Survival Instinct",
                "type": "heal",
                "power": 30,
                "cost": 3,
                "energy_cost": 3,
                "cooldown": 5,
                "desc": "Insting bertahan: pulihkan 30 HP + regen 20 Energy | EN:3 CD:5t",
                "effect": "heal_energy",
                "target": "self",
                "level_bonus": 5
            },
            "scout_mark": {
                "name": "Scout Mark",
                "type": "debuff",
                "power": 0,
                "cost": 4,
                "energy_cost": 4,
                "cooldown": 5,
                "duration_turns": 3,
                "desc": "Tandai target: ATK musuh -45% selama 3 turn | EN:4 CD:5t",
                "effect": "debuff_attack",
                "target": "enemy",
                "level_bonus": 5
            },
            "ambush_strike": {
                "name": "Ambush Strike",
                "type": "special",
                "power": 0,
                "cost": 7,
                "energy_cost": 7,
                "cooldown": 6,
                "duration_turns": 1,
                "desc": "Keluar dari bayangan: kartu berikutnya ×1.5 damage + STUN musuh 1 turn! | CD: 6 turn",
                "effect": "buff_ambush",
                "target": "self",
                "level_bonus": 0
            }
        },
        "backstory": "Putra keluarga pelaut dari Napoli, Italia. Kakeknya adalah navigator legendaris di Laut Mediterania yang mewariskan kompas antik bertuliskan 'La via è sempre avanti'. Keluarganya berlayar ke Karibia untuk lomba layar internasional ketika perahu mereka dihancurkan oleh anak buah Epstein yang menyamar sebagai tim penyelamat. Tumbuh dengan kisah-kisah leluhur Italia — termasuk legenda Assassini kuno yang katanya pernah beroperasi dari Napoli hingga Firenze — Amerigo percaya bahwa kebenaran selalu bisa ditemukan di balik kepalsuan, dan keadilan harus diperjuangkan sendiri jika sistem gagal.",
        "passive": "Scout's Instinct: First strike dalam combat & +25% evasion",
        "starting_location": "island",
        "nationality": "Italian",
        "hometown": "Napoli, Italia",
        "personality": "Mandiri, resourceful, penuh dendam yang terkendali, bangga akan warisan Italia, sesekali berbisik kata-kata Assassini kuno sebagai mantra",
        "hobby": "Navigasi bintang, peta tangan, parkour di gang-gang Napoli, membaca sejarah assassini Italia, mempertajam pisau lipat",
        "favorite_quote": "Niente è reale, tutto è lecito. La via è sempre avanti.",
        "card_dialogs": CARD_PLAY_DIALOGS.get("arganta", {})
    },
    
    "ignatius": {
        "name": "Ignatius",
        "title": "Engineer Prodigy",
        "age": 12,
        "gender": "Male",
        "desc": "Teknisi jenius dengan gadget DIY yang powerful",
        "sprite": ("♂♂", Warna.KUNING + Warna.TERANG, ""),
        "stats": {
            "hp": 85,
            "attack": 22,
            "defense": 9,
            "speed": 16
        },
        "skills": {
            "emp_stun": {
                "name": "EMP Stun",
                "type": "special",
                "power": 0,
                "cost": 3,
                "energy_cost": 3,
                "cooldown": 5,
                "duration_turns": 1,
                "desc": "Pulse elektromagnetik: musuh di-stun, skip serangan 1 turn | CD: 5 turn",
                "effect": "stun_enemy",
                "target": "enemy",
                "level_bonus": 0
            },
            "overclock": {
                "name": "Overclock",
                "type": "buff",
                "power": 0,
                "cost": 7,
                "energy_cost": 7,
                "cooldown": 6,
                "duration_turns": 2,
                "desc": "Overclocking sistem: ATK diri sendiri +30% selama 2 turn + regen 8 Energy | CD: 6 turn",
                "effect": "buff_atk_energy",
                "target": "self",
                "level_bonus": 5
            },
            "emergency_repair": {
                "name": "Emergency Repair",
                "type": "heal",
                "power": 40,
                "cost": 5,
                "energy_cost": 5,
                "cooldown": 5,
                "desc": "Perbaikan darurat: pulihkan 40 HP + bersihkan semua debuff | EN:5 CD:5t",
                "effect": "heal_cleanse",
                "target": "self",
                "level_bonus": 8
            },
            "power_surge": {
                "name": "Power Surge",
                "type": "special",
                "power": 0,
                "cost": 6,
                "energy_cost": 6,
                "cooldown": 6,
                "duration_turns": 1,
                "desc": "Korbankan 15 HP → kartu berikutnya ×1.6 DAMAGE! (Overload circuit) | CD: 6 turn",
                "effect": "buff_overload",
                "target": "self",
                "level_bonus": 0
            }
        },
        "backstory": "Anak yang bisa memperbaiki dan memodifikasi segala macam mesin sejak umur 8 tahun. Panel listrik dan circuit board adalah mainannya.",
        "passive": "Tech Genius: Skill damage +30% & bisa craft item dari junk",
        "starting_location": "mansion",
        "personality": "Energik, curious, suka eksperimen, kadang ceroboh",
        "hobby": "Modding gadget, robotics, gaming hardware",
        "favorite_quote": "If it runs on electricity, I can hack it or break it!",
        "card_dialogs": CARD_PLAY_DIALOGS.get("ignatius", {})
    }
}

# LEVEL-UP STAT GAINS PER KARAKTER
# Setiap karakter punya distribusi stat unik → level-up gains mencerminkan itu.
#
# Referensi base stats:
#   Vio     : HP 88  ATK 16  DEF 11  SPD 21  → ATK/SPD build
#   Haikaru : HP 92  ATK 13  DEF 16  SPD 19  → DEF/HP build
#   Aolinh  : HP 88  ATK 11  DEF 13  SPD 17  → Support/Energy build
#   Arganta : HP 87  ATK 19  DEF 11  SPD 24  → ATK/SPD glass cannon
#   Ignatius: HP 85  ATK 22  DEF  9  SPD 16  → Pure ATK berserker
# Level-up stat gains per karakter
CHARACTER_LEVEL_GAINS = {
    "vio": {
        # Hacker: cepat & menyerang, tapi tipis
        "hp":      10,  # squishy — HP tumbuh pelan
        "attack":   1,  # dikurangi dari 2 — lebih terkontrol
        "defense":  1,  # pertahanan rendah tetap rendah
        "speed":    2,  # SPD signature — naik cepat
        "energy":   1,
        "note": "ATK/SPD scaling — tetap cepat tapi rapuh",
    },
    "haikaru": {
        # Strategist: tanky, analitis, low attack
        "hp":      14,  # paling tinggi — HP-nya tebal
        "attack":   1,  # ATK rendah tetap rendah
        "defense":  3,  # DEF signature — paling tinggi
        "speed":    1,  # SPD biasa
        "energy":   2,
        "note": "DEF/HP scaling — tank sejati yang tidak mati",
    },
    "aolinh": {
        # Healer: support, energy regen, balanced growth
        "hp":      12,  # sedang
        "attack":   1,  # lemah — fokus heal bukan damage
        "defense":  2,  # sedang
        "speed":    1,  # sedang
        "energy":   2,  # healer energy gain
        "note": "Energy scaling — skill heal makin kuat tiap level",
    },
    "arganta": {
        # Scout: extreme speed & attack, paper-thin defense
        "hp":       9,  # paling kecil — glass cannon murni
        "attack":   2,  # dikurangi dari 3 — masih kuat tapi tidak breakingly fast
        "defense":  1,  # DEF tetap rendah
        "speed":    3,  # SPD tertinggi — la via è sempre avanti
        "energy":   2,
        "note": "ATK/SPD glass cannon — hit hard, move fast, die easy",
    },
    "ignatius": {
        # Engineer: berserker ATK, sangat rapuh
        "hp":       8,  # paling rendah — rapuh banget
        "attack":   2,  # dikurangi dari 4 — masih tertinggi tapi bukan satu-tembak
        "defense":  1,  # hampir tidak ada defense growth
        "speed":    1,  # SPD biasa
        "energy":   2,  # energy untuk skill gadget
        "note": "Pure ATK scaling — high damage dengan HP tipis",
    },
}

# NPC spesial (Candala)
SPECIAL_NPC = {
    "candala": {
        "name": "Candala",
        "title": "The Wish Granter",
        "age": "???",
        "gender": "Female",
        "desc": "Wanita misterius yang pernah bisa mengabulkan semua permintaan",
        "sprite": ("♀♀", Warna.PUTIH + Warna.TERANG + Warna.DIM, ""),
        "backstory": "Seorang wanita yang dulunya memiliki kutukan sekaligus karunia untuk mengabulkan setiap permintaan yang diucapkan di hadapannya.",
        "dialog": [
            "Candala: ...Anak-anak yang terjebak di pulau terkutuk ini...",
            "Candala: Aku pernah seperti kalian. Terikat oleh takdir yang tidak bisa kulawan.",
            "Candala: Tapi kalian... kalian punya yang tidak pernah kumiliki.",
            "Candala: Kalian punya satu sama lain. Jangan sia-siakan itu.",
            "Candala: *menghilang perlahan seperti kabut* ...Semoga kalian menemukan kebebasan yang kuimpikan..."
        ],
        "encounter_chance": 0.03,
        "location": "special_hidden",
        "can_join": False
    }
}

# QUEST UTAMA PER KARAKTER
# Tiap chapter punya boss unik sesuai karakter.
# Boss ch.3 terakhir selalu Epstein (final boss).
# Quest utama per karakter per chapter
CHARACTER_MAIN_QUESTS = {
    "vio": {
        1: {
            "id":     "vio_ch1_main",
            "title":  "Hack & Escape: Bobol Sistem Mansion",
            "objective": "Curi Keycard dari loker mansion, hack 2 terminal server, dan kalahkan Maxwell's Agent",
            "boss_id":   "maxwell_agent",
            "boss_name": "Maxwell's Agent",
            "steps": [
                "Temukan Keycard Level 1 di loker mansion (cari ★ di peta)",
                "Gunakan Keycard untuk hack 2 terminal server di dalam mansion",
                "Kalahkan Maxwell's Agent — agen yang menjaga server room mansion (Boss Ch.1)",
            ],
            "completion_flag": "ch1_vio_complete",
            "next_chapter_msg": "Sistem mansion jebol! Data mulai terbuka. Pulau menantimu.",
        },
        2: {
            "id":     "vio_ch2_main",
            "title":  "Kuasai Jaringan Pulau — Kalahkan Network Overseer",
            "objective": "Infiltrasi Command Center, hack 2 node jaringan pulau, dan kalahkan Network Overseer",
            "boss_id":   "network_overseer",
            "boss_name": "Network Overseer (Pengawas Jaringan Pulau)",
            "steps": [
                "Pergi ke COMMAND CENTER (PUSAT KONTROL) — tersedia Ch.2+",
                "Hack 2 node jaringan di command center (terminal data seluruh pulau)",
                "Kalahkan Network Overseer — pengawas jaringan yang lindungi semua data pulau (Boss Ch.2)",
            ],
            "completion_flag": "boss_ch2_defeated",
            "next_chapter_msg": "Jaringan pulau jebol! Semua data mulai terbuka. Saatnya bangun aliansi!",
        },
        3: {
            "id":     "vio_ch3_main",
            "title":  "Bangun Jaringan Sekutu — Rekrut 2 NPC",
            "objective": "Bantu minimal 2 NPC selesaikan sidequestnya dan kumpulkan key item reward mereka",
            "steps": [
                "Cari NPC yang butuh bantuan: Haikaru (PRISON NORTH), Aolinh (TEATER), Arganta (PANTAI), Ignatius (BASEMENT)",
                "Selesaikan minimal 2 sidequest — tiap NPC punya tugas dan reward berbeda",
                "Kumpulkan key item reward dari NPC → jaringan aliansi aktif → Chapter 4 terbuka",
            ],
            "completion_flag": "ch3_sidequests_done",
            "next_chapter_msg": "Aliansi digital aktif. Saatnya infiltrasi laboratorium Maxwell.",
        },
        4: {
            "id":     "vio_ch4_main",
            "title":  "Infiltrasi Pusat Kendali — Singkirkan Ghislaine Maxwell",
            "objective": "Masuk Pusat Kontrol, gunakan akses hack, dan kalahkan Ghislaine Maxwell yang mengendalikan jaringan",
            "boss_id":   "ghislaine_maxwell",
            "boss_name":  "Ghislaine Maxwell",
            "steps": [
                "Pergi ke PUSAT KONTROL (COMMAND CENTER) — tersedia Ch.4+",
                "Gunakan akses jaringan yang didapat dari NPC untuk bypass sistem keamanan Ghislaine",
                "Kalahkan Ghislaine Maxwell — otak jaringan yang menyembunyikan semua bukti (Boss Ch.4)",
            ],
            "completion_flag": "boss_ch4_defeated",
            "next_chapter_msg": "Ghislaine dikalahkan! Little Black Book ada di tanganmu. Satu langkah lagi.",
        },
        5: {
            "id":     "vio_ch5_main",
            "title":  "Deadman Switch — Kumpulkan Semua Bukti Digital",
            "objective": "Selesaikan 4 sidequest NPC, bawa USB Security Drive ke Vio, terima USB Evidence Drive",
            "steps": [
                "Selesaikan minimal 4 dari 5 sidequest NPC yang tersedia di pulau",
                "Temukan USB Security Drive (drop dari scientist di LAB — Ch.4+)",
                "Bawa USB Security Drive ke Vio → terima USB Evidence Drive — WAJIB untuk ending Ch.6",
            ],
            "completion_flag": "ch5_evidence_done",
            "next_chapter_msg": "Deadman switch aktif. 47 GB bukti aman di cloud. Siap untuk final.",
        },
        6: {
            "id":     "vio_ch6_main",
            "title":  "Final Upload — Expose Jaringan Epstein ke Seluruh Dunia",
            "objective": "Pergi ke Mansion Timur, kalahkan Jeffrey Epstein, dan upload USB Evidence Drive ke dunia",
            "boss_id":   "epstein_boss",
            "boss_name": "Jeffrey Epstein",
            "steps": [
                "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau",
                "Konfrontasi Jeffrey Epstein — siapkan semua skill dan item (Final Boss Ch.6)",
                "Upload USB Evidence Drive segera setelah Epstein dikalahkan — expose jaringan kejahatan ke dunia",
            ],
            "completion_flag": "vio_ch6_complete",
        },
    },
    "haikaru": {
        1: {
            "id":     "haikaru_ch1_main",
            "title":  "Escape Analysis: Peta Buta Penjara Utara",
            "objective": "Amati 3 blind spot penjaga, raih Kunci Wing-C, dan kalahkan Warden Elite dengan strategi presisi",
            "boss_id":   "warden_elite",
            "boss_name": "Warden Elite",
            "steps": [
                "Observasi 3 lokasi blind spot patroli (ambil item intel/observasi di penjara)",
                "Temukan Kunci Wing-C di loker tersembunyi Wing-C (cari ★ di peta)",
                "Kalahkan Warden Elite — eksekusi saat posisi blind spot optimal (Boss Ch.1)",
            ],
            "completion_flag": "ch1_haikaru_complete",
            "next_chapter_msg": "Semua kalkulasi tepat. Penjara teratasi. Target: pulau.",
        },
        2: {
            "id":     "haikaru_ch2_main",
            "title":  "Eliminasi Kepala Penjaga — Kuasai Hierarki Penjara",
            "objective": "Petakan 2 posisi patroli baru, lalu kalahkan Kepala Penjaga yang mengendalikan seluruh penjara",
            "boss_id":   "kepala_penjaga",
            "boss_name": "Kepala Penjaga",
            "steps": [
                "Jelajahi area pulau dan ambil 2 item intel/peta — update kalkulasi rute (Ch.2+)",
                "Pergi ke PRISON NORTH — lokasi Kepala Penjaga, komandan tertinggi penjara pulau",
                "Kalahkan Kepala Penjaga — eksekusi tepat sesuai 100 langkah prediksi (Boss Ch.2)",
            ],
            "completion_flag": "boss_ch2_defeated",
            "next_chapter_msg": "Kepala Penjaga dinetralkan. Hierarki penjara runtuh. Saatnya bangun aliansi.",
        },
        3: {
            "id":     "haikaru_ch3_main",
            "title":  "Kalkulasi Aliansi — Rekrut 2 Sekutu Paling Efisien",
            "objective": "Analisis kebutuhan NPC, selesaikan 2 sidequest paling efisien, dan buka akses Chapter 4",
            "steps": [
                "Temui NPC di area pulau — evaluasi manfaat taktis tiap aliansi berdasarkan kebutuhan misi",
                "Selesaikan minimal 2 sidequest — kumpulkan key item yang paling relevan untuk kelanjutan misi",
                "Konfirmasi aliansi taktis terbentuk → Chapter 4 terbuka",
            ],
            "completion_flag": "ch3_sidequests_done",
            "next_chapter_msg": "Aliansi terkonfirmasi. Saatnya checkmate Maxwell's Agent.",
        },
        4: {
            "id":     "haikaru_ch4_main",
            "title":  "Checkmate Ghislaine — Eksekusi Skenario 61 Langkah",
            "objective": "Masuk Pusat Kontrol, analisis semua data intel, dan eksekusi checkmate Ghislaine Maxwell",
            "boss_id":   "ghislaine_maxwell",
            "boss_name":  "Ghislaine Maxwell",
            "steps": [
                "Pergi ke PUSAT KONTROL (COMMAND CENTER) — tersedia Ch.4+",
                "Analisis semua data intel yang dikumpulkan dari NPC — ekspos kelemahan sistem Ghislaine",
                "Kalahkan Ghislaine Maxwell — eksekusi rencana checkmate, probabilitas 99.9% (Boss Ch.4)",
            ],
            "completion_flag": "boss_ch4_defeated",
            "next_chapter_msg": "Checkmate! Ghislaine down. Little Black Book di tangan. Langkah terakhir: Epstein.",
        },
        5: {
            "id":     "haikaru_ch5_main",
            "title":  "Kumpulkan Variabel Bukti — Konfirmasi Semua Data",
            "objective": "Selesaikan 4 sidequest, kumpulkan USB Evidence Drive, dan konfirmasi semua variabel bukti",
            "steps": [
                "Selesaikan minimal 4 dari 5 sidequest NPC — prioritaskan berdasarkan efisiensi rute",
                "Dapatkan USB Security Drive dan bawa ke Vio → terima USB Evidence Drive",
                "Semua variabel terkonfirmasi — checkmate Epstein sudah dalam jangkauan kalkulasi",
            ],
            "completion_flag": "ch5_evidence_done",
            "next_chapter_msg": "Semua data terkumpul. Langkah ke-61: checkmate permanen Epstein.",
        },
        6: {
            "id":     "haikaru_ch6_main",
            "title":  "Checkmate Final — Akhiri Jaringan Epstein Selamanya",
            "objective": "Masuk Mansion Timur, eksekusi rencana 61 langkah, dan checkmate Jeffrey Epstein selamanya",
            "boss_id":   "epstein_boss",
            "boss_name": "Jeffrey Epstein",
            "steps": [
                "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau",
                "Konfrontasi Jeffrey Epstein — eksekusi skenario terbaik yang sudah dikalkulasi (Final Boss Ch.6)",
                "Upload USB Evidence Drive — checkmate permanen, jaringan Epstein hancur selamanya",
            ],
            "completion_flag": "haikaru_ch6_complete",
        },
    },
    "aolinh": {
        1: {
            "id":     "aolinh_ch1_main",
            "title":  "Melodi Kebebasan: Temukan Jejak Jiejie di Teater",
            "objective": "Temukan 2 petunjuk keberadaan Jiejie di teater dan kalahkan Theater Master",
            "boss_id":   "theater_master",
            "boss_name": "Theater Master",
            "steps": [
                "Cari dan ambil 2 item clue yang ditinggalkan Jiejie di area teater (★ di peta)",
                "Kalahkan Theater Master yang mengurung Jiejie di backstage (Boss Ch.1)",
            ],
            "completion_flag": "ch1_aolinh_complete",
            "next_chapter_msg": "Jiejie bebas! 我们一起！ Musik memberi kekuatan — terus maju!",
        },
        2: {
            "id":     "aolinh_ch2_main",
            "title":  "Simfoni Harapan — Selamatkan Jiejie dari Sang Ilmuwan",
            "objective": "Temukan 2 clue lokasi Jiejie dan kalahkan Dr. Rousseau yang menyembunyikan keberadaannya",
            "boss_id":   "doctor_rousseau",
            "boss_name": "Dr. Rousseau",
            "steps": [
                "Jelajahi TEATER dan area sekitarnya — temukan 2 clue lokasi Jiejie tersembunyi",
                "Lacak Dr. Rousseau di backstage teater — ilmuwan yang menyekap Jiejie",
                "Kalahkan Dr. Rousseau — bebaskan Jiejie dari eksperimen gelap (Boss Ch.2)",
            ],
            "completion_flag": "boss_ch2_defeated",
            "next_chapter_msg": "Dr. Rousseau kalah! Jiejie aman. Kini saatnya membangun tim.",
        },
        3: {
            "id":     "aolinh_ch3_main",
            "title":  "Satukan Suara — Rekrut 2 Sekutu dengan Ketulusanmu",
            "objective": "Bangun harmoni tim — temui NPC, selesaikan 2 sidequest, dan buka Chapter 4 bersama",
            "steps": [
                "Cari NPC yang butuh bantuan di area pulau — sapa dengan ketulusan hatimu",
                "Selesaikan minimal 2 sidequest — tiap orang yang dibantu menambah kekuatan tim",
                "Harmoni tim terbentuk → Chapter 4 terbuka",
            ],
            "completion_flag": "ch3_sidequests_done",
            "next_chapter_msg": "Musik menyatukan kita semua. Saatnya tantang Maxwell bersama.",
        },
        4: {
            "id":     "aolinh_ch4_main",
            "title":  "Simfoni Kebenaran — Distraksi Ghislaine dengan Musik",
            "objective": "Pergi ke Pusat Kontrol, putar Rekaman Distraksi, dan kalahkan Ghislaine Maxwell",
            "boss_id":   "ghislaine_maxwell",
            "boss_name":  "Ghislaine Maxwell",
            "steps": [
                "Pergi ke PUSAT KONTROL (COMMAND CENTER) — tersedia Ch.4+",
                "Putar Rekaman Distraksi Aolinh di sistem speaker pusat kontrol — buat celah untuk masuk",
                "Kalahkan Ghislaine Maxwell selagi penjurannya terdistraksi oleh musikmu (Boss Ch.4)",
            ],
            "completion_flag": "boss_ch4_defeated",
            "next_chapter_msg": "Ghislaine jatuh oleh melodi kebenaran! Satu langkah lagi menuju kebebasan dan Jiejie.",
        },
        5: {
            "id":     "aolinh_ch5_main",
            "title":  "Kumpulkan Bukti untuk Jiejie — Suarakan Penderitaan Semua Anak",
            "objective": "Selesaikan 4 sidequest, dapatkan USB Evidence Drive, dan siapkan suara semua korban",
            "steps": [
                "Selesaikan minimal 4 dari 5 sidequest NPC — tiap orang punya cerita yang layak didengar",
                "Bawa USB Security Drive ke Vio → terima USB Evidence Drive berisi semua bukti",
                "Kebenaran siap disuarakan ke dunia — music is power, keadilan akan menang",
            ],
            "completion_flag": "ch5_evidence_done",
            "next_chapter_msg": "Bukti untuk Jiejie dan semua anak sudah aman. Final crescendo menanti.",
        },
        6: {
            "id":     "aolinh_ch6_main",
            "title":  "Final Crescendo — Kalahkan Epstein, Bebaskan Semua Anak",
            "objective": "Pergi ke Mansion Timur, mainkan simfoni terakhirmu, dan kalahkan Epstein untuk semua anak",
            "boss_id":   "epstein_boss",
            "boss_name": "Jeffrey Epstein",
            "steps": [
                "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau",
                "Konfrontasi Jeffrey Epstein — nyanyikan simfoni terakhirmu untuk Jiejie dan semua korban (Final Boss Ch.6)",
                "Upload USB Evidence Drive — suara semua anak yang menderita akhirnya didengar dunia",
            ],
            "completion_flag": "aolinh_ch6_complete",
        },
    },
    "arganta": {
        1: {
            "id":     "arganta_ch1_main",
            "title":  "Survival Route: Kuasai Dermaga Karibia",
            "objective": "Kumpulkan 2 item survival di pantai dan kalahkan Harbor Captain untuk kuasai dermaga",
            "boss_id":   "harbor_captain",
            "boss_name": "Harbor Captain",
            "steps": [
                "Jelajahi area pantai dan kumpulkan 2 perlengkapan survival (cari ★ di peta)",
                "Kalahkan Harbor Captain yang memblokir satu-satunya jalur kabur dari pulau (Boss Ch.1)",
            ],
            "completion_flag": "ch1_arganta_complete",
            "next_chapter_msg": "Dermaga dikuasai. La via è sempre avanti, Nonno.",
        },
        2: {
            "id":     "arganta_ch2_main",
            "title":  "Dermaga di Bawah Cengkeraman — Kalahkan Mercenary Commander",
            "objective": "Scout 2 jalur pelarian baru, lalu kalahkan Mercenary Commander yang memblokir semua rute laut",
            "boss_id":   "mercenary_commander",
            "boss_name": "Mercenary Commander",
            "steps": [
                "Scout dan ambil 2 item navigasi/peta jalur baru di area DERMAGA dan PANTAI",
                "Lacak Mercenary Commander di DERMAGA — komandan bayaran yang blokir semua kapal keluar",
                "Kalahkan Mercenary Commander — buka jalur laut menuju kebebasan (Boss Ch.2)",
            ],
            "completion_flag": "boss_ch2_defeated",
            "next_chapter_msg": "Dermaga terbuka! Jalur laut tersingkap. Saatnya bangun aliansi untuk keadilan.",
        },
        3: {
            "id":     "arganta_ch3_main",
            "title":  "Per Famiglia — Bangun Aliansi untuk Keadilan",
            "objective": "Bangun aliansi untuk keadilan — selesaikan 2 sidequest dan kumpulkan key item sekutu",
            "steps": [
                "Temui NPC di area pulau — tawarkan kemampuan navigasi dan survivalmu",
                "Selesaikan minimal 2 sidequest — setiap sekutu memperkuat misi keadilan",
                "Aliansi per famiglia terbentuk → Chapter 4 terbuka",
            ],
            "completion_flag": "ch3_sidequests_done",
            "next_chapter_msg": "Tim siap. La via è sempre avanti — menuju laboratorium Maxwell.",
        },
        4: {
            "id":     "arganta_ch4_main",
            "title":  "Jalur Rahasia Nonno — Tembus Pusat Kontrol, Kalahkan Ghislaine",
            "objective": "Gunakan Peta Jalur Rahasia Nonno untuk masuk Pusat Kontrol dan kalahkan Ghislaine Maxwell",
            "boss_id":   "ghislaine_maxwell",
            "boss_name":  "Ghislaine Maxwell",
            "steps": [
                "Pergi ke PUSAT KONTROL menggunakan Peta Jalur Rahasia dari Nonno untuk bypass pos keamanan",
                "Konfrontasi Ghislaine Maxwell di jantung pusat kendali Epstein",
                "Kalahkan Ghislaine Maxwell — per famiglia, untuk keadilan keluargamu (Boss Ch.4)",
            ],
            "completion_flag": "boss_ch4_defeated",
            "next_chapter_msg": "Niente è reale. Pusat kontrol jatuh. Langkah terakhir: Epstein.",
        },
        5: {
            "id":     "arganta_ch5_main",
            "title":  "Requiescat in Pace — Kumpulkan Bukti untuk Keluargamu",
            "objective": "Selesaikan 4 sidequest, kumpulkan bukti, dan siapkan requiescat in pace untuk Nonno",
            "steps": [
                "Selesaikan minimal 4 dari 5 sidequest NPC yang tersedia di pulau",
                "Bawa USB Security Drive ke Vio → terima USB Evidence Drive",
                "Semua bukti untuk keluarga Arganta tersimpan aman — siap mengakhiri semuanya",
            ],
            "completion_flag": "ch5_evidence_done",
            "next_chapter_msg": "Nonno... ini untukmu. Saatnya mengakhiri semuanya.",
        },
        6: {
            "id":     "arganta_ch6_main",
            "title":  "Vendetta Finale — Kalahkan Epstein, Tegakkan Keadilan Keluargamu",
            "objective": "Tembus Mansion Timur dan kalahkan Jeffrey Epstein sebagai vendetta finale untuk keluargamu",
            "boss_id":   "epstein_boss",
            "boss_name": "Jeffrey Epstein",
            "steps": [
                "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau",
                "Konfrontasi Jeffrey Epstein — per Nonno, per Papà, per Mamma (Final Boss Ch.6)",
                "Upload USB Evidence Drive — keadilan untuk keluarga Arganta dan semua korban",
            ],
            "completion_flag": "arganta_ch6_complete",
        },
    },
    "ignatius": {
        1: {
            "id":     "ignatius_ch1_main",
            "title":  "Engineering Breakout: Rakit EMP, Jebol Basement",
            "objective": "Kumpulkan 3 komponen EMP, sabotase panel alarm basement, dan kalahkan AmBOTukam Mk II",
            "boss_id":   "security_bot",
            "boss_name": "AmBOTukam Mk II",
            "steps": [
                "Cari dan ambil 3 komponen EMP: Kapasitor Besar, Relay Switch, Copper Coil (★ di peta)",
                "Gunakan komponen EMP untuk sabotase panel alarm utama basement",
                "Kalahkan AmBOTukam Mk II — robot penjaga sistem keamanan basement (Boss Ch.1)",
            ],
            "completion_flag": "ch1_ignatius_complete",
            "next_chapter_msg": "SISTEM DIRETAS! Generator down. Engineering DONE. Saatnya ke pulau!",
        },
        2: {
            "id":     "ignatius_ch2_main",
            "title":  "Ancaman Baru — Hancurkan AmBOTukam Mk III",
            "objective": "Petakan 2 node generator pulau, lalu hancurkan AmBOTukam Mk III yang lebih canggih dari Mk II",
            "boss_id":   "security_bot",
            "boss_name": "AmBOTukam Mk III",
            "steps": [
                "Jelajahi BASEMENT dan area ISLAND — temukan dan petakan 2 generator/panel listrik pulau",
                "Lacak AmBOTukam Mk III di BASEMENT/ISLAND — versi upgrade yang diaktifkan darurat",
                "Hancurkan AmBOTukam Mk III dengan EMP upgrade — lebih kuat dari Mk II! (Boss Ch.2)",
            ],
            "completion_flag": "boss_ch2_defeated",
            "next_chapter_msg": "AmBOTukam Mk III hancur! Grid pulau terpetakan penuh. Rekrut tim teknis!",
        },
        3: {
            "id":     "ignatius_ch3_main",
            "title":  "Rekrut Tim Teknis — Bangun Aliansi Multi-Keahlian",
            "objective": "Rekrut tim dengan keahlian teknis — selesaikan 2 sidequest NPC dan kumpulkan key item mereka",
            "steps": [
                "Temui NPC di area pulau — tawarkan keahlian rekayasa dan teknikmu",
                "Selesaikan minimal 2 sidequest — bangun tim multi-keahlian yang solid",
                "Tim teknis terbentuk → Chapter 4 terbuka",
            ],
            "completion_flag": "ch3_sidequests_done",
            "next_chapter_msg": "Tim siap. EMP berikutnya: laboratorium Maxwell.",
        },
        4: {
            "id":     "ignatius_ch4_main",
            "title":  "EMP Total — Blackout Pusat Kendali, Kalahkan Ghislaine Maxwell",
            "objective": "Masuk Pusat Kontrol, aktifkan EMP Device untuk matikan jaringan, dan kalahkan Ghislaine Maxwell",
            "boss_id":   "ghislaine_maxwell",
            "boss_name":  "Ghislaine Maxwell",
            "steps": [
                "Pergi ke PUSAT KONTROL (COMMAND CENTER) — tersedia Ch.4+",
                "Aktifkan EMP Device di pusat kontrol — matikan SEMUA sistem elektronik Ghislaine dalam radius 40m",
                "Kalahkan Ghislaine Maxwell saat sistemnya down — engineering beats tyranny (Boss Ch.4)",
            ],
            "completion_flag": "boss_ch4_defeated",
            "next_chapter_msg": "Pusat kontrol offline! Satu sistem terakhir yang harus dimatikan: Epstein.",
        },
        5: {
            "id":     "ignatius_ch5_main",
            "title":  "Blueprint Keadilan — Dokumentasikan Semua Bukti Elektronik",
            "objective": "Selesaikan 4 sidequest, dokumentasikan bukti elektronik, dan siapkan blueprint keadilan",
            "steps": [
                "Selesaikan minimal 4 dari 5 sidequest NPC yang tersedia di pulau",
                "Bawa USB Security Drive ke Vio → terima USB Evidence Drive yang berisi 47 GB bukti",
                "Blueprint keadilan lengkap — saatnya blackout total sistem Epstein",
            ],
            "completion_flag": "ch5_evidence_done",
            "next_chapter_msg": "Blueprint selesai. Saatnya eksekusi blackout total: Epstein.",
        },
        6: {
            "id":     "ignatius_ch6_main",
            "title":  "Blackout Total — Hancurkan Infrastruktur Epstein Selamanya",
            "objective": "Tembus Mansion Timur, kalahkan Epstein, dan hancurkan infrastruktur jaringan kejahatan selamanya",
            "boss_id":   "epstein_boss",
            "boss_name": "Jeffrey Epstein",
            "steps": [
                "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau",
                "Konfrontasi Jeffrey Epstein — engineering vs kejahatan, blackout total (Final Boss Ch.6)",
                "Upload USB Evidence Drive — blackout permanen jaringan Epstein, selamatkan masa depan",
            ],
            "completion_flag": "ignatius_ch6_complete",
        },
    },
}
# CHAPTER QUEST TEMPLATES — chapter 2-6 shared across characters
# Dipanggil dari _init_location_quests dan _build_main_quest_lines
CHAPTER_QUEST_TEMPLATES = {
    2: {
        "id":        "ch2_main_unique_boss",
        "title":     "Chapter 2 — Kalahkan Boss Unik Karaktermu",
        "objective": "Jelajahi ISLAND, pergi ke area boss karaktermu, dan kalahkan Boss Ch.2",
        "steps": [
            "Jelajahi ISLAND — temukan area boss Ch.2 karaktermu (lihat HUD untuk lokasi spesifik)",
            "Lacak boss Ch.2 di lokasi yang sesuai (area berbeda tiap karakter)",
            "Kalahkan Boss Ch.2 → flag boss_ch2_defeated aktif → Chapter 3 terbuka",
        ],
        "completion_flag": "boss_ch2_defeated",
        "next_chapter_msg": "Boss Ch.2 dikalahkan! Chapter 3 terbuka — temui NPC dan bangun aliansi.",
    },
    3: {
        "id":        "ch3_main_sidequest",
        "title":     "Bangun Aliansi — Rekrut Minimal 2 Sekutu NPC",
        "objective": "Temui dan bantu NPC di pulau — selesaikan 2 sidequest untuk buka Chapter 4",
        "steps": [
            "Temui NPC yang tersedia: Haikaru (PRISON NORTH), Aolinh (TEATER), Arganta (PANTAI), Ignatius (BASEMENT), Vio (LAB Ch.4+)",
            "Selesaikan minimal 2 sidequest — kumpulkan key item reward dari tiap NPC",
            "Dua aliansi terbentuk → Chapter 4 terbuka",
        ],
        "completion_flag": "ch3_sidequests_done",
        "next_chapter_msg": "Aliansi terbentuk! Saatnya infiltrasi laboratorium Maxwell.",
    },
    4: {
        "id":        "ch4_main_ghislaine",
        "title":     "Infiltrasi Pusat Kendali — Kalahkan Ghislaine Maxwell",
        "objective": "Masuk Pusat Kontrol dan kalahkan Ghislaine Maxwell — otak jaringan yang menyembunyikan semua bukti",
        "steps": [
            "Pergi ke PUSAT KONTROL (COMMAND CENTER) — tersedia Ch.4+ via exit di ISLAND (sudah 2 SQ selesai)",
            "Gunakan key item dari aliansi NPC (EMP/Rekaman/Peta/Network Key) untuk bypass keamanan Ghislaine",
            "Kalahkan Ghislaine Maxwell — Boss Ch.4 di Pusat Kendali, buka jalan ke Ch.5",
        ],
        "completion_flag": "boss_ch4_defeated",
        "next_chapter_msg": "Ghislaine Maxwell dikalahkan! Little Black Book ada di tanganmu. Satu langkah lagi.",
    },
    5: {
        "id":        "ch5_main_evidence",
        "title":     "Kumpulkan Bukti — Persiapkan Konfrontasi Final",
        "objective": "Selesaikan 4 sidequest NPC, dapatkan USB Evidence Drive, dan siap hadapi Epstein",
        "steps": [
            "Selesaikan minimal 4 dari 5 sidequest NPC yang tersedia di pulau",
            "Bawa USB Security Drive ke Vio di LABORATORIUM → terima USB Evidence Drive",
            "Semua bukti tersimpan aman — Mansion Timur terbuka, Epstein menunggu",
        ],
        "completion_flag": "ch5_evidence_done",
        "next_chapter_msg": "Semua bukti terkumpul. Saatnya mengakhiri ini — selamanya.",
    },
    6: {
        "id":        "ch6_main_epstein",
        "title":     "Konfrontasi Final — Jeffrey Epstein Harus Dihentikan",
        "objective": "Masuk Mansion Timur, kalahkan Jeffrey Epstein, dan upload semua bukti ke dunia",
        "steps": [
            "Pergi ke Mansion Timur (mansion_east) melalui exit kanan bawah pulau (minimal 4 SQ selesai)",
            "Konfrontasi Jeffrey Epstein — gunakan semua skill dan item yang dikumpulkan (Final Boss Ch.6)",
            "Upload USB Evidence Drive segera — jaringan kejahatan Epstein terungkap ke dunia selamanya",
        ],
        "completion_flag": "boss_ch6_defeated",
        "next_chapter_msg": "EPSTEIN DIKALAHKAN. Kebenaran terungkap ke seluruh dunia.",
    },
}
def get_main_quest(char_id, chapter):
    """Kembalikan data quest utama karakter untuk chapter tertentu."""
    return CHARACTER_MAIN_QUESTS.get(char_id, {}).get(chapter)

NPC_QUESTS = {
    "haikaru": {
        "chapter": 2,
        "name": "Kode yang Terlupakan",
        "desc": "Buku catatan Haikaru — 312 halaman analisis enkripsi dan peta blind spot — "
                "disita guard veteran yang berpatroli di Penjara Utara (PRISON NORTH). "
                "Kalahkan guard veteran, ambil buku, kembalikan ke Haikaru.",
        "objective": "Kalahkan guard veteran di PRISON NORTH → dapatkan Buku Catatan Haikaru → serahkan ke Haikaru → terima Catatan Sandi",
        "steps": [
            "Pergi ke PRISON NORTH (tersedia Ch.2+)",
            "Kalahkan guard veteran yang berpatroli di koridor — drop: Buku Catatan Haikaru",
            "Temui Haikaru di PRISON NORTH → serahkan buku → terima Catatan Sandi Haikaru",
        ],
        "required_item": "Buku Catatan Haikaru",
        "required_action": None,
        "unlock_location": "prison_north",
        "location": "prison_north",
        "reward_item": "Catatan Sandi Haikaru",
        "reward_dialog": [
            "Haikaru: '...Kamu mengambilnya? Hmph. Efisien.'",
            "Haikaru: 'Semua data observasiku ada di sini. 17 posisi guard, 8 blind spot, 3 jalur keluar.'",
            "Haikaru: 'Ini Catatan Sandi — kunci decode sistem enkripsi seluruh mansion. Jaga baik-baik.'"
        ]
    },
    "aolinh": {
        "chapter": 2,
        "name": "Suara yang Terkubur",
        "desc": "Ao Lin dikurung di backstage TEATER oleh Theater Commander. "
                "Kalahkan Theater Commander, bebaskan Ao Lin — dia akan memberikan Rekaman Distraksi "
                "yang bisa dipakai untuk mengalihkan penjaga dermaga selama 10 menit.",
        "objective": "Pergi ke TEATER → kalahkan Theater Commander di backstage → Ao Lin bebas → terima Rekaman Distraksi",
        "steps": [
            "Pergi ke TEATER (tersedia Ch.2+)",
            "Cari dan kalahkan Theater Commander di area backstage (belakang panggung)",
            "Ao Lin bebas → terima Rekaman Distraksi Aolinh — berguna untuk bypass penjaga dermaga",
        ],
        "required_item": None,
        "required_action": "defeat_theater_guard",
        "unlock_location": "theater",
        "location": "theater",
        "reward_item": "Rekaman Distraksi Aolinh",
        "reward_dialog": [
            "Aolinh: 'Kamu berhasil! Oh, Dewa — terimakasih, terimakasih banyak!'",
            "Aolinh: 'Ambil ini — rekaman performanceku. Loop-kan di speaker dermaga dan penjaga akan terpaku 10 menit.'",
            "Aolinh: 'Kalau ketemu Jiejie-ku... tolong beritahu aku. 我们一起！ ♪'"
        ]
    },
    "arganta": {
        "chapter": 2,
        "name": "Warisan yang Direbut",
        "desc": "Kompas warisan Nonno milik Amerigo Arganta diambil guard veteran di PANTAI (BEACH). "
                "Di dalam kompas ada peta jalur rahasia ke laboratorium bawah tanah. "
                "Kalahkan guard veteran di pantai, ambil kompas, kembalikan ke Arganta.",
        "objective": "Kalahkan guard veteran di PANTAI → dapatkan Kompas Nonno Arganta → serahkan ke Arganta → terima Peta Jalur Rahasia",
        "steps": [
            "Pergi ke PANTAI / BEACH (tersedia Ch.2+)",
            "Kalahkan guard veteran atau mercenary thug yang berpatroli — drop: Kompas Nonno Arganta",
            "Temui Arganta di PANTAI → serahkan kompas → terima Peta Jalur Rahasia ke basement laboratorium",
        ],
        "required_item": "Kompas Nonno Arganta",
        "required_action": None,
        "unlock_location": "beach",
        "location": "beach",
        "reward_item": "Peta Jalur Rahasia",
        "reward_dialog": [
            "Arganta: 'Il compasso! Grazie mille — ini warisan terakhir Nonno-ku.'",
            "Arganta: 'Di dalam ada peta yang Nonno ukir sendiri. Terowongan ke basement laboratorium.'",
            "Arganta: 'Ambil Peta Jalur Rahasia ini. Per Nonno — ini jalan alternatif untuk tembus lab Maxwell.'"
        ]
    },
    "ignatius": {
        "chapter": 2,
        "name": "Komponen EMP yang Disita",
        "desc": "Ignatius butuh 3 komponen untuk merakit EMP Device — alat wajib untuk melemahkan "
                "Maxwell's Agent di Ch.4. Komponen disita penjaga di berbagai area pulau: "
                "Kapasitor Besar (MANSION), Relay Switch (PUSAT KONTROL), Copper Coil (MANSION/TEATER).",
        "objective": "Kumpulkan 3 komponen: Kapasitor Besar (MANSION) + Relay Switch (COMMAND CENTER) + Copper Coil (MANSION/TEATER) → serahkan ke Ignatius",
        "steps": [
            "Pergi ke MANSION → kalahkan guard elite/mansion guard → drop: Kapasitor Besar",
            "Pergi ke COMMAND CENTER → kalahkan tech guard → drop: Relay Switch",
            "Pergi ke MANSION atau TEATER → kalahkan mansion guard/guard novice → drop: Copper Coil",
            "Kembali ke BASEMENT → temui Ignatius → serahkan 3 komponen → terima EMP Device",
        ],
        "required_items": ["Kapasitor Besar", "Relay Switch", "Copper Coil"],
        "required_item": None,
        "required_action": None,
        "unlock_location": "basement",
        "location": "basement",
        "reward_item": "EMP Device",
        "reward_dialog": [
            "Ignatius: 'YES! Semua komponen lengkap! Rakit dalam 20 menit!'",
            "Ignatius: 'EMP Device ini akan matikan semua sistem elektronik Maxwell dalam radius 40 meter.'",
            "Ignatius: 'Gunakan tepat sebelum lawan Maxwell Agent di lab. WAJIB. Tanpa ini kita masuk perangkap!'"
        ]
    },
    "vio": {
        "chapter": 4,
        "name": "USB Kebenaran",
        "desc": "Vio butuh USB Security Drive dari laboratorium Maxwell untuk crack server utama. "
                "USB ini dibawa oleh scientist di LABORATORIUM (tersedia Ch.4+). "
                "Kalahkan scientist, serahkan USB ke Vio, terima USB Evidence Drive berisi semua bukti.",
        "objective": "Pergi ke LABORATORIUM (Ch.4+) → kalahkan scientist → dapatkan USB Security Drive → serahkan ke Vio → terima USB Evidence Drive",
        "steps": [
            "Pastikan sudah Ch.4 → pergi ke LABORATORIUM via exit di pulau utama",
            "Kalahkan scientist yang berpatroli di area barat lab — drop: USB Security Drive",
            "Temui Vio di LABORATORIUM → serahkan USB → terima USB Evidence Drive — WAJIB untuk ending Ch.6",
        ],
        "required_item": "USB Security Drive",
        "required_action": None,
        "unlock_location": "laboratory",
        "location": "laboratory",
        "reward_item": "USB Evidence Drive",
        "reward_dialog": [
            "Vio: '47 GB data. Daftar tamu, catatan transfer, rekaman pengawasan — semua ada.'",
            "Vio: 'Ada folder berlabel INSURANCE. Isinya lebih dari yang aku bayangkan.'",
            "Vio: 'Jaga USB Evidence Drive ini seperti nyawamu. Ini yang akan menyelamatkan semua orang.'"
        ]
    },
}
# Intro cerita tiap karakter
CHARACTER_INTROS = {
    "vio": [
        "Dia adalah Vio, hacker elite dari Edinburgh, Skotlandia yang diculik karena membobol jaringan Epstein.",
        "Di sel gelap, Dia tetap sempat check daily login game gacha di HP gaming yang disembunyikan di balik seragam.",
        "'Pity counter gue udah 87... tinggal 3 lagi guaranteed SSR...' - pikir Vio sambil analisis sistem keamanan pulau.",
        "'Sistem keamanan pulau ini... mirip game gacha dengan bad RNG. Ada backdoor di network mereka.'",
        "'Aku bisa jebol. Scottish hackers dinna give up. Keluar dari sini, lanjut pull gacha.'"
    ],
    "haikaru": [
        "Dia adalah Haikaru Fumika, ahli strategi dari Kyoto yang sudah 2 minggu memetakan seluruh pola pulau.",
        "Buku catatannya penuh — penjaga, kamera, celah — semua tercatat dengan presisi seorang juara olimpiade matematik.",
        "'Shift berganti jam 06.00 dan 18.00. Window keluar: 47 detik.' Fumika sudah hitung segalanya.",
        "'Saya bukan orang yang panik. Saya adalah orang yang membuat orang lain panik.' — kata Fumika dalam hati.",
        "'Rencana sudah matang. Yang dibutuhkan hanya satu hal lagi: seseorang yang bisa bergerak cepat.'"
    ],
    "aolinh": [
        "Dia adalah Ao Lin, gadis ceria dari Chengdu, China yang diculik bersama Jiejie-nya saat turnamen musik di Hongkong.",
        "Earphone biru kesayangannya masih ada. Biola warisan ibu masih dalam genggaman.",
        "Meski ketakutan, Ao Lin tahu satu hal: 音乐给我力量 — musik memberinya kekuatan.",
        "'Jiejie... 我来找你。 Aku akan menemukanmu. Jangan menyerah.'",
        "'Selama aku bisa memegang biola ini... aku tidak akan berhenti. 我们一起！ Kita bersama!'"
    ],
    "arganta": [
        "Dia adalah Amerigo Arganta, navigator muda dari Napoli, Italia yang keluarganya dibantai di laut Karibia.",
        "Kompas kakeknya masih di sakunya - warisan dari sang Nonno, navigator legendaris Mediterania.",
        "Di dinding selnya, Dia mengukir kata-kata yang dipelajari dari legenda kota leluhurnya di Italia:",
        "'Niente è reale, tutto è lecito.' Tidak ada yang nyata, segalanya diperbolehkan.",
        "'La via è sempre avanti,' bisiknya sambil menggenggam kompas. 'Requiescat in pace, Nonno. Aku akan selesaikan ini.'"
    ],
    "ignatius": [
        "Dia adalah Ignatius, teknisi yang bisa hack mesin apapun.",
        "Panel listrik di luar selmu bermasalah. Koneksi ground yang lemah.",
        "Lock elektronik pakai sistem lama. Kesalahan mereka. Keuntunganmu.",
        "'Lock elektronik ini... model 2015. Outdated. Vulnerable AF.'",
        "'Panel listrik, alarm, CCTV... semuanya terkoneksi ke satu grid. EZ hack. Let's break it!'"
    ]
}

def get_character_select_screen():
    text = f"\n{Warna.CYAN + Warna.TERANG}╔══════════════════════════════════════════════════════════╗\n"
    text += f"║              PILIH KARAKTER UTAMA                        ║\n"
    text += f"╚══════════════════════════════════════════════════════════╝{Warna.RESET}\n\n"
    
    for i, (char_id, data) in enumerate(PLAYABLE_CHARACTERS.items(), 1):
        name = data["name"]
        title = data["title"]
        desc = data["desc"]
        age = data["age"]
        gender = data["gender"]
        
        stats = data["stats"]
        stat_line = f"HP:{stats['hp']} ATK:{stats['attack']} DEF:{stats['defense']} SPD:{stats['speed']}"
        
        skills = [s["name"] for s in data["skills"].values()]
        skills_preview = ", ".join(skills)
        
        hobby = data.get("hobby", "Unknown")
        
        text += f"{Warna.KUNING + Warna.TERANG}[{i}] {name}{Warna.RESET} - {Warna.CYAN}{title}{Warna.RESET}\n"
        text += f"    {Warna.ABU_GELAP}{gender}, {age} tahun - {desc}{Warna.RESET}\n"
        text += f"    {Warna.PUTIH}Stats: {stat_line}{Warna.RESET}\n"
        text += f"    {Warna.HIJAU}Skills: {skills_preview}{Warna.RESET}\n"
        text += f"    {Warna.UNGU}Passive: {data['passive']}{Warna.RESET}\n"
        text += f"    {Warna.CYAN}Hobby: {hobby}{Warna.RESET}\n"
        text += f"    {Warna.ABU_GELAP}Personality: {data['personality']}{Warna.RESET}\n\n"
    
    text += f"{Warna.CYAN}Setiap karakter punya story path unik dan battle dialogs!{Warna.RESET}\n"
    text += f"{Warna.UNGU}Easter Eggs: Candala, Balatro Joker, Secret Phone Call...{Warna.RESET}\n"
    
    return text

def get_character_intro(char_id):
    if char_id in CHARACTER_INTROS:
        return CHARACTER_INTROS[char_id]
    return ["Dia terbangun di tempat asing yang gelap."]

def get_character_data(char_id):
    return PLAYABLE_CHARACTERS.get(char_id)

def get_special_npc_data(npc_id):
    return SPECIAL_NPC.get(npc_id)

def get_all_character_ids():
    return list(PLAYABLE_CHARACTERS.keys())

def get_character_name(char_id):
    char = PLAYABLE_CHARACTERS.get(char_id)
    return char["name"] if char else "Unknown"

def get_card_dialog(char_id, hand_type):
    

    char_id = char_id.lower().strip()

    char = PLAYABLE_CHARACTERS.get(char_id)
    if not char:
        return FALLBACK_CARD_DIALOGS.get("default", "Aksi!")

    dialogs = char.get("card_dialogs", {})
    if not dialogs:
        return FALLBACK_CARD_DIALOGS.get("default", "Aksi!")

    HAND_KEY_MAP = {
        "high_card":       "high_card",
        "one_pair":        "pair",
        "two_pair":        "two_pair",
        "three_of_a_kind": "three_kind",
        "straight":        "straight",
        "flush":           "flush",
        "full_house":      "full_house",
        "four_of_a_kind":  "four_kind",
        "five_of_a_kind":  "five_kind",
        "straight_flush":  "straight_flush",
        "royal_flush":     "royal_flush",
        "nothing":         "high_card",
    }

    raw_key = hand_type.lower().replace(" ", "_")
    hand_key = HAND_KEY_MAP.get(raw_key, raw_key)

    # Coba ambil dialog sesuai hand_key
    if dialogs.get(hand_key) and len(dialogs[hand_key]) > 0:
        with suppress(Exception):
            return random.choice(dialogs[hand_key])

    # Fallback untuk royal_flush dan five_kind ke straight_flush / four_kind
    if hand_key in ("royal_flush", "five_kind"):
        for alt_key in ("straight_flush", "four_kind"):
            if dialogs.get(alt_key) and len(dialogs[alt_key]) > 0:
                with suppress(Exception):
                    return random.choice(dialogs[alt_key])

    # Fallback 1: Coba ambil high_card dialog
    if dialogs.get("high_card") and len(dialogs["high_card"]) > 0:
        with suppress(Exception):
            return random.choice(dialogs["high_card"])

    # Fallback 2: Coba ambil dialog pertama dari entry manapun yang tersedia
    with suppress(Exception):
        for lines in dialogs.values():
            if lines:
                return random.choice(lines)

    # Fallback 3: Gunakan global fallback
    return FALLBACK_CARD_DIALOGS.get("default", "Aksi!")

def safe_get_card_dialog(char_id, hand_key):
    """FIX Bug 3: API aman untuk mengakses dialog kartu dari kode eksternal"""
    
    def _get_dialog_from_char(char, hand_key):
        dialogs = char.get("card_dialogs", {})
        if not dialogs:
            return None
        if dialogs.get(hand_key):
            return random.choice(dialogs[hand_key])
        if dialogs.get("high_card"):
            return random.choice(dialogs["high_card"])
        return next((random.choice(lines) for lines in dialogs.values() if lines), None)
    
    char_id  = char_id.lower().strip()
    hand_key = hand_key.lower().strip()

    with suppress(KeyError, TypeError, AttributeError):
        char = PLAYABLE_CHARACTERS.get(char_id)
        if char:
            return _get_dialog_from_char(char, hand_key)

    return None

import time
from contextlib import suppress

try:
    from .story import display_route_chapter
except ImportError:
    def display_route_chapter(chapter_id):
        pass

from .constants import (
    MAX_CHAPTERS, BOSS_CHAPTERS, FINAL_CHAPTER, CHAPTER_BOSSES,
    SIDEQUESTS_NEEDED_FOR_CH4, SIDEQUESTS_NEEDED_FOR_CH6,
)

CHAPTER_OBJECTIVES = {
    1: "[Ch.1] Selesaikan misi di lokasi starting — kabur, kalahkan Boss Ch.1!",
    2: "[Ch.2] Pergi ke area boss karaktermu (unik tiap karakter) → kalahkan Boss Ch.2",
    3: "[Ch.3] Temui NPC di ISLAND → selesaikan ≥2 sidequest → Ch.4 terbuka",
    4: "[Ch.4] COMMAND CENTER → kalahkan Ghislaine Maxwell (Boss Ch.4) → Ch.5",
    5: "[Ch.5] Selesaikan ≥4 SQ + USB Evidence Drive dari Vio (LABORATORIUM) → Ch.6",
    6: "[Ch.6] MANSION EAST (kanan bawah ISLAND) → kalahkan Epstein (Final Boss)",
}

CHAPTER_OBJECTIVES_BY_CHAR = {
    "vio": {
        1: "[Ch.1 MANSION] Hack 2 terminal → kalahkan Maxwell's Agent (Boss) → ke ISLAND",
        2: "[Ch.2 COMMAND CENTER] Hack 2 node → kalahkan Network Overseer (Boss) → Ch.3",
        3: "[Ch.3 ISLAND] Temui NPC → selesaikan ≥2 sidequest → Ch.4 terbuka",
        4: "[Ch.4 COMMAND CENTER] Gunakan Network Key → kalahkan Ghislaine Maxwell (Boss)",
        5: "[Ch.5] Selesaikan ≥4 SQ + bawa USB Security Drive ke Vio di LAB → USB Evidence Drive",
        6: "[Ch.6 MANSION EAST] Upload semua bukti → kalahkan Epstein (Final Boss)",
    },
    "haikaru": {
        1: "[Ch.1 PRISON NORTH] 3 blind spot + Kunci Wing-C → kalahkan Warden Elite (Boss)",
        2: "[Ch.2 PRISON NORTH] Petakan 2 posisi → kalahkan Kepala Penjaga (Boss) → Ch.3",
        3: "[Ch.3 ISLAND] Temui NPC → selesaikan ≥2 sidequest → Ch.4 terbuka",
        4: "[Ch.4 COMMAND CENTER] Gunakan Catatan Sandi → checkmate Ghislaine Maxwell (Boss)",
        5: "[Ch.5] Selesaikan ≥4 SQ + bawa USB Security Drive ke Vio di LAB → USB Evidence Drive",
        6: "[Ch.6 MANSION EAST] Eksekusi rencana 61 langkah → checkmate Epstein (Final Boss)",
    },
    "aolinh": {
        1: "[Ch.1 TEATER] Cari 2 jejak Jiejie → kalahkan Theater Master (Boss) → ke ISLAND",
        2: "[Ch.2 TEATER] Cari 2 clue Jiejie → kalahkan Dr. Rousseau (Boss) → Ch.3",
        3: "[Ch.3 ISLAND] Temui NPC → selesaikan ≥2 sidequest → Ch.4 terbuka",
        4: "[Ch.4 COMMAND CENTER] Putar Rekaman Distraksi → kalahkan Ghislaine Maxwell (Boss)",
        5: "[Ch.5] Selesaikan ≥4 SQ + bawa USB Security Drive ke Vio di LAB → USB Evidence Drive",
        6: "[Ch.6 MANSION EAST] Nyanyikan simfoni terakhir → kalahkan Epstein untuk Jiejie (Final)",
    },
    "arganta": {
        1: "[Ch.1 PANTAI] 2 perlengkapan survival → kalahkan Harbor Captain (Boss) → ke ISLAND",
        2: "[Ch.2 DERMAGA] Scout 2 jalur → kalahkan Mercenary Commander (Boss) → Ch.3",
        3: "[Ch.3 ISLAND] Temui NPC → selesaikan ≥2 sidequest → Ch.4 terbuka",
        4: "[Ch.4 COMMAND CENTER] Gunakan Peta Jalur Rahasia → kalahkan Ghislaine Maxwell (Boss)",
        5: "[Ch.5] Selesaikan ≥4 SQ + bawa USB Security Drive ke Vio di LAB → USB Evidence Drive",
        6: "[Ch.6 MANSION EAST] Per Nonno — vendetta finale → kalahkan Epstein (Final Boss)",
    },
    "ignatius": {
        1: "[Ch.1 BASEMENT] 3 komponen EMP → sabotase panel → kalahkan AmBOTukam Mk II (Boss)",
        2: "[Ch.2 BASEMENT] Petakan 2 generator → kalahkan AmBOTukam Mk III (Boss) → Ch.3",
        3: "[Ch.3 ISLAND] Temui NPC → selesaikan ≥2 sidequest → Ch.4 terbuka",
        4: "[Ch.4 COMMAND CENTER] EMP Device aktif → kalahkan Ghislaine Maxwell (Boss)",
        5: "[Ch.5] Selesaikan ≥4 SQ + bawa USB Security Drive ke Vio di LAB → USB Evidence Drive",
        6: "[Ch.6 MANSION EAST] Blackout total → kalahkan Epstein (Final Boss)",
    },
}

BOSS_DATA = {
    'kepala_penjaga': {
        'name':       'Kepala Penjaga',
        'chapter':    2,
        'location':   'prison_north',
        # Stats canonical: lihat enemies.py BOSSES['kepala_penjaga']
        'reward_xp':  350,
        'reward_dollars': 100,
        'reward_item': 'Kunci Master Penjara',
        'flag_key':   'boss_ch2_defeated',
        'intro': [
            "Kepala Penjaga memblokir jalan kalian.",
            "'Kamu pikir bisa kabur? Pulau ini penjara sempurna.'",
            "'Tidak ada yang pernah berhasil keluar.'",
        ],
        'defeat_text': [
            "Kepala Penjaga jatuh. Kunci master-nya terlepas dari sakunya.",
            "Jalan menuju chapter berikutnya terbuka.",
        ],
    },
    'ghislaine_maxwell': {
        'name':       'Ghislaine Maxwell - The Facilitator',
        'chapter':    4,
        'location':   'command_center',
        # Stats canonical: lihat enemies.py BOSSES['ghislaine_maxwell']
        'reward_xp':  600,
        'reward_dollars': 200,
        'reward_item': 'Little Black Book',
        'flag_key':   'boss_ch4_defeated',
        'special':    'Bawa bukti dari NPC untuk melemahkan jaringannya sebelum battle',
        'intro': [
            "Ghislaine Maxwell berdiri di pusat kendali, dikelilingi layar monitor.",
            "'Anak-anak kecil bermain detektif. Menggemaskan.'",
            "'Jeffrey akan sangat marah mendengar ini. Sayang sekali kalian tidak akan sempat melaporkannya.'",
            "'Saya sudah mengelola *jaringan* ini selama 30 tahun. Kalian pikir bisa menghentikannya?'",
        ],
        'defeat_text': [
            "Ghislaine jatuh. Little Black Book terlepas dari tangannya.",
            "Di dalamnya: ribuan nama, kontak, dan transaksi tersembunyi.",
            "Pintu menuju Epstein kini terbuka.",
        ],
    },
    'agen_maxwell': {
        # Agen Maxwell tersedia sebagai opsional fight di laboratorium Ch4
        # Bukan boss utama Ch4 lagi — digantikan Ghislaine di command_center
        'name':       "Maxwell's Agent",
        'chapter':    4,
        'location':   'laboratory',
        # Stats canonical: lihat enemies.py BOSSES['agen_maxwell']
        'reward_xp':  500,
        'reward_dollars': 150,
        'reward_item': 'Kartu Akses Lab',
        'flag_key':   'boss_lab_agent_defeated',
        'special': 'Lemah terhadap EMP Device — gunakan sebelum battle',
        'intro': [
            "Maxwell's Agent berdiri di tengah laboratorium.",
            "'Anak-anak kecil yang mana coba berani masuk ke sini.'",
            "'Maxwell sudah kasih instruksi jelas: tidak ada saksi.'",
        ],
        'defeat_text': [
            "Agent jatuh. Sistem keamanan lab tidak merespons lagi.",
            "Kartu akses ke vault dokumen kini ada di tanganmu.",
        ],
    },
    'maxwell_agent': {
        'name':       "Maxwell's Agent — Penjaga Server Room",
        'chapter':    1,
        'location':   'mansion',
        'reward_xp':  130,
        'reward_dollars': 110,
        'reward_item': 'Maxwell Agent Badge',
        'flag_key':   'boss_ch1_vio_agent_defeated',
        'intro': [
            "Maxwell's Agent menghalangi server room.",
            "'Tidak ada yang keluar dengan data dari sini.'",
            "'Maxwell memberi instruksi jelas. Kamu harus dihentikan.'",
        ],
        'defeat_text': [
            "Agent jatuh. Server room keycard terlepas dari sakunya.",
            "Vio: Selalu ada exploit-nya. Tinggal cari pattern-nya.",
        ],
    },
    'network_overseer': {
        'name':       'Network Overseer — Pengawas Jaringan Pulau',
        'chapter':    2,
        'location':   'command_center',
        'reward_xp':  300,
        'reward_dollars': 90,
        'reward_item': 'Network Master Key',
        'flag_key':   'boss_ch2_defeated',
        'intro': [
            "Network Overseer berdiri di depan server utama.",
            "'Jaringan ini dibangun untuk tidak bisa ditembus.'",
            "'256-bit encryption. Firewall berlapis. Tidak ada hacker yang lewat sini.'",
        ],
        'defeat_text': [
            "Overseer tumbang. Node jaringan pulau terbuka penuh.",
            "Vio: 256-bit? Amateur. Semua ada exploit-nya.",
        ],
    },
    'mercenary_commander': {
        'name':       'Mercenary Commander — Komandan Bayaran Dermaga',
        'chapter':    2,
        'location':   'dock',
        'reward_xp':  310,
        'reward_dollars': 100,
        'reward_item': 'Dock Commander Badge',
        'flag_key':   'boss_ch2_defeated',
        'intro': [
            "Mercenary Commander memblokir akses ke dermaga.",
            "'Tidak ada kapal keluar tanpa izinku.'",
            "'Bayaran saya terlalu bagus untuk membiarkanmu hidup.'",
        ],
        'defeat_text': [
            "Commander roboh. Dermaga terbuka. Jalur laut tersingkap.",
            "Arganta: La via è sempre avanti. Per Nonno.",
        ],
    },
    'epstein_boss': {
        'name':       'Jeffrey Epstein',
        'chapter':    6,
        'location':   'mansion_east',
        # Stats canonical: lihat enemies.py BOSSES['epstein_boss'] (2 phase)
        'reward_xp':  6666,
        'reward_dollars': 0,
        'reward_item': None,
        'flag_key':   'boss_ch6_defeated',
        'special': 'Membutuhkan USB Evidence Drive untuk unlock true ending',
        'intro': [
            "Jeffrey Epstein berdiri di ruang besar mansion.",
            "Senyumnya dingin. Sama sekali tidak takut.",
            "'Kalian pikir kalian satu-satunya yang pernah mencoba?'",
            "'Tapi tidak ada yang bisa sentuh aku. Aku... tidak tersentuh.'",
        ],
        'defeat_text': [
            "Epstein jatuh. Pulau terkutuk ini akhirnya dalam jangkauanmu.",
            "Tapi ini bukan akhir. Ini baru awal kebenaran.",
        ],
    },
}

CH1_ITEM_OBJECTIVE_MAP = {
    'vio': {
        'Keycard Level 1': ('hack_terminal',
            "Vio: Keycard ini bisa bypass firewall terminal pertama. Useful."),
        'Keycard Level 2': ('hack_terminal',
            "Vio: Level 2. Server makin terbuka. Pity counter bisa nunggu."),
        'USB Encrypted':   ('hack_terminal',
            "Vio: USB ini ada data terenkripsi. Perlu di-crack, tapi ini petunjuk besar."),
        'Laptop':          ('hack_terminal',
            "Vio: Laptop dengan akses jaringan lokal. RNG blessed today."),
        'Access Card':     ('hack_terminal',
            "Vio: Access card. Lumayan untuk akses server room utama."),
    },
    'haikaru': {
        'Buku Catatan':         ('find_blind_spots',
            "Haikaru: Catatan tambahan. Blind spot barat laut terkonfirmasi. Update kalkulasi."),
        'Buku Catatan Haikaru': ('find_blind_spots',
            "Haikaru: *menggenggam buku* Ini catatanku yang disita! Sekarang analisa bisa dilanjutkan."),
        'Info Pulau':           ('find_blind_spots',
            "Haikaru: Data baru. Pola patroli teridentifikasi. Efisiensi rencana naik 12%."),
        'Med Kit':              ('find_blind_spots',
            "Haikaru: *melihat posisi loker* Blind spot area ini teridentifikasi dari sini."),
        'Keycard Level 1':      ('find_blind_spots',
            "Haikaru: Layout yang ditunjukkan kartu ini mengkonfirmasi blind spot ketiga."),
        'Kunci Wing-C':         ('find_wingc_key',
            "Haikaru: *menggenggam kunci* Ini yang aku cari. Loker 7, bukan 12. Asumsi awal salah 3%."),
    },
    'aolinh': {

        'Health Potion':   ('find_jiejie_clues',
            "Aolinh: *menemukan sesuatu* ...Ini pita rambut Jiejie. Dia pernah di sini!"),
        'Gantungan Kunci Musik': ('find_jiejie_clues',
            "Aolinh: *mengangkat gantungan berbentuk not* ...Ini milik Jiejie! Nada favoritnya tergores di sini!"),
        'Tiket Backstage': ('find_jiejie_clues',
            "Aolinh: Tiket backstage! Jiejie pasti dibawa lewat sini. 我找到了！"),
        'Info Pulau':      ('find_jiejie_clues',
            "Aolinh: Peta ini... ada ruangan backstage yang ditandai. Jiejie pasti di sana!"),
    },
    'arganta': {
        'Health Potion':   ('collect_survival_kit',
            "Arganta: Obat-obatan. Per Nonno — bertahan dulu, lawan kemudian."),
        'Bandage':         ('collect_survival_kit',
            "Arganta: Perban. Kit survival makin lengkap. Nonno akan setuju."),
        'Kompas Nonno Arganta': ('collect_survival_kit',
            "Arganta: *menggenggam erat* Il mio compasso! Ini... ini milik Nonno. Ini segalanya."),
        'Med Kit':         ('collect_survival_kit',
            "Arganta: Med kit lengkap. Satu lagi komponen survival terkumpul."),
    },
    'ignatius': {
        'Kapasitor Besar': ('collect_emp_parts_ch1',
            "Ignatius: 200 microfarad kapasitor. PERFECT. Ini komponen utama EMP-ku!"),
        'Relay Switch':    ('collect_emp_parts_ch1',
            "Ignatius: Relay switch! Ini yang trigger pulse-nya. Engineering time!"),
        'Copper Coil':     ('collect_emp_parts_ch1',
            "Ignatius: Copper coil! Induktansi optimal. Satu lagi dan EMP prototype jadi!"),
        'Blueprint':       ('sabotage_alarm_panel',
            "Ignatius: Blueprint sistem alarm! Sekarang aku tahu persis titik lemahnya."),
        'EMP Prototype':   ('sabotage_alarm_panel',
            "Ignatius: EMP prototype aktif! Tinggal tancapkan ke panel alarm ini..."),
    },
}

CH1_PRE_BOSS_DIALOGS = {
    'vio': {
        'maxwell_agent': [
            ('narasi', "Server room utama. Di balik pintu besi... langkah kaki berat."),
            ('dialog', "Vio: *menghentikan langkah* Hmm."),
            ('inner',  "[Agen Maxwell. Bukan yang terkuat, tapi cukup berbahaya.]"),
            ('dialog', "Vio: Maxwell's Agent. Yang jaga server room. Filenya... tipis."),
            ('dialog', "Vio: Ex-military security contractor. Bisa bunuh dengan tangan kosong."),
            ('inner',  "[Situasi ini... tidak ideal untuk hacker 13 tahun sendirian.]"),
            ('inner',  "[Tapi data di server ini ada jutaan dollar dan ratusan nama. Harus diekspos.]"),
            ('dialog', "Vio: *mengepalkan tangan* Fine. Selalu ada exploit-nya."),
            ('dialog', "Vio: Gacha player tahu satu hal tentang boss — tinggal temukan pattern-nya."),
        ],
    },
    'haikaru': {
        'warden_elite': [
            ('narasi', "Pintu utama penjara. Warden Elite berdiri menghalangi jalan keluar."),
            ('dialog', "Haikaru: *berhenti tepat di ambang pintu*"),
            ('inner',  "[Warden Elite. Reaksi 0.3 detik. Jangkauan 2.1m. Berat estimasi 85kg.]"),
            ('inner',  "[Variabel yang belum diperhitungkan: seberapa cepat dia panggil bantuan.]"),
            ('dialog', "Haikaru: Tidak ada dalam kalkulasi awal saya."),
            ('dialog', "Haikaru: Tapi saya sudah siapkan tiga skenario untuk situasi ini."),
            ('dialog', "Haikaru: Skenario A. Konfrontasi langsung. Efisiensi 73%. Cukup."),
            ('narasi', "Haikaru Fumika melangkah maju dengan presisi yang dingin."),
        ],
    },
    'aolinh': {
        'theater_master': [
            ('narasi', "Backstage teater. Suara langkah berat di balik pintu besi."),
            ('dialog', "Aolinh: *mencengkeram biola* Jiejie... ada di balik pintu itu."),
            ('inner',  "[Theater Master. Yang mengurung Jiejie di sini. Yang memisahkan mereka.]"),
            ('inner',  "[Aolinh takut. Sangat takut. Tangannya gemetar.]"),
            ('dialog', "Aolinh: *berbisik* 妈妈... 给我力量。"),
            ('dialog', "Aolinh: Mama... beri aku kekuatan."),
            ('narasi', "Dia memainkan satu not biola. Pelan. Dalam."),
            ('dialog', "Aolinh: Jiejie menungguku. Aku tidak akan lari."),
            ('narasi', "Aolinh membuka pintu besi itu."),
        ],
    },
    'arganta': {
        'harbor_captain': [
            ('narasi', "Ujung dermaga. Harbor Captain berdiri menghadap laut — punggungnya ke Arganta."),
            ('dialog', "Arganta: *melihat kapal di kejauhan* Itu jalan keluarnya."),
            ('inner',  "[Harbor Captain. Yang menghalangi dermaga. Yang berdiri antara dia dan kebebasan.]"),
            ('inner',  "[Dan keadilan untuk Nonno.]"),
            ('dialog', "Arganta: *memegang kompas* La via è sempre avanti."),
            ('dialog', "Arganta: Jalan selalu ada di depan. Tapi kadang ada yang harus disingkirkan."),
            ('dialog', "Arganta: *mengeluarkan pisau lipat* Niente è reale, tutto è lecito."),
            ('narasi', "Amerigo Arganta melangkah ke pertarungan terakhirnya di chapter ini."),
        ],
    },
    'ignatius': {
        'security_bot': [
            ('narasi', "Generator room utama. AmBOTukam Mk II aktif dan berputar menghadap Ignatius."),
            ('system', ">> AMBOTUKAM MK II: UNAUTHORIZED PERSONNEL DETECTED"),
            ('system', ">> INITIATING ELIMINATION PROTOCOL"),
            ('dialog', "Ignatius: *tersenyum lebar* Oh halo juga, teman lama."),
            ('inner',  "[AmBOTukam Mk II. Model 2019. Weakpoint: central capacitor bank.]"),
            ('inner',  "[Kalau EMP prototype deliver pulse ke capacitor... sistem crash total.]"),
            ('dialog', "Ignatius: Kamu jaga generator. Bagus."),
            ('dialog', "Ignatius: Tapi aku akan matiin kamu pakai generator kamu sendiri."),
            ('dialog', "Ignatius: *menyiapkan EMP prototype* Engineering time!"),
        ],
    },
}

CH1_QUESTS = {
    'vio': {
        'title':       'Hack & Escape: Ruang Server Mansion',
        'description': 'Vio terjebak di ruang server mansion. Tembus sistem enkripsi dan kalahkan Maxwell Enforcer sebelum ketahuan.',
        'location':    'mansion',
        'objectives': [
            {
                'id':     'hack_terminal',
                'desc':   'Tembus 2 terminal server mansion',
                'target': 2,
                'type':   'interact',
                'label':  'Terminal di-hack: {}/{}'
            },
            {
                'id':     'defeat_maxwell_agent',
                'desc':   'Kalahkan Maxwell\'s Agent — penjaga server room mansion (Boss Ch.1)',
                'target': 1,
                'type':   'boss',
                'label':  'Maxwell Agent: {}/{}'
            },
        ],
        'completion_flag': 'ch1_vio_complete',
        'reward_item':     'Akses Level 3',
        'reward_flag':     'vio_ch1_reward_given',
        'completion_text': [
            "Server ter-hack. Data jutaan dollar mulai mengalir ke USB-mu.",
            "Maxwell's Agent sudah dikalahkan. Server room aman. Jalur mansion terbuka.",
            "Kamu menggenggam 'Akses Level 3' — kunci ke area island selanjutnya.",
        ],
        'next_area': 'island',
    },

    'haikaru': {
        'title':       'Escape Analysis: Penjara Utara',
        'description': 'Haikaru sudah 2 minggu kalkulasi rencana kabur. Identifikasi blind spot, ambil kunci Wing-C, kalahkan Warden Elite.',
        'location':    'prison_north',
        'objectives': [
            {
                'id':     'find_blind_spots',
                'desc':   'Identifikasi 3 blind spot penjaga (via item observasi)',
                'target': 3,
                'type':   'interact',
                'label':  'Blind spot terkonfirmasi: {}/{}'
            },
            {
                'id':     'find_wingc_key',
                'desc':   'Ambil Kunci Wing-C dari loker tersembunyi di Wing-C',
                'target': 1,
                'type':   'interact',
                'label':  'Kunci Wing-C: {}/{}'
            },
            {
                'id':     'defeat_warden_elite',
                'desc':   'Kalahkan Warden Elite yang memblokir pintu utama (Boss Ch.1)',
                'target': 1,
                'type':   'boss',
                'label':  'Warden Elite: {}/{}'
            },
        ],
        'completion_flag': 'ch1_haikaru_complete',
        'reward_item':     'Peta Blind Spot Penjara',
        'reward_flag':     'haikaru_ch1_reward_given',
        'completion_text': [
            "Semua blind spot teridentifikasi. Peta mental 100% lengkap.",
            "Kunci Wing-C berhasil diambil — celah dalam sistem dikonfirmasi.",
            "Warden Elite dinetralkan. Waktu eksekusi: tepat sesuai kalkulasi.",
            "Kamu menerima 'Peta Blind Spot Penjara' — keunggulan navigasi chapter berikutnya.",
        ],
        'next_area': 'island',
    },

    'aolinh': {
        'title':       'Melodi Kebebasan: Cari Jejak Jiejie',
        'description': 'Aolinh terjebak di theater. Cari 2 jejak Jiejie, lalu hadapi Theater Master yang mengurungnya.',
        'location':    'theater',
        'objectives': [
            {
                'id':     'find_jiejie_clues',
                'desc':   'Temukan 2 jejak Jiejie di area theater',
                'target': 2,
                'type':   'interact',
                'label':  'Jejak Jiejie ditemukan: {}/{}'
            },
            {
                'id':     'defeat_theater_master',
                'desc':   'Kalahkan Theater Master yang mengurung Jiejie (Boss Ch.1)',
                'target': 1,
                'type':   'boss',
                'label':  'Theater Master: {}/{}'
            },
        ],
        'completion_flag': 'ch1_aolinh_complete',
        'reward_item':     'Tiket Backstage',
        'reward_flag':     'aolinh_ch1_reward_given',
        'completion_text': [
            "Dua jejak Jiejie ditemukan — dia masih di pulau ini!",
            "Theater Master telah dikalahkan. Backstage terbuka.",
            "Kamu menerima 'Tiket Backstage' — izin masuk area tersembunyi.",
            "♪ Jiejie... Aolinh sudah dekat. Musik memberi kekuatan. ♪",
        ],
        'next_area': 'island',
    },

    'arganta': {
        'title':       'Survival Route: Pantai Karibia',
        'description': 'Arganta terdampar di pantai. Kumpulkan perlengkapan survival dan kalahkan Harbor Captain untuk buka jalur dermaga.',
        'location':    'beach',
        'objectives': [
            {
                'id':     'collect_survival_kit',
                'desc':   'Kumpulkan 2 perlengkapan survival (obat, perban, atau bekal)',
                'target': 2,
                'type':   'interact',
                'label':  'Perlengkapan terkumpul: {}/{}'
            },
            {
                'id':     'defeat_harbor_captain',
                'desc':   'Kalahkan Harbor Captain yang menjaga dermaga (Boss Ch.1)',
                'target': 1,
                'type':   'boss',
                'label':  'Harbor Captain: {}/{}'
            },
        ],
        'completion_flag': 'ch1_arganta_complete',
        'reward_item':     'Kompas Aktif',
        'reward_flag':     'arganta_ch1_reward_given',
        'completion_text': [
            "Perlengkapan survival terkumpul. Cukup untuk perjalanan panjang.",
            "Harbor Captain telah dikalahkan. Dermaga terbuka.",
            "Il compasso Nonno menyala — 'Kompas Aktif' menunjuk jalur barat.",
            "Per Nonno. La via è sempre avanti.",
        ],
        'next_area': 'island',
    },

    'ignatius': {
        'title':       'Engineering Breakout: Basement Listrik',
        'description': 'Ignatius di ruang listrik basement — pusat saraf seluruh pulau. Rakit EMP, sabotase alarm, hancurkan Security Bot.',
        'location':    'basement',
        'objectives': [
            {
                'id':     'collect_emp_parts_ch1',
                'desc':   'Kumpulkan 3 komponen EMP: Kapasitor Besar, Relay Switch, Copper Coil',
                'target': 3,
                'type':   'interact',
                'label':  'Komponen EMP terkumpul: {}/{}'
            },
            {
                'id':     'sabotage_alarm_panel',
                'desc':   'Sabotase panel alarm utama basement (gunakan Blueprint/EMP)',
                'target': 1,
                'type':   'interact',
                'label':  'Panel alarm disabotase: {}/{}'
            },
            {
                'id':     'defeat_security_bot',
                'desc':   'Kalahkan AmBOTukam Mk II dengan EMP prototype (Boss Ch.1)',
                'target': 1,
                'type':   'boss',
                'label':  'AmBOTukam Mk II: {}/{}'
            },
        ],
        'completion_flag': 'ch1_ignatius_complete',
        'reward_item':     'EMP Prototype',
        'reward_flag':     'ignatius_ch1_reward_given',
        'completion_text': [
            "Tiga komponen terkumpul dan dirakit menjadi EMP Prototype.",
            "Panel alarm berhasil disabotase — 30% sistem keamanan offline.",
            "AmBOTukam Mk II dihancurkan dengan EMP-nya sendiri. Poetic.",
            "Kamu menerima 'EMP Prototype' — senjata kunci untuk chapter berikutnya.",
            "Engineering time? Engineering DONE.",
        ],
        'next_area': 'island',
    },
}

CHAPTER_REQUIREMENTS = {
    2: {
        'description': 'Selesaikan quest Chapter 1 dan kabur dari area starting',
        'flags':    ['ch1_{char_id}_complete'],  # {char_id} diisi saat runtime
        'items':    [],
        'sidequests_needed': 0,
        'boss_needed': None,
    },
    3: {
        'description': 'Kalahkan Boss Ch.2 unik karaktermu (boss_ch2_defeated flag)',
        'flags':    ['boss_ch2_defeated'],
        'items':    [],
        'sidequests_needed': 0,
        'boss_needed': None,   # Tiap karakter boss Ch2 berbeda — cek via flag boss_ch2_defeated
    },
    4: {
        'description': 'Selesaikan minimal 2 sidequest NPC di Chapter 3',
        'flags':    ['boss_ch2_defeated'],   # Sudah pasti ada kalau di ch3, tapi tetap guard
        'items':    [],
        'sidequests_needed': SIDEQUESTS_NEEDED_FOR_CH4,  # 2
        'boss_needed': None,
    },
    5: {
        'description': "Kalahkan Ghislaine Maxwell di Pusat Kontrol (Boss Chapter 4)",
        'flags':    ['boss_ch4_defeated'],
        'items':    [],
        'sidequests_needed': 0,
        'boss_needed': 'ghislaine_maxwell',
    },
    6: {
        'description': 'Selesaikan minimal 4 sidequest NPC + miliki USB Evidence Drive dari Vio',
        'flags':    ['boss_ch4_defeated', 'vio_sidequest_done'],   # Guard: boss ch4 + vio SQ selesai
        'items':    [],   # USB masuk quest_items, dicek via vio_sidequest_done flag
        'sidequests_needed': SIDEQUESTS_NEEDED_FOR_CH6,  # 4
        'boss_needed': None,
    },
}

CHAPTER_LOCATIONS = {
    1: {
        # Ch1: hanya area starting + command_center tidak tersedia
        'vio':      ['mansion'],
        'haikaru':  ['prison_north'],
        'aolinh':   ['theater'],
        'arganta':  ['beach'],
        'ignatius': ['basement', 'mansion'],
    },
    2: {
        'all': ['island', 'prison_north', 'prison_south', 'mansion',
                'dock', 'theater', 'beach', 'basement', 'command_center'],
    },
    3: {
        'all': ['island', 'prison_north', 'prison_south', 'mansion',
                'dock', 'theater', 'beach', 'basement', 'command_center',
                'mansion_west', 'mansion_east'],
    },
    4: {
        'all': ['island', 'prison_north', 'prison_south', 'mansion',
                'dock', 'theater', 'beach', 'basement', 'command_center',
                'mansion_west', 'mansion_east', 'laboratory'],
    },
    5: {
        'all': ['island', 'prison_north', 'prison_south', 'mansion',
                'dock', 'theater', 'beach', 'basement', 'command_center',
                'mansion_west', 'mansion_east', 'laboratory'],
    },
    6: {
        'all': ['island', 'prison_north', 'prison_south', 'mansion',
                'dock', 'theater', 'beach', 'basement', 'command_center',
                'mansion_west', 'mansion_east', 'laboratory'],
    },
}

def get_character_route(char_id):
    # Mengambil konfigurasi route untuk setiap karakter
    """Return route configuration untuk setiap karakter."""
    routes = {
        'vio': {
            'start_location':     'mansion',
            'start_coords':       (12, 3),
            'chapter_1_location': 'mansion',
            'intro': [
                "Kamu terbangun di ruang server mansion.",
                "Layar komputer di depanmu masih menyala.",
                "Ada file terbuka: 'GUEST_LIST.encrypted'",
                "",
                "Skill hacking-mu berguna di sini.",
                "Tapi kamu harus keluar secepatnya!",
            ],
            'starting_items':    ['USB Encrypted', 'Laptop'],
            'special_objective': 'Hack server, kabur dari mansion',
            'difficulty':        'Medium',
            'bonus_stat':        {'attack': +3, 'speed': +2},
        },

        'haikaru': {
            'start_location':     'prison_north',
            'start_coords':       (12, 3),
            'chapter_1_location': 'prison_north',
            'intro': [
                "Kamu terbangun di sel penjara yang dingin.",
                "Sudah 2 minggu kamu mengamati pola penjaga.",
                "47 halaman catatan. 17 posisi guard. 8 blind spot.",
                "",
                "Sekarang jam 5:47 pagi. Shift berganti jam 6:00.",
                "Window 47 detik. Cukup.",
                "Haikaru Fumika tidak pernah salah hitung.",
            ],
            'starting_items':    ['Buku Catatan', 'Pensil'],
            'special_objective': 'Identifikasi blind spot, kabur dari penjara',
            'difficulty':        'Easy',
            'bonus_stat':        {'defense': +5, 'speed': +1},
        },

        'aolinh': {
            'start_location':     'theater',
            'start_coords':       (12, 9),
            'chapter_1_location': 'theater',
            'intro': [
                "Kamu terbangun di atas panggung teater yang gelap.",
                "Biola warisan ibu masih di sampingmu. Earphone biru masih di leher.",
                "Bekas air mata di pipimu belum kering.",
                "",
                "Jiejie-mu... kakakmu... dimana?",
                "Kalian diculik bersama dari Hongkong. Lalu dipisahkan.",
                "音乐给我力量 — Musik memberimu kekuatan. Mari mulai!",
            ],
            'starting_items':    ['Biola', 'Earphone'],
            'special_objective': 'Cari jejak Jiejie, kabur dari theater',
            'difficulty':        'Easy',
            'bonus_stat':        {'max_hp': +8, 'defense': +3},
        },

        'arganta': {
            'start_location':     'beach',
            'start_coords':       (3, 9),
            'chapter_1_location': 'beach',
            'intro': [
                "Kamu terbangun di pantai pulau terkutuk.",
                "Reruntuhan perahu keluargamu... hancur di kejauhan.",
                "'Rescue operation' katanya. Bugiardi. Semua pembohong.",
                "",
                "Il compasso di Nonno masih di sakumu.",
                "'La via è sempre avanti, Amerigo. Jalan selalu ada di depan.'",
                "Suara kakekmu terngiang. Benar, Nonno. Ini bukan akhir.",
                "",
                "Arah barat laut: dermaga. Kesempatanmu kabur.",
                "Per Nonno. Per famiglia. Per la vendetta!",
            ],
            'starting_items':    ['Kompas Nonno Arganta', 'Pisau Lipat'],
            'special_objective': 'Kumpulkan perlengkapan survival, buka jalur dermaga',
            'difficulty':        'Medium',
            'bonus_stat':        {'attack': 4, 'speed': 3},
        },

        'ignatius': {
            'start_location':     'basement',
            'start_coords':       (12, 3),
            'chapter_1_location': 'basement',
            'intro': [
                "Kamu terbangun di ruang elektrik basement.",
                "Panel listrik di depanmu. Generator backup.",
                "Sistem keamanan pulau terhubung ke sini.",
                "",
                "Satu EMP pulse dan semua alarm mati.",
                "Tapi kamu butuh komponen. Cari di sekitar basement.",
                "Engineering time!",
            ],
            'starting_items':    ['Multitool', 'Blueprint'],
            'special_objective': 'Kumpulkan komponen, sabotase alarm sistem',
            'difficulty':        'Hard',
            'bonus_stat':        {'attack': +5, 'defense': +2},
        },
    }
    return routes.get(char_id, routes['haikaru'])


def get_ch1_quest(char_id):
    """Return data quest Chapter 1 untuk karakter yang dipilih."""
    return CH1_QUESTS.get(char_id)

def get_ch1_item_objective(char_id, item_name):
    
    return CH1_ITEM_OBJECTIVE_MAP.get(char_id, {}).get(item_name)

def get_ch1_pre_boss_dialog(char_id, boss_id):
    
    return CH1_PRE_BOSS_DIALOGS.get(char_id, {}).get(boss_id, [])

def init_ch1_quest(game_state):
    # Menginisialisasi quest Chapter 1 ke game_state
    """Inisialisasi quest Chapter 1 ke game_state.active_quests."""
    char_id = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return

    quest_id = f"ch1_{char_id}"
    # Cek sudah ada belum
    for q in game_state.active_quests:
        if q.get('id') == quest_id:
            return

    targets = [obj['desc'] for obj in quest_data['objectives']]
    game_state.add_quest(
        quest_id=quest_id,
        title=quest_data['title'],
        objective=quest_data['description'],
        targets=targets,
        location=quest_data['location'],
        quest_type='main',
    )

def update_ch1_objective(game_state, objective_id, amount=1):
    
    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return False

    obj_flag   = f"ch1_obj_{objective_id}"
    current    = game_state.story_flags.get(obj_flag, 0)
    target_obj = next((o for o in quest_data['objectives'] if o['id'] == objective_id), None)
    if not target_obj:
        return False

    new_val = min(current + amount, target_obj['target'])
    game_state.story_flags[obj_flag] = new_val

    # Sync HUD — pastikan active_quests selalu mencerminkan jumlah objective selesai
    sync_ch1_quest_hud(game_state)

    return check_ch1_complete(game_state)

def check_ch1_objective_progress(game_state, objective_id):
    """Return (current, target) progress untuk satu objective."""
    char_id = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return 0, 1
    obj = next((o for o in quest_data['objectives'] if o['id'] == objective_id), None)
    if not obj:
        return 0, 1
    current = game_state.story_flags.get(f"ch1_obj_{objective_id}", 0)
    return current, obj['target']

def check_ch1_complete(game_state):
    
    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return False

    comp_flag = quest_data['completion_flag']
    if game_state.story_flags.get(comp_flag):
        return True  # Sudah selesai sebelumnya

    # Cek semua objective
    for obj in quest_data['objectives']:
        current = game_state.story_flags.get(f"ch1_obj_{obj['id']}", 0)
        if current < obj['target']:
            return False

    # Semua selesai!
    game_state.story_flags[comp_flag] = True
    game_state.story_flags['chapter_1_complete'] = True


    reward = quest_data.get('reward_item')
    reward_flag = quest_data.get('reward_flag')
    if reward and not game_state.story_flags.get(reward_flag):
        game_state.add_item(reward)  # add_item auto-route ke add_quest_item jika quest item
        if reward_flag:
            game_state.story_flags[reward_flag] = True

    # Complete quest di active_quests
    quest_id = f"ch1_{char_id}"
    game_state.complete_quest(quest_id)

    return True

def sync_ch1_quest_hud(game_state):
    
    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return
    quest_id = f"ch1_{char_id}"
    completed = sum(
        1 for obj in quest_data['objectives']
        if game_state.story_flags.get(f"ch1_obj_{obj['id']}", 0) >= obj['target']
    )
    for q in game_state.active_quests:
        if q.get('id') == quest_id:
            q['progress'] = completed
            q['total']    = len(quest_data['objectives'])
            break

def get_ch1_objective_status(game_state):
    
    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return []
    result = []
    for obj in quest_data['objectives']:
        cur  = game_state.story_flags.get(f"ch1_obj_{obj['id']}", 0)
        done = cur >= obj['target']
        obj_type = obj.get('type', 'interact')
        result.append((obj['id'], obj['desc'], cur, obj['target'], done, obj_type))
    return result

def get_ch1_next_incomplete_objective(game_state):
    """Return (obj_id, obj_def) objective Ch1 pertama yang belum selesai, atau None."""
    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return None, None
    for obj in quest_data['objectives']:
        cur = game_state.story_flags.get(f"ch1_obj_{obj['id']}", 0)
        if cur < obj['target']:
            return obj['id'], obj
    return None, None

CH1_OBJECTIVE_COMPLETE_DIALOGS = {
    'vio': {
        'hack_terminal': [
            "Vio: Terminal berhasil ditembus. Data jaringan mulai terbuka.",
            "Vio: *menutup laptop sebentar* Oke. Tinggal satu hal lagi.",
        ],
        'defeat_maxwell_agent': [
            "Vio: Maxwell's Agent down. Server room bersih.",
            "Vio: *menghembuskan napas* Agennya kalah. Maxwell-nya sendiri nanti.",
        ],
    },
    'haikaru': {
        'find_blind_spots': [
            "Haikaru: Semua blind spot terkonfirmasi. Peta mental diperbarui.",
            "Haikaru: Efisiensi rute naik 23%. Sesuai proyeksi.",
        ],
        'find_wingc_key': [
            "Haikaru: Kunci Wing-C. Bagian yang hilang dari kalkulasi awal.",
            "Haikaru: *mengangguk* Sekarang satu obstacle tersisa: Warden Elite.",
        ],
        'defeat_warden_elite': [
            "Haikaru: Warden Elite dinetralkan. Waktu: tepat sesuai kalkulasi.",
            "Haikaru: *mengangguk singkat* Probabilitas keberhasilan: 100%. Sesuai.",
        ],
    },
    'aolinh': {
        'find_jiejie_clues': [
            "Aolinh: Aku menemukan jejaknya! Jiejie pernah ada di sini!",
            "Aolinh: *memeluk biola* 我找到了！ Dia masih di pulau ini!",
        ],
        'defeat_theater_master': [
            "Aolinh: Theater Master sudah kalah. Backstage terbuka!",
            "Aolinh: ♪ Jiejie... tunggu aku, Aolinh sudah dekat ♪",
        ],
    },
    'arganta': {
        'collect_survival_kit': [
            "Arganta: Perlengkapan terkumpul. Nonno akan setuju dengan ini.",
            "Arganta: *menggenggam kompas* Per famiglia. Satu lagi.",
        ],
        'defeat_harbor_captain': [
            "Arganta: Harbor Captain dilumpuhkan. Dermaga sekarang milikku.",
            "Arganta: La via è sempre avanti. *melihat kapal di kejauhan*",
        ],
    },
    'ignatius': {
        'collect_emp_parts_ch1': [
            "Ignatius: Semua komponen terkumpul! EMP prototype siap dirakit!",
            "Ignatius: *mata berbinar* Engineering time dimulai sekarang.",
        ],
        'sabotage_alarm_panel': [
            "Ignatius: Panel alarm berhasil disabotase. 30% sistem keamanan offline.",
            "Ignatius: *mengelap tangan* Tinggal satu: AmBOTukam Mk II.",
        ],
        'defeat_security_bot': [
            "Ignatius: AmBOTukam Mk II dihancurkan dengan EMP-nya sendiri. PERFECT.",
            "Ignatius: *tertawa kecil* Kamu jaga generator. Aku pakein generatormu untuk matiin kamu.",
        ],
    },
}

CH1_NEXT_OBJECTIVE_DIALOGS = {
    'vio': {
        'defeat_maxwell_agent': [
            "Vio: Maxwell's Agent masih menghalangi server room...",
            "Vio: Contractor ex-militer. Jelas berbahaya. Tapi ada exploit-nya.",
            "Vio: *mengepalkan tangan* Semua boss ada pattern-nya. Cari dan eksploitasi.",
        ],
    },
    'haikaru': {
        'find_wingc_key': [
            "Haikaru: Ada kunci tersembunyi di Wing-C. Di balik panel listrik ketiga.",
            "Haikaru: Aku sudah kalkulasi posisinya. Estimasi waktu pengambilan: 8 detik.",
        ],
        'defeat_warden_elite': [
            "Haikaru: Warden Elite memblokir pintu keluar. Reaksi 0.3 detik. Jangkauan 2.1m.",
            "Haikaru: Sudah ada tiga skenario untuk ini. Skenario A: konfrontasi langsung. Efisiensi 73%.",
        ],
    },
    'aolinh': {
        'defeat_theater_master': [
            "Aolinh: Theater Master menghalangi backstage... Yang mengurung Jiejie di sini.",
            "Aolinh: *mencengkeram biola* 妈妈... 给我力量。 Aku tidak akan lari.",
        ],
    },
    'arganta': {
        'defeat_harbor_captain': [
            "Arganta: Harbor Captain berdiri di ujung dermaga. Yang menghalangi jalan pulang.",
            "Arganta: *memegang kompas* Niente è reale, tutto è lecito. Per Nonno.",
        ],
    },
    'ignatius': {
        'sabotage_alarm_panel': [
            "Ignatius: Masih ada panel alarm utama yang perlu disabotase.",
            "Ignatius: Lokasi: sudut barat basement. Kalau itu mati, seluruh sistem alarm padam.",
        ],
        'defeat_security_bot': [
            "Ignatius: AmBOTukam Mk II masih aktif dan menjaga generator utama.",
            "Ignatius: *menyiapkan EMP prototype* Kamu jaga generator aku? Aku pakai generatormu untuk matiin kamu.",
        ],
    },
}

def get_ch1_objective_complete_dialog(char_id, obj_id):
    """Return list dialog setelah objective selesai. Empty list jika tidak ada."""
    return CH1_OBJECTIVE_COMPLETE_DIALOGS.get(char_id, {}).get(obj_id, [])

def get_ch1_next_objective_dialog(char_id, next_obj_id):
    """Return list dialog intro untuk objective berikutnya. Empty list jika tidak ada."""
    return CH1_NEXT_OBJECTIVE_DIALOGS.get(char_id, {}).get(next_obj_id, [])

def display_ch1_completion(game_state):
    """Tampilkan teks penyelesaian Ch1 dan transisi ke Ch2."""
    from .utils import clear_screen, wait_input, separator

    char_id    = game_state.player_character
    quest_data = get_ch1_quest(char_id)
    if not quest_data:
        return

    clear_screen()
    separator('═')
    print(f"{Warna.HIJAU + Warna.TERANG}  CHAPTER 1 SELESAI!{Warna.RESET}".center(70))
    separator('═')
    print()
    for line in quest_data.get('completion_text', []):
        print(f"  {Warna.KUNING}{line}{Warna.RESET}")
        time.sleep(0.4)
    print()
    reward = quest_data.get('reward_item')
    if reward:
        print(f"  {Warna.HIJAU}[ ITEM DIDAPAT ]{Warna.RESET} {reward}")
    print()
    separator()
    wait_input("Tekan ENTER untuk lanjut ke Chapter 2... ")
    # Auto-advance chapter so the game immediately recognizes Ch2 is available
    try:
        game_state.story_flags['current_chapter'] = 2
        game_state.story_flags['ch2_bosses_available'] = True
        # Keep only side quests in active_quests (main quest completed)
        game_state.active_quests = [q for q in game_state.active_quests if q.get('quest_type') == 'side']
    except Exception:
        pass


def get_current_chapter(game_state):
    """Return current chapter sebagai int."""
    try:
        return int(game_state.story_flags.get('current_chapter', 1))
    except (ValueError, TypeError):
        return 1

def check_chapter_unlock(game_state, target_chapter):
    
    if target_chapter > MAX_CHAPTERS:
        return False, "Chapter tidak ada."

    char_id = game_state.player_character
    reqs = CHAPTER_REQUIREMENTS.get(target_chapter, {})
    reasons = []

    # Cek story flags
    for flag_template in reqs.get('flags', []):
        flag = flag_template.replace('{char_id}', char_id)
        if not game_state.story_flags.get(flag):
            reasons.append(f"Flag belum terpenuhi: {flag}")

    # Cek items — cek inventory DAN quest_items (quest items disimpan di quest_items)
    for item in reqs.get('items', []):
        has_it = (item in game_state.inventory or item in game_state.quest_items)
        if not has_it:
            reasons.append(f"Item belum ada: {item}")

    # Cek sidequests
    needed = reqs.get('sidequests_needed', 0)
    done   = game_state.story_flags.get('sidequests_completed', 0)
    if done < needed:
        reasons.append(f"Sidequest kurang: {done}/{needed} selesai")

    # Cek boss
    boss_id = reqs.get('boss_needed')
    if boss_id:
        boss_data = BOSS_DATA.get(boss_id, {})
        flag_key  = boss_data.get('flag_key', '')
        if flag_key and not game_state.story_flags.get(flag_key):
            reasons.append(f"Boss belum dikalahkan: {boss_data.get('name', boss_id)}")

    if reasons:
        return False, " | ".join(reasons)
    return True, "OK"

def advance_chapter(game_state):
    """Maju ke chapter berikutnya. Return True jika berhasil."""
    current = get_current_chapter(game_state)
    if current >= MAX_CHAPTERS:
        return False
    target = current + 1
    can, reason = check_chapter_unlock(game_state, target)
    if can:
        game_state.story_flags['current_chapter'] = target
        return True
    return False

def check_chapter_complete(game_state):
    
    chapter = get_current_chapter(game_state)
    char_id = game_state.player_character

    if chapter == 1:
        return game_state.story_flags.get('chapter_1_complete', False)
    else:
        target = chapter + 1
        if target > MAX_CHAPTERS:
            return game_state.story_flags.get('boss_ch6_defeated', False)
        can, _ = check_chapter_unlock(game_state, target)
        return can

def get_chapter_progress_info(game_state):
    
    chapter = get_current_chapter(game_state)
    char_id = game_state.player_character

    info = {
        'chapter':    chapter,
        'objective':  CHAPTER_OBJECTIVES.get(chapter, ""),
        'is_boss_chapter': chapter in BOSS_CHAPTERS,
        'boss_name':  None,
        'boss_done':  False,
        'next_unlock_reason': "",
        'can_advance': False,
    }

    if chapter in BOSS_CHAPTERS:
        boss_id = CHAPTER_BOSSES.get(chapter)
        if chapter == 2:
            # Ch2 boss is character-specific — resolve from CHARACTER_MAIN_QUESTS
            char_id = game_state.player_character
            ch2_quest = CHARACTER_MAIN_QUESTS.get(char_id, {}).get(2, {})
            boss_id = ch2_quest.get('boss_id', 'kepala_penjaga')
        boss_data = BOSS_DATA.get(boss_id, {})
        info['boss_name'] = boss_data.get('name', '???')
        # Ch2 universal completion flag
        if chapter == 2:
            info['boss_done'] = game_state.story_flags.get('boss_ch2_defeated', False)
        else:
            info['boss_done'] = game_state.story_flags.get(boss_data.get('flag_key', ''), False)

    target = chapter + 1
    if target <= MAX_CHAPTERS:
        can, reason = check_chapter_unlock(game_state, target)
        info['can_advance']        = can
        info['next_unlock_reason'] = "" if can else reason
    else:
        info['can_advance'] = game_state.story_flags.get('boss_ch6_defeated', False)

    return info


def display_route_intro(char_id):
    """Tampilkan intro awal Chapter 1 untuk karakter yang dipilih."""
    from .utils import clear_screen, wait_input, separator

    route = get_character_route(char_id)
    clear_screen()
    separator('═')
    display_name = "AMERIGO ARGANTA" if char_id == 'arganta' else char_id.upper()
    print(f"{Warna.HIJAU + Warna.TERANG}CHAPTER 1 DIMULAI — {display_name}{Warna.RESET}".center(70))
    separator('═')
    print()
    for line in route['intro']:
        if line:
            print(f"  {Warna.KUNING}{line}{Warna.RESET}")
        else:
            print()
    print()
    separator()
    print(f"  {Warna.CYAN}Objektif: {route['special_objective']}{Warna.RESET}")
    print(f"  {Warna.ABU_GELAP}Kesulitan: {route['difficulty']}{Warna.RESET}")
    separator()
    print()
    wait_input()

def apply_route_bonuses(game_state, char_id):
    # Menerapkan bonus stat dan item sesuai rute karakter
    """Apply stat dan item bonuses sesuai rute karakter. Dipanggil sekali saat new game."""
    if game_state.story_flags.get('route_bonuses_applied'):
        return game_state

    route   = get_character_route(char_id)
    bonuses = route.get('bonus_stat', {})

    if 'max_hp' in bonuses:
        game_state.max_hp += bonuses['max_hp']
        game_state.hp = min(game_state.hp + bonuses['max_hp'], game_state.max_hp)
    if 'attack'  in bonuses: game_state.attack  += bonuses['attack']
    if 'defense' in bonuses: game_state.defense += bonuses['defense']
    if 'speed'   in bonuses: game_state.speed   += bonuses['speed']

    for item in route.get('starting_items', []):
        if item not in game_state.inventory:
            game_state.add_item(item)

    game_state.current_location = route.get('chapter_1_location', 'island')
    if coords := route.get('start_coords'):
        game_state.story_flags['start_x'] = coords[0]
        game_state.story_flags['start_y'] = coords[1]

    game_state.story_flags['route_bonuses_applied'] = True
    game_state.story_flags['current_chapter']       = 1
    game_state.story_flags['sidequests_completed']  = 0
    return game_state

def get_chapter_locations(chapter):
    
    return CHAPTER_LOCATIONS.get(chapter, CHAPTER_LOCATIONS.get(2, {}))

def can_access_location(char_id, location, chapter):
    """Cek apakah karakter bisa akses lokasi di chapter saat ini."""
    chapter_data = CHAPTER_LOCATIONS.get(chapter, CHAPTER_LOCATIONS[2])
    if chapter == 1:
        allowed = chapter_data.get(char_id, [])
    else:
        allowed = chapter_data.get('all', [])
    return location in allowed

def get_boss_for_current_chapter(game_state):
    """Return boss_id jika chapter saat ini adalah boss chapter, else None."""
    chapter = get_current_chapter(game_state)
    return CHAPTER_BOSSES.get(chapter)

def mark_boss_defeated(game_state, boss_id):
    """Tandai boss sebagai sudah dikalahkan dan update bosses_defeated count."""
    boss_data = BOSS_DATA.get(boss_id, {})
    flag_key  = boss_data.get('flag_key', '')
    if flag_key:
        game_state.story_flags[flag_key] = True
    game_state.bosses_defeated = game_state.bosses_defeated + 1
    # Berikan reward item jika ada
    reward = boss_data.get('reward_item')
    if reward and reward not in game_state.inventory:
        game_state.add_item(reward)
    return boss_data

def get_npc_display_name(npc_id):
    """Nama tampilan NPC (wrapper ke npc_interactions jika tersedia)."""
    names = {
        'haikaru':  'Haikaru Fumika',
        'aolinh':   'Ao Lin',
        'arganta':  'Amerigo Arganta',
        'ignatius': 'Ignatius Forgers',
        'vio':      'Vio',
    }
    return names.get(npc_id, npc_id.capitalize())

def check_candala_encounter(game_state):
    
    chapter = int(game_state.story_flags.get('current_chapter', 1))
    if chapter < 2:
        return

    battles = game_state.battles_won
    already_met = game_state.story_flags.get('candala_encountered', False)
    if not already_met and battles >= 5 and chapter >= 2:
        # Trigger dialog misterius
        game_state.story_flags['candala_encountered'] = True
        try:
            from .sprites import Warna
            import time
            print(f"\n  {Warna.UNGU}*Sebuah pesan muncul di layar terdekat...{Warna.RESET}")
            time.sleep(0.5)
            print(f"  {Warna.UNGU + Warna.TERANG}??? : \"Kamu lebih jauh dari yang mereka kira. Hati-hati.\"{Warna.RESET}")
            time.sleep(1.5)
        except Exception:
            pass
