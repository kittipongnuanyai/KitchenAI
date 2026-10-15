import 'package:flutter/material.dart';

import '../data/ai_config.dart';
import '../data/app_settings.dart';
import '../data/gemini_client.dart';

/// หน้าตั้งค่า — ใส่ Gemini API key / เปิดโหมดสาธิต / ทดสอบการเชื่อมต่อ
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key, required this.settings});
  final AppSettings settings;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final _keyCtrl = TextEditingController(text: widget.settings.apiKey);
  late bool _demo = widget.settings.demoMode;
  bool _showKey = false;
  bool _testing = false;
  String? _testResult;
  bool _testOk = false;

  @override
  void dispose() {
    _keyCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    await widget.settings.save(apiKey: _keyCtrl.text, demoMode: _demo);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('บันทึกแล้ว')));
    Navigator.pop(context);
  }

  /// ส่งคำถามสั้น ๆ เพื่อเช็กว่า key ใช้ได้
  Future<void> _test() async {
    setState(() {
      _testing = true;
      _testResult = null;
    });
    // บันทึกค่าที่พิมพ์ไว้ก่อน แล้วค่อยสร้าง service จากค่าล่าสุด
    await widget.settings.save(apiKey: _keyCtrl.text, demoMode: _demo);
    try {
      final reply = await widget.settings.aiService.ping();
      if (!mounted) return;
      setState(() {
        _testOk = true;
        _testResult = reply;
      });
    } on AiException catch (e) {
      if (!mounted) return;
      setState(() {
        _testOk = false;
        _testResult = e.message;
      });
    } finally {
      if (mounted) setState(() => _testing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ตั้งค่า')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Gemini API key', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 6),
          const Text('ขอ key ฟรีได้ที่ aistudio.google.com/apikey (ดูขั้นตอนในคู่มือ Step 1) '
              'key จะถูกเก็บไว้ในเครื่องนี้เท่านั้น'),
          const SizedBox(height: 10),
          TextField(
            controller: _keyCtrl,
            obscureText: !_showKey,
            autocorrect: false,
            enableSuggestions: false,
            decoration: InputDecoration(
              labelText: 'API key',
              hintText: 'AIza...',
              suffixIcon: IconButton(
                icon: Icon(_showKey ? Icons.visibility_off : Icons.visibility),
                onPressed: () => setState(() => _showKey = !_showKey),
              ),
            ),
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('โหมดสาธิต (ไม่ใช้ AI จริง)'),
            subtitle: const Text('ตอบด้วยข้อมูลจำลอง ไว้ดู UI ตอนยังไม่มี key'),
            value: _demo,
            onChanged: (v) => setState(() => _demo = v),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _testing ? null : _test,
                  icon: const Icon(Icons.network_check),
                  label: Text(_testing ? 'กำลังทดสอบ...' : 'ทดสอบการเชื่อมต่อ'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: FilledButton.icon(
                  onPressed: _save,
                  icon: const Icon(Icons.save),
                  label: const Text('บันทึก'),
                ),
              ),
            ],
          ),
          if (_testResult != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _testOk ? Colors.green.shade50 : Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(_testOk ? Icons.check_circle : Icons.error,
                      color: _testOk ? Colors.green : Colors.red),
                  const SizedBox(width: 8),
                  Expanded(child: Text(_testResult!)),
                ],
              ),
            ),
          ],
          const SizedBox(height: 24),
          Text('ข้อมูลเทคนิค', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          Text('โมเดล: $kGeminiModel\nURL: $kGeminiBaseUrl',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
        ],
      ),
    );
  }
}
