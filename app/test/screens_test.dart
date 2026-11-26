import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:card_world/app/strings.dart';
import 'package:card_world/core/game.dart';
import 'package:card_world/core/providers.dart';
import 'package:card_world/features/find/find_screen.dart';
import 'package:card_world/features/parent/parent_gate.dart';

import 'helpers.dart';

/// The play time, the back key, the voice and parent mode, as the sibling
/// apps were checked for (docs/design.md 「每次玩多久」).
void main() {
  Duration played(TestApp app) => app.container.read(sittingProvider).played;

  /// Plays on the card box for [d] (the guard counts it on its next check).
  Future<void> play(TestApp app, Duration d) async {
    app.now = app.now.add(d);
    await app.settle(2400);
  }

  testWidgets('time in parent mode is not the child\'s play time', (tester) async {
    final app = await TestApp.start(tester);
    await play(app, const Duration(minutes: 3));
    await app.tapLabel(Strings.parent, ms: 800);
    await app.answerGate();
    expect(app.location, '/parent');
    await play(app, const Duration(minutes: 8));
    expect(app.location, '/parent');
    await app.back();
    expect(app.location, '/');
    await app.settle(2400);
    expect(app.location, '/', reason: 'only three minutes were played');
    expect(played(app), const Duration(minutes: 3));
    await play(app, const Duration(minutes: 7, seconds: 1));
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('the time running out does not close the parent gate, and its time is not play time', (tester) async {
    final app = await TestApp.start(tester);
    await play(app, const Duration(minutes: 9, seconds: 50));
    await app.tapLabel(Strings.parent, ms: 800);
    expect(find.byType(ParentGatePage), findsOneWidget);
    await play(app, const Duration(minutes: 2));
    expect(find.byType(ParentGatePage), findsOneWidget, reason: 'a parent is answering');
    expect(app.game.restSince, isNull);
    await app.tapLabel(Strings.cancel, ms: 800);
    await app.settle(2400);
    expect(app.location, '/');
    await play(app, const Duration(seconds: 11));
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('the background is not play time, a rest never starts there, ten minutes away is a new sitting', (tester) async {
    final app = await TestApp.start(tester);
    await play(app, const Duration(minutes: 6));
    await app.hide();
    await play(app, const Duration(minutes: 5));
    await app.show();
    await app.settle(2400);
    expect(app.location, '/');
    expect(played(app), const Duration(minutes: 6), reason: 'a phone call is not play time');

    // The time would run out while the app is away: no rest there, and
    // half an hour away is a rest already.
    await play(app, const Duration(minutes: 3));
    await app.hide();
    await play(app, const Duration(minutes: 30));
    expect(app.game.restSince, isNull);
    expect(app.location, '/');
    await app.show();
    await app.settle(2400);
    expect(app.location, '/');
    expect(played(app), Duration.zero);
    await play(app, const Duration(minutes: 9));
    expect(app.location, '/');
    await play(app, const Duration(minutes: 1, seconds: 1));
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('closing the app and opening it again soon goes on with the sitting', (tester) async {
    final t = DateTime(2026, 11, 6, 10);
    var app = await TestApp.start(tester, now: t);
    await play(app, const Duration(minutes: 4));
    await app.hide();
    final saved = Game.fromJson(app.store.saved);
    expect(saved.sitting!.played, const Duration(minutes: 4));
    expect(saved.sitting!.seen, t.add(const Duration(minutes: 4)));
    await app.show();
    await app.end();

    // Five minutes later: the same sitting, the closed time does not count.
    app = await TestApp.start(tester, game: saved, now: t.add(const Duration(minutes: 9)));
    expect(played(app), const Duration(minutes: 4));
    await play(app, const Duration(minutes: 5, seconds: 50));
    expect(app.location, '/');
    await play(app, const Duration(seconds: 12));
    expect(app.location, '/rest');
    await app.end();

    // Ten minutes or more later: a new sitting.
    app = await TestApp.start(tester, game: saved, now: t.add(const Duration(minutes: 14)));
    expect(played(app), Duration.zero);
    await app.end();

    // A phone clock moved back while it was closed: still the same sitting.
    app = await TestApp.start(tester, game: saved, now: t.subtract(const Duration(hours: 3)));
    expect(played(app), const Duration(minutes: 4));
    await app.end();
  });

  testWidgets('a phone clock moved back gives no extra play time and does not end a rest early', (tester) async {
    final app = await TestApp.start(tester);
    await play(app, const Duration(minutes: 9));
    await play(app, const Duration(hours: -1));
    expect(played(app), const Duration(minutes: 9));
    await play(app, const Duration(minutes: 1, seconds: 1));
    expect(app.location, '/rest');
    // Back by two hours in the rest: the rest goes on (an hour from now).
    await play(app, const Duration(hours: -2));
    expect(app.location, '/rest');
    expect(app.game.restSince, app.now);
    await play(app, const Duration(minutes: 59));
    expect(app.location, '/rest');
    await play(app, const Duration(minutes: 2));
    expect(app.location, '/');
    await app.end();
  });

  testWidgets('time up during a 找找看 question: that question is finished first, at most a minute', (tester) async {
    final app = await TestApp.start(tester);
    await app.tapLabel('動物', ms: 800);
    await app.tapLabel(Strings.find, ms: 800);
    expect(app.location, '/find/animals');
    await play(app, const Duration(minutes: 10, seconds: 1));
    expect(app.location, '/find/animals', reason: 'the question being asked is finished');
    final state = tester.state(find.byType(FindScreen)) as dynamic;
    await app.tapLabel(book.byId[state.debugTarget as String]!.zh, ms: 900);
    await app.settle(2400);
    expect(app.location, '/find/animals', reason: 'still saying 「對了！」');
    await app.settle(2400);
    expect(app.location, '/rest', reason: 'not the next question');

    // A question nobody answers: the rest a minute later.
    app.container.read(gameProvider.notifier).change((g) => g.playOn());
    app.container.read(sittingProvider).restart();
    await app.settle(2400);
    app.go('/deck/animals');
    await app.settle(800);
    await app.tapLabel(Strings.find, ms: 800);
    await play(app, const Duration(minutes: 10, seconds: 1));
    expect(app.location, '/find/animals');
    await play(app, const Duration(seconds: 50));
    expect(app.location, '/find/animals');
    await play(app, const Duration(seconds: 10));
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('time up while a card is being named: the name and its sound first', (tester) async {
    final voice = SlowVoice();
    final app = await TestApp.start(tester, voice: voice);
    voice.held = false;
    await app.tapLabel('動物', ms: 800);
    voice.held = true;
    await app.tapLabel(Strings.flipMe, ms: 900);
    expect(voice.said.last, '小狗');
    await play(app, const Duration(minutes: 10, seconds: 1));
    expect(app.location, '/deck/animals', reason: '小狗 is still being said');
    voice.finish();
    await app.settle(600);
    expect(app.sounds.played.last, 'say_dog');
    await app.settle(2400);
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('the system back key goes where the screen\'s own button goes; at home and in the rest it does nothing', (tester) async {
    final closed = <String>[];
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, (call) async {
      if (call.method == 'SystemNavigator.pop') closed.add(call.method);
      return null;
    });
    addTearDown(() => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, null));
    final app = await TestApp.start(tester);
    await app.back();
    expect(app.location, '/');
    expect(closed, isEmpty, reason: 'the card box is home: the app stays open');

    await app.tapLabel('動物', ms: 800);
    await app.tapLabel(Strings.find, ms: 800);
    await app.back();
    expect(app.location, '/deck/animals', reason: 'as 回去');
    await app.back();
    expect(app.location, '/', reason: 'as 回卡片盒');

    await app.tapLabel(Strings.parent, ms: 800);
    await app.back();
    expect(find.byType(ParentGatePage), findsNothing, reason: 'as 取消');
    expect(app.location, '/');
    await app.tapLabel(Strings.parent, ms: 800);
    await app.answerGate();
    expect(app.location, '/parent');
    await app.back();
    expect(app.location, '/');

    await play(app, const Duration(minutes: 10, seconds: 1));
    expect(app.location, '/rest');
    await app.back();
    expect(app.location, '/rest');
    expect(closed, isEmpty);
    await app.end();
  });

  testWidgets('leaving 找找看 stops its question, never the next screen\'s first line', (tester) async {
    final app = await TestApp.start(tester);
    await app.tapLabel('動物', ms: 800);
    await app.tapLabel(Strings.find, ms: 800);
    expect(app.voice.log.last, endsWith('在哪裡？'));
    await app.back();
    expect(app.voice.log.last, '(stop)', reason: 'the question is not said over 翻翻卡');

    // The rest comes while 找找看 is showing (nobody answers for a minute):
    // 找找看 going away does not cut off the rest's line.
    await app.tapLabel(Strings.find, ms: 800);
    await play(app, const Duration(minutes: 11, seconds: 1));
    expect(app.location, '/rest');
    await app.settle(1200);
    expect(app.voice.log.last, startsWith('眼睛休息一下'));
    await app.end();
  });

  testWidgets('parent mode and the gate close when the app goes to the background or after five quiet minutes', (tester) async {
    final app = await TestApp.start(tester);
    await app.tapLabel(Strings.parent, ms: 800);
    await app.hide();
    await app.show();
    await app.settle(1000);
    expect(find.byType(ParentGatePage), findsNothing);

    await app.tapLabel(Strings.parent, ms: 800);
    await app.answerGate();
    expect(app.location, '/parent');
    await app.hide();
    await app.show();
    expect(app.location, '/');
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up: the gate again');

    await app.tapLabel(Strings.parent, ms: 800);
    await app.answerGate();
    expect(app.location, '/parent');
    await tester.pump(const Duration(minutes: 4));
    await tester.tap(find.byKey(const ValueKey('minutes-15')));
    await tester.pump(const Duration(minutes: 4));
    expect(app.location, '/parent', reason: 'a touch keeps it open');
    await tester.pump(const Duration(minutes: 1, seconds: 1));
    await app.settle();
    expect(app.location, '/');

    await app.tapLabel(Strings.parent, ms: 800);
    await tester.pump(const Duration(minutes: 5, seconds: 1));
    await app.settle(1000);
    expect(find.byType(ParentGatePage), findsNothing);
    await app.end();
  });

  testWidgets('the gate locks for one minute, then five, then fifteen; closing the app does not open it', (tester) async {
    final t = DateTime(2026, 11, 6, 10);
    var app = await TestApp.start(tester, now: t);
    Future<void> miss(int times) async {
      for (var i = 0; i < times; i++) {
        await app.answerGate(right: false);
      }
    }

    await app.tapLabel(Strings.parent, ms: 800);
    await miss(3);
    expect(find.text(Strings.gateWait(const Duration(minutes: 1))), findsOneWidget);
    app.now = t.add(const Duration(minutes: 1, seconds: 1));
    await app.settle(1200);
    await miss(3);
    expect(find.text(Strings.gateWait(const Duration(minutes: 5))), findsOneWidget);

    // Closed and opened again: still locked.
    final saved = Game.fromJson(app.store.saved);
    await app.end();
    app = await TestApp.start(tester, game: saved, now: t.add(const Duration(minutes: 3)));
    await app.tapLabel(Strings.parent, ms: 800);
    expect(find.textContaining('加'), findsNothing);
    expect(find.text(Strings.gateWait(const Duration(minutes: 3, seconds: 1))), findsOneWidget);
    app.now = t.add(const Duration(minutes: 7, seconds: 2));
    await app.settle(1200);
    await miss(3);
    expect(find.text(Strings.gateWait(const Duration(minutes: 15))), findsOneWidget);

    // The phone clock moved back a day: locked fifteen minutes from now, not a day.
    app.now = app.now.subtract(const Duration(days: 1));
    await app.settle(1200);
    expect(find.text(Strings.gateWait(const Duration(minutes: 15))), findsOneWidget);
    app.now = app.now.add(const Duration(minutes: 15, seconds: 1));
    await app.settle(1200);
    // A right answer opens it, and the next lock is one minute again.
    await app.answerGate();
    expect(app.location, '/parent');
    expect(app.game.gate.locks, 0);
    await app.end();
  });
}
