<div align="center">

<img width="1280" alt="CURSED ISLAND ESCAPE" src="https://github.com/user-attachments/assets/b6282a8b-c6b9-4d60-a140-b213a60d1cc4" />

<strong>Sebuah Adventure RPG dengan Sistem Pertarungan Kartu (Big Two) Berbasis Command-Line Interface (CLI)</strong>

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
</div>

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
      <h2>Deskripsi Singkat</h2>
    </summary>
  </ul>
</div>

Cursed Island adalah sebuah permainan petualangan RPG berbasis Command-Line Interface (CLI) yang dibangun menggunakan bahasa pemrograman Python. Pemain berperan sebagai salah satu dari lima karakter unik yang terjebak di sebuah pulau misterius.

Tujuan utama pemain adalah melarikan diri dari pulau terkutuk ini dengan cara mengumpulkan anggota tim, mencari item kunci, memecahkan misteri, dan mengalahkan musuh menggunakan strategi kombinasi kartu poker. Proyek ini merupakan tugas akhir dari kelas X RPL 1 SMKN 2 JAKARTA dan kegabutan para contributornya.

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Fitur Utama</h2>
    </summary>
  </ul>
</div>

- **Sistem Karakter Unik:** 5 karakter pilihan (Vio, Haikaru, Ao Lin, Arganta, Ignatius) dengan latar belakang, stats, dan skill spesifik yang memengaruhi strategi permainan.
- **Mekanisme Combat Kartu:** Sistem pertarungan turn-based menggunakan logika poker (High Card, Pair, Flush, Straight Flush, dll) untuk menentukan kekuatan serangan.
- **Inventory:** Pengelolaan item kunci dan *quest items* untuk memecahkan puzzle lingkungan serta membuka progres chapter.
- **Peta Eksplorasi:** Sistem pergerakan pemain di peta 2D yang dinamis, lengkap dengan kemunculan musuh, NPC interaktif, dan objek tersembunyi.
- **Save/Load System:** Fitur penyimpanan progres yang kini mendukung hingga 5 slot (data.txt hingga data4.txt) dengan sistem proteksi data Base64.
- **Multi-language UI:** Antarmuka yang mendukung karakter UTF-8 untuk visualisasi peta yang kaya warna dan fitur *autofit* yang responsif terhadap ukuran terminal.
- **Boss Retry & Checkpoint:** Mekanisme percobaan ulang hingga 3 kali saat kalah melawan Boss dan sistem *snapshot* status otomatis sebelum pertempuran besar dimulai.
- **Layanan Walkie-Talkie:** Akses menu toko dan interaksi NPC khusus (Bran Edwards) secara praktis melalui tombol pintas **[B]** tanpa harus kembali ke lokasi tertentu.
- **Progresi Chapter:** Alur cerita mendalam yang terbagi dalam 6 Chapter, di mana setiap Chapter memiliki objektif unik dan syarat penyelesaian *sidequest* tertentu.

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Cara Menjalankan Program</h2>
    </summary>
  </ul>
</div>

### Prasyarat (Requirements)
- **Python 3.6 atau versi lebih baru** terinstal di komputer Anda.
- Terminal atau Command Prompt (Windows/Linux/macOS).

### Langkah Instalasi & Menjalankan

1.  **Clone Repository**
    Unduh atau clone repository ini ke komputer lokal Anda.
    ```bash
    git clone https://github.com/Prono365/ludo
    cd ludo
    ```
    *(Jika menggunakan file ZIP, ekstrak file tersebut dan buka foldernya).*

2.  **Struktur repo**
    Kode permainan berada di paket Python `cursed_island/`; data dialog kartu ada di `cursed_island/data/`. File save dibuat otomatis di folder `saves/` (folder ini sudah disertakan di repo; isi file save tidak di-commit). Jika Anda memiliki save lama bernama `data.txt` … `data4.txt` di root project, pindahkan ke `saves/` agar slot load tetap dikenali.

3.  **Jalankan game**
    Dari folder root repository:

    ```bash
    python main.py
    ```

    Atau sebagai modul:

    ```bash
    python -m cursed_island
    ```

    Di Windows Anda juga bisa menjalankan `launcher.bat`.

    *(Jika `python` tidak dikenali, coba `py` atau `python3`.)*

4.  **Mulai Bermain**
    Game akan membersihkan layar terminal dan memulai dengan menu utama. Ikuti petunjuk pada layar untuk memilih karakter dan memulai petualangan.

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Struktur Folder/File</h2>
    </summary>
  </ul>
</div>

Berikut adalah struktur utama repository:

```
├── launcher.bat            # Pintasan Windows ke `py main.py` dari root repo.
├── main.py                 # Titik masuk: memanggil `cursed_island.main`.
├── pyproject.toml          # Metadata proyek (PEP 621) untuk pip / distribusi.
├── LICENSE
├── README.md
├── saves/                  # File save slot (data.txt … data4.txt), di-gitignore.
└── cursed_island/          # Paket permainan.
    ├── __main__.py         # Mendukung `python -m cursed_island`.
    ├── main.py             # Menu utama, loop game, pengaturan runtime.
    ├── settings.py         # Objek pengaturan global (mis. kecepatan dialog).
    ├── characters.py       # Karakter, stats, skill, NPC.
    ├── enemies.py          # Musuh, boss, spawn.
    ├── exploration.py      # Peta (GameMap), pergerakan, eksplorasi.
    ├── combat.py           # Pertarungan kartu / poker hands, damage.
    ├── story.py            # Narasi chapter dan ending.
    ├── npc_interactions.py # Dialog NPC (side quest & story).
    ├── sprites.py          # Warna ANSI & ASCII art UI.
    ├── gamestate.py        # GameState, save/load.
    ├── utils.py            # Utilitas terminal (clear, input, dll.).
    ├── constants.py        # Konstanta global (versi, terminal min, dll.).
    ├── tutorial.py         # Tutorial interaktif.
    └── data/
        └── card_dialogs.json   # Dialog singkat saat combat per kartu.
```

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Anggota Kelompok</h2>
    </summary>
  </ul>
</div>

Proyek ini dikembangkan oleh siswa **SMKN 2 JAKARTA Kelas X RPL 1**:

1.  **Ahmad Haikal Ramadhan**
2.  **Alif Rizky Ramadhan Atmadja**
3.  **M Vallerian Aprilio Gunawan**
4.  **Ignatius Nino Jumantoro**
5.  **Evan Arganta**

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Cara Bermain (Singkat)</h2>
    </summary>
  </ul>
</div>

- **Navigasi:** Gunakan tombol `W`, `A`, `S`, `D` untuk bergerak di peta.
- **Interaksi:** Tekan `I` untuk Inventory,`X` untuk Save.
- **Combat:** Pilih kartu dengan memasukkan nomor indeks (contoh: `0,1,2` untuk memainkan 3 kartu sekaligus).
- **Skill:** Tekan `S` saat bertarung untuk menggunakan kemampuan khusus karakter.
- **Tujuan:** Selesaikan quest utama setiap chapter, rekrut teman, dan kalahkan boss untuk melarikan diri.

#

<div id="user-content-toc">
  <ul style="list-style: none;">
    <summary>
        <h2>Lisensi</h2>
    </summary>
  </ul>
</div>

Proyek ini dibuat sebagai tugas sekolah dan dirilis di bawah ![License](https://img.shields.io/badge/license-MIT-blue).

#

<p align="center">
<strong>Justice for the Victims</strong>
</p>
