import 'package:flutter/material.dart';

class AppColors {
  static const Color primary = Color(0xFF00BCD4);
  static const Color secondary = Color(0xFF7C4DFF);
  static const Color background = Color(0xFF121212);
  static const Color surface = Color(0xFF1E1E2E);
  static const Color cardBackground = Color(0xFF252540);
  static const Color error = Color(0xFFCF6679);
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color accent = Color(0xFF00E5FF);
  static const Color gradientStart = Color(0xFF00BCD4);
  static const Color gradientEnd = Color(0xFF7C4DFF);

  // Signal strength colors
  static const Color signalExcellent = Color(0xFF4CAF50);
  static const Color signalGood = Color(0xFF8BC34A);
  static const Color signalFair = Color(0xFFFFC107);
  static const Color signalWeak = Color(0xFFFF9800);
  static const Color signalPoor = Color(0xFFF44336);

  // Frequency band colors
  static const Color band24 = Color(0xFF2196F3);
  static const Color band5 = Color(0xFF9C27B0);
  static const Color band6 = Color(0xFFE91E63);
}

class AppStrings {
  static const String appName = 'SpectraLens';
  static const String tagline = 'Making the invisible visible, one frequency at a time.';
  static const String version = 'v1.0.0';

  // Dashboard
  static const String dashboard = 'Dashboard';
  static const String totalNetworks = 'Total Networks';
  static const String activeScans = 'Active Scans';
  static const String dataPoints = 'Data Points';
  static const String coverage = 'Coverage';

  // Scanner
  static const String scanner = 'WiFi Scanner';
  static const String startScan = 'Start Scan';
  static const String stopScan = 'Stop Scan';
  static const String scanning = 'Scanning...';
  static const String noNetworks = 'No networks found';

  // Heatmap
  static const String heatmap = 'Signal Heatmap';
  static const String generateHeatmap = 'Generate Heatmap';
  static const String noData = 'No data available';

  // Data Collection
  static const String dataCollection = 'Data Collection';
  static const String importCSV = 'Import CSV';
  static const String exportCSV = 'Export CSV';
  static const String addDataPoint = 'Add Data Point';

  // Settings
  static const String settings = 'Settings';
  static const String scanInterval = 'Scan Interval';
  static const String darkMode = 'Dark Mode';
  static const String notifications = 'Notifications';
}

class AppDimensions {
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  static const double borderRadius = 12.0;
  static const double cardElevation = 4.0;
  static const double iconSize = 24.0;
  static const double chartHeight = 250.0;
}

class ApiEndpoints {
  static const String baseUrl = 'http://localhost:5000';
  static const String scan = '$baseUrl/api/scan';
  static const String data = '$baseUrl/api/data';
  static const String heatmap = '$baseUrl/api/heatmap';
  static const String networks = '$baseUrl/api/networks';
}
