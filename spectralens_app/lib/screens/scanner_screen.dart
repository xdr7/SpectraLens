import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/scan_provider.dart';
import '../utils/constants.dart';
import '../models/measurement.dart';

class ScannerScreen extends StatelessWidget {
  const ScannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('WiFi Scanner'),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scan, _) {
          return Column(
            children: [
              // Scan Controls
              Container(
                padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                child: Column(
                  children: [
                    // Status & Progress
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                        child: Column(
                          children: [
                            Row(
                              children: [
                                Container(
                                  width: 12,
                                  height: 12,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: scan.isScanning
                                        ? AppColors.success
                                        : AppColors.textSecondary,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Text(
                                    scan.statusMessage,
                                    style: const TextStyle(
                                      color: AppColors.textPrimary,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                if (scan.isScanning)
                                  const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: AppColors.primary,
                                    ),
                                  ),
                              ],
                            ),
                            if (scan.isScanning) ...[
                              const SizedBox(height: 12),
                              ClipRRect(
                                borderRadius: BorderRadius.circular(4),
                                child: LinearProgressIndicator(
                                  value: scan.scanProgress / 100,
                                  backgroundColor: Colors.white.withOpacity(0.1),
                                  valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                                  minHeight: 6,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: scan.isScanning ? null : () => scan.startScan(),
                            icon: const Icon(Icons.play_arrow),
                            label: const Text('Start Scan'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: scan.isScanning ? () => scan.stopScan() : null,
                            icon: const Icon(Icons.stop),
                            label: const Text('Stop'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.error,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        IconButton.filled(
                          onPressed: () => scan.refreshScan(),
                          icon: const Icon(Icons.refresh),
                          style: IconButton.styleFrom(
                            backgroundColor: AppColors.surface,
                            foregroundColor: AppColors.primary,
                            padding: const EdgeInsets.all(14),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Networks List
              Expanded(
                child: scan.discoveredNetworks.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.wifi_find,
                              size: 64,
                              color: Colors.white.withOpacity(0.3),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              scan.isScanning ? 'Scanning...' : 'No networks found',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.5),
                                fontSize: 16,
                              ),
                            ),
                            if (!scan.isScanning) ...[
                              const SizedBox(height: 8),
                              Text(
                                'Tap "Start Scan" to begin',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.3),
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: scan.discoveredNetworks.length,
                        itemBuilder: (context, index) {
                          final network = scan.discoveredNetworks[index];
                          return _buildNetworkCard(network);
                        },
                      ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildNetworkCard(WiFiNetwork network) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            // Signal Strength Indicator
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _getSignalColor(network.signalStrength).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Icon(
                  Icons.wifi,
                  color: _getSignalColor(network.signalStrength),
                  size: 24,
                ),
              ),
            ),
            const SizedBox(width: 14),
            // Network Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    network.ssid,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      _buildTag(network.band, _getBandColor(network.band)),
                      const SizedBox(width: 8),
                      _buildTag(network.security, AppColors.textSecondary),
                      const SizedBox(width: 8),
                      Text(
                        'Ch ${network.channel}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Signal Strength
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${network.signalStrength.toStringAsFixed(0)} dBm',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: _getSignalColor(network.signalStrength),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  network.signalQuality,
                  style: TextStyle(
                    fontSize: 11,
                    color: _getSignalColor(network.signalStrength).withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTag(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Color _getSignalColor(double strength) {
    if (strength >= -50) return AppColors.signalExcellent;
    if (strength >= -60) return AppColors.signalGood;
    if (strength >= -70) return AppColors.signalFair;
    if (strength >= -80) return AppColors.signalWeak;
    return AppColors.signalPoor;
  }

  Color _getBandColor(String band) {
    switch (band) {
      case '2.4GHz':
        return AppColors.band24;
      case '5GHz':
        return AppColors.band5;
      case '6GHz':
        return AppColors.band6;
      default:
        return AppColors.textSecondary;
    }
  }
}
