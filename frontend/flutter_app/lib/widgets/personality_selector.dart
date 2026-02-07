import 'package:flutter/material.dart';

class PersonalitySelector extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onChanged;

  PersonalitySelector({required this.selected, required this.onChanged});

  final List<Map<String, String>> options = [
    {"key": "zen_coach", "label": "Zen"},
    {"key": "tough_love", "label": "Tough Love"},
    {"key": "supportive", "label": "Supportive"},
  ];

  @override
  Widget build(BuildContext context) {
    return DropdownButton<String>(
      value: selected,
      underline: SizedBox(),
      items: options
          .map(
            (o) => DropdownMenuItem(value: o['key'], child: Text(o['label']!)),
          )
          .toList(),
      onChanged: (v) {
        if (v != null) onChanged(v);
      },
    );
  }
}
