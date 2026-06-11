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
| 1 | Pindai jaringan WiFi, dapatkan nilai RSSI | `pywifiscan` / `netsh` / `iwlist` |
| 2 | Catat posisi (X,Y) dan kekuatan sinyal saat berjalan | Input manual / file CSV/JSON |
| 3 | Interpolasi titik yang tidak terukur menggunakan IDW + KNN | NumPy, SciPy (cKDTree) |
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
- **power** (default: 2) — Mengontrol seberapa cepat pengaruh sinyal berkurang dengan jarak
- **k** (default: 5) — Jumlah tetangga terdekat yang digunakan (KNN)
- **smoothing** (default: 1e-12) — Faktor smoothing untuk menghindari division by zero

---

## 🛠️ Teknologi yang Digunakan

| Kategori | Teknologi |
|----------|-----------|
| Bahasa | Python 3.8+ |
| Pemindaian WiFi | pywifiscan, netsh (Windows), iwlist (Linux), airport (macOS) |
| Komputasi Numerik | numpy, scipy (cKDTree) |
| Visualisasi 2D | matplotlib, seaborn |
| Visualisasi 3D | plotly (interaktif), matplotlib (static) |
| Basis Data | sqlite3 (SQLite) |
| CLI Framework | argparse |
| Format Data | CSV, JSON |

---

## 📁 Struktur Proyek

```
spectralens/
│
├── main.py                    # Titik masuk utama (CLI)
├── requirements.txt           # Dependencies
├── checklist.md               # Progress checklist
│
├── scanner/                   # Akuisisi data WiFi
│   ├── __init__.py
│   ├── wifi_scanner.py        # Membaca RSSI dari adapter WiFi
│   └── data_collector.py      # Merekam posisi + kekuatan sinyal
│
├── interpolation/             # Interpolasi spasial
│   ├── __init__.py
│   ├── idw.py                 # Algoritma IDW dengan KNN optimization
│   └── grid_builder.py        # Membuat grid untuk visualisasi
│
├── visualization/             # Pembuatan output visual
│   ├── __init__.py
│   ├── heatmap_2d.py          # Peta panas 2D (contourf + scatter)
│   └── surface_3d.py          # Plot permukaan 3D (static + interactive)
│
├── storage/                   # Penyimpanan data
│   ├── __init__.py
│   └── database.py            # Operasi SQLite (sessions, data_points)
│
├── utils/                     # Fungsi bantuan
│   ├── __init__.py
│   └── geometry.py            # Perhitungan jarak, bounding box, RSSI conversion
│
└── data/                      # Data sample
    └── sample_measurements.csv # Contoh data pengukuran untuk testing
```

---

## 🚀 Cara Memulai (Instalasi)

### Prasyarat

- Python 3.8 atau lebih baru
- WiFi adapter (bawaan laptop/PC sudah cukup)
- Hak akses Administrator/Root (untuk pemindaian WiFi di beberapa OS)

### Langkah-langkah

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
python main.py --help
```

---

## 📝 Panduan Penggunaan CLI

### Melihat Bantuan

```bash
python main.py --help
python main.py scan --help
python main.py visualize --help
```

### Memindai Jaringan WiFi

```bash
# Pindai semua jaringan WiFi di sekitar
python main.py scan

# Pindai dengan SSID spesifik
python main.py scan --ssid MyWiFi

# Simpan hasil scan ke file
python main.py scan --output scan_results.csv
```

### Visualisasi Data dari File CSV

```bash
# Generate heatmap 2D dari data sample
python main.py visualize data/sample_measurements.csv --type heatmap

# Generate 3D surface
python main.py visualize data/sample_measurements.csv --type surface

# Generate heatmap dengan resolusi grid lebih tinggi
python main.py visualize data/sample_measurements.csv --type heatmap --resolution 100

# Generate dengan parameter IDW yang berbeda
python main.py visualize data/sample_measurements.csv --type heatmap --power 3 --k 8

# Generate semua jenis visualisasi sekaligus
python main.py visualize data/sample_measurements.csv --type all

# Tentukan nama file output
python main.py visualize data/sample_measurements.csv --type heatmap --output my_heatmap.png
```

### Mengelola Database

```bash
# Lihat statistik database
python main.py db-stats
```

### Contoh Sederhana

```bash
# Langsung generate heatmap dari sample data
python main.py visualize data/sample_measurements.csv --type all
```

Output akan tersimpan di folder `output/`:
- `output/heatmap_15points.png` — Peta panas 2D
- `output/surface_3d_50x50.png` — Permukaan 3D static
- `output/surface_3d_interactive_50x50.html` — Permukaan 3D interaktif

---

## 📊 Contoh Output

### Peta Panas 2D

Peta panas menunjukkan distribusi kekuatan sinyal WiFi di suatu area:
- **Merah** = Sinyal kuat (RSSI tinggi, mendekati -30 dBm)
- **Biru** = Sinyal lemah (RSSI rendah, mendekati -100 dBm)
- **Titik hitam** = Lokasi pengukuran dengan nilai RSSI
- **Garis kontur** = Batas area dengan kekuatan sinyal yang sama

### Permukaan 3D

Visualisasi 3D menunjukkan "medan frekuensi":
- **Puncak** = Area dengan sinyal terbaik
- **Lembah** = Area dengan sinyal terburuk
- Dapat diputar dan diperbesar (versi interaktif Plotly HTML)

---

## 🗺️ Peta Jalan (Roadmap)

| Fase | Status |
|------|--------|
| Konsep & Ideasi | ✅ Selesai |
| Desain Algoritma IDW | ✅ Selesai |
| Implementasi Python (dasar) | ✅ Selesai |
| Implementasi Python (lengkap) | ✅ Selesai |
| Testing & Dokumentasi | 🔄 Sedang Berjalan |
| Porting ke Flutter (Mobile) | 📋 Direncanakan |
| Mode Rekam Jalan Langsung | 📋 Direncanakan |
| Pengajuan Paten / Hak Cipta | 📋 Direncanakan |

---

## 🤝 Kontribusi

Proyek ini saat ini sedang dalam pengembangan awal oleh pencipta. Untuk pertanyaan atau kolaborasi, silakan hubungi:

**Asmaul Asni Subegi, S.Kom** – sabayonx@gmail.com

---

## 📜 Lisensi

Hak Cipta (c) 2026 Asmaul Asni Subegi, S.Kom

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file LICENSE untuk detail lengkap.

---

## 📧 Kontak

| Platform | Link / Info |
|----------|-------------|
| Email | sabayonx@gmail.com |
| GitHub | github.com/xdr7 |
