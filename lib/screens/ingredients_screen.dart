import 'package:flutter/material.dart';

import '../data/ai_service.dart';
import '../data/gemini_client.dart';
import '../models/menu_suggestion.dart';
import '../widgets/error_box.dart';
import '../widgets/menu_card.dart';

/// หน้า "พิมพ์วัตถุดิบ" → ส่งให้ AI → แสดงเมนูแนะนำ
class IngredientsScreen extends StatefulWidget {
  const IngredientsScreen({super.key, required this.ai, this.initialIngredients = const []});

  final AiService ai;

  /// รายการเริ่มต้น (หน้า "ถ่ายรูป" ส่งมาให้)
  final List<String> initialIngredients;

  @override
  State<IngredientsScreen> createState() => _IngredientsScreenState();
}

class _IngredientsScreenState extends State<IngredientsScreen> {
  final _inputCtrl = TextEditingController();
  final _extraCtrl = TextEditingController();
  late final List<String> _ingredients = [...widget.initialIngredients];

  bool _loading = false;
  String? _error;
  MenuResult? _result;

  @override
  void dispose() {
    _inputCtrl.dispose();
    _extraCtrl.dispose();
    super.dispose();
  }

  /// เพิ่มวัตถุดิบจากช่องพิมพ์ (พิมพ์หลายอย่างคั่นด้วย , ได้)
  void _addIngredient() {
    final items = _inputCtrl.text
        .split(RegExp(r'[,\n]'))
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty && !_ingredients.contains(e));
    setState(() => _ingredients.addAll(items));
    _inputCtrl.clear();
  }

  /// ส่งรายการวัตถุดิบไปถาม AI
  Future<void> _ask() async {
    if (_ingredients.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('ใส่วัตถุดิบอย่างน้อย 1 อย่างก่อน')));
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });
    try {
      final result = await widget.ai.suggestMenus(_ingredients, extra: _extraCtrl.text);
      if (!mounted) return;
      setState(() => _result = result);
    } on AiException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (e) {
      // เช่น AI ตอบ JSON ผิดรูปแบบ → FormatException
      if (!mounted) return;
      setState(() => _error = 'อ่านคำตอบของ AI ไม่ได้: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('เมนูจากวัตถุดิบ')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ---- ช่องพิมพ์วัตถุดิบ ----
          TextField(
            controller: _inputCtrl,
            decoration: InputDecoration(
              labelText: 'วัตถุดิบที่มี',
              hintText: 'เช่น ไข่, หมูสับ, กระเทียม',
              suffixIcon: IconButton(icon: const Icon(Icons.add), onPressed: _addIngredient),
            ),
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _addIngredient(),
          ),
          const SizedBox(height: 10),
          // ---- รายการที่เพิ่มแล้ว (chips) ----
          if (_ingredients.isEmpty)
            Text('ยังไม่มีรายการ — พิมพ์แล้วกด + หรือ Enter',
                style: TextStyle(color: Colors.grey.shade600))
          else
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: _ingredients
                  .map((item) => InputChip(
                        label: Text(item),
                        onDeleted: () => setState(() => _ingredients.remove(item)),
                      ))
                  .toList(),
            ),
          const SizedBox(height: 12),
          TextField(
            controller: _extraCtrl,
            decoration: const InputDecoration(
              labelText: 'เงื่อนไขเพิ่มเติม (ไม่บังคับ)',
              hintText: 'เช่น ไม่กินเผ็ด, ทำใน 15 นาที, มังสวิรัติ',
            ),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _loading ? null : _ask,
            icon: const Icon(Icons.auto_awesome),
            label: Text(_loading ? 'AI กำลังคิด...' : 'ให้ AI แนะนำเมนู'),
          ),
          const SizedBox(height: 16),
          // ---- ส่วนแสดงผล: กำลังโหลด / ผิดพลาด / ผลลัพธ์ ----
          if (_loading) const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
          if (_error != null) ErrorBox(message: _error!, onRetry: _ask),
          if (_result != null) ..._buildResult(_result!),
        ],
      ),
    );
  }

  List<Widget> _buildResult(MenuResult r) => [
        if (r.summary.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(r.summary, style: const TextStyle(fontStyle: FontStyle.italic)),
          ),
        Text('เมนูแนะนำ ${r.menus.length} รายการ',
            style: Theme.of(context).textTheme.titleMedium),
        ...r.menus.asMap().entries.map((e) => MenuCard(menu: e.value, initiallyExpanded: e.key == 0)),
      ];
}
