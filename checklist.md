# SpectraLens - Implementation Checklist

## Fase 1: Fondasi Proyek ✅
- [x] Buat struktur folder (scanner, interpolation, visualization, storage, utils)
- [x] Buat `requirements.txt` dengan semua dependencies
- [x] Buat `main.py` sebagai entry point CLI

## Fase 2: Scanner & Akuisisi Data ✅
- [x] Implementasi `WiFiScanner` (pywifiscan + fallback netsh/iwlist/airport)
- [x] Implementasi `DataCollector` (CSV/JSON import/export)
- [x] Implementasi `DataPoint` model

## Fase 3: Interpolasi Spasial ✅
- [x] Implementasi `IDWInterpolator` dengan KNN optimization
- [x] Implementasi `GridBuilder` untuk grid generation

## Fase 4: Visualisasi ✅
- [x] Implementasi `Heatmap2D` (contourf + scatter overlay)
- [x] Implementasi `Surface3D` (Matplotlib static + Plotly interactive)

## Fase 5: Penyimpanan Data ✅
- [x] Implementasi `Database` (SQLite dengan sessions, data_points, interpolation_params)

## Fase 6: Utilitas & Geometri ✅
- [x] Implementasi `geometry.py` (jarak, bounding box, normalisasi, RSSI conversion)

## Fase 7: Testing & Dokumentasi ✅
- [x] Buat sample data CSV untuk testing
- [x] Install dependencies & test scan command
- [x] Test visualize command with sample data
- [x] Update README.md dengan dokumentasi lengkap
- [x] 106 unit tests passed

## Fase 8: GUI Application ✅
- [x] PyQt5 GUI dengan 7 tabs (Dashboard, Scanner, Visualization, Data Collection, Realtime, Spectrum Analyzer, Signal Propagation)
- [x] Fix Signal Propagation tab - semua 4 metode render langsung di matplotlib canvas
- [x] GUI berjalan dan berfungsi penuh
- [x] Commit & push ke GitHub

## Fase 9: Mode Rekam Jalan Langsung ✅
- [x] Fitur recording path dengan live position tracking
- [x] Auto-scan WiFi di setiap posisi yang direkam
- [x] Live heatmap update selama recording
- [x] Export recording ke CSV

## Fase 10: Porting ke Flutter (Mobile) ✅
- [x] Setup project Flutter
- [x] Halaman Dashboard dengan stats overview
- [x] Halaman Scanner untuk scan WiFi
- [x] Halaman Heatmap untuk visualisasi 2D
- [x] Halaman Realtime Monitor
- [x] Dark theme seperti GUI desktop
