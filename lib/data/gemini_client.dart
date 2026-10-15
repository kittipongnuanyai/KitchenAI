import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import 'ai_config.dart';

/// ข้อผิดพลาดจากการเรียก AI — เก็บข้อความภาษาไทยที่พร้อมแสดงให้ผู้ใช้
class AiException implements Exception {
  AiException(this.message, [this.statusCode]);
  final String message;
  final int? statusCode;

  @override
  String toString() => 'AiException($statusCode): $message';
}

/// ชั้นล่างสุด: คุยกับ Gemini ผ่าน HTTP โดยตรง (REST API `generateContent`)
///
/// ไม่รู้จัก "เมนู" หรือ "วัตถุดิบ" — รู้แค่ว่า ส่งข้อความ (+รูป) ไป แล้วได้ข้อความกลับมา
class GeminiClient {
  GeminiClient({required this.apiKey, http.Client? client, this.model = kGeminiModel})
      : _client = client ?? http.Client();

  final String apiKey;
  final String model;
  final http.Client _client;

  /// URL ปลายทาง เช่น
  /// https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent
  Uri get endpoint => Uri.parse('$kGeminiBaseUrl/models/$model:generateContent');

  /// ส่งคำถามไป Gemini แล้วคืน "ข้อความตอบกลับ"
  ///
  /// - [prompt]            ข้อความที่ผู้ใช้ถาม
  /// - [systemInstruction] บทบาท/กติกาที่ให้ AI ยึด (ไม่บังคับ)
  /// - [imageBytes]        รูปภาพ (ไม่บังคับ) ส่งเป็น base64 ใน inline_data
  /// - [responseSchema]    ถ้ากำหนด จะบังคับให้ AI ตอบเป็น JSON ตามโครงสร้างนี้
  Future<String> generate({
    required String prompt,
    String? systemInstruction,
    Uint8List? imageBytes,
    String imageMimeType = 'image/jpeg',
    Map<String, dynamic>? responseSchema,
    double temperature = 0.7,
  }) async {
    if (apiKey.trim().isEmpty) {
      throw AiException('ยังไม่ได้ตั้งค่า API key — ไปที่หน้า "ตั้งค่า" ก่อน');
    }

    // 1) ประกอบ "ชิ้นส่วน" ของคำถาม: ข้อความ และรูป (ถ้ามี)
    final parts = <Map<String, dynamic>>[
      {'text': prompt},
      if (imageBytes != null)
        {
          'inline_data': {'mime_type': imageMimeType, 'data': base64Encode(imageBytes)},
        },
    ];

    // 2) ประกอบ body ตามรูปแบบที่ Gemini ต้องการ
    final body = <String, dynamic>{
      if (systemInstruction != null)
        'system_instruction': {
          'parts': [
            {'text': systemInstruction},
          ],
        },
      'contents': [
        {'role': 'user', 'parts': parts},
      ],
      'generationConfig': {
        'temperature': temperature,
        'maxOutputTokens': 8192,
        // ลดเวลาคิดของโมเดล (ไม่ใส่ = medium ซึ่งช้ากว่ามาก)
        if (kThinkingLevel.isNotEmpty) 'thinkingConfig': {'thinkingLevel': kThinkingLevel},
        if (responseSchema != null) 'responseMimeType': 'application/json',
        if (responseSchema != null) 'responseSchema': responseSchema,
      },
    };

    // 3) ยิง HTTP POST — key ส่งใน header ไม่ใส่ใน URL
    http.Response res;
    try {
      res = await _client
          .post(
            endpoint,
            headers: {'Content-Type': 'application/json', 'x-goog-api-key': apiKey},
            body: jsonEncode(body),
          )
          .timeout(kAiTimeout);
    } on TimeoutException {
      throw AiException('AI ตอบช้าเกินไป (เกิน ${kAiTimeout.inSeconds} วินาที) ลองใหม่อีกครั้ง');
    } on SocketException {
      throw AiException('เชื่อมต่ออินเทอร์เน็ตไม่ได้ ตรวจสอบ Wi-Fi หรือเน็ตมือถือ');
    } on http.ClientException catch (e) {
      throw AiException('ส่งคำขอไม่สำเร็จ: ${e.message}');
    }

    // 4) ตรวจสถานะ HTTP
    if (res.statusCode != 200) {
      throw AiException(describeHttpError(res.statusCode, res.body), res.statusCode);
    }

    // 5) แกะข้อความออกจาก JSON ที่ตอบกลับ
    return extractText(jsonDecode(res.body) as Map<String, dynamic>);
  }

  /// แปลงรหัสสถานะ HTTP + body เป็นข้อความภาษาไทย
  static String describeHttpError(int status, String body) {
    String serverMessage = '';
    try {
      final json = jsonDecode(body) as Map<String, dynamic>;
      serverMessage = (json['error']?['message'] ?? '').toString();
    } catch (_) {}
    final detail = serverMessage.isEmpty ? '' : '\n($serverMessage)';
    switch (status) {
      case 400:
        if (serverMessage.contains('API key')) {
          return 'API key ไม่ถูกต้อง ตรวจสอบที่หน้า "ตั้งค่า"$detail';
        }
        return 'คำขอผิดรูปแบบ (400)$detail';
      case 401:
      case 403:
        return 'API key นี้ไม่มีสิทธิ์ใช้งาน ($status)$detail';
      case 404:
        return 'ไม่พบโมเดล "$kGeminiModel" — ชื่อโมเดลอาจเปลี่ยน ตรวจสอบใน ai_config.dart$detail';
      case 429:
        return 'ใช้โควตาฟรีเกินกำหนดชั่วคราว (429) รอสัก 1 นาทีแล้วลองใหม่$detail';
      case 500:
      case 503:
        return 'เซิร์ฟเวอร์ Gemini ขัดข้องชั่วคราว ($status) ลองใหม่อีกครั้ง$detail';
      default:
        return 'เกิดข้อผิดพลาด HTTP $status$detail';
    }
  }

  /// ดึงข้อความจาก JSON ตอบกลับของ Gemini
  ///
  /// รูปแบบ: { "candidates": [ { "content": { "parts": [ { "text": "..." } ] }, "finishReason": "STOP" } ] }
  static String extractText(Map<String, dynamic> json) {
    final feedback = json['promptFeedback'] as Map<String, dynamic>?;
    if (feedback?['blockReason'] != null) {
      throw AiException('AI ปฏิเสธคำถามนี้ (${feedback!['blockReason']}) ลองเปลี่ยนคำถาม');
    }
    final candidates = json['candidates'] as List<dynamic>?;
    if (candidates == null || candidates.isEmpty) {
      throw AiException('AI ไม่ได้ส่งคำตอบกลับมา');
    }
    final first = candidates.first as Map<String, dynamic>;
    final parts = (first['content']?['parts'] as List<dynamic>?) ?? const [];
    final text = parts
        .map((p) => (p as Map<String, dynamic>)['text'])
        .whereType<String>()
        .join();
    if (text.trim().isEmpty) {
      final reason = first['finishReason'] ?? 'ไม่ทราบสาเหตุ';
      throw AiException('AI ตอบกลับมาว่างเปล่า (finishReason: $reason)');
    }
    return text;
  }
}
