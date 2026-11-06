import 'dart:convert';

import 'package:flutter/services.dart';

/// One picture card (assets/cards.json, from design/cards.json).
class CardItem {
  const CardItem({required this.id, required this.deck, required this.zh, required this.en, this.says = ''});

  final String id;
  final String deck;
  final String zh;
  final String en;

  /// The sound it makes, written out for the card ("汪汪"); empty when it
  /// has none.
  final String says;

  /// Its pictures: the realistic one and the cartoon one.
  String art({required bool cartoon}) => 'assets/art/cards/$deck/$id${cartoon ? '_cartoon' : ''}.svg';

  /// Its own sound (design/sounds/), when it has one.
  String? get sound => (deck == 'animals' || deck == 'vehicles' || says.isNotEmpty) ? 'say_$id' : null;
}

class Deck {
  const Deck({required this.id, required this.zh, required this.en, required this.cards});

  final String id;
  final String zh;
  final String en;
  final List<CardItem> cards;
}

class CardBook {
  CardBook(this.decks) : byId = {for (final d in decks) for (final c in d.cards) c.id: c};

  final List<Deck> decks;
  final Map<String, CardItem> byId;

  Deck? deck(String id) => decks.where((d) => d.id == id).firstOrNull;

  factory CardBook.fromJson(Map<String, dynamic> j) => CardBook([
        for (final d in j['decks'] as List)
          Deck(
            id: (d as Map)['id'] as String,
            zh: d['zh'] as String,
            en: d['en'] as String,
            cards: [
              for (final c in d['cards'] as List)
                CardItem(id: (c as Map)['id'] as String, deck: d['id'] as String, zh: c['zh'] as String, en: c['en'] as String, says: c['says'] as String? ?? ''),
            ],
          ),
      ]);

  static Future<CardBook> load([AssetBundle? bundle]) async =>
      CardBook.fromJson(jsonDecode(await (bundle ?? rootBundle).loadString('assets/cards.json')) as Map<String, dynamic>);
}
