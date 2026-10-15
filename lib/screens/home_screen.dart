import 'package:flutter/material.dart';

import '../data/app_settings.dart';
import '../theme.dart';
import 'ingredients_screen.dart';
import 'photo_screen.dart';
import 'settings_screen.dart';

/// หน้าแรก — เลือกว่าจะถาม AI ด้วย "ข้อความ" หรือ "รูปภาพ"
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, required this.settings});
  final AppSettings settings;

  @override
  Widget build(BuildContext context) {
    // ListenableBuilder: วาดใหม่ทุกครั้งที่ settings เปลี่ยน (เช่น เพิ่งบันทึก key)
    return ListenableBuilder(
      listenable: settings,
      builder: (context, _) => Scaffold(
        appBar: AppBar(
          title: const Text('KitchenAI'),
          actions: [
            IconButton(
              icon: const Icon(Icons.settings),
              tooltip: 'ตั้งค่า',
              onPressed: () => _openSettings(context),
            ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (!settings.ready) _SetupBanner(onTap: () => _openSettings(context)),
            if (settings.demoMode) const _DemoBanner(),
            const SizedBox(height: 8),
            Text('ผู้ช่วยครัว AI', style: Theme.of(context).textTheme.headlineSmall),
            const Text('มีของอะไรในตู้เย็น? ให้ AI ช่วยคิดเมนูให้'),
            const SizedBox(height: 16),
            _FeatureCard(
              icon: Icons.format_list_bulleted,
              color: kPrimary,
              title: 'พิมพ์วัตถุดิบที่มี',
              subtitle: 'เช่น ไข่ หมูสับ กระเทียม → AI แนะนำเมนูพร้อมวิธีทำ',
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => IngredientsScreen(ai: settings.aiService)),
              ),
            ),
            _FeatureCard(
              icon: Icons.photo_camera,
              color: kAccent,
              title: 'ถ่ายรูปวัตถุดิบ',
              subtitle: 'ส่งรูปให้ AI ดูว่ามีอะไรบ้าง แล้วต่อยอดเป็นเมนู',
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => PhotoScreen(ai: settings.aiService)),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'โมเดล: ${settings.demoMode ? "โหมดสาธิต" : "Gemini"} · วิชา 5534408',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  void _openSettings(BuildContext context) => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => SettingsScreen(settings: settings)),
      );
}

class _FeatureCard extends StatelessWidget {
  const _FeatureCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          contentPadding: const EdgeInsets.all(16),
          leading: CircleAvatar(
            radius: 26,
            backgroundColor: color.withValues(alpha: 0.15),
            child: Icon(icon, color: color, size: 28),
          ),
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          subtitle: Padding(padding: const EdgeInsets.only(top: 4), child: Text(subtitle)),
          trailing: const Icon(Icons.chevron_right),
          onTap: onTap,
        ),
      );
}

class _SetupBanner extends StatelessWidget {
  const _SetupBanner({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => MaterialBanner(
        backgroundColor: Colors.amber.shade100,
        leading: const Icon(Icons.key, color: Colors.brown),
        content: const Text('ยังไม่ได้ใส่ Gemini API key — ใส่ key หรือเปิดโหมดสาธิตก่อนใช้งาน'),
        actions: [TextButton(onPressed: onTap, child: const Text('ไปตั้งค่า'))],
      );
}

class _DemoBanner extends StatelessWidget {
  const _DemoBanner();

  @override
  Widget build(BuildContext context) => Container(
        margin: const EdgeInsets.only(bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(color: Colors.blue.shade50, borderRadius: BorderRadius.circular(8)),
        child: const Row(
          children: [
            Icon(Icons.science, color: Colors.blue),
            SizedBox(width: 8),
            Expanded(child: Text('โหมดสาธิต: คำตอบเป็นข้อมูลจำลอง ไม่ได้ส่งไป Gemini จริง')),
          ],
        ),
      );
}
