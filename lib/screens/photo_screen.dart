// ignore_for_file: unused_import, unused_field, unused_element, prefer_final_fields, unused_local_variable
// (คำเตือนพวกนี้จะหายไปเองเมื่อเขียน TODO ครบ — ลบบรรทัดนี้ได้เมื่อทำเสร็จ)
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../data/ai_service.dart';
import '../data/gemini_client.dart';
import '../models/photo_analysis.dart';
import '../widgets/error_box.dart';
import '../widgets/waiting_indicator.dart';
import 'ingredients_screen.dart';

/// หน้า "ถ่ายรูป" → ส่งรูปให้ AI → แสดงของที่เห็น → ต่อยอดเป็นเมนู
class PhotoScreen extends StatefulWidget {
  const PhotoScreen({super.key, required this.ai});
  final AiService ai;

  @override
  State<PhotoScreen> createState() => _PhotoScreenState();
}

class _PhotoScreenState extends State<PhotoScreen> {
  final _picker = ImagePicker();

  Uint8List? _imageBytes; // รูปที่เลือก (เป็น bytes พร้อมส่ง)
  String _mimeType = 'image/jpeg';
  bool _loading = false;
  String? _error;
  PhotoAnalysis? _result;

  /// เปิดกล้องหรือคลังรูป แล้วย่อรูปให้เล็กลงก่อนส่ง (ประหยัดเน็ตและโควตา)
  Future<void> _pickImage(ImageSource source) async {
    // TODO(Step 7.1): เปิดกล้อง/คลังด้วย _picker.pickImage(source: source, maxWidth: 1024,
    //   maxHeight: 1024, imageQuality: 80) → ถ้า null (ผู้ใช้ยกเลิก) ให้ return
    //   อ่าน bytes ด้วย file.readAsBytes() แล้ว setState: _imageBytes, _mimeType
    //   (file.mimeType ?? _guessMime(file.name)) และล้าง _result/_error
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('ยังไม่ได้เขียน _pickImage() — ทำตามคู่มือ Step 7')),
    );
  }

  static String _guessMime(String name) {
    final n = name.toLowerCase();
    if (n.endsWith('.png')) return 'image/png';
    if (n.endsWith('.webp')) return 'image/webp';
    if (n.endsWith('.heic')) return 'image/heic';
    return 'image/jpeg';
  }

  /// ส่งรูปไปให้ AI วิเคราะห์
  Future<void> _analyze() async {
    final bytes = _imageBytes;
    if (bytes == null) return;
    // TODO(Step 7.2): โครงเดียวกับ _ask() ในหน้า IngredientsScreen
    //   แต่เรียก widget.ai.analyzePhoto(bytes, mimeType: _mimeType)
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('ยังไม่ได้เขียน _analyze() — ทำตามคู่มือ Step 7')),
    );
  }

  /// เอาชื่อของที่ AI เห็น ไปเปิดหน้า "เมนูจากวัตถุดิบ"
  void _suggestMenus() {
    final names = _result?.itemNames ?? const [];
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => IngredientsScreen(ai: widget.ai, initialIngredients: names)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final sizeKb = _imageBytes == null ? null : (_imageBytes!.lengthInBytes / 1024).round();
    return Scaffold(
      appBar: AppBar(title: const Text('ถ่ายรูปวัตถุดิบ')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ---- พื้นที่แสดงรูป ----
          AspectRatio(
            aspectRatio: 4 / 3,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade400),
              ),
              clipBehavior: Clip.antiAlias,
              child: _imageBytes == null
                  ? const Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.image_outlined, size: 56, color: Colors.grey),
                          SizedBox(height: 8),
                          Text('ยังไม่ได้เลือกรูป', style: TextStyle(color: Colors.grey)),
                        ],
                      ),
                    )
                  : Image.memory(_imageBytes!, fit: BoxFit.cover),
            ),
          ),
          if (sizeKb != null)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text('ขนาดรูปที่จะส่ง: $sizeKb KB ($_mimeType)',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
            ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _loading ? null : () => _pickImage(ImageSource.camera),
                  icon: const Icon(Icons.photo_camera),
                  label: const Text('ถ่ายรูป'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _loading ? null : () => _pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('เลือกจากคลัง'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          FilledButton.icon(
            onPressed: (_imageBytes == null || _loading) ? null : _analyze,
            icon: const Icon(Icons.auto_awesome),
            label: Text(_loading ? 'AI กำลังดูรูป...' : 'ให้ AI วิเคราะห์รูป'),
          ),
          const SizedBox(height: 16),
          if (_loading) const WaitingIndicator(),
          if (_error != null) ErrorBox(message: _error!, onRetry: _analyze),
          if (_result != null) ..._buildResult(_result!),
        ],
      ),
    );
  }

  List<Widget> _buildResult(PhotoAnalysis r) => [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('AI เห็นอะไรในรูป', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 6),
                Text(r.description),
              ],
            ),
          ),
        ),
        if (r.items.isEmpty)
          const Padding(padding: EdgeInsets.all(8), child: Text('ไม่พบวัตถุดิบในรูปนี้'))
        else
          ...r.items.map(
            (it) => ListTile(
              dense: true,
              leading: const Icon(Icons.check_circle_outline, color: Colors.green),
              title: Text(it.name),
              subtitle: Text([it.amount, it.note].where((s) => s.isNotEmpty).join(' · ')),
            ),
          ),
        if (r.items.isNotEmpty) ...[
          const SizedBox(height: 8),
          FilledButton.tonalIcon(
            onPressed: _suggestMenus,
            icon: const Icon(Icons.restaurant_menu),
            label: Text('แนะนำเมนูจากของ ${r.items.length} อย่างนี้'),
          ),
        ],
      ];
}
