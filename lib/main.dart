import 'package:flutter/material.dart';

import 'data/app_settings.dart';
import 'screens/home_screen.dart';
import 'theme.dart';

void main() {
  runApp(const KitchenAiApp());
}

/// รากของแอป — โหลดการตั้งค่าแล้วเปิดหน้าแรก
class KitchenAiApp extends StatefulWidget {
  const KitchenAiApp({super.key, this.settings});

  /// ส่ง settings เข้ามาเองได้ (ใช้ในเทสต์) ถ้าไม่ส่งจะสร้างใหม่และโหลดจากเครื่อง
  final AppSettings? settings;

  @override
  State<KitchenAiApp> createState() => _KitchenAiAppState();
}

class _KitchenAiAppState extends State<KitchenAiApp> {
  late final AppSettings _settings = widget.settings ?? (AppSettings()..load());

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KitchenAI',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(),
      home: HomeScreen(settings: _settings),
    );
  }
}
