import 'package:flutter/material.dart';

/// สีหลักของแอป — เขียวครัว · ส้มอำพัน
const Color kPrimary = Color(0xFF2E7D32);
const Color kAccent = Color(0xFFFF8F00);

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(seedColor: kPrimary);
  return ThemeData(
    colorScheme: scheme,
    useMaterial3: true,
    appBarTheme: AppBarTheme(
      backgroundColor: kPrimary,
      foregroundColor: Colors.white,
      centerTitle: true,
      titleTextStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: Colors.white),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(48),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ),
    inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
    cardTheme: const CardThemeData(elevation: 1, margin: EdgeInsets.symmetric(vertical: 6)),
  );
}
