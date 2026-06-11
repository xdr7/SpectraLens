import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import '../models/measurement.dart';

class ScanProvider extends ChangeNotifier {
  List<WiFiNetwork> _discoveredNetworks = [];
  bool _isScanning = false;
  Timer? _scanTimer;
  int _scanProgress = 0;
  String _statusMessage = 'Ready to scan';
  List<double> _signalHistory = [];
  int _totalPackets = 0;

  // Getters
  List<WiFiNetwork> get discoveredNetworks => _discoveredNetworks;
  bool get isScanning => _isScanning;
  int get scanProgress => _scanProgress;
  String get statusMessage => _statusMessage;
  List<double> get signalHistory => _signalHistory;
  int get totalPackets => _totalPackets;

  // Mock WiFi networks for demo
  static final List<Map<String, dynamic>> _mockNetworks = [
    {'ssid': 'HomeNetwork', 'bssid': '00:11:22:33:44:01', 'signal': -45, 'freq': '2412', 'band': '2.4GHz', 'security': 'WPA2', 'channel': '1'},
    {'ssid': 'Office_WiFi', 'bssid': '00:11:22:33:44:02', 'signal': -62, 'freq': '5180', 'band': '5GHz', 'security': 'WPA3', 'channel': '36'},
    {'ssid': 'Guest_Network', 'bssid': '00:11:22:33:44:03', 'signal': -55, 'freq': '2437', 'band': '2.4GHz', 'security': 'Open', 'channel': '6'},
    {'ssid': 'IoT_Devices', 'bssid': '00:11:22:33:44:04', 'signal': -70, 'freq': '2462', 'band': '2.4GHz', 'security': 'WPA2', 'channel': '11'},
    {'ssid': '5G_FastNet', 'bssid': '00:11:22:33:44:05', 'signal': -58, 'freq': '5200', 'band': '5GHz', 'security': 'WPA2', 'channel': '40'},
    {'ssid': 'Neighbor_Net', 'bssid': '00:11:22:33:44:06', 'signal': -78, 'freq': '2412', 'band': '2.4GHz', 'security': 'WPA2', 'channel': '1'},
    {'ssid': '6G_Ultra', 'bssid': '00:11:22:33:44:07', 'signal': -50, 'freq': '5955', 'band': '6GHz', 'security': 'WPA3', 'channel': '5'},
    {'ssid': 'Cafe_WiFi', 'bssid': '00:11:22:33:44:08', 'signal': -72, 'freq': '2437', 'band': '2.4GHz', 'security': 'WPA2', 'channel': '6'},
  ];

  void startScan() {
    if (_isScanning) return;
    
    _isScanning = true;
    _scanProgress = 0;
    _statusMessage = 'Scanning networks...';
    _discoveredNetworks.clear();
    _signalHistory.clear();
    notifyListeners();

    // Simulate progressive scan
    _scanTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      _scanProgress += 10;
      
      // Add random networks progressively
      if (_scanProgress % 20 == 0 && _discoveredNetworks.length < _mockNetworks.length) {
        final index = _discoveredNetworks.length;
        final net = _mockNetworks[index];
        _discoveredNetworks.add(WiFiNetwork(
          ssid: net['ssid'] as String,
          bssid: net['bssid'] as String,
          signalStrength: (net['signal'] as int).toDouble(),
          frequency: net['freq'] as String,
          band: net['band'] as String,
          security: net['security'] as String,
          channel: net['channel'] as String,
        ));
        
        // Add to signal history
        _signalHistory.add((net['signal'] as int).toDouble());
        _totalPackets += Random().nextInt(50) + 10;
      }

      if (_scanProgress >= 100) {
        timer.cancel();
        _isScanning = false;
        _statusMessage = 'Scan complete - ${_discoveredNetworks.length} networks found';
        notifyListeners();
        return;
      }
      
      _statusMessage = 'Scanning... ${_scanProgress}%';
      notifyListeners();
    });
  }

  void stopScan() {
    _scanTimer?.cancel();
    _isScanning = false;
    _statusMessage = 'Scan stopped';
    notifyListeners();
  }

  void refreshScan() {
    _discoveredNetworks.clear();
    _signalHistory.clear();
    _totalPackets = 0;
    notifyListeners();
    startScan();
  }

  @override
  void dispose() {
    _scanTimer?.cancel();
    super.dispose();
  }
}
