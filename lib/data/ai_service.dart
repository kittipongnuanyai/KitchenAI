// ignore_for_file: unused_import, unused_field, unused_element, prefer_final_fields, unused_local_variable
// (คำเตือนพวกนี้จะหายไปเองเมื่อเขียน TODO ครบ — ลบบรรทัดนี้ได้เมื่อทำเสร็จ)
import 'dart:typed_data';

import '../models/menu_suggestion.dart';
import '../models/photo_analysis.dart';
import 'gemini_client.dart';
import 'prompts.dart';

/// "งาน" ที่แอปเราต้องการจาก AI — หน้าจอต่าง ๆ เรียกผ่าน interface นี้
///
/// มี 2 แบบ: [GeminiAiService] ใช้ AI จริง และ [DemoAiService] ตอบข้อมูลจำลอง
/// (ไว้ดู UI โดยไม่ต้องมี API key และใช้ในเทสต์)
abstract class AiService {
  /// ส่งรายการวัตถุดิบ → ได้เมนูแนะนำ
  Future<MenuResult> suggestMenus(List<String> ingredients, {String? extra});

  /// ส่งรูป → ได้รายการของที่เห็นในรูป
  Future<PhotoAnalysis> analyzePhoto(Uint8List imageBytes, {String mimeType = 'image/jpeg'});

  /// ทดสอบว่า key ใช้ได้ไหม → คืนข้อความสั้น ๆ จาก AI
  Future<String> ping();
}

/// ใช้ Gemini จริง — ประกอบ prompt + schema แล้วแปลงคำตอบเป็น model ของเรา
class GeminiAiService implements AiService {
  GeminiAiService(this.client);
  final GeminiClient client;

  @override
  Future<MenuResult> suggestMenus(List<String> ingredients, {String? extra}) async {
    // TODO(Step 6.2): เรียก client.generate(prompt: buildMenuPrompt(...), systemInstruction: ...,
    //   responseSchema: kMenuResponseSchema) แล้วแปลงด้วย MenuResult.fromJsonText(...)
    throw UnimplementedError('ยังไม่ได้เขียน suggestMenus() — ทำตามคู่มือ Step 6');
  }

  @override
  Future<PhotoAnalysis> analyzePhoto(Uint8List imageBytes, {String mimeType = 'image/jpeg'}) async {
    // TODO(Step 7.3): เหมือน suggestMenus แต่ส่ง imageBytes + imageMimeType และใช้ kPhotoPrompt,
    //   kPhotoResponseSchema, temperature ต่ำ (0.2) แล้วแปลงด้วย PhotoAnalysis.fromJsonText(...)
    throw UnimplementedError('ยังไม่ได้เขียน analyzePhoto() — ทำตามคู่มือ Step 7');
  }

  @override
  Future<String> ping() => client.generate(
        prompt: 'ทักทายสั้น ๆ 1 ประโยค แล้วบอกชื่อโมเดลของคุณ',
        temperature: 0.2,
      );
}

/// โหมดสาธิต — ตอบข้อมูลจำลองหลังหน่วงเวลาสั้น ๆ ไม่ต้องต่อเน็ต ไม่ใช้ key
class DemoAiService implements AiService {
  DemoAiService({this.delay = const Duration(milliseconds: 800)});
  final Duration delay;

  @override
  Future<MenuResult> suggestMenus(List<String> ingredients, {String? extra}) async {
    await Future<void>.delayed(delay);
    final have = ingredients.isEmpty ? 'ของในครัว' : ingredients.join(', ');
    return MenuResult(
      summary: '(โหมดสาธิต) จาก $have ทำเมนูง่าย ๆ ได้หลายอย่าง นี่คือตัวอย่าง',
      menus: [
        MenuSuggestion(
          name: 'ไข่เจียวหมูสับ',
          description: 'เมนูพื้นฐานที่ใช้ไข่กับหมูสับ ทำไว ทานกับข้าวสวยร้อน ๆ',
          ingredients: ['ไข่ไก่ 2 ฟอง', 'หมูสับ 50 กรัม', 'น้ำปลา 1 ช้อนชา', 'น้ำมันพืช 3 ช้อนโต๊ะ'],
          missing: [],
          steps: [
            'ตีไข่กับหมูสับและน้ำปลาให้เข้ากัน',
            'ตั้งกระทะ ใส่น้ำมัน รอให้ร้อนจัด',
            'เทไข่ลงไป ทอดจนเหลืองกรอบทั้งสองด้าน',
            'ตักขึ้นเสิร์ฟกับข้าวสวยและซอสพริก',
          ],
          time: '10 นาที',
          difficulty: 'ง่าย',
        ),
        MenuSuggestion(
          name: 'ผัดกะเพราหมูสับ',
          description: 'เมนูสิ้นคิดยอดนิยม หอมกะเพรา เผ็ดกำลังดี',
          ingredients: ['หมูสับ 150 กรัม', 'กระเทียม 3 กลีบ', 'พริกขี้หนู 5 เม็ด', 'ใบกะเพรา 1 กำมือ', 'ซอสหอยนางรม 1 ช้อนโต๊ะ'],
          missing: ['ใบกะเพรา', 'พริกขี้หนู'],
          steps: [
            'โขลกกระเทียมกับพริกพอหยาบ',
            'ตั้งกระทะ ผัดกระเทียมพริกกับน้ำมันให้หอม',
            'ใส่หมูสับ ผัดจนสุก ปรุงรสด้วยซอสหอยนางรม น้ำปลา น้ำตาลเล็กน้อย',
            'ใส่ใบกะเพรา ผัดเร็ว ๆ แล้วปิดไฟ',
          ],
          time: '15 นาที',
          difficulty: 'ง่าย',
        ),
        MenuSuggestion(
          name: 'ต้มจืดไข่น้ำ',
          description: 'ซุปใสรสอ่อน ทำง่าย เหมาะกับคนไม่กินเผ็ด',
          ingredients: ['ไข่ไก่ 2 ฟอง', 'หมูสับ 50 กรัม', 'น้ำซุป 2 ถ้วย', 'ต้นหอม 1 ต้น'],
          missing: ['ต้นหอม'],
          steps: [
            'ต้มน้ำซุปให้เดือด ใส่หมูสับปั้นเป็นก้อนเล็ก ๆ',
            'ตีไข่ แล้วค่อย ๆ เทลงในน้ำเดือด คนเบา ๆ ให้ไข่เป็นเส้น',
            'ปรุงรสด้วยน้ำปลา โรยต้นหอม พริกไทย',
          ],
          time: '15 นาที',
          difficulty: 'ปานกลาง',
        ),
      ],
    );
  }

  @override
  Future<PhotoAnalysis> analyzePhoto(Uint8List imageBytes, {String mimeType = 'image/jpeg'}) async {
    await Future<void>.delayed(delay);
    return PhotoAnalysis(
      description: '(โหมดสาธิต) รูปถ่ายวัตถุดิบบนโต๊ะครัว เห็นไข่ไก่ หมูสับ และผักสดบางส่วน',
      items: [
        FoundItem(name: 'ไข่ไก่', amount: '4 ฟอง', note: 'สด'),
        FoundItem(name: 'หมูสับ', amount: 'ประมาณ 200 กรัม', note: 'ยังดิบ'),
        FoundItem(name: 'ผักคะน้า', amount: '1 กำ', note: 'ใบเริ่มเหี่ยวเล็กน้อย'),
        FoundItem(name: 'กระเทียม', amount: '1 หัว', note: ''),
      ],
    );
  }

  @override
  Future<String> ping() async {
    await Future<void>.delayed(delay);
    return 'สวัสดีครับ นี่คือโหมดสาธิต ยังไม่ได้ต่อกับ Gemini จริง';
  }
}
