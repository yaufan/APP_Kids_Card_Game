import 'package:flutter/material.dart';

/// 小卡認天下's colours: quiet paper, a soft teal and one colour for each
/// deck (docs/design.md: slow, calm screens with nothing flashing).
abstract final class Calm {
  static const paper = Color(0xFFF4F0E8);
  static const paperDeep = Color(0xFFE6DED1);
  static const ink = Color(0xFF3E4A4A);
  static const inkSoft = Color(0xFF8A9592);

  static const teal = Color(0xFF4E9A8F);
  static const tealDeep = Color(0xFF3B7F75);
  static const tealSoft = Color(0xFFDCEDE9);
  static const gold = Color(0xFFF2C14E);
  static const night = Color(0xFF2E3A66);

  static const parentBg = Color(0xFFF2F4F5);

  static const decks = {
    'animals': Color(0xFFE5A65A),
    'fruits': Color(0xFF8BB86C),
    'vehicles': Color(0xFF5B8FC9),
    'body': Color(0xFFE39A8A),
    'home': Color(0xFF4E9A8F),
    'clothes': Color(0xFFA48BCF),
  };

  static Color deck(String id) => decks[id] ?? teal;
}

abstract final class CalmTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Calm.teal, surface: Calm.paper),
      scaffoldBackgroundColor: Calm.paper,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Calm.ink, displayColor: Calm.ink, fontFamily: font));
  }
}
