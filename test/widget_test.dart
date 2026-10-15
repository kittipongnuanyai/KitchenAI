import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kitchen_ai/data/ai_service.dart';
import 'package:kitchen_ai/data/app_settings.dart';
import 'package:kitchen_ai/main.dart';
import 'package:kitchen_ai/models/menu_suggestion.dart';
import 'package:kitchen_ai/models/photo_analysis.dart';
import 'package:kitchen_ai/screens/ingredients_screen.dart';
import 'package:kitchen_ai/screens/photo_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// ทดสอบหน้าจอด้วย DemoAiService (ไม่หน่วงเวลา) — ไม่ต้องมี key ไม่ต้องต่อเน็ต
void main() {
  final demo = DemoAiService(delay: Duration.zero);

  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('หน้าแรกเตือนให้ตั้งค่า key เมื่อยังไม่มี', (tester) async {
    final settings = AppSettings();
    await settings.load();
    await tester.pumpWidget(KitchenAiApp(settings: settings));
    await tester.pumpAndSettle();

    expect(find.text('KitchenAI'), findsOneWidget);
    expect(find.textContaining('ยังไม่ได้ใส่ Gemini API key'), findsOneWidget);
    expect(find.text('พิมพ์วัตถุดิบที่มี'), findsOneWidget);
    expect(find.text('ถ่ายรูปวัตถุดิบ'), findsOneWidget);
  });

  testWidgets('เปิดโหมดสาธิตแล้วแบนเนอร์เตือนหายไป', (tester) async {
    SharedPreferences.setMockInitialValues({'demo_mode': true});
    final settings = AppSettings();
    await settings.load();
    await tester.pumpWidget(KitchenAiApp(settings: settings));
    await tester.pumpAndSettle();

    expect(find.textContaining('ยังไม่ได้ใส่ Gemini API key'), findsNothing);
    expect(find.textContaining('โหมดสาธิต'), findsWidgets);
  });

  testWidgets('หน้าวัตถุดิบ: เพิ่ม chip แล้วขอเมนู → แสดงการ์ดเมนู', (tester) async {
    await tester.pumpWidget(MaterialApp(home: IngredientsScreen(ai: demo)));

    await tester.enterText(find.byType(TextField).first, 'ไข่, หมูสับ');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pump();
    expect(find.widgetWithText(InputChip, 'ไข่'), findsOneWidget);
    expect(find.widgetWithText(InputChip, 'หมูสับ'), findsOneWidget);

    await tester.tap(find.text('ให้ AI แนะนำเมนู'));
    await tester.pumpAndSettle();

    expect(find.text('เมนูแนะนำ 3 รายการ'), findsOneWidget);
    expect(find.text('ไข่เจียวหมูสับ'), findsOneWidget);
    expect(find.textContaining('ตีไข่กับหมูสับ'), findsOneWidget); // การ์ดแรกขยายอยู่
  });

  testWidgets('หน้าวัตถุดิบ: ไม่มีรายการ → เตือนด้วย SnackBar', (tester) async {
    await tester.pumpWidget(MaterialApp(home: IngredientsScreen(ai: demo)));
    await tester.tap(find.text('ให้ AI แนะนำเมนู'));
    await tester.pump();
    expect(find.text('ใส่วัตถุดิบอย่างน้อย 1 อย่างก่อน'), findsOneWidget);
  });

  testWidgets('หน้าวัตถุดิบ: AI ผิดพลาด → แสดง ErrorBox', (tester) async {
    await tester.pumpWidget(MaterialApp(home: IngredientsScreen(ai: _FailingAi(), initialIngredients: const ['ไข่'])));
    await tester.tap(find.text('ให้ AI แนะนำเมนู'));
    await tester.pumpAndSettle();
    expect(find.text('เกิดข้อผิดพลาด'), findsOneWidget);
    expect(find.textContaining('โควตา'), findsOneWidget);
    expect(find.text('ลองใหม่'), findsOneWidget);
  });

  testWidgets('หน้ารูป: ปุ่มวิเคราะห์ปิดอยู่จนกว่าจะเลือกรูป', (tester) async {
    await tester.pumpWidget(MaterialApp(home: PhotoScreen(ai: demo)));
    expect(find.text('ยังไม่ได้เลือกรูป'), findsOneWidget);
    // ปุ่มอยู่ใต้รูป อาจอยู่นอกจอทดสอบ → เลื่อนให้เห็นก่อน
    await tester.scrollUntilVisible(find.text('ให้ AI วิเคราะห์รูป'), 200);
    final btn = tester.widget<FilledButton>(
      find.ancestor(of: find.text('ให้ AI วิเคราะห์รูป'), matching: find.bySubtype<FilledButton>()),
    );
    expect(btn.onPressed, isNull);
  });
}

/// AI ปลอมที่ล้มเหลวเสมอ — ไว้ทดสอบการแสดงข้อผิดพลาด
class _FailingAi implements AiService {
  @override
  Future<MenuResult> suggestMenus(List<String> ingredients, {String? extra}) async =>
      throw _quota();

  @override
  Future<PhotoAnalysis> analyzePhoto(bytes, {String mimeType = 'image/jpeg'}) async => throw _quota();

  @override
  Future<String> ping() async => throw _quota();

  static Object _quota() => Exception('ใช้โควตาฟรีเกินกำหนดชั่วคราว');
}
