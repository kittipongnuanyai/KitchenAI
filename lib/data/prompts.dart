// ข้อความ prompt และโครงสร้าง JSON ที่ให้ AI ตอบ — รวมไว้ที่เดียวจะได้ปรับง่าย

/// "บทบาท" ที่ให้ AI สวม ใช้กับทุกคำถามในแอป
const String kChefSystemInstruction = '''
คุณคือเชฟอาหารไทยที่ใจดี ชอบสอนคนเริ่มทำอาหาร
- ตอบเป็นภาษาไทยที่อ่านง่าย ใช้ชื่อวัตถุดิบและหน่วยแบบไทย (ช้อนโต๊ะ, ถ้วย, กรัม)
- แนะนำเมนูที่ทำได้จริงในครัวบ้านทั่วไป ใช้เวลาไม่นาน
- ถ้าวัตถุดิบไม่พอ ให้บอกชัดเจนว่าต้องซื้ออะไรเพิ่ม (ของพื้นฐานอย่างน้ำปลา น้ำตาล น้ำมัน กระเทียม ถือว่ามีอยู่แล้ว)
''';

/// สร้างคำถามสำหรับขอเมนูจากรายการวัตถุดิบ
String buildMenuPrompt(List<String> ingredients, {String? extra}) {
  final list = ingredients.map((e) => '- $e').join('\n');
  final condition = (extra == null || extra.trim().isEmpty) ? '' : '\nเงื่อนไขเพิ่มเติม: ${extra.trim()}';
  return '''
ตอนนี้ฉันมีวัตถุดิบดังนี้:
$list
$condition
ช่วยแนะนำเมนูที่ทำได้ 3 เมนู เรียงจากเมนูที่ใช้ของที่มีอยู่ครบที่สุดก่อน
แต่ละเมนูบอก: ชื่อเมนู, คำอธิบายสั้น ๆ, วัตถุดิบที่ใช้ (พร้อมปริมาณ), ของที่ต้องซื้อเพิ่ม, ขั้นตอนการทำทีละข้อ, เวลาที่ใช้, ความยาก
''';
}

/// โครงสร้าง JSON ที่ให้ AI ตอบสำหรับ "แนะนำเมนู" (JSON Schema แบบย่อที่ Gemini รองรับ)
const Map<String, dynamic> kMenuResponseSchema = {
  'type': 'object',
  'properties': {
    'summary': {'type': 'string', 'description': 'สรุปสั้น ๆ 1-2 ประโยคว่าวัตถุดิบชุดนี้เหมาะทำอะไร'},
    'menus': {
      'type': 'array',
      'items': {
        'type': 'object',
        'properties': {
          'name': {'type': 'string'},
          'description': {'type': 'string'},
          'ingredients': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'วัตถุดิบพร้อมปริมาณ เช่น "ไข่ไก่ 2 ฟอง"',
          },
          'missing': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'ของที่ต้องซื้อเพิ่ม (ว่างได้ถ้าครบ)',
          },
          'steps': {
            'type': 'array',
            'items': {'type': 'string'},
          },
          'time': {'type': 'string', 'description': 'เช่น "15 นาที"'},
          'difficulty': {'type': 'string', 'enum': ['ง่าย', 'ปานกลาง', 'ยาก']},
        },
        'required': ['name', 'description', 'ingredients', 'missing', 'steps', 'time', 'difficulty'],
      },
    },
  },
  'required': ['summary', 'menus'],
};

/// คำถามสำหรับให้ AI "ดูรูป" แล้วบอกว่ามีอะไรบ้าง
const String kPhotoPrompt = '''
ดูรูปนี้แล้วบอกว่าเห็นวัตถุดิบ/อาหารอะไรบ้าง
- ระบุชื่อเป็นภาษาไทย ประมาณปริมาณคร่าว ๆ และสภาพ (เช่น สด, สุกแล้ว) ถ้าดูออก
- ถ้าในรูปไม่มีอาหารเลย ให้บอกตามจริงใน description และให้ items เป็นรายการว่าง
''';

/// โครงสร้าง JSON สำหรับผล "วิเคราะห์รูป"
const Map<String, dynamic> kPhotoResponseSchema = {
  'type': 'object',
  'properties': {
    'description': {'type': 'string', 'description': 'บรรยายภาพรวมของรูป 1-3 ประโยค'},
    'items': {
      'type': 'array',
      'items': {
        'type': 'object',
        'properties': {
          'name': {'type': 'string'},
          'amount': {'type': 'string', 'description': 'ปริมาณโดยประมาณ เช่น "2 ฟอง", "ประมาณ 200 กรัม"'},
          'note': {'type': 'string', 'description': 'สภาพ/หมายเหตุ เช่น "สด", "เริ่มเหี่ยว"'},
        },
        'required': ['name', 'amount', 'note'],
      },
    },
  },
  'required': ['description', 'items'],
};
