import 'dart:io';

import 'package:integration_test/integration_test_driver_extended.dart';

/// ตัวขับสำหรับ `flutter drive` — รับภาพหน้าจอจาก integration test แล้วบันทึกเป็นไฟล์
/// ใช้: flutter drive --driver=test_driver/integration_test.dart --target=integration_test/screenshots_test.dart
Future<void> main() async {
  await integrationDriver(
    onScreenshot: (String name, List<int> bytes, [Map<String, Object?>? args]) async {
      final file = File('docs/shots/$name.png');
      await file.parent.create(recursive: true);
      await file.writeAsBytes(bytes);
      return true;
    },
  );
}
