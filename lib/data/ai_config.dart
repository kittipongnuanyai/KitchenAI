/// ค่าคงที่สำหรับติดต่อ Gemini API — แก้ที่ไฟล์นี้ที่เดียว
///
/// โมเดลที่ใช้ได้ฟรี (ดูรายการล่าสุดที่ https://ai.google.dev/gemini-api/docs/models)
/// ถ้าโดนจำกัดโควตา (429) ลองเปลี่ยนเป็น 'gemini-3.5-flash-lite'
const String kGeminiModel = 'gemini-3.8-flash';

/// URL หลักของ Gemini API (เวอร์ชัน v1beta)
const String kGeminiBaseUrl = 'https://generativelanguage.googleapis.com/v1beta';

/// เวลาสูงสุดที่รอ AI ตอบ
const Duration kAiTimeout = Duration(seconds: 90);

/// สำหรับทดสอบเร็ว ๆ ใส่ key ตรงนี้ได้ แต่ **ห้าม commit ขึ้น git เด็ดขาด**
/// (ปกติให้ใส่ผ่านหน้า "ตั้งค่า" ในแอป ซึ่งเก็บไว้ในเครื่องเท่านั้น)
const String kDevApiKey = '';
