# SpectraLens

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-active-brightgreen)

> **Mewujudkan Frekuensi WiFi Menjadi Bentuk Visual**  
> *"Making the invisible visible, one frequency at a time."*

---

## 👤 Creator & Owner

**Asmaul Asni Subegi, S.Kom**

- **Email**: sabayonx@gmail.com  
- **GitHub**: [xdr7](https://github.com/xdr7)  
- **Role**: Creator, Lead Developer, Concept Owner  
- **Project Start**: June 2026  
- **Repository**: [github.com/xdr7/SpectraLens](https://github.com/xdr7/SpectraLens)

---

## 🎯 Ringkasan Proyek

**SpectraLens** adalah aplikasi inovatif yang mengubah gelombang frekuensi WiFi (2.4 GHz / 5 GHz) menjadi representasi visual yang dapat dipahami. Dengan menangkap data kekuatan sinyal (RSSI) dari **WiFi adapter standar laptop/PC** dan menerapkan algoritma interpolasi spasial, SpectraLens menghasilkan:

| Output | Deskripsi |
|--------|-----------|
| 🗺️ **Peta Panas 2D** | Distribusi kekuatan sinyal di suatu ruangan (merah = kuat, biru = lemah) |
| 🏔️ **Model Permukaan 3D** | "Medan frekuensi" yang menunjukkan area dengan sinyal terbaik dan terburuk |
| 📊 **Peta Spasial** | Analisis ruangan untuk penempatan router yang optimal |

---

## 💡 Akar Ide: Pertanyaan Mendasar

Proyek ini lahir dari sebuah pertanyaan sederhana namun mendalam:

> *"Apakah mungkin frekuensi dipetakan ke dalam bentuk gambar? Karena frekuensi itu gelombang, dan jangkauannya bisa diukur jaraknya, bisakah ia dibentuk menjadi wujud?"*

**Jawabannya:** **YA.** Frekuensi WiFi dapat diubah menjadi:
- Peta panas 2D
- Model permukaan 3D
- Peta spasial frekuensi

Semua ini dapat dicapai hanya dengan **WiFi adapter standar** dan **Python** — tanpa perlu perangkat keras khusus.

---

## 🔬 Bagaimana Cara Kerjanya?

```

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Pemindaian  │     │  Data RSSI  │     │ Interpolasi │     │  Visualisasi│
│    WiFi     │ ──► │ + Posisi    │ ──► │    IDW      │ ──► │   2D / 3D   │
│ (pywifiscan)│     │ (x,y)       │     │ + KNN       │     │ (Plotly,    │
└─────────────┘     └─────────────┘     └─────────────┘     │ Matplotlib) │
└─────────────┘

```

| Langkah | Deskripsi | Teknologi |
|---------|-----------|------------|
| 1 | Pindai jaringan WiFi, dapatkan nilai RSSI | `pywifiscan` |
| 2 | Catat posisi (X,Y) dan kekuatan sinyal saat berjalan | Input manual / file |
| 3 | Interpolasi titik yang tidak terukur menggunakan IDW + KNN | NumPy, SciPy |
| 4 | Visualisasikan hasilnya sebagai peta panas atau permukaan 3D | Matplotlib, Plotly |

---

## 📊 Algoritma Inti: Inverse Distance Weighting (IDW)

Rumus interpolasi yang digunakan:

```python
# Rata-rata tertimbang berdasarkan jarak
weight = 1 / (distance ^ power)   # Semakin dekat, semakin besar bobotnya
value = Σ(weight_i × rssi_i) / Σ(weight_i)
```

Parameter yang dapat disesuaikan:

· power = 2 — Mengontrol seberapa cepat pengaruh sinyal berkurang dengan jarak
· k = 5 — Jumlah tetangga terdekat yang digunakan (KNN)

---

🛠️ Teknologi yang Digunakan

Kategori Teknologi
Bahasa Python 3.8+
Pemindaian WiFi pywifiscan / miniwifi
Komputasi Numerik numpy, scipy
Visualisasi 2D matplotlib, seaborn
Visualisasi 3D plotly, pyvista
Basis Data sqlite3
Geometri scipy.spatial.cKDTree

---

📁 Struktur Proyek (Rencana)

```
spectralens/
│
├── main.py                    # Titik masuk utama
├── requirements.txt           # Dependencies
│
├── scanner/                   # Akuisisi data WiFi
│   ├── wifi_scanner.py        # Membaca RSSI dari adapter WiFi
│   └── data_collector.py      # Merekam posisi + kekuatan sinyal
│
├── interpolation/             # Interpolasi spasial
│   ├── idw.py                 # Algoritma IDW
│   └── grid_builder.py        # Membuat grid untuk visualisasi
│
├── visualization/             # Pembuatan output visual
│   ├── heatmap_2d.py          # Peta panas 2D
│   └── surface_3d.py          # Plot permukaan 3D
│
├── storage/                   # Penyimpanan data
│   └── database.py            # Operasi SQLite
│
└── utils/                     # Fungsi bantuan
    └── geometry.py            # Perhitungan jarak, koordinat
```

---

🚀 Cara Memulai (Instalasi)

Prasyarat

· Python 3.8 atau lebih baru
· WiFi adapter (bawaan laptop/PC sudah cukup)
· Hak akses Administrator/Root (untuk pemindaian WiFi di beberapa OS)

Langkah-langkah

```bash
# 1. Clone repository
git clone https://github.com/xdr7/SpectraLens.git
cd SpectraLens

# 2. (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate  # Di Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan aplikasi
python main.py
```

---

📝 Panduan Penggunaan (Rencana)

1. Pindai Jaringan WiFi
   Aplikasi akan menampilkan semua jaringan WiFi di sekitar beserta nilai RSSI-nya.
2. Pilih SSID Target
   Masukkan nama WiFi (SSID) yang ingin Anda petakan.
3. Kumpulkan Titik Data
   Berjalanlah di sekitar ruangan sambil merekam posisi (koordinat X,Y dalam meter) dan kekuatan sinyal secara manual.
4. Hasilkan Visualisasi
   · Peta Panas 2D menunjukkan distribusi sinyal
   · Permukaan 3D menunjukkan medan frekuensi
5. Simpan & Ekspor
   Data secara otomatis disimpan ke database SQLite untuk referensi di masa mendatang.

---

📸 Contoh Output (Akan Ditambahkan)

Peta Panas 2D

[Tangkapan layar peta panas akan ditambahkan setelah implementasi]

Permukaan 3D

[Tangkapan layar visualisasi 3D akan ditambahkan setelah implementasi]

---

📋 Daftar Dependency (requirements.txt)

```
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0
pyvista>=0.40.0
pywifiscan>=1.0.0
pandas>=2.0.0
```

---

🗺️ Peta Jalan (Roadmap)

Fase Status
Konsep & Ideasi ✅ Selesai
Desain Algoritma IDW ✅ Selesai
Implementasi Python (dasar) 🔄 Sedang Berjalan
Porting ke Flutter (Mobile) 📋 Direncanakan
Mode Rekam Jalan Langsung 📋 Direncanakan
Pengajuan Paten / Hak Cipta 📋 Direncanakan

---

🤝 Kontribusi

Proyek ini saat ini sedang dalam pengembangan awal oleh pencipta. Untuk pertanyaan atau kolaborasi, silakan hubungi:

Asmaul Asni Subegi, S.Kom – sabayonx@gmail.com

---

📜 Lisensi

Hak Cipta (c) 2026 Asmaul Asni Subegi, S.Kom

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file LICENSE untuk detail lengkap.

---

📧 Kontak

Platform Link / Info
Email sabayonx@gmail.com
GitHub github.com/xdr7