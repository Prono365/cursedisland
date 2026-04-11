# State game: stats, quest, save/load

import os
import json
import shutil
import hashlib
import base64
from datetime import datetime
from .constants import (
    BASE_XP_TO_LEVEL,
    LEVEL_UP_HP_GAIN,
    LEVEL_UP_ATTACK_GAIN,
    LEVEL_UP_DEFENSE_GAIN,
    LEVEL_UP_SPEED_GAIN,
    LEVEL_UP_ENERGY_GAIN,
    XP_SCALE_FACTOR,
    GAME_VERSION,
    QUEST_ITEM_NAMES,
)

# Data Sync
_SET_FIELDS  = ('visited_locations', 'npcs_recruited', 'card_dialogs_seen')
_SKIP_FIELDS = ('start_time',)

# 5-slot save files under saves/ (slot 0→data.txt … slot 4→data4.txt)
_SAVE_DIR = "saves"
SLOT_FILES = {
    0: os.path.join(_SAVE_DIR, "data.txt"),
    1: os.path.join(_SAVE_DIR, "data1.txt"),
    2: os.path.join(_SAVE_DIR, "data2.txt"),
    3: os.path.join(_SAVE_DIR, "data3.txt"),
    4: os.path.join(_SAVE_DIR, "data4.txt"),
}

class GameState:

    def __init__(self):
        self.player_name = ""
        self.player_character = ""
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = BASE_XP_TO_LEVEL

        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 10
        self.speed = 10

        # Per-character level-up gains — diset saat karakter dipilih
        # Default = nilai dari constants.py (fallback aman)
        self.level_up_gains = {
            'hp':     LEVEL_UP_HP_GAIN,
            'attack': LEVEL_UP_ATTACK_GAIN,
            'defense':LEVEL_UP_DEFENSE_GAIN,
            'speed':  LEVEL_UP_SPEED_GAIN,
            'energy': LEVEL_UP_ENERGY_GAIN,
        }

        self.energy = 30
        self.max_energy = 30
        self.energy_regen_rate = 5

        self.inventory = []
        self.key_items = []
        self.quest_items = []

        self.current_location = "island"
        self.visited_locations = set()
        self.defeated_enemies = []
        self.bosses_defeated = 0
        self.npcs_recruited = set()

        self.story_flags = {
            'current_chapter': 1,
            'prologue_complete': False,
            'tutorial_shown': False,
        }
        self.discovered_secrets = []
        self.active_quests = []
        self.completed_quests = []
        
        # Cache untuk quest data dari NPC_SIDEQUEST_DATA (untuk konsistensi save/load)
        # Format: {npc_id: {quest_metadata}}
        # Ini mencegah inkonsistensi jika NPC_SIDEQUEST_DATA berubah di tengah game
        self.npc_quest_cache = {}

        self.dollars = 0          # Mata uang Dollar, didapat dari mengalahkan musuh

        self.battles_won = 0
        self.battles_fled = 0
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        self.perfect_victories = 0
        self.combo_max = 0

        self.candala_encountered = False
        self.balatro_joker_met = False
        self.phone_call_found = False
        self.easter_eggs_found = []

        self.card_dialogs_seen = set()
        self.evidence_collected = []

        self.start_time = datetime.now()
        self.total_playtime_seconds = 0
        self.save_version = GAME_VERSION
        self.last_save = None
        self.game_completed = False
        self.current_slot = 0  # Public: active save slot (0–4)
        
        # Game settings - saved with game state
        self.settings = {
            'dialog_speed': 0.03,
            'combat_difficulty': 1.2,
            'auto_save': False,
            'show_tutorial': True
        }

        self.checkpoint_data = {}
        self.boss_retry_count = 0

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            leveled_up = True

            # Gunakan gains per-karakter — tiap karakter punya scaling unik
            gains = self.level_up_gains
            hp_gain     = gains.get('hp',      LEVEL_UP_HP_GAIN)
            atk_gain    = gains.get('attack',  LEVEL_UP_ATTACK_GAIN)
            def_gain    = gains.get('defense', LEVEL_UP_DEFENSE_GAIN)
            spd_gain    = gains.get('speed',   LEVEL_UP_SPEED_GAIN)
            energy_gain = gains.get('energy',  LEVEL_UP_ENERGY_GAIN)

            self.max_hp  += hp_gain
            self.hp       = self.max_hp   # restore full HP on level up
            self.attack  += atk_gain
            self.defense += def_gain
            self.speed   += spd_gain
            self.max_energy += energy_gain
            self.energy = min(self.energy + energy_gain, self.max_energy)
            self.xp_to_next_level = int(self.xp_to_next_level * XP_SCALE_FACTOR)
        return leveled_up

    def apply_character_level_gains(self, char_id):
        
        try:
            from .characters import CHARACTER_LEVEL_GAINS
            gains = CHARACTER_LEVEL_GAINS.get(char_id)
            if gains:
                self.level_up_gains = {
                    'hp':      gains.get('hp',      LEVEL_UP_HP_GAIN),
                    'attack':  gains.get('attack',  LEVEL_UP_ATTACK_GAIN),
                    'defense': gains.get('defense', LEVEL_UP_DEFENSE_GAIN),
                    'speed':   gains.get('speed',   LEVEL_UP_SPEED_GAIN),
                    'energy':  gains.get('energy',  LEVEL_UP_ENERGY_GAIN),
                }
        except Exception:
            pass  # Fallback ke default constants jika import gagal

    def regen_energy(self, amount=None):
        """Regenerasi energy — dipanggil tiap langkah eksplorasi."""
        gain = amount if amount is not None else self.energy_regen_rate
        self.energy = min(self.energy + gain, self.max_energy)

    def use_energy(self, cost):
        """Kurangi energy untuk skill. Kembalikan True jika berhasil."""
        if self.energy >= cost:
            self.energy -= cost
            return True
        return False

    def add_quest_item(self, item_name):
        if item_name not in self.quest_items:
            self.quest_items.append(item_name)
        while self.inventory.count(item_name) > 1:
            self.inventory.remove(item_name)
        if item_name in self.inventory:
            self.inventory.remove(item_name)

    def add_item(self, item_name):
        if item_name in QUEST_ITEM_NAMES:
            self.add_quest_item(item_name)
        else:
            self.inventory.append(item_name)

    def remove_item(self, item_name):
        if item_name in self.quest_items:
            self.quest_items.remove(item_name)
            return True
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def add_quest(self, quest_id, title, objective, targets=None, location=None, quest_type="main"):
        """Tambahkan quest baru ke daftar aktif."""
        for q in self.active_quests:
            if q.get("id") == quest_id:
                return
        # Jangan tambahkan quest yang sudah selesai (mencegah re-add setelah complete)
        for q in self.completed_quests:
            if q.get("id") == quest_id:
                return
        self.active_quests.append({
            "id":        quest_id,
            "title":     title,
            "objective": objective,
            "targets":   targets or [],
            "location":  location or "",
            "progress":  0,
            "total":     len(targets) if targets else 1,
            "quest_type": quest_type,  # "main" or "side"
        })

    def complete_quest(self, quest_id):
        """Tandai quest sebagai selesai."""
        for q in list(self.active_quests):
            if q.get("id") == quest_id:
                self.active_quests.remove(q)
                q["completed"] = True
                self.completed_quests.append(q)
                return True
        return False

    def update_quest_progress(self, quest_id, amount=1):
        """Update progress sebuah quest."""
        for q in self.active_quests:
            if q.get("id") == quest_id:
                q["progress"] = min(q.get("progress", 0) + amount, q.get("total", 1))
                return q["progress"] >= q["total"]
        return False

    def get_primary_quest(self):
        """Kembalikan quest aktif paling utama (pertama di list)."""
        if self.active_quests:
            return self.active_quests[0]
        return None

    def get_chapter_objective(self):
        """Kembalikan kalimat objektif chapter sesuai karakter dan quest aktif."""
        chapter = self.story_flags.get("current_chapter", 1)
        try:
            chapter = int(chapter)
        except (ValueError, TypeError):
            chapter = 1

        try:
            from .characters import CHARACTER_MAIN_QUESTS, CHAPTER_QUEST_TEMPLATES, CHAPTER_OBJECTIVES_BY_CHAR
            # Priority 1: Character-specific short objective for HUD
            char_obj = CHAPTER_OBJECTIVES_BY_CHAR.get(self.player_character, {})
            if chapter in char_obj:
                return char_obj[chapter]
            # Priority 2: Character-specific quest title
            char_quests = CHARACTER_MAIN_QUESTS.get(self.player_character, {})
            quest_data  = char_quests.get(chapter)
            if quest_data:
                return quest_data['title']
            template = CHAPTER_QUEST_TEMPLATES.get(chapter)
            if template:
                return template['title']
        except Exception:
            pass

        try:
            from .characters import CHAPTER_OBJECTIVES_BY_CHAR, CHAPTER_OBJECTIVES
            char_obj = CHAPTER_OBJECTIVES_BY_CHAR.get(self.player_character, {})
            if chapter in char_obj:
                return char_obj[chapter]
            return CHAPTER_OBJECTIVES.get(chapter, "Survive di Cursed Island!")
        except Exception:
            pass

        generic = {
            1: "Selesaikan misi awal — kabur dari lokasi starting, kalahkan Boss Ch.1!",
            2: "Pergi ke area boss karaktermu → kalahkan Boss Ch.2 unik (lokasi beda tiap karakter)",
            3: "Temui NPC di ISLAND → selesaikan 2 sidequest → Chapter 4 terbuka",
            4: "Pergi ke PUSAT KONTROL (COMMAND CENTER) → kalahkan Ghislaine Maxwell (Boss Ch.4)",
            5: "Selesaikan 4 sidequest NPC + dapat USB Evidence Drive dari Vio di LABORATORIUM",
            6: "Pergi ke MANSION EAST (sudut kanan bawah ISLAND) → kalahkan Epstein (Final Boss)",
        }
        return generic.get(chapter, "Survive di Cursed Island!")

    def get_sidequest_progress(self):
        """Kembalikan jumlah sidequest NPC yang sudah selesai dan reward sudah diterima."""
        npc_ids = ['haikaru', 'aolinh', 'arganta', 'ignatius', 'vio']
        reward_flags = {
            'haikaru':  'haikaru_sidequest_done',
            'aolinh':   'aolinh_sidequest_done',
            'arganta':  'arganta_sidequest_done',
            'ignatius': 'ignatius_sidequest_done',
            'vio':      'vio_sidequest_done',
        }
        count = 0
        for npc_id in npc_ids:
            flag = reward_flags.get(npc_id, f"{npc_id}_sidequest_done")
            if self.story_flags.get(flag):
                count += 1
        return count

    def get_sidequest_ready_count(self):
        """Kembalikan jumlah sidequest yang syaratnya sudah terpenuhi tapi reward belum diambil."""
        npc_ids = ['haikaru', 'aolinh', 'arganta', 'ignatius', 'vio']
        reward_flags = {
            'haikaru':  'haikaru_sidequest_done',
            'aolinh':   'aolinh_sidequest_done',
            'arganta':  'arganta_sidequest_done',
            'ignatius': 'ignatius_sidequest_done',
            'vio':      'vio_sidequest_done',
        }
        count = 0
        try:
            from .npc_interactions import is_sidequest_complete
            for npc_id in npc_ids:
                reward_flag = reward_flags.get(npc_id, f"{npc_id}_sidequest_done")
                already_rewarded = self.story_flags.get(reward_flag, False)
                if not already_rewarded and is_sidequest_complete(npc_id, self):
                    count += 1
        except Exception:
            pass
        return count

    @property
    def main_quest_status(self):
        """Property — kembalikan string status quest utama untuk HUD tracker."""
        chapter = self.story_flags.get('current_chapter', 1)
        try:
            chapter = int(chapter)
        except (ValueError, TypeError):
            chapter = 1
        obj = self.get_chapter_objective()
        return f"Ch.{chapter} — {obj}"

    def reconcile_state(self):
        """Sinkronkan state game: pastikan data konsisten setiap render frame."""
        self.hp = max(0, min(self.hp, self.max_hp))
        self.energy = max(0, min(self.energy, self.max_energy))
        if not isinstance(self.story_flags, dict):
            self.story_flags = {"current_chapter": 1}
        if "current_chapter" not in self.story_flags:
            self.story_flags["current_chapter"] = 1
        if not isinstance(self.inventory, list):
            self.inventory = []
        if not isinstance(self.quest_items, list):
            self.quest_items = []
        if not isinstance(self.visited_locations, set):
            self.visited_locations = set(self.visited_locations) if self.visited_locations else set()
        if not isinstance(self.npcs_recruited, set):
            self.npcs_recruited = set(self.npcs_recruited) if self.npcs_recruited else set()

    def update_playtime(self):
        try:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.total_playtime_seconds += int(elapsed)
            self.start_time = datetime.now()
        except Exception:
            pass

    def get_playtime_string(self):
        hours   = self.total_playtime_seconds // 3600
        minutes = (self.total_playtime_seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def save_checkpoint(self, location=None):
        
        import copy
        self.checkpoint_data = {
            'location':     location or self.current_location,
            'hp':           self.hp,
            'max_hp':       self.max_hp,
            'energy':       self.energy,
            'max_energy':   self.max_energy,
            'inventory':    list(self.inventory),
            'key_items':    list(self.key_items),
            'quest_items':  list(self.quest_items),
            'story_flags':  copy.deepcopy(self.story_flags),
            'dollars':      self.dollars,
            'xp':           self.xp,
            'level':        self.level,
        }
        self.boss_retry_count = 0   # reset retry counter untuk boss baru

    def load_checkpoint(self):
        
        import copy
        if not self.checkpoint_data:
            self.hp = max(1, int(self.max_hp * 0.50))
            return False

        data = self.checkpoint_data
        self.current_location  = data.get('location', self.current_location)
        self.hp                = max(1, data.get('hp', self.max_hp))
        self.max_hp            = data.get('max_hp', self.max_hp)
        self.energy            = data.get('energy', self.max_energy)
        self.max_energy        = data.get('max_energy', self.max_energy)
        self.inventory         = list(data.get('inventory', self.inventory))
        self.key_items         = list(data.get('key_items', self.key_items))
        self.quest_items       = list(data.get('quest_items', self.quest_items))
        self.story_flags       = copy.deepcopy(data.get('story_flags', self.story_flags))
        self.dollars           = data.get('dollars', self.dollars)
        self.xp                = data.get('xp', self.xp)
        return True

    def get_slot_filename(self):
        # Public: resolve active slot → filename
        return SLOT_FILES.get(self.current_slot, os.path.join(_SAVE_DIR, "data.txt"))

    def save_to_file(self, filename=None):
        """Save game state dengan sistem anti-tamper yang sophisticated:"""
        # Data Sync: resolve filename from active slot if not explicit
        if filename is None:
            filename = self.get_slot_filename()
        save_dir = os.path.dirname(filename)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        backup_name = f"{filename}.bak"
        try:
            # Ensure playtime and last_save are up-to-date in the serialized data
            try:
                self.update_playtime()
            except Exception:
                pass
            try:
                self.last_save = datetime.now()
            except Exception:
                pass
            if os.path.exists(filename):
                shutil.copy2(filename, backup_name)

            # Prepare save data
            save_data = {}
            for key, val in self.__dict__.items():
                if key in _SKIP_FIELDS:
                    continue
                if key in _SET_FIELDS:
                    save_data[key] = list(val)
                else:
                    save_data[key] = val

            # Calculate checksum BEFORE adding metadata
            # Must use sort_keys=True and default=str for consistent hashing
            json_for_checksum = json.dumps(save_data, sort_keys=True, default=str)
            checksum = hashlib.sha256(json_for_checksum.encode()).hexdigest()
            
            # Add checksum dan version ke data
            save_data['_checksum'] = checksum
            save_data['_version'] = GAME_VERSION
            save_data['_timestamp'] = datetime.now().isoformat()
            
            # Validate JSON before writing (use consistent formatting)
            # IMPORTANT: Must use same format as verification for checksum to match
            json_str = json.dumps(save_data, sort_keys=True, default=str)
            json.loads(json_str)  # Validate by re-parsing

            # Encode ke Base64 untuk obscurity
            encoded = base64.b64encode(json_str.encode()).decode()
            
            # Add magic header untuk prevent direct editing
            magic_header = f"CURSED_ISLAND_SAVE_v{GAME_VERSION}\n"
            final_content = magic_header + encoded

            # Atomic write: write to temp file, then rename
            temp_name = f"{filename}.tmp"
            with open(temp_name, "w", encoding="utf-8") as f:
                f.write(final_content)
            
            # Rename temp to actual (atomic operation)
            if os.path.exists(filename):
                os.remove(filename)
            os.rename(temp_name, filename)
            
            self.last_save = datetime.now()
            return True, f"Game saved successfully to {filename}"
            
        except Exception as e:
            # Try to restore from backup if save failed
            if os.path.exists(backup_name):
                try:
                    shutil.copy2(backup_name, filename)
                except Exception:
                    pass
            return False, f"Save failed: {e}. Data backup preserved."

    def _check_tampering(self, save_data):
        
        if '_checksum' not in save_data:
            return False, "Missing checksum - file corrupted or invalid"
        
        stored_checksum = save_data['_checksum']
        
        # Recalculate checksum (exclude all metadata fields that were added after original hash)
        # These fields are: _checksum, _version, _timestamp
        metadata_fields = {'_checksum', '_version', '_timestamp'}
        data_for_verify = {k: v for k, v in save_data.items() if k not in metadata_fields}
        json_for_verify = json.dumps(data_for_verify, sort_keys=True, default=str)
        calculated_checksum = hashlib.sha256(json_for_verify.encode()).hexdigest()
        
        if stored_checksum != calculated_checksum:
            return False, "Checksum mismatch - file has been tampered with!"
        
        return True, "OK"

    def _show_vio_tampering_message(self):
        
        try:
            from .sprites import Warna
            import time
            
            print(f"\n{Warna.MERAH + Warna.TERANG}═══════════════════════════════════════════════════════════{Warna.RESET}")
            print(f"{Warna.MERAH + Warna.TERANG}                    ⚠️  FILE INTEGRITY FAILED ⚠️{Warna.RESET}")
            print(f"{Warna.MERAH + Warna.TERANG}═══════════════════════════════════════════════════════════{Warna.RESET}\n")
            
            dialogs = [
                "Vio: Nice try, tapi enkripsi gue nggak selemah itu.",
                "Vio: Gue detect perubahan di save file lo...",
                "Vio: Kira-kira lo nyoba ngedit attack: 9999?",
                "Vio: Atau dollars: 1000000?",
                "",
                "Vio: Well... terlalu buruk.",
                "Vio: File lo gue hapus sekarang.",
                "Vio: Balik lagi ke tutorial, friend. Lebih hati-hati kali ini.",
            ]
            
            for dialog in dialogs:
                print(f"  {Warna.CYAN + Warna.TERANG}{dialog}{Warna.RESET}")
                time.sleep(0.8)
            
            print(f"\n{Warna.MERAH}Save file lo udah dihapus. Enjoy!{Warna.RESET}\n")
            time.sleep(2)
            
        except ImportError:
            # Fallback jika Warna tidak tersedia
            print("\n⚠️  FILE TAMPERING DETECTED!")
            print("Save file has been modified and is invalid.")
            print("File will be deleted.\n")

    def load_from_file(self, filename=None):
        # Data Sync: resolve filename from active slot if not explicit
        if filename is None:
            filename = self.get_slot_filename()
        try:
            if not os.path.exists(filename):
                backup_name = f"{filename}.bak"
                if os.path.exists(backup_name):
                    try:
                        shutil.copy2(backup_name, filename)
                    except Exception:
                        pass
                    return False, f"Save file not found. Restored from backup."
                return False, f"Save file {filename} not found."

            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()

                # Validate magic header - handle both Windows (\r\n) and Unix (\n) line endings
                # Strip whitespace first to remove any carriage returns or extra newlines
                lines = content.strip().splitlines()
                if not lines or not lines[0].startswith('CURSED_ISLAND_SAVE_v'):
                    raise ValueError("Invalid file header - not a valid save file")
                
                if len(lines) < 2:
                    raise ValueError("File corrupted - missing save data")
                
                # Decode Base64 - strip any remaining whitespace
                encoded_data = lines[1].strip()
                json_str = base64.b64decode(encoded_data).decode()
                save_data = json.loads(json_str)

                # Check tampering
                is_valid, error_msg = self._check_tampering(save_data)
                if not is_valid:
                    # Tampering detected!
                    print(f"\n{error_msg}")
                    self._show_vio_tampering_message()
                    
                    # Delete corrupted file
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
                    
                    # Try to restore from backup
                    backup_name = f"{filename}.bak"
                    if os.path.exists(backup_name):
                        try:
                            shutil.copy2(backup_name, filename)
                            return False, "Save file was corrupted. Restored from backup."
                        except Exception:
                            pass
                    
                    return False, "Save file was tampered with and deleted. Please restart from beginning."

                # Private: convert set-fields first
                for field in _SET_FIELDS:
                    if field in save_data:
                        setattr(self, field, set(save_data[field]))

                # Private: load remaining fields, skip SET_FIELDS and metadata
                _skip_on_load = set(_SET_FIELDS) | set(_SKIP_FIELDS)
                for key, value in save_data.items():
                    if not key.startswith('_') and key not in _skip_on_load:
                        try:
                            setattr(self, key, value)
                        except Exception:
                            pass

                self.last_save = datetime.now()

                self.checkpoint_data = {}
                self.boss_retry_count = 0

                return True, "Game loaded successfully"

            except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError, ValueError) as json_err:
                # JSON atau Base64 decode error - likely tampering or corruption
                print(f"\nFile corruption detected: {json_err}")
                self._show_vio_tampering_message()
                
                # Delete corrupted file
                try:
                    os.remove(filename)
                except Exception:
                    pass
                
                # Try backup
                backup_name = f"{filename}.bak"
                if os.path.exists(backup_name):
                    try:
                        shutil.copy2(backup_name, filename)
                        return False, "Save file corrupted. Restored from backup."
                    except Exception:
                        pass
                
                return False, "Save file corrupted and cannot be recovered. Restart game."

        except Exception as e:
            return False, f"Failed to load: {e}"

    def get_save_summary(self, filename=None):
        # Public: extract save info without full load
        if filename is None:
            filename = self.get_slot_filename()
        try:
            if not os.path.exists(filename):
                return None

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Validate dan extract dari format baru (magic header + base64)
            # Handle both Windows (\r\n) and Unix (\n) line endings
            lines = content.strip().splitlines()
            if not lines or not lines[0].startswith('CURSED_ISLAND_SAVE_v'):
                return None  # Format lama atau invalid
            
            if len(lines) < 2:
                return None  # File corrupt
            
            # Decode Base64 - strip whitespace
            try:
                json_str = base64.b64decode(lines[1].strip()).decode()
                data = json.loads(json_str)
            except Exception:
                return None  # Decode failed - file is corrupted

            secs = data.get('total_playtime_seconds', 0)
            hrs  = secs // 3600
            mins = (secs % 3600) // 60

            return {
                "version":    data.get('save_version', '?'),
                "date":       data.get('last_save', '?'),
                "playtime":   f"{hrs}h {mins}m",
                "player":     data.get('player_name', 'Unknown'),
                "character":  data.get('player_character', '?'),
                "level":      data.get('level', 1),
                "location":   data.get('current_location', '?'),
                "bosses":     data.get('bosses_defeated', 0),
            }

        except Exception:
            return None
