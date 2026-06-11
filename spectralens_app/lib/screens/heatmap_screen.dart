import 'dart:math';
import 'package:flutter/material.dart';
import '../utils/constants.dart';

class HeatmapScreen extends StatelessWidget {
  const HeatmapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Signal Heatmap'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.paddingMedium),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Heatmap Canvas
            Card(
              child: Container(
                width: double.infinity,
                height: 350,
                padding: const EdgeInsets.all(16),
                child: CustomPaint(
                  painter: HeatmapPainter(),
                  size: const Size(double.infinity, 350),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Legend
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Signal Strength Legend',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        _buildLegendItem(AppColors.signalExcellent, 'Excellent'),
                        const SizedBox(width: 16),
                        _buildLegendItem(AppColors.signalGood, 'Good'),
                        const SizedBox(width: 16),
                        _buildLegendItem(AppColors.signalFair, 'Fair'),
                        const SizedBox(width: 16),
                        _buildLegendItem(AppColors.signalWeak, 'Weak'),
                        const SizedBox(width: 16),
                        _buildLegendItem(AppColors.signalPoor, 'Poor'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Controls
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Heatmap Controls',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildControlButton(
                            Icons.interpolation,
                            'Interpolation',
                            AppColors.primary,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildControlButton(
                            Icons.layers,
                            'Overlay',
                            AppColors.secondary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _buildControlButton(
                            Icons.screenshot,
                            'Export PNG',
                            AppColors.success,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildControlButton(
                            Icons.fullscreen,
                            'Fullscreen',
                            AppColors.warning,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Stats
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.paddingMedium),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Coverage Statistics',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildStatRow('Total Area', '250 m²'),
                    _buildStatRow('Covered Area', '180 m²'),
                    _buildStatRow('Coverage Ratio', '72%'),
                    _buildStatRow('Avg Signal', '-62 dBm'),
                    _buildStatRow('Hotspots', '3'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegendItem(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildControlButton(IconData icon, String label, Color color) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppColors.textSecondary,
              fontSize: 13,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}

class HeatmapPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Background
    final bgPaint = Paint()..color = const Color(0xFF1A1A2E);
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), bgPaint);

    // Grid lines
    final gridPaint = Paint()
      ..color = Colors.white.withOpacity(0.05)
      ..strokeWidth = 1;
    
    for (double x = 0; x < size.width; x += 30) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }
    for (double y = 0; y < size.height; y += 30) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // Draw heatmap circles (simulated)
    final random = Random(42);
    final centers = <Offset>[];
    for (int i = 0; i < 5; i++) {
      centers.add(Offset(
        random.nextDouble() * size.width,
        random.nextDouble() * size.height,
      ));
    }

    // Draw heatmap gradient circles
    for (final center in centers) {
      final gradient = RadialGradient(
        colors: [
          AppColors.signalExcellent.withOpacity(0.3),
          AppColors.signalGood.withOpacity(0.2),
          AppColors.signalFair.withOpacity(0.1),
          Colors.transparent,
        ],
      );
      
      final rect = Rect.fromCircle(center: center, radius: 80);
      final paint = Paint()
        ..shader = gradient.createShader(rect);
      
      canvas.drawCircle(center, 80, paint);
    }

    // Draw measurement points
    for (int i = 0; i < 20; i++) {
      final point = Offset(
        random.nextDouble() * size.width,
        random.nextDouble() * size.height,
      );
      
      final signalStrength = -30 - random.nextDouble() * 50;
      final pointPaint = Paint()
        ..color = _getSignalColor(signalStrength)
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(point, 4, pointPaint);
      
      // Border
      final borderPaint = Paint()
        ..color = Colors.white.withOpacity(0.3)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;
      canvas.drawCircle(point, 4, borderPaint);
    }

    // Labels
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );
    
    textPainter.text = TextSpan(
      text: 'Signal Heatmap Preview',
      style: TextStyle(
        color: Colors.white.withOpacity(0.3),
        fontSize: 14,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        size.width / 2 - textPainter.width / 2,
        size.height / 2 - textPainter.height / 2 + 30,
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

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
