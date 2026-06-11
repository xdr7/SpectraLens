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

## Fase 7: Testing & Dokumentasi 🔄
- [x] Buat sample data CSV untuk testing
- [ ] Install dependencies & test scan command
- [ ] Test visualize command with sample data
- [ ] Update README.md dengan dokumentasi lengkap
