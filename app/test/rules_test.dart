import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:card_world/core/find.dart';
import 'package:card_world/core/game.dart';
import 'package:card_world/core/store.dart';
import 'package:card_world/features/rest/rest_screen.dart';

import 'helpers.dart';

/// The cards, 找找看's rounds, the play time and the saved game.
void main() {
  test('six decks of twenty, the same as design/cards.json', () {
    final design = jsonDecode(File('../design/cards.json').readAsStringSync());
    expect(jsonDecode(File('assets/cards.json').readAsStringSync()), design);
    expect(book.decks.map((d) => d.id), ['animals', 'fruits', 'vehicles', 'body', 'home', 'clothes']);
    for (final d in book.decks) {
      expect(d.cards.length, 20, reason: d.id);
    }
    expect(book.byId.length, 120, reason: 'every card has its own id');
  });

  test('every card has both pictures, and every sound it asks for exists', () {
    final missing = <String>[];
    for (final d in book.decks) {
      for (final c in d.cards) {
        for (final cartoon in [false, true]) {
          final f = File(c.art(cartoon: cartoon));
          if (!f.existsSync() || !f.readAsStringSync().trimRight().endsWith('</svg>')) missing.add(f.path);
        }
        final s = c.sound;
        if (s != null && !File('assets/sounds/$s.wav').existsSync()) missing.add('sound $s');
      }
    }
    for (final s in ['music_play', 'music_rest', 'tap', 'flip', 'next', 'switch', 'right', 'try', 'star', 'rest']) {
      if (!File('assets/sounds/$s.wav').existsSync()) missing.add('sound $s');
    }
    expect(missing, isEmpty);
  });

  test('找找看 asks for one card among different cards, never the same twice running', () {
    final r = math.Random(4);
    final animals = book.deck('animals')!;
    String? last;
    for (var i = 0; i < 40; i++) {
      final n = 2 + i % 3;
      final round = FindRound.deal(animals, n, r, last: last);
      expect(round.choices.length, n);
      expect(round.choices.map((c) => c.id).toSet().length, n);
      expect(round.choices, contains(round.target));
      expect(round.target.id, isNot(last));
      expect(round.choices.every((c) => c.deck == 'animals'), isTrue);
      last = round.target.id;
    }
    // Once a few cards were turned over, it asks for those.
    final seen = {'dog', 'cat', 'cow'};
    for (var i = 0; i < 20; i++) {
      expect(seen, contains(FindRound.deal(animals, 2, r, seen: seen).target.id));
    }
  });

  test('play time: resting lasts an hour or until a parent says so', () {
    final t = DateTime(2026, 11, 6, 10);
    var g = const Game().rest(t);
    expect(g.resting(t.add(const Duration(minutes: 59))), isTrue);
    expect(g.resting(t.add(const Duration(minutes: 61))), isFalse);
    g = g.playOn();
    expect(g.restSince, isNull);
    expect(g.resting(t), isFalse);
  });

  test('cards seen and found; a card is known after three finds', () async {
    var g = const Game().saw('dog').saw('cat').saw('dog').foundCard('dog').foundCard('dog');
    expect(g.seen, {'dog': 2, 'cat': 1});
    expect(g.recent, ['dog', 'cat']);
    expect(g.knows('dog'), isFalse);
    g = g.foundCard('dog');
    expect(g.knows('dog'), isTrue);
    g = g.rest(DateTime(2026, 11, 6, 10)).copyWith(settings: const Settings(minutes: 15, cartoon: true, english: true, choices: 3, music: false));
    final store = MemoryStore()..write(g.toJson());
    final back = Game.fromJson(await store.read());
    expect(back.toJson(), g.toJson());
    expect(Game.fromJson({'seen': 3, 'recent': 'x', 'restSince': 5, 'settings': {'minutes': 7, 'choices': 9}}).settings.minutes, 10);
    expect(Game.fromJson({'settings': {'choices': 9}}).settings.choices, 4);
  });

  test('the rest screen sends the child to find something just seen at home', () {
    expect(RestScreen.pick(book, ['dog', 'banana', 'cup']).id, 'banana');
    expect(RestScreen.pick(book, ['dog', 'car']).id, 'cup');
    expect(RestScreen.pick(book, ['nose']).id, 'nose');
  });
}
