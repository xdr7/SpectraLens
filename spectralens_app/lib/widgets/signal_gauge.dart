import 'dart:math';
import 'package:flutter/material.dart';
import '../utils/constants.dart';

class SignalGauge extends StatelessWidget {
  final double signalStrength;
  final double size;

  const SignalGauge({
    super.key,
    required this.signalStrength,
    this.size = 120,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _SignalGaugePainter(signalStrength: signalStrength),
        size: Size(size, size),
      ),
    );
  }
}

class _SignalGaugePainter extends CustomPainter {
  final double signalStrength;

  _SignalGaugePainter({required this.signalStrength});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 10;

    // Background arc
    final bgPaint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      pi * 0.75,
      pi * 1.5,
      false,
      bgPaint,
    );

    // Signal arc
    final signalRatio = ((signalStrength + 100) / 70).clamp(0.0, 1.0);
    final signalColor = _getSignalColor();
    
    final signalPaint = Paint()
      ..color = signalColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      pi * 0.75,
      pi * 1.5 * signalRatio,
      false,
      signalPaint,
    );

    // Center text
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
      textAlign: TextAlign.center,
    );

    textPainter.text = TextSpan(
      text: '${signalStrength.toStringAsFixed(0)}',
      style: TextStyle(
        color: signalColor,
        fontSize: size.width * 0.25,
        fontWeight: FontWeight.bold,
      ),
    );
    textPainter.layout(maxWidth: size.width);
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy - textPainter.height / 2 - 8,
      ),
    );

    // dBm label
    textPainter.text = TextSpan(
      text: 'dBm',
      style: TextStyle(
        color: Colors.white.withOpacity(0.5),
        fontSize: size.width * 0.08,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy + size.width * 0.08,
      ),
    );

    // Quality label
    textPainter.text = TextSpan(
      text: _getSignalQuality(),
      style: TextStyle(
        color: signalColor.withOpacity(0.7),
        fontSize: size.width * 0.07,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy + size.width * 0.16,
      ),
    );
  }

  Color _getSignalColor() {
    if (signalStrength >= -50) return AppColors.signalExcellent;
    if (signalStrength >= -60) return AppColors.signalGood;
    if (signalStrength >= -70) return AppColors.signalFair;
    if (signalStrength >= -80) return AppColors.signalWeak;
    return AppColors.signalPoor;
  }

  String _getSignalQuality() {
    if (signalStrength >= -50) return 'Excellent';
    if (signalStrength >= -60) return 'Good';
    if (signalStrength >= -70) return 'Fair';
    if (signalStrength >= -80) return 'Weak';
    return 'Poor';
  }

  @override
  bool shouldRepaint(covariant _SignalGaugePainter oldDelegate) {
    return oldDelegate.signalStrength != signalStrength;
  }
}
