import 'package:flutter/material.dart';

import '../models/menu_suggestion.dart';
import '../theme.dart';

/// การ์ดเมนู 1 รายการ — กดเพื่อขยายดูวัตถุดิบและวิธีทำ
class MenuCard extends StatelessWidget {
  const MenuCard({super.key, required this.menu, this.initiallyExpanded = false});

  final MenuSuggestion menu;
  final bool initiallyExpanded;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      clipBehavior: Clip.antiAlias,
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        leading: CircleAvatar(
          backgroundColor: scheme.primaryContainer,
          child: const Icon(Icons.restaurant, color: kPrimary),
        ),
        title: Text(menu.name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Wrap(
            spacing: 6,
            runSpacing: 4,
            children: [
              _Tag(icon: Icons.schedule, text: menu.time),
              _Tag(icon: Icons.signal_cellular_alt, text: menu.difficulty),
              if (menu.missing.isEmpty)
                const _Tag(icon: Icons.check_circle, text: 'ของครบ', color: kPrimary)
              else
                _Tag(icon: Icons.shopping_cart, text: 'ซื้อเพิ่ม ${menu.missing.length}', color: kAccent),
            ],
          ),
        ),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(menu.description),
          const SizedBox(height: 12),
          const _SectionTitle('วัตถุดิบ'),
          ...menu.ingredients.map((e) => _Bullet(e)),
          if (menu.missing.isNotEmpty) ...[
            const SizedBox(height: 8),
            const _SectionTitle('ต้องซื้อเพิ่ม', color: kAccent),
            Wrap(
              spacing: 6,
              children: menu.missing
                  .map((m) => Chip(
                        label: Text(m),
                        avatar: const Icon(Icons.add_shopping_cart, size: 16),
                        visualDensity: VisualDensity.compact,
                      ))
                  .toList(),
            ),
          ],
          const SizedBox(height: 8),
          const _SectionTitle('วิธีทำ'),
          ...List.generate(menu.steps.length, (i) => _Step(i + 1, menu.steps[i])),
        ],
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  const _Tag({required this.icon, required this.text, this.color});
  final IconData icon;
  final String text;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = color ?? Colors.grey.shade700;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: c),
        const SizedBox(width: 3),
        Text(text, style: TextStyle(fontSize: 12, color: c)),
      ],
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.text, {this.color = kPrimary});
  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Text(text, style: TextStyle(fontWeight: FontWeight.bold, color: color)),
      );
}

class _Bullet extends StatelessWidget {
  const _Bullet(this.text);
  final String text;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 2),
        child: Text('• $text'),
      );
}

class _Step extends StatelessWidget {
  const _Step(this.no, this.text);
  final int no;
  final String text;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 11,
              backgroundColor: kPrimary,
              child: Text('$no', style: const TextStyle(color: Colors.white, fontSize: 12)),
            ),
            const SizedBox(width: 8),
            Expanded(child: Text(text)),
          ],
        ),
      );
}
