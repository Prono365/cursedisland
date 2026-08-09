from .sprites import Warna
import random


ENEMIES = {
    "guard_novice": {
        "id": "guard_novice",
        "name": "Security Guard - Novice",
        "level": 1,
        "hp": 155,
        "max_hp": 155,
        "attack": 17,
        "defense": 9,
        "speed": 13,
        "xp": 35,
        "dollars": 15,
        "desc": "Nervous rookie guard",
        "sprite": "G",
        "ai_style": "defensive",
        "loot": ["Health Potion", "Keycard Level 1", "Flashlight"],
        "dialog": {
            "encounter": "Hey! Stop right there, kid!",
            "defeat": "I'm just doing my job..."
        }
    },
    
    "guard_veteran": {
        "id": "guard_veteran",
        "name": "Security Guard - Veteran",
        "level": 3,
        "hp": 210,
        "max_hp": 210,
        "attack": 23,
        "defense": 16,
        "speed": 17,
        "xp": 65,
        "dollars": 25,
        "desc": "Experienced guard",
        "sprite": "G",
        "ai_style": "balanced",
        "loot": ["Med Kit", "Keycard Level 2", "Stun Baton"],
        "dialog": {
            "encounter": "You kids aren't going anywhere!",
            "defeat": "How did... you're just children..."
        }
    },
    
    "guard_elite": {
        "id": "guard_elite",
        "name": "Elite Security Guard",
        "level": 5,
        "hp": 260,
        "max_hp": 260,
        "attack": 28,
        "defense": 23,
        "speed": 21,
        "xp": 95,
        "dollars": 40,
        "desc": "Elite military background guard",
        "sprite": "G",
        "ai_style": "aggressive",
        "loot": ["Armor Vest", "Keycard Level 3", "Tactical Knife"],
        "dialog": {
            "encounter": "Kids? Doesn't matter. You're not leaving.",
            "defeat": "Impossible... defeated by children..."
        }
    },
    
    "mercenary_thug": {
        "id": "mercenary_thug",
        "name": "Mercenary Thug",
        "level": 2,
        "hp": 180,
        "max_hp": 180,
        "attack": 27,
        "defense": 12,
        "speed": 18,
        "xp": 50,
        "dollars": 30,
        "desc": "Hired muscle",
        "sprite": "M",
        "ai_style": "reckless",
        "loot": ["Baseball Bat", "Cash $50", "Bandage"],
        "dialog": {
            "encounter": "Boss says no one leaves.",
            "defeat": "Damn it..."
        }
    },
    
    "mercenary_sniper": {
        "id": "mercenary_sniper",
        "name": "Mercenary Sniper",
        "level": 4,
        "hp": 200,
        "max_hp": 200,
        "attack": 26,
        "defense": 12,
        "speed": 20,
        "xp": 80,
        "dollars": 40,
        "desc": "Long-range specialist",
        "sprite": "S",
        "ai_style": "patient",
        "loot": ["Scope", "Rifle Parts", "Med Kit"],
        "dialog": {
            "encounter": "Target acquired.",
            "defeat": "Mission... failed..."
        }
    },
    
    "scientist": {
        "id": "scientist",
        "name": "Corrupted Scientist",
        "level": 3,
        "hp": 155,
        "max_hp": 155,
        "attack": 21,
        "defense": 15,
        "speed": 14,
        "xp": 65,
        "dollars": 30,
        "desc": "Researcher in dark experiments",
        "sprite": "R",
        "ai_style": "tactical",
        "loot": ["Research Notes", "Serum", "Lab Keycard"],
        "dialog": {
            "encounter": "Test subjects escaping!",
            "defeat": "My research..."
        }
    },
    
    "mansion_guard": {
        "id": "mansion_guard",
        "name": "Mansion Security",
        "level": 2,
        "hp": 180,
        "max_hp": 180,
        "attack": 21,
        "defense": 12,
        "speed": 14,
        "xp": 50,
        "dollars": 25,
        "desc": "Regular mansion security patrol",
        "sprite": "G",
        "ai_style": "balanced",
        "loot": ["Med Kit", "Keycard Level 2", "Walkie Talkie"],
        "dialog": {
            "encounter": "Intruder in the mansion!",
            "defeat": "Backup... need backup..."
        }
    },
    
    "tech_guard": {
        "id": "tech_guard",
        "name": "Tech Security",
        "level": 3,
        "hp": 200,
        "max_hp": 200,
        "attack": 23,
        "defense": 15,
        "speed": 16,
        "xp": 65,
        "dollars": 35,
        "desc": "Guard protecting server room",
        "sprite": "T",
        "ai_style": "defensive",
        "loot": ["Access Card", "Laptop Charger", "Med Kit"],
        "dialog": {
            "encounter": "Server room is restricted!",
            "defeat": "How did you... bypass the system..."
        }
    }
}


# Data boss
BOSSES = {
    "maxwell_enforcer": {
        "id": "maxwell_enforcer",
        "name": "Maxwell - Head of Security",
        "level": 8,
        "hp": 570,
        "max_hp": 570,
        "attack": 30,
        "defense": 18,
        "speed": 22,
        "xp": 150,
        "dollars": 150,
        "desc": "Former military, Epstein's head enforcer",
        "sprite": "M",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "ai_style": "boss_tactical",
        "loot": ["Master Keycard", "Maxwell's Badge", "Encrypted USB"],
        "skills": {
            "intimidate": {
                "name": "Intimidating Shout",
                "power": 40,
                "effect": "Reduces party defense 20% for 2 turns"
            },
            "tactical_strike": {
                "name": "Tactical Strike",
                "power": 60,
                "effect": "High damage, ignores 50% defense"
            },
            "call_backup": {
                "name": "Call Backup",
                "power": 0,
                "effect": "Summons 2 guards",
                "uses": 1
            }
        },
        "dialog": {
            "encounter": [
                "Maxwell: Five kids. Made it farther than expected.",
                "Maxwell: But this ends here. Mr. Epstein pays well.",
                "Maxwell: And I always deliver."
            ],
            "phase2": [
                "Maxwell: *Grits teeth* Tougher than you look...",
                "Maxwell: But I was Special Forces!"
            ],
            "defeat": [
                "Maxwell: No... can't lose to kids...",
                "*Maxwell collapses. His radio crackles.*"
            ]
        }
    },
    
    "doctor_rousseau": {
        "id": "doctor_rousseau",
        "name": "Dr. Rousseau - Lead Researcher",
        "level": 9,
        "hp": 530,
        "max_hp": 530,
        "attack": 26,
        "defense": 15,
        "speed": 25,
        "xp": 180,
        "dollars": 180,
        "desc": "Twisted scientist conducting experiments",
        "sprite": "R",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "ai_style": "boss_tricky",
        "loot": ["Experimental Serum", "Lab Master Key", "Research Data"],
        "skills": {
            "neurotoxin": {
                "name": "Neurotoxin Gas",
                "power": 30,
                "effect": "Poison - 15 damage per turn for 3 turns"
            },
            "enhancement_serum": {
                "name": "Enhancement Serum",
                "power": 0,
                "effect": "Boosts ATK/DEF 40% for 3 turns"
            },
            "release_subjects": {
                "name": "Release Test Subjects",
                "power": 0,
                "effect": "Summons 3 enhanced subjects",
                "uses": 1
            }
        },
        "dialog": {
            "encounter": [
                "Dr. Rousseau: Fascinating! Remarkable resilience!",
                "Dr. Rousseau: How does it feel to defy your captors?",
                "Dr. Rousseau: Let's make this a proper experiment!"
            ],
            "phase2": [
                "Dr. Rousseau: *Laughs maniacally* This data is incredible!",
                "Dr. Rousseau: Your survival instincts are off the charts!"
            ],
            "defeat": [
                "Dr. Rousseau: No... the experiment...",
                "Dr. Rousseau: You've ruined everything...",
                "*She collapses among broken test tubes.*"
            ]
        }
    },
    
    "ghislaine_maxwell": {
        "id": "ghislaine_maxwell",
        "name": "Ghislaine Maxwell - The Facilitator",
        "level": 10,
        "hp": 600,
        "max_hp": 600,
        "attack": 29,
        "defense": 20,
        "speed": 26,
        "xp": 200,
        "dollars": 200,
        "desc": "Epstein's right hand, recruited countless victims",
        "sprite": "G",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "ai_style": "boss_manipulative",
        "loot": ["Little Black Book", "Private Island Keys", "Incriminating Photos"],
        "skills": {
            "manipulation": {
                "name": "Manipulative Lies",
                "power": 35,
                "effect": "Confusion + fear debuff"
            },
            "summon_guards": {
                "name": "Call Elite Guards",
                "power": 0,
                "effect": "Summons 3 elite guards",
                "uses": 2
            },
            "desperate_strike": {
                "name": "Desperate Attack",
                "power": 65,
                "effect": "High damage when cornered"
            }
        },
        "dialog": {
            "encounter": [
                "Ghislaine: *berbalik dari panel monitor* Oh. Tamu tak diundang.",
                "Ghislaine: Saya sudah mengelola jaringan ini selama 30 tahun.",
                "Ghislaine: Anak-anak yang lari? Biasanya kami yang menangkap mereka kembali.",
                "Ghislaine: Tapi kalian berbeda... Kalian sudah terlalu jauh. Sayang sekali."
            ],
            "phase2": [
                "Ghislaine: *marah* Saya membangun SEMUA ini dari nol!",
                "Ghislaine: Tidak ada satu pun anak yang pernah lolos!",
                "Ghislaine: Jaringan ini tidak bisa dihancurkan hanya oleh kalian!"
            ],
            "defeat": [
                "Ghislaine: No... my network... my protection...",
                "Ghislaine: Jeffrey... where are you... I need—",
                "Ghislaine: *Jatuh* They promised I'd never be touched...",
                "*Little Black Book terlepas dari tangannya. Ribuan nama. Ribuan koneksi.*",
                "*Pintu menuju Epstein kini terbuka.*"
            ]
        }
    },
    
    "prince_andrew": {
        "id": "prince_andrew",
        "name": "Prince Andrew - The Royal Predator",
        "level": 10,
        "hp": 560,
        "max_hp": 560,
        "attack": 31,
        "defense": 18,
        "speed": 24,
        "xp": 220,
        "dollars": 220,
        "desc": "Duke of York, frequent island visitor, protected by crown",
        "sprite": "P",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "ai_style": "boss_entitled",
        "loot": ["Royal Seal", "Private Photos", "Incriminating Documents"],
        "skills": {
            "royal_immunity": {
                "name": "Royal Immunity Claim",
                "power": 0,
                "effect": "Reduces damage taken by 50% for 3 turns"
            },
            "privileged_strike": {
                "name": "Privileged Strike",
                "power": 55,
                "effect": "High damage, thinks he's untouchable"
            },
            "deny_everything": {
                "name": "Deny Everything",
                "power": 30,
                "effect": "Confusion attack + attempt to gaslight"
            }
        },
        "dialog": {
            "encounter": [
                "Prince Andrew: I don't recall... I don't sweat...",
                "Prince Andrew: You have no proof I was ever here!",
                "Prince Andrew: I have diplomatic immunity! You can't touch me!",
                "Prince Andrew: The crown will protect me. It always has."
            ],
            "phase2": [
                "Prince Andrew: This is preposterous!",
                "Prince Andrew: I was at Pizza Express in Woking!",
                "Prince Andrew: My lawyers will bury you!"
            ],
            "defeat": [
                "Prince Andrew: The photographs... my alibi...",
                "Prince Andrew: This will ruin everything...",
                "Prince Andrew: *Falls* The Queen will... disown me...",
                "*His phone falls, showing damning text messages.*"
            ]
        }
    },
    
    "bill_clinton": {
        "id": "bill_clinton",
        "name": "Bill Clinton - The Former President",
        "level": 11,
        "hp": 625,
        "max_hp": 625,
        "attack": 33,
        "defense": 19,
        "speed": 24,
        "xp": 240,
        "dollars": 250,
        "desc": "Ex-president, frequent flyer on Lolita Express",
        "sprite": "B",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "ai_style": "boss_political",
        "loot": ["Flight Logs", "Secret Service Records", "Burner Phone"],
        "skills": {
            "political_spin": {
                "name": "Political Spin",
                "power": 35,
                "effect": "Confuse + reduce party attack"
            },
            "executive_order": {
                "name": "Executive Power",
                "power": 60,
                "effect": "Command guards, massive damage"
            },
            "deny_plausibly": {
                "name": "Plausible Deniability",
                "power": 0,
                "effect": "Dodge attacks, claim innocence"
            }
        },
        "dialog": {
            "encounter": [
                "Clinton: I did not have relations with that island.",
                "Clinton: My trips were purely humanitarian work.",
                "Clinton: You can't prove anything. The records are sealed.",
                "Clinton: I'm a former president. Touch me and face consequences."
            ],
            "phase2": [
                "Clinton: *Furious* You think you can take ME down?",
                "Clinton: I've survived worse scandals!",
                "Clinton: The deep state protects its own!"
            ],
            "defeat": [
                "Clinton: The flight logs... oh god, the flight logs...",
                "Clinton: 26 times... they said it was just once...",
                "Clinton: *Collapses* My legacy... ruined...",
                "*His briefcase opens, revealing classified documents.*"
            ]
        }
    },
    

    "warden_elite": {
        "id": "warden_elite",
        "name": "Warden Elite - Kepala Penjaga",
        "level": 7,
        "hp": 540,
        "max_hp": 540,
        "attack": 25,
        "defense": 15,
        "speed": 18,
        "xp": 130,
        "dollars": 120,
        "desc": "Penjaga kepala yang blokir jalur keluar penjara",
        "sprite": "W",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Master Key Penjara", "Walkie-Talkie Penjaga"],
        "dialog": {
            "encounter": [
                "Warden: Kamu mau kemana, tahanan?",
                "Warden: Tidak ada yang pernah keluar hidup-hidup dari sini.",
                "Warden: Rencana apapun yang kamu punya... sudah aku antisipasi."
            ],
            "defeat": [
                "Warden: Im-imposibel... tidak ada yang pernah...",
                "*Warden jatuh. Kunci master terlepas dari sabuknya.*"
            ]
        }
    },
    
    "theater_master": {
        "id": "theater_master",
        "name": "Theater Master - Penguasa Panggung",
        "level": 7,
        "hp": 500,
        "max_hp": 500,
        "attack": 23,
        "defense": 14,
        "speed": 22,
        "xp": 120,
        "dollars": 110,
        "desc": "Pengelola teater yang menjaga Jiejie",
        "sprite": "T",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Kunci Ruang Belakang", "Tiket Backstage"],
        "dialog": {
            "encounter": [
                "Theater Master: Kamu mengacaukan pertunjukanku!",
                "Theater Master: Perempuan itu? Oh, dia koleksi pribadiku.",
                "Theater Master: Tidak akan ada yang menyelamatkannya."
            ],
            "defeat": [
                "Theater Master: K-kamu... merusak segalanya...",
                "*Theater Master roboh di atas panggungnya sendiri.*",
                "Dari balik pintu backstage: 'Aolinh...? Aolinh, itu kamu?'"
            ]
        }
    },
    
    "harbor_captain": {
        "id": "harbor_captain",
        "name": "Harbor Captain - Kapten Pelabuhan",
        "level": 7,
        "hp": 525,
        "max_hp": 525,
        "attack": 27,
        "defense": 16,
        "speed": 16,
        "xp": 140,
        "dollars": 130,
        "desc": "Kapten yang jaga jalur keluar dermaga",
        "sprite": "C",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Kunci Dermaga", "Peta Jalur Laut"],
        "dialog": {
            "encounter": [
                "Captain: Ha! Bocah nyasar di pelabuhan-ku.",
                "Captain: Tidak ada kapal yang keluar tanpa izin-ku.",
                "Captain: Dan kamu... tidak punya izin."
            ],
            "defeat": [
                "Captain: Accidenti...! Chi sei tu...?",
                "*Kapten terjatuh. Kunci dermaga menggelinding ke kakimu.*"
            ]
        }
    },
    
    "security_bot": {
        "id": "security_bot",
        "name": "AmBOTukam Mk II",
        "level": 8,
        "hp": 575,
        "max_hp": 575,
        "attack": 28,
        "defense": 20,
        "speed": 14,
        "xp": 150,
        "dollars": 140,
        "desc": "Robot keamanan penjaga generator utama basement",
        "sprite": "R",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.4],
        "loot": ["Generator Key", "Circuit Fragments"],
        "dialog": {
            "encounter": [
                "AMBOTUKAM MK II: INTRUDER DETECTED.",
                "AMBOTUKAM MK II: INITIATING THREAT ELIMINATION PROTOCOL.",
                "AMBOTUKAM MK II: RESISTANCE IS FUTILE."
            ],
            "defeat": [
                "AMBOTUKAM MK II: SYSTEM FAIL... CORE BREACH...",
                "*Robot berhenti bergerak. Lampu merahnya mati perlahan.*",
                "Ignatius: Satu EMP tepat sasaran. Seperti yang sudah kuhitung."
            ]
        }
    },

    "kepala_penjaga": {
        "id": "kepala_penjaga",
        "name": "Kepala Penjaga",
        "level": 10,
        "hp": 690,
        "max_hp": 690,
        "attack": 28,
        "defense": 15,
        "speed": 12,
        "xp": 300,
        "dollars": 80,
        "desc": "Kepala Penjaga pulau yang memblokir jalan utama",
        "sprite": "K",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Kunci Master Penjara", "Walkie-Talkie Penjaga"],
        "dialog": {
            "encounter": [
                "Kepala Penjaga memblokir jalan kalian.",
                "'Kamu pikir bisa kabur? Pulau ini penjara sempurna.'",
                "'Tidak ada yang pernah berhasil keluar.'",
            ],
            "defeat": [
                "Kepala Penjaga jatuh. Kunci master-nya terlepas dari sakunya.",
                "Jalan menuju chapter berikutnya terbuka.",
            ]
        }
    },

    "agen_maxwell": {
        "id": "agen_maxwell",
        "name": "Maxwell's Agent",
        "level": 13,
        "hp": 1000,
        "max_hp": 1000,
        "attack": 44,
        "defense": 22,
        "speed": 18,
        "xp": 500,
        "dollars": 150,
        "desc": "Agen Maxwell yang menjaga laboratorium dengan instruksi tanpa ampun",
        "sprite": "A",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Kartu Akses Lab", "Encrypted Files"],
        "dialog": {
            "encounter": [
                "Maxwell's Agent berdiri di tengah laboratorium.",
                "'Anak-anak kecil yang mana coba berani masuk ke sini.'",
                "'Maxwell sudah kasih instruksi jelas: tidak ada saksi.'",
            ],
            "defeat": [
                "Agent jatuh. Sistem keamanan lab tidak merespons lagi.",
                "Kartu akses ke vault dokumen kini ada di tanganmu.",
            ]
        }
    },


    "maxwell_agent": {
        "id": "maxwell_agent",
        "name": "Maxwell's Agent — Penjaga Server Room",
        "level": 7,
        "hp": 525,
        "max_hp": 525,
        "attack": 25,
        "defense": 14,
        "speed": 18,
        "xp": 130,
        "dollars": 110,
        "desc": "Agen kepercayaan Maxwell yang menjaga server room mansion — Vio Ch1",
        "sprite": "A",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Server Room Keycard", "Maxwell Agent Badge"],
        "dialog": {
            "encounter": [
                "Agent: Siapa yang berani masuk server room ini?",
                "Agent: Anak kecil? Ironis. Maxwell kirim saya untuk urusan ini.",
                "Agent: Instruksinya jelas: tidak ada saksi. Tidak ada data keluar.",
                "Agent: Kamu salah tempat, salah waktu."
            ],
            "phase2": [
                "Agent: *terengah-engah* Jangan remehkan—",
                "Agent: Maxwell tidak akan senang dengan ini!",
                "Agent: *mengaktifkan alarm cadangan* LOCKDOWN SEKARANG!"
            ],
            "defeat": [
                "Agent: Im-impossible... seorang anak...",
                "*Agent tumbang. Keycard server room terlepas dari sakunya.*",
                "Vio: Pattern ditemukan. Tinggal exploit-nya."
            ]
        }
    },

    "network_overseer": {
        "id": "network_overseer",
        "name": "Network Overseer — Pengawas Jaringan Pulau",
        "level": 10,
        "hp": 700,
        "max_hp": 700,
        "attack": 30,
        "defense": 18,
        "speed": 22,
        "xp": 300,
        "dollars": 90,
        "desc": "Pengawas jaringan data pulau yang menjaga server utama — Vio Ch2",
        "sprite": "N",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Network Master Key", "Server Access Card"],
        "dialog": {
            "encounter": [
                "Overseer: Intrusi terdeteksi di node jaringan utama.",
                "Overseer: Aku yang membangun arsitektur keamanan ini dari awal.",
                "Overseer: 256-bit encryption. Firewall berlapis tiga. AI watchdog.",
                "Overseer: Tidak ada hacker yang pernah menembus layer-3 saya."
            ],
            "phase2": [
                "Overseer: *panik* Bagaimana kamu bisa bypass firewall layer-2?!",
                "Overseer: SISTEM LOCKDOWN DARURAT — AKTIF!",
                "Overseer: Saya akan matikan seluruh grid pulau kalau perlu!"
            ],
            "defeat": [
                "Overseer: 256-bit... ditembus... oleh anak 13 tahun...",
                "*Overseer tumbang. Node jaringan pulau terbuka sepenuhnya.*",
                "Vio: 256-bit? Ch.1 difficulty di dunia hacking. Terlalu santai."
            ]
        }
    },

    "mercenary_commander": {
        "id": "mercenary_commander",
        "name": "Mercenary Commander — Komandan Bayaran Dermaga",
        "level": 10,
        "hp": 675,
        "max_hp": 675,
        "attack": 34,
        "defense": 13,
        "speed": 24,
        "xp": 310,
        "dollars": 100,
        "desc": "Komandan pasukan bayaran yang memblokir jalur dermaga — Arganta Ch2",
        "sprite": "C",
        "boss": True,
        "phases": 2,
        "phase_thresholds": [0.5],
        "loot": ["Dock Commander Badge", "Mercenary Contract"],
        "dialog": {
            "encounter": [
                "Commander: Heh. Bocah Italia nyasar di dermaga saya.",
                "Commander: Keluargamu sudah tidak bisa menolong. Mereka sudah... pergi.",
                "Commander: Tidak ada kapal keluar tanpa izin saya. Dan kamu tidak punya izin.",
                "Commander: Bayaran saya terlalu bagus untuk membiarkan kamu hidup."
            ],
            "phase2": [
                "Commander: *menghunus senjata cadangan* BUNUH DIA SEKARANG!",
                "Commander: Satu bocah tidak mungkin mengalahkan unit saya!",
                "Commander: Kamu pikir kompas tua itu bisa melawan peluru?!"
            ],
            "defeat": [
                "Commander: Accidenti... figlio di—",
                "*Commander roboh di dermaga. Peluit komando jatuh ke laut.*",
                "Arganta: *menggenggam kompas* Per Nonno. La via è sempre avanti."
            ]
        }
    },

    "epstein_boss": {
        "id": "epstein_boss",
        "name": "Jeffrey Epstein",
        "level": 20,
        "hp": 2100,
        "max_hp": 2100,
        "attack": 80,
        "defense": 38,
        "speed": 33,
        "xp": 6666,
        "desc": "The predator. The monster. The man who must be stopped.",
        "sprite": "E",
        "boss": True,
        "final_boss": True,
        "ai_style": "final_boss",
        "phases": 2,
        "phase_thresholds": [0.50],
        "loot": ["Kebebasan"],
        "skills": {
            "corruption": {
                "name": "Corrupting Influence",
                "power": 45,
                "effect": "Massive debuff - all stats -30% for 2 turns"
            },
            "power_play": {
                "name": "Power Play",
                "power": 80,
                "effect": "Massive single target damage"
            },
            "network_summon": {
                "name": "Summon The Network",
                "power": 0,
                "effect": "Summons elite enemies",
                "uses": 2
            },
            "last_resort": {
                "name": "Desperate Gambit",
                "power": 100,
                "effect": "Huge damage but leaves vulnerable"
            }
        },
        "dialog": {
            "encounter": [
                "Epstein: So you're the ones causing trouble.",
                "Epstein: Five children think they can bring me down?",
                "Epstein: I've destroyed people far more powerful than you.",
                "Epstein: Presidents, royalty, billionaires - they all owe me.",
                "Epstein: Let me teach you how the real world works."
            ],
            "phase2": [
                "Epstein: *Breathing heavily* Persistent little brats...",
                "Epstein: But I always win. ALWAYS.",
                "Epstein: I have too much power, too many connections!",
                "Epstein: ENOUGH! I will NOT lose to children!",
                "Epstein: I am JEFFREY EPSTEIN! I am UNTOUCHABLE!",
                "Epstein: Even if you kill me, the network survives!",
                "Epstein: You can't possibly win!"
            ],
            "defeat": [
                "Epstein: No... no... this isn't... possible...",
                "Epstein: I'm... Jeffrey Epstein... I can't... lose...",
                "Epstein: My connections... my power... everything...",
                "Epstein: *Gasping* The evidence... in my safe... destroy it...",
                "Epstein: Please... I'll tell you everything... just—",
                "",
                "*He collapses. The monster is defeated.*",
                "",
                "Around the island, alarms begin to shut down.",
                "The security systems fail. The doors unlock.",
                "You did it. You actually did it.",
                "",
                f"{Warna.HIJAU + Warna.TERANG}The island is free.{Warna.RESET}",
                f"{Warna.KUNING}And you have all the evidence to expose the entire network.{Warna.RESET}"
            ]
        }
    },

    "benjamin_superboss": {
        "id": "benjamin_superboss",
        "name": "BENJAMIN, SCOURGE OF THE SQUIRT SEAS",
        "level": 30,
        "hp": 5000,
        "max_hp": 5000,
        "attack": 115,
        "defense": 50,
        "speed": 40,
        "xp": 50000,
        "dollars": 20000,
        "desc": "The mythic abyssal leviathan. Lord of the Squirt Seas. The undisputed supreme terror of Cursed Island.",
        "sprite": "S",
        "boss": True,
        "superboss": True,
        "ai_style": "superboss",
        "phases": 3,
        "phase_thresholds": [0.65, 0.30],
        "loot": ["Crown of the Squirt Seas", "Abyssal Pearl"],
        "skills": {
            "squirt_tsunami": {
                "name": "Taunt, or: the Torrential Tsunami to Tear the Tainted",
                "power": 65,
                "effect": "Small abyssal water wave damage"
            },
            "abyssal_drown": {
                "name": "Reach for the Abyss and Drown! Drown! Drown!",
                "power": 60,
                "effect": "Inflicts drowning horror - drains HP & Energy"
            },
            "scourge_crush": {
                "name": "Abyssus Abyssum Invocat",
                "power": 150,
                "effect": "Devastating crushing strike from the ocean depths"
            }
        },
        "dialog": {
            "encounter": [
                "*Hening yang mencekam memenuhi palung abisal... lalu ombak samudra bergemuruh dari kegelapan terkutuk.*",
                "BENJAMIN: Ah... another wanderer brave enough to step into the sunless deep...",
                "BENJAMIN: Tell me, traveler... do you hear the weeping beneath these tides?",
                "BENJAMIN: For millennia, I have watched empires crumble and sunken stars fade into dust.",
                "BENJAMIN: I am Benjamin... Scourge of the Squirt Seas, warden of forgotten tears.",
                "BENJAMIN: If it is death you seek in this cold abyss... I shall grant you eternal rest!"
            ],
            "phase2": [
                "*Air laut berubah menjadi hitam pekat saat aura abisal membumbung tinggi, menggetarkan dasar samudra!*",
                "BENJAMIN: Fierce is thy blade, land-dweller... yet the abyss knows no warmth, nor pity.",
                "BENJAMIN: Hear the roar of a thousand drowned souls crying from the deep!",
                "BENJAMIN: Behold! The Torrent of Sorrow — wash away into oblivion!"
            ],
            "phase3": [
                "*Tubuh raksasa Benjamin membara dengan cahaya abisal bergelora. Pusaran air merobek dasar palung!*",
                "BENJAMIN: Even as my ancient core fractures... the tide shall NEVER yield!",
                "BENJAMIN: O fathomless void... lend me thy final, tragic splendor!",
                "BENJAMIN: Sink with me into the starless, endless abyss!"
            ],
            "defeat": [
                "*Cahaya abisal perlahan memudar... Suara gemuruh samudra kini berganti menjadi hening yang begitu pedih.*",
                "BENJAMIN: Ah... so the tide finally recedes...",
                "BENJAMIN: The cold... the quiet... How long has it been since I saw the light of the sun?",
                "",
                "BENJAMIN: \"Upon the bed of sunless blue,",
                "BENJAMIN:  Where ancient tides eternally weep,",
                "BENJAMIN:  A lonely lord bids his adieu,",
                "BENJAMIN:  To rest at last in boundless deep.",
                "",
                "BENJAMIN:  No crowns remain, no seas to keep...",
                "BENJAMIN:  Only the silence... of final sleep.\"",
                "",
                "BENJAMIN: Forgive me, my sea... I could not guard thy depths...",
                "",
                "*Pusaran air mereda menjadi buih keemasan yang tenang. BENJAMIN, SCOURGE OF THE SQUIRT SEAS telah kembali ke pangkuan samudra.*"
            ]
        }
    }
}

# create_enemy_instance: lihat definisi lengkap di bawah (dengan chapter scaling)


def create_boss_instance(boss_id):
    """Create a fully independent boss instance.
    Uses deepcopy so mutations during combat never bleed back into BOSSES.
    Also guarantees hp == max_hp at creation time regardless of any typo in
    the data dict, and initialises the phase-tracking fields combat.py needs.
    """
    import copy
    boss = BOSSES.get(boss_id)
    if boss is None:
        return None
    instance = copy.deepcopy(boss)
    # Safety: always start with full HP (catches any hp/max_hp typo left in data)
    instance['hp'] = instance['max_hp']
    # Phase tracking — consumed by check_boss_phase() in combat.py
    instance.setdefault('current_phase', 1)
    instance['_phases_triggered'] = set()
    return instance

def get_enemy_for_location(location, chapter=1):
    """Get appropriate enemy for location based on chapter progression"""
    
    if chapter == 1:
        location_enemies = {
            "island":       ["guard_novice", "guard_novice"],         # +1 extra patrol
            "prison_north": ["guard_novice", "guard_novice"],
            "prison_south": ["guard_novice"],
            "mansion":      ["guard_novice", "mansion_guard", "guard_novice"],  # +1 extra
            "dock":         ["guard_novice", "mansion_guard"],
            "theater":      ["guard_novice"],
            "beach":        ["guard_novice"],
            "basement":     ["guard_novice", "tech_guard"],           # +tech_guard
        }
    elif chapter == 2:
        location_enemies = {
            "island":       ["guard_novice", "guard_veteran", "guard_veteran"],  # +1 extra
            "prison_north": ["guard_novice", "guard_veteran"],
            "prison_south": ["guard_novice", "guard_veteran", "mercenary_thug"],  # +merc
            "mansion":      ["mansion_guard", "guard_veteran", "tech_guard", "guard_elite"],  # +elite
            "dock":         ["guard_veteran", "mercenary_thug", "guard_veteran"],  # +1 extra
            "theater":      ["guard_veteran", "mercenary_thug"],      # +merc
            "beach":        ["guard_veteran", "guard_veteran"],       # +1 extra
            "basement":     ["guard_veteran", "tech_guard", "guard_elite"],  # +elite
        }
    else:
        location_enemies = {
            "island":       ["guard_veteran", "mercenary_thug", "guard_elite"],  # +elite
            "prison_north": ["guard_veteran", "guard_elite"],
            "prison_south": ["guard_veteran", "mercenary_thug"],      # +merc
            "mansion":      ["guard_veteran", "guard_elite", "tech_guard", "mercenary_sniper"],  # +sniper
            "dock":         ["guard_elite", "mercenary_sniper", "guard_elite"],  # +extra
            "laboratory":   ["scientist", "guard_elite", "scientist"],  # +scientist
        }
    
    enemies = location_enemies.get(location, ["guard_novice"])
    return random.choice(enemies)

def get_boss_for_location(location):
    """Get boss for specific location"""
    boss_map = {
        "dock": "mercenary_commander",          # Ch2 Arganta
        "laboratory": "doctor_rousseau",
        "command_center": "ghislaine_maxwell",  # Ghislaine Maxwell di Pusat Kontrol (Ch4)
        "mansion_west": "prince_andrew",
        "mansion_east": "epstein_boss"
    }
    
    return boss_map.get(location)

# Probabilitas spawn musuh per lokasi per chapter
SPAWN_RATES = {
    1: {
        "island":       0.10,   # naik dari 0.08
        "prison_north": 0.12,   # naik dari 0.10
        "prison_south": 0.12,
        "mansion":      0.15,   # naik dari 0.12
        "dock":         0.15,
        "theater":      0.12,
        "beach":        0.10,
        "basement":     0.15,
    },
    2: {
        "island":       0.15,   # naik dari 0.12
        "prison_north": 0.18,
        "prison_south": 0.18,
        "mansion":      0.22,   # naik dari 0.18
        "dock":         0.25,   # naik dari 0.20
        "theater":      0.18,
        "beach":        0.15,
        "basement":     0.22,
    },
    3: {
        "island":       0.18,   # naik dari 0.15
        "prison_north": 0.23,
        "prison_south": 0.23,
        "mansion":      0.28,   # naik dari 0.25
        "dock":         0.35,   # naik dari 0.30
        "laboratory":   0.32,
    }
}

def should_spawn_enemy(location, chapter=1):
    """Check if enemy should spawn based on chapter"""
    # Safe zone adalah area aman — tidak ada enemy yang spawn di sini
    if location == 'safe_zone':
        return False
    chapter_rates = SPAWN_RATES.get(chapter, SPAWN_RATES[1])
    spawn_rate = chapter_rates.get(location, 0.10)
    return random.random() < spawn_rate

def get_all_boss_ids():
    """Get list of all boss IDs"""
    return list(BOSSES.keys())

def get_boss_count():
    """Get total number of bosses"""
    return len(BOSSES)



def scale_enemy_for_chapter(enemy, chapter, player_level=1):
    # Balance: Regular enemy scale with player level; boss HP fixed (no level scale)
    import copy
    e = copy.deepcopy(enemy)
    is_boss = e.get('boss', False)

    ch_factor = 1.0 + (max(1, int(chapter)) - 1) * 0.12
    if is_boss:
        # Boss: chapter scale only, no player_level scaling (HP already tuned)
        total = ch_factor
    else:
        # Regular enemy: scale with player level (+8% per level above 1)
        lv_factor = 1.0 + (max(1, int(player_level)) - 1) * 0.08
        total     = ch_factor * lv_factor

    e['hp']      = max(e.get('hp', 50),      int(e['hp'] * total))
    e['max_hp']  = e['hp']
    e['attack']  = max(e.get('attack', 10),  int(e['attack'] * total))
    e['defense'] = max(e.get('defense', 5),  int(e['defense'] * total))
    e['speed']   = max(e.get('speed', 10),   int(e['speed'] * total))
    e['xp']      = int(e.get('xp', 10) * (ch_factor if is_boss else total))
    return e


def create_enemy_instance(enemy_id, chapter=1, player_level=1):
    # Public: create enemy instance with chapter/level scaling + Hard Mode 1.2x
    if enemy_id in ENEMIES:
        base = ENEMIES[enemy_id].copy()
    elif enemy_id in BOSSES:
        base = BOSSES[enemy_id].copy()
    else:
        return None
    # Tambah variance kecil ±10%
    import random
    variance = random.uniform(0.90, 1.10)
    base['hp']     = int(base.get('hp', 50)     * variance)
    base['max_hp'] = base['hp']
    # Scale berdasarkan chapter/level
    return scale_enemy_for_chapter(base, chapter, player_level)




def check_boss_phase(enemy):
    """Called from combat.py each turn after the player deals damage.

    Checks whether the boss HP has crossed a phase threshold and, if so,
    triggers the phase-transition sequence.  Returns a dict when a new phase
    fires, None otherwise.

    Return shape:
        {
            'new_phase' : int,          # 2 or 3
            'dialog'    : list[str],    # lines to print
            'atk_mult'  : float,        # already applied to enemy dict
            'def_mult'  : float,
            'spd_mult'  : float,
            'heal'      : int,          # HP restored (0 if none)
        }

    Side-effects: mutates enemy['current_phase'], enemy['_phases_triggered'],
    and the enemy's attack / defense / speed / hp values.
    Safe to call on regular enemies — returns None immediately.
    """
    if not enemy.get('boss'):
        return None

    thresholds = enemy.get('phase_thresholds', [])
    total_phases = enemy.get('phases', 1)
    if total_phases <= 1 or not thresholds:
        return None

    max_hp = enemy.get('max_hp', 1)
    hp     = max(0, enemy.get('hp', 0))
    hp_pct = hp / max(max_hp, 1)

    triggered = enemy.setdefault('_phases_triggered', set())

    for i, threshold in enumerate(thresholds):
        target_phase = i + 2          # phase indices: 2, 3, ...
        if hp_pct <= threshold and target_phase not in triggered:
            triggered.add(target_phase)
            enemy['current_phase'] = target_phase

            dialog_key = f'phase{target_phase}'
            dialog = enemy.get('dialog', {}).get(dialog_key, [])
            if isinstance(dialog, str):
                dialog = [dialog]

            # Stat multipliers — phase 2 moderate, phase 3 aggressive
            if target_phase == 2:
                atk_mult = 1.35
                def_mult = 1.20
                spd_mult = 1.10
                heal     = 0
            elif target_phase == 3:
                atk_mult = 1.60
                def_mult = 1.10
                spd_mult = 1.25
                heal     = int(max_hp * 0.08)   # restore 8% max HP
            else:
                atk_mult = 1.20
                def_mult = 1.10
                spd_mult = 1.05
                heal     = 0

            # Apply to live enemy dict
            enemy['attack']  = int(enemy.get('attack',  10) * atk_mult)
            enemy['defense'] = int(enemy.get('defense',  5) * def_mult)
            enemy['speed']   = int(enemy.get('speed',   10) * spd_mult)
            if heal > 0:
                enemy['hp'] = min(max_hp, enemy['hp'] + heal)

            return {
                'new_phase': target_phase,
                'dialog':    dialog,
                'atk_mult':  atk_mult,
                'def_mult':  def_mult,
                'spd_mult':  spd_mult,
                'heal':      heal,
            }

    return None


def get_enemy_dialog_lines(enemy_id, dialog_type='encounter'):
    """Return enemy dialog lines for encounter, phase, or defeat."""
    enemy = ENEMIES.get(enemy_id) or BOSSES.get(enemy_id)
    if not enemy:
        return []

    dialogs = enemy.get('dialog', {})
    if not isinstance(dialogs, dict):
        return []

    dialog_type = (dialog_type or 'encounter').lower().strip()
    if dialog_type == 'mid_fight':
        if dialogs.get('phase2'):
            dialog_type = 'phase2'
        elif dialogs.get('phase3'):
            dialog_type = 'phase3'
        else:
            dialog_type = 'encounter'

    lines = dialogs.get(dialog_type)
    if isinstance(lines, str):
        lines = [lines]
    if not lines and dialog_type == 'encounter':
        for fallback_key in ('phase2', 'phase3', 'defeat'):
            alt = dialogs.get(fallback_key)
            if isinstance(alt, str):
                lines = [alt]
                break
            if isinstance(alt, list) and alt:
                lines = alt
                break

    return lines if isinstance(lines, list) else []


# Secret NPC Candala
CANDALA_NPC = {
    "id": "candala",
    "name": "Candala",
    "title": "The Witness in the Shadows",
    "intro": [
        "Candala: '...Saya sudah menunggu seseorang yang mau mendengar.'",
        "Candala: 'Saya tahu segalanya tentang tempat ini. Saya pernah bekerja di sini.'",
        "Candala: 'Telepon itu... kamu menemukannya. Berarti kamu sudah lihat.'",
        "Candala: 'Nama-nama dalam kontak itu... simpan baik-baik. Dunia perlu tahu.'",
    ],
    "secret_dialog": [
        "Candala: 'Ada ruangan yang tidak ada di peta resmi. Basement sub-level 2.'",
        "Candala: 'Di sana tersimpan semua rekaman asli. Jangan dibiarkan hancur.'",
        "Candala: 'Satu lagi... jika kamu bertemu seseorang bernama Maxwell di luar...'",
        "Candala: '...beritahu dia bahwa Candala masih ingat segalanya.'",
        "Candala: 'Sekarang pergi. Sebelum dia kembali.'",
        "*Candala menghilang ke sudut gelap. Hanya bayangan yang tersisa.*",
    ],
    "reward_flag": "candala_secret_obtained",
    "reward_item": "Rekaman Candala",
}
