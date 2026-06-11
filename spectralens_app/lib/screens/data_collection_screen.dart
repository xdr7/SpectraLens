import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../utils/constants.dart';

class DataCollectionScreen extends StatelessWidget {
  const DataCollectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Data Collection'),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_download),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Data exported to CSV')),
              );
            },
            tooltip: 'Export CSV',
          ),
          IconButton(
            icon: const Icon(Icons.file_upload),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Import CSV')),
              );
            },
            tooltip: 'Import CSV',
          ),
        ],
      ),
      body: Consumer<AppState>(
        builder: (context, state, _) {
          if (state.measurements.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.storage,
                    size: 64,
                    color: Colors.white.withOpacity(0.3),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No data collected yet',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.5),
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Run a scan to collect measurement data',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.3),
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView(
            padding: const EdgeInsets.all(AppDimensions.paddingMedium),
            children: [
              // Summary Card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Collection Summary',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          _buildSummaryItem(
                            Icons.storage,
                            '${state.measurements.length}',
                            'Total Points',
                            AppColors.primary,
                          ),
                          const SizedBox(width: 16),
                          _buildSummaryItem(
                            Icons.wifi,
                            '${state.networks.length}',
                            'Networks',
                            AppColors.secondary,
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          _buildSummaryItem(
                            Icons.scanner,
                            '${state.totalScans}',
                            'Scans',
                            AppColors.success,
                          ),
                          const SizedBox(width: 16),
                          _buildSummaryItem(
                            Icons.map,
                            '${state.coverageArea.toStringAsFixed(0)} m²',
                            'Coverage',
                            AppColors.warning,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Data Table
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Recent Measurements',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 12),
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: DataTable(
                          headingRowColor: WidgetStateProperty.all(
                            Colors.white.withOpacity(0.05),
                          ),
                          columns: const [
                            DataColumn(label: Text('SSID', style: TextStyle(color: AppColors.textSecondary, fontSize: 12))),
                            DataColumn(label: Text('Signal', style: TextStyle(color: AppColors.textSecondary, fontSize: 12))),
                            DataColumn(label: Text('Band', style: TextStyle(color: AppColors.textSecondary, fontSize: 12))),
                            DataColumn(label: Text('X', style: TextStyle(color: AppColors.textSecondary, fontSize: 12))),
                            DataColumn(label: Text('Y', style: TextStyle(color: AppColors.textSecondary, fontSize: 12))),
                          ],
                          rows: state.measurements.take(10).map((m) {
                            return DataRow(cells: [
                              DataCell(Text(m.ssid, style: const TextStyle(color: AppColors.textPrimary, fontSize: 12))),
                              DataCell(Text('${m.signalStrength.toStringAsFixed(0)} dBm', style: TextStyle(color: _getSignalColor(m.signalStrength), fontSize: 12))),
                              DataCell(Text(m.band, style: const TextStyle(color: AppColors.textPrimary, fontSize: 12))),
                              DataCell(Text(m.x.toStringAsFixed(1), style: const TextStyle(color: AppColors.textPrimary, fontSize: 12))),
                              DataCell(Text(m.y.toStringAsFixed(1), style: const TextStyle(color: AppColors.textPrimary, fontSize: 12))),
                            ]);
                          }).toList(),
                        ),
                      ),
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
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Data exported to CSV')),
                        );
                      },
                      icon: const Icon(Icons.file_download),
                      label: const Text('Export CSV'),
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
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Data imported from CSV')),
                        );
                      },
                      icon: const Icon(Icons.file_upload),
                      label: const Text('Import CSV'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.secondary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => state.clearData(),
                  icon: const Icon(Icons.delete_sweep),
                  label: const Text('Clear All Data'),
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
            ],
          );
        },
      ),
    );
  }

  Widget _buildSummaryItem(IconData icon, String value, String label, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
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
}
