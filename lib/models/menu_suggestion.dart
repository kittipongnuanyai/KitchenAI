import 'dart:convert';

/// เมนู 1 รายการที่ AI แนะนำ
class MenuSuggestion {
  MenuSuggestion({
    required this.name,
    required this.description,
    required this.ingredients,
    required this.missing,
    required this.steps,
    required this.time,
    required this.difficulty,
  });

  final String name;
  final String description;
  final List<String> ingredients; // วัตถุดิบที่ใช้ (พร้อมปริมาณ)
  final List<String> missing; // ต้องซื้อเพิ่ม
  final List<String> steps; // ขั้นตอนทำ
  final String time;
  final String difficulty;

  factory MenuSuggestion.fromJson(Map<String, dynamic> json) => MenuSuggestion(
        name: (json['name'] ?? '').toString(),
        description: (json['description'] ?? '').toString(),
        ingredients: _stringList(json['ingredients']),
        missing: _stringList(json['missing']),
        steps: _stringList(json['steps']),
        time: (json['time'] ?? '-').toString(),
        difficulty: (json['difficulty'] ?? '-').toString(),
      );

  static List<String> _stringList(dynamic v) =>
      (v as List<dynamic>? ?? const []).map((e) => e.toString()).toList();
}

/// ผลลัพธ์ทั้งชุดจากการขอเมนู
class MenuResult {
  MenuResult({required this.summary, required this.menus});

  final String summary;
  final List<MenuSuggestion> menus;

  factory MenuResult.fromJson(Map<String, dynamic> json) => MenuResult(
        summary: (json['summary'] ?? '').toString(),
        menus: (json['menus'] as List<dynamic>? ?? const [])
            .map((m) => MenuSuggestion.fromJson(m as Map<String, dynamic>))
            .toList(),
      );

  /// แปลงจากข้อความ JSON ที่ AI ตอบกลับมา
  factory MenuResult.fromJsonText(String text) =>
      MenuResult.fromJson(jsonDecode(text) as Map<String, dynamic>);
}
