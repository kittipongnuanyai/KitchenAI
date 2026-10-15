// ignore_for_file: unused_import, unused_field, unused_element, prefer_final_fields, unused_local_variable
// (คำเตือนพวกนี้จะหายไปเองเมื่อเขียน TODO ครบ — ลบบรรทัดนี้ได้เมื่อทำเสร็จ)
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

    // TODO(Step 5.1): ประกอบ parts = [ {'text': prompt}, (ถ้ามีรูป) {'inline_data': {...}} ]

    // TODO(Step 5.2): ประกอบ body ตามรูปแบบของ Gemini
    //   system_instruction (ถ้ามี) · contents · generationConfig (temperature, maxOutputTokens,
    //   และถ้ามี responseSchema ให้ใส่ responseMimeType + responseSchema)

    // TODO(Step 5.3): ยิง HTTP POST ไปที่ endpoint พร้อม header 'x-goog-api-key'
    //   ครอบด้วย try/catch: TimeoutException, SocketException, http.ClientException → AiException

    // TODO(Step 5.4): ถ้า statusCode != 200 → throw AiException(describeHttpError(...), statusCode)

    // TODO(Step 5.5): แกะข้อความด้วย extractText(jsonDecode(res.body))
    throw UnimplementedError('ยังไม่ได้เขียน generate() — ทำตามคู่มือ Step 5');
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
    // TODO(Step 5.6): ดึง candidates[0].content.parts[*].text มาต่อกัน
    //   - ถ้า promptFeedback.blockReason มีค่า → throw AiException('AI ปฏิเสธคำถามนี้ ...')
    //   - ถ้า candidates ว่าง หรือข้อความว่าง → throw AiException พร้อม finishReason
    throw UnimplementedError('ยังไม่ได้เขียน extractText() — ทำตามคู่มือ Step 5');
  }
}
