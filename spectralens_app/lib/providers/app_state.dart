import 'package:flutter/material.dart';
import '../models/measurement.dart';

class AppState extends ChangeNotifier {
  List<Measurement> _measurements = [];
  List<WiFiNetwork> _networks = [];
  bool _isScanning = false;
  bool _isDarkMode = true;
  int _scanInterval = 5;
  int _totalScans = 0;
  double _coverageArea = 0;

  // Getters
  List<Measurement> get measurements => _measurements;
  List<WiFiNetwork> get networks => _networks;
  bool get isScanning => _isScanning;
  bool get isDarkMode => _isDarkMode;
  int get scanInterval => _scanInterval;
  int get totalScans => _totalScans;
  double get coverageArea => _coverageArea;
  int get totalNetworks => _networks.length;
  int get dataPoints => _measurements.length;

  // Methods
  void addMeasurement(Measurement measurement) {
    _measurements.add(measurement);
    notifyListeners();
  }

  void addMeasurements(List<Measurement> measurements) {
    _measurements.addAll(measurements);
    notifyListeners();
  }

  void setNetworks(List<WiFiNetwork> networks) {
    _networks = networks;
    notifyListeners();
  }

  void setScanning(bool scanning) {
    _isScanning = scanning;
    if (scanning) _totalScans++;
    notifyListeners();
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
  }

  void setScanInterval(int interval) {
    _scanInterval = interval;
    notifyListeners();
  }

  void setCoverageArea(double area) {
    _coverageArea = area;
    notifyListeners();
  }

  void clearData() {
    _measurements.clear();
    _networks.clear();
    _totalScans = 0;
    _coverageArea = 0;
    notifyListeners();
  }

  // Get signal strength distribution
  Map<String, int> get signalDistribution {
    final distribution = <String, int>{
      'Excellent': 0,
      'Good': 0,
      'Fair': 0,
      'Weak': 0,
      'Poor': 0,
    };
    for (final network in _networks) {
      distribution[network.signalQuality] =
          (distribution[network.signalQuality] ?? 0) + 1;
    }
    return distribution;
  }

  // Get band distribution
  Map<String, int> get bandDistribution {
    final distribution = <String, int>{};
    for (final network in _networks) {
      distribution[network.band] = (distribution[network.band] ?? 0) + 1;
    }
    return distribution;
  }
}
