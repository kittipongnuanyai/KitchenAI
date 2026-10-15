import 'package:flutter/material.dart';

/// กล่องแสดงข้อผิดพลาด พร้อมปุ่ม "ลองใหม่"
class ErrorBox extends StatelessWidget {
  const ErrorBox({super.key, required this.message, this.onRetry});

  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: scheme.errorContainer,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.error_outline, color: scheme.onErrorContainer),
              const SizedBox(width: 8),
              Text('เกิดข้อผิดพลาด',
                  style: TextStyle(fontWeight: FontWeight.bold, color: scheme.onErrorContainer)),
            ],
          ),
          const SizedBox(height: 6),
          Text(message, style: TextStyle(color: scheme.onErrorContainer)),
          if (onRetry != null) ...[
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('ลองใหม่'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
