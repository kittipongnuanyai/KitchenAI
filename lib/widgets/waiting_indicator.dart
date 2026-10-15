import 'dart:async';

import 'package:flutter/material.dart';

/// วงกลมหมุน + นับวินาทีที่รอ AI — ให้ผู้ใช้รู้ว่าแอปยังทำงานอยู่ (AI ใช้เวลา 3–30 วินาที)
class WaitingIndicator extends StatefulWidget {
  const WaitingIndicator({super.key});

  @override
  State<WaitingIndicator> createState() => _WaitingIndicatorState();
}

class _WaitingIndicatorState extends State<WaitingIndicator> {
  int _seconds = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => setState(() => _seconds++));
  }

  @override
  void dispose() {
    _timer?.cancel(); // สำคัญ: หยุด timer เมื่อ widget หายไป ไม่งั้น setState หลัง dispose
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 10),
              Text('AI กำลังคิด... $_seconds วินาที', style: TextStyle(color: Colors.grey.shade700)),
            ],
          ),
        ),
      );
}
