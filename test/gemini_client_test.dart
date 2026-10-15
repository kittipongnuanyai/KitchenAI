import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kitchen_ai/data/gemini_client.dart';

/// ทดสอบ GeminiClient ด้วย "เซิร์ฟเวอร์ปลอม" (MockClient) — ไม่ต้องต่อเน็ต ไม่ใช้ key จริง
void main() {
  /// สร้าง client ที่ตอบ [body] พร้อมสถานะ [status] และจำคำขอล่าสุดไว้ให้ตรวจ
  (GeminiClient, List<http.Request>) fakeClient(int status, Map<String, dynamic> body) {
    final seen = <http.Request>[];
    final mock = MockClient((req) async {
      seen.add(req);
      return http.Response(jsonEncode(body), status, headers: {'content-type': 'application/json'});
    });
    return (GeminiClient(apiKey: 'test-key', client: mock), seen);
  }

  final okBody = {
    'candidates': [
      {
        'content': {
          'parts': [
            {'text': 'สวัสดี'},
            {'text': 'ครับ'},
          ],
        },
        'finishReason': 'STOP',
      },
    ],
  };

  test('ส่ง header x-goog-api-key และ body ตามรูปแบบ Gemini', () async {
    final (client, seen) = fakeClient(200, okBody);
    final text = await client.generate(prompt: 'ทดสอบ', systemInstruction: 'คุณคือเชฟ');

    expect(text, 'สวัสดีครับ'); // รวมข้อความจากทุก part
    expect(seen, hasLength(1));
    final req = seen.single;
    expect(req.method, 'POST');
    expect(req.url.toString(), contains(':generateContent'));
    expect(req.url.queryParameters.containsKey('key'), isFalse); // key ไม่หลุดไปอยู่ใน URL
    expect(req.headers['x-goog-api-key'], 'test-key');

    final body = jsonDecode(req.body) as Map<String, dynamic>;
    expect(body['contents'][0]['parts'][0]['text'], 'ทดสอบ');
    expect(body['system_instruction']['parts'][0]['text'], 'คุณคือเชฟ');
    expect(body['generationConfig'].containsKey('responseSchema'), isFalse);
    expect(body['generationConfig']['thinkingConfig']['thinkingLevel'], 'low'); // ลดเวลารอ
  });

  test('แนบรูปเป็น inline_data (base64) และบังคับ JSON เมื่อส่ง schema', () async {
    final (client, seen) = fakeClient(200, okBody);
    final bytes = Uint8List.fromList([1, 2, 3]);
    await client.generate(
      prompt: 'ดูรูป',
      imageBytes: bytes,
      imageMimeType: 'image/png',
      responseSchema: {'type': 'object'},
    );

    final body = jsonDecode(seen.single.body) as Map<String, dynamic>;
    final parts = body['contents'][0]['parts'] as List<dynamic>;
    expect(parts, hasLength(2));
    expect(parts[1]['inline_data']['mime_type'], 'image/png');
    expect(parts[1]['inline_data']['data'], base64Encode(bytes));
    expect(body['generationConfig']['responseMimeType'], 'application/json');
    expect(body['generationConfig']['responseSchema'], {'type': 'object'});
  });

  test('ไม่มี key → โยน AiException โดยไม่ยิงคำขอ', () async {
    final mock = MockClient((_) async => throw StateError('ไม่ควรถูกเรียก'));
    final client = GeminiClient(apiKey: '  ', client: mock);
    expect(() => client.generate(prompt: 'x'), throwsA(isA<AiException>()));
  });

  test('HTTP 429 → ข้อความเรื่องโควตา พร้อม statusCode', () async {
    final (client, _) = fakeClient(429, {
      'error': {'code': 429, 'message': 'Resource has been exhausted', 'status': 'RESOURCE_EXHAUSTED'},
    });
    try {
      await client.generate(prompt: 'x');
      fail('ควรโยน AiException');
    } on AiException catch (e) {
      expect(e.statusCode, 429);
      expect(e.message, contains('โควตา'));
      expect(e.message, contains('Resource has been exhausted'));
    }
  });

  test('HTTP 400 "API key not valid" → บอกให้ตรวจ key', () async {
    final (client, _) = fakeClient(400, {
      'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.'},
    });
    expect(
      () => client.generate(prompt: 'x'),
      throwsA(isA<AiException>().having((e) => e.message, 'message', contains('API key'))),
    );
  });

  test('คำตอบว่าง / ถูกบล็อก → AiException', () {
    expect(() => GeminiClient.extractText({'candidates': []}), throwsA(isA<AiException>()));
    expect(
      () => GeminiClient.extractText({'promptFeedback': {'blockReason': 'SAFETY'}}),
      throwsA(isA<AiException>().having((e) => e.message, 'message', contains('SAFETY'))),
    );
    expect(
      () => GeminiClient.extractText({
        'candidates': [
          {'content': {'parts': []}, 'finishReason': 'MAX_TOKENS'},
        ],
      }),
      throwsA(isA<AiException>().having((e) => e.message, 'message', contains('MAX_TOKENS'))),
    );
  });
}
