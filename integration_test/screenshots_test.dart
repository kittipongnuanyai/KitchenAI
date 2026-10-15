// ถ่ายภาพหน้าจอทุกหน้าในโหมดสาธิต (ใช้ทำคู่มือ) — รันบนอีมูเลเตอร์:
//   flutter drive --driver=test_driver/integration_test.dart --target=integration_test/screenshots_test.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image_picker_platform_interface/image_picker_platform_interface.dart';
import 'package:integration_test/integration_test.dart';
import 'package:kitchen_ai/data/app_settings.dart';
import 'package:kitchen_ai/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// image_picker ปลอม — คืนรูปตัวอย่างจาก assets แทนการเปิดกล้อง
class _FakeImagePicker extends ImagePickerPlatform {
  @override
  Future<XFile?> getImageFromSource({required ImageSource source, ImagePickerOptions options = const ImagePickerOptions()}) async {
    final data = await rootBundle.load('assets/sample_ingredients.jpg');
    return XFile.fromData(data.buffer.asUint8List(), name: 'sample.jpg', mimeType: 'image/jpeg');
  }
}

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Future<void> shot(WidgetTester tester, String name) async {
    await tester.pumpAndSettle();
    await binding.takeScreenshot(name);
  }

  testWidgets('ถ่ายภาพทุกหน้า', (tester) async {
    await binding.convertFlutterSurfaceToImage();
    ImagePickerPlatform.instance = _FakeImagePicker();

    // 1) หน้าแรกตอนยังไม่มี key
    SharedPreferences.setMockInitialValues({});
    final settings = AppSettings();
    await settings.load();
    await tester.pumpWidget(KitchenAiApp(settings: settings));
    await tester.pumpAndSettle();
    await shot(tester, '01_home_no_key');

    // 2) หน้าตั้งค่า
    await tester.tap(find.byIcon(Icons.settings));
    await tester.pumpAndSettle();
    await shot(tester, '02_settings');
    await tester.tap(find.byType(Switch));
    await tester.pumpAndSettle();
    await tester.tap(find.text('ทดสอบการเชื่อมต่อ'));
    await tester.pumpAndSettle(const Duration(seconds: 2));
    await shot(tester, '03_settings_demo_ok');
    await tester.tap(find.text('บันทึก'));
    await tester.pumpAndSettle();
    await shot(tester, '04_home_demo');

    // 3) หน้าวัตถุดิบ
    await tester.tap(find.text('พิมพ์วัตถุดิบที่มี'));
    await tester.pumpAndSettle();
    await shot(tester, '05_ingredients_empty');
    await tester.enterText(find.byType(TextField).first, 'ไข่, หมูสับ, กระเทียม');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).last, 'ไม่กินเผ็ด');
    await tester.pumpAndSettle();
    await shot(tester, '06_ingredients_filled');
    await tester.tap(find.text('ให้ AI แนะนำเมนู'));
    await tester.pump(const Duration(milliseconds: 300));
    await binding.takeScreenshot('07_ingredients_loading');
    await tester.pumpAndSettle(const Duration(seconds: 2));
    await shot(tester, '08_ingredients_result');
    await tester.dragUntilVisible(find.text('วิธีทำ').first, find.byType(ListView), const Offset(0, -300));
    await shot(tester, '09_ingredients_result_steps');
    await tester.pageBack();
    await tester.pumpAndSettle();

    // 4) หน้ารูป
    await tester.tap(find.text('ถ่ายรูปวัตถุดิบ'));
    await tester.pumpAndSettle();
    await shot(tester, '10_photo_empty');
    await tester.tap(find.text('เลือกจากคลัง'));
    await tester.pumpAndSettle();
    await shot(tester, '11_photo_picked');
    await tester.tap(find.text('ให้ AI วิเคราะห์รูป'));
    await tester.pumpAndSettle(const Duration(seconds: 2));
    await tester.dragUntilVisible(find.textContaining('แนะนำเมนูจากของ').first, find.byType(ListView), const Offset(0, -300));
    await shot(tester, '12_photo_result');
    await tester.tap(find.textContaining('แนะนำเมนูจากของ').first);
    await tester.pumpAndSettle();
    await shot(tester, '13_photo_to_ingredients');
  });
}
