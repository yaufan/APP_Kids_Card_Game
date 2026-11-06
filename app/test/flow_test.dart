import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:card_world/app/strings.dart';
import 'package:card_world/core/game.dart';
import 'package:card_world/core/providers.dart';
import 'package:card_world/features/find/find_screen.dart';
import 'package:card_world/features/rest/rest_screen.dart';

import 'helpers.dart';

/// A child's sitting from the card box to the rest, on a phone and a
/// tablet. Screenshots go to `build/screenshots/<device>/`.
void main() {
  Future<void> walk(WidgetTester tester, String device, Size size, double ratio) async {
    await tester.runAsync(loadFonts);
    final app = await TestApp.start(tester, size: size, ratio: ratio);
    await app.settle(800);
    await shoot(tester, device, '01_card_box');

    // Animals: the first card face down, then turned over.
    await app.tapLabel('動物', ms: 800);
    expect(app.location, '/deck/animals');
    expect(app.voice.said.last, '動物');
    await shoot(tester, device, '02_card_back');
    await app.tapLabel(Strings.flipMe, ms: 1200);
    expect(app.sounds.played, contains('flip'));
    expect(app.voice.said.last, '小狗');
    await app.settle(1400);
    expect(app.sounds.played, contains('say_dog'));
    expect(app.game.seen['dog'], 1);
    await shoot(tester, device, '03_dog');

    // Tap again to hear it again; switch to the cartoon picture and back.
    await app.tapLabel('小狗', ms: 600);
    expect(app.voice.said.where((s) => s == '小狗').length, 2);
    await app.tapLabel(Strings.toCartoon, ms: 800);
    expect(app.container.read(cartoonProvider), isTrue);
    expect(app.sounds.played, contains('switch'));
    await shoot(tester, device, '04_dog_cartoon');
    await app.tapLabel(Strings.toReal, ms: 600);
    expect(app.container.read(cartoonProvider), isFalse);

    // The next cards.
    for (final name in ['小貓', '兔子', '牛']) {
      await app.tapLabel(Strings.next, ms: 500);
      await app.tapLabel(Strings.flipMe, ms: 1200);
      expect(app.voice.said.last, name);
    }
    await shoot(tester, device, '05_cow');
    await app.tapLabel(Strings.previous, ms: 500);
    await app.tapLabel(Strings.flipMe, ms: 1200);
    expect(app.voice.said.last, '兔子');

    // 找找看: a wrong card says what it is, the right one moves on.
    await app.tapLabel(Strings.find, ms: 800);
    expect(app.location, '/find/animals');
    final state = tester.state(find.byType(FindScreen)) as dynamic;
    for (var round = 0; round < FindScreen.rounds; round++) {
      final target = state.debugTarget as String;
      final name = book.byId[target]!.zh;
      expect(app.voice.said.last, '$name在哪裡？');
      if (round == 0) await shoot(tester, device, '06_find');
      if (round == 1) {
        final wrong = (state.debugChoices as List<String>).firstWhere((id) => id != target);
        await app.tapLabel(book.byId[wrong]!.zh, ms: 700);
        expect(app.sounds.played.last, 'try');
        expect(app.voice.said.last, '這是${book.byId[wrong]!.zh}喔，再找找$name');
        await shoot(tester, device, '07_find_wrong');
      }
      await app.tapLabel(name, ms: 900);
      expect(app.sounds.played, contains('right'));
      if (round == 0) await shoot(tester, device, '08_find_right');
      await app.settle(2200);
    }
    expect(app.sounds.played.last, 'star');
    expect(find.text(Strings.allFound), findsOneWidget);
    await shoot(tester, device, '09_all_found');
    expect(app.game.found.values.fold(0, (a, b) => a + b), FindScreen.rounds);
    await app.tapLabel(Strings.backToCards, ms: 800);
    expect(app.location, '/deck/animals');
    await app.tapLabel(Strings.home, ms: 800);
    expect(app.location, '/');

    // Fruits, and one at home to find later.
    await app.tapLabel('水果', ms: 800);
    await app.tapLabel(Strings.flipMe, ms: 1200);
    expect(app.voice.said.last, '蘋果');
    await app.tapLabel(Strings.home, ms: 600);

    // Time is up: the rest screen asks to find the apple at home.
    app.now = app.now.add(const Duration(minutes: 10, seconds: 1));
    await app.settle(2400);
    expect(app.location, '/rest');
    expect(app.game.restSince, isNotNull);
    expect(app.sounds.music?.file, 'music_rest');
    expect(find.text(Strings.restLine(book.byId['apple']!)), findsOneWidget);
    await app.settle(800);
    await shoot(tester, device, '10_rest');
    // The card box stays closed while resting.
    app.go('/');
    await app.settle(2400);
    expect(app.location, '/rest');

    // A parent lets play go on.
    await app.tapLabel(Strings.parent, ms: 800);
    await shoot(tester, device, '11_parent_gate');
    final question = find.textContaining('加').evaluate().first.widget as Text;
    final digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    final parts = question.data!.split(' ');
    final sum = digits[parts[0]]! + digits[parts[2]]!;
    for (final d in '$sum'.split('')) {
      await tester.tap(find.byKey(ValueKey('gate-key-$d')));
      await app.settle(200);
    }
    await app.settle(800);
    expect(app.location, '/');
    expect(app.game.restSince, isNull);

    // Parent mode.
    await app.tapLabel(Strings.parent, ms: 800);
    final again = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
    for (final d in '${digits[again[0]]! + digits[again[2]]!}'.split('')) {
      await tester.tap(find.byKey(ValueKey('gate-key-$d')));
      await app.settle(200);
    }
    await app.settle(800);
    expect(app.location, '/parent');
    await shoot(tester, device, '12_parent');
    await tester.tap(find.byKey(const ValueKey('minutes-15')));
    await app.settle();
    expect(app.game.settings.minutes, 15);
    await tester.tap(find.byKey(const ValueKey('choices-3')));
    await app.settle();
    expect(app.game.settings.choices, 3);
    await tester.scrollUntilVisible(find.byKey(const ValueKey('english')), 200);
    await tester.tap(find.byKey(const ValueKey('english')));
    await app.settle();
    expect(app.game.settings.english, isTrue);
    await tester.scrollUntilVisible(find.text(Strings.progress), 300);
    await app.settle();
    await shoot(tester, device, '13_parent_progress');
    await app.end();
  }

  testWidgets('phone: turn cards over, find them, rest, parent mode', (tester) async {
    await walk(tester, 'phone', const Size(1080, 2340), 2.75);
  });

  testWidgets('tablet: the same on a big screen', (tester) async {
    await walk(tester, 'tablet', const Size(2048, 2732), 2);
  });

  testWidgets('a rest carries over when the app opens again', (tester) async {
    final t = DateTime(2026, 11, 6, 10);
    final app = await TestApp.start(tester, game: const Game().rest(t));
    app.now = t.add(const Duration(minutes: 5));
    await app.settle(2400);
    expect(app.location, '/rest');
    expect(find.byType(RestScreen), findsOneWidget);
    // An hour later play goes on by itself.
    app.now = t.add(const Duration(minutes: 61));
    await app.settle(2400);
    expect(app.location, '/');
    expect(app.game.restSince, isNull);
    await app.end();
  });
}
