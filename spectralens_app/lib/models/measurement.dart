class Measurement {
  final String id;
  final double x;
  final double y;
  final double signalStrength;
  final String frequency;
  final String ssid;
  final String bssid;
  final DateTime timestamp;
  final String band; // 2.4GHz, 5GHz, 6GHz

  Measurement({
    required this.id,
    required this.x,
    required this.y,
    required this.signalStrength,
    required this.frequency,
    required this.ssid,
    required this.bssid,
    required this.timestamp,
    required this.band,
  });

  factory Measurement.fromJson(Map<String, dynamic> json) {
    return Measurement(
      id: json['id'] ?? '',
      x: (json['x'] ?? 0).toDouble(),
      y: (json['y'] ?? 0).toDouble(),
      signalStrength: (json['signal_strength'] ?? 0).toDouble(),
      frequency: json['frequency'] ?? '',
      ssid: json['ssid'] ?? 'Unknown',
      bssid: json['bssid'] ?? '',
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
      band: json['band'] ?? '2.4GHz',
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'x': x,
    'y': y,
    'signal_strength': signalStrength,
    'frequency': frequency,
    'ssid': ssid,
    'bssid': bssid,
    'timestamp': timestamp.toIso8601String(),
    'band': band,
  };

  String get signalQuality {
    if (signalStrength >= -50) return 'Excellent';
    if (signalStrength >= -60) return 'Good';
    if (signalStrength >= -70) return 'Fair';
    if (signalStrength >= -80) return 'Weak';
    return 'Poor';
  }
}

class WiFiNetwork {
  final String ssid;
  final String bssid;
  final double signalStrength;
  final String frequency;
  final String band;
  final String security;
  final String channel;
  final bool isConnected;

  WiFiNetwork({
    required this.ssid,
    required this.bssid,
    required this.signalStrength,
    required this.frequency,
    required this.band,
    required this.security,
    required this.channel,
    this.isConnected = false,
  });

  factory WiFiNetwork.fromJson(Map<String, dynamic> json) {
    return WiFiNetwork(
      ssid: json['ssid'] ?? 'Unknown',
      bssid: json['bssid'] ?? '',
      signalStrength: (json['signal_strength'] ?? 0).toDouble(),
      frequency: json['frequency'] ?? '',
      band: json['band'] ?? '2.4GHz',
      security: json['security'] ?? 'Open',
      channel: json['channel'] ?? '1',
      isConnected: json['is_connected'] ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'ssid': ssid,
    'bssid': bssid,
    'signal_strength': signalStrength,
    'frequency': frequency,
    'band': band,
    'security': security,
    'channel': channel,
    'is_connected': isConnected,
  };

  String get signalQuality {
    if (signalStrength >= -50) return 'Excellent';
    if (signalStrength >= -60) return 'Good';
    if (signalStrength >= -70) return 'Fair';
    if (signalStrength >= -80) return 'Weak';
    return 'Poor';
  }
}

class ScanResult {
  final String id;
  final DateTime timestamp;
  final int networkCount;
  final List<WiFiNetwork> networks;
  final double duration;

  ScanResult({
    required this.id,
    required this.timestamp,
    required this.networkCount,
    required this.networks,
    required this.duration,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      id: json['id'] ?? '',
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
      networkCount: json['network_count'] ?? 0,
      networks: (json['networks'] as List<dynamic>?)
          ?.map((e) => WiFiNetwork.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      duration: (json['duration'] ?? 0).toDouble(),
    );
  }
}
