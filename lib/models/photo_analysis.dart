import 'dart:convert';

/// ของ 1 ชิ้นที่ AI เห็นในรูป
class FoundItem {
  FoundItem({required this.name, required this.amount, required this.note});

  final String name;
  final String amount;
  final String note;

  factory FoundItem.fromJson(Map<String, dynamic> json) => FoundItem(
        name: (json['name'] ?? '').toString(),
        amount: (json['amount'] ?? '').toString(),
        note: (json['note'] ?? '').toString(),
      );
}

/// ผลการวิเคราะห์รูป 1 รูป
class PhotoAnalysis {
  PhotoAnalysis({required this.description, required this.items});

  final String description;
  final List<FoundItem> items;

  /// ชื่อวัตถุดิบล้วน ๆ เอาไปส่งต่อให้หน้า "แนะนำเมนู"
  List<String> get itemNames => items.map((e) => e.name).where((n) => n.isNotEmpty).toList();

  factory PhotoAnalysis.fromJson(Map<String, dynamic> json) => PhotoAnalysis(
        description: (json['description'] ?? '').toString(),
        items: (json['items'] as List<dynamic>? ?? const [])
            .map((e) => FoundItem.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  factory PhotoAnalysis.fromJsonText(String text) =>
      PhotoAnalysis.fromJson(jsonDecode(text) as Map<String, dynamic>);
}
