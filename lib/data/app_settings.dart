import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'ai_config.dart';
import 'ai_service.dart';
import 'gemini_client.dart';

/// การตั้งค่าของแอป (API key, โหมดสาธิต) — เก็บไว้ในเครื่องด้วย shared_preferences
///
/// เป็น ChangeNotifier: เมื่อค่าเปลี่ยน หน้าจอที่ฟังอยู่จะวาดใหม่เอง
class AppSettings extends ChangeNotifier {
  static const _keyApiKey = 'gemini_api_key';
  static const _keyDemo = 'demo_mode';

  String _apiKey = kDevApiKey;
  bool _demoMode = false;
  bool _loaded = false;

  String get apiKey => _apiKey;
  bool get demoMode => _demoMode;
  bool get loaded => _loaded;
  bool get hasApiKey => _apiKey.trim().isNotEmpty;

  /// พร้อมใช้ AI หรือยัง (มี key หรือเปิดโหมดสาธิต)
  bool get ready => demoMode || hasApiKey;

  /// สร้าง AiService ตามการตั้งค่าปัจจุบัน
  AiService get aiService =>
      _demoMode ? DemoAiService() : GeminiAiService(GeminiClient(apiKey: _apiKey));

  /// โหลดค่าที่เคยบันทึกไว้ (เรียกครั้งเดียวตอนเปิดแอป)
  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _apiKey = prefs.getString(_keyApiKey) ?? kDevApiKey;
    _demoMode = prefs.getBool(_keyDemo) ?? false;
    _loaded = true;
    notifyListeners();
  }

  Future<void> save({required String apiKey, required bool demoMode}) async {
    _apiKey = apiKey.trim();
    _demoMode = demoMode;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyApiKey, _apiKey);
    await prefs.setBool(_keyDemo, _demoMode);
  }
}
