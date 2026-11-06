import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cards.dart';
import 'game.dart';
import 'sounds.dart';
import 'store.dart';
import 'voice.dart';

/// What time it is (tests and screenshots set it).
final clockProvider = Provider<DateTime Function()>((ref) => DateTime.now);

/// Dice for 找找看 (tests give a seeded one).
final randomProvider = Provider<math.Random>((ref) => math.Random());

final storeProvider = Provider<GameStore>((ref) => MemoryStore());
final savedGameProvider = Provider<Game>((ref) => const Game());
final cardBookProvider = Provider<CardBook>((ref) => throw UnimplementedError('loaded in main'));
final soundsProvider = Provider<Sounds>((ref) => const SilentSounds());
final voiceProvider = Provider<Voice>((ref) => const SilentVoice());

/// The game; every change is saved straight away.
final gameProvider = NotifierProvider<GameNotifier, Game>(GameNotifier.new);

class GameNotifier extends Notifier<Game> {
  @override
  Game build() => ref.read(savedGameProvider);

  void change(Game Function(Game g) f) {
    final next = f(state);
    if (identical(next, state)) return;
    state = next;
    ref.read(storeProvider).write(next.toJson());
  }

  void settings(Settings Function(Settings s) f) => change((g) => g.copyWith(settings: f(g.settings)));
}

/// When this sitting started (reset when a parent lets play go on).
final sessionStartProvider = NotifierProvider<SessionStart, DateTime>(SessionStart.new);

class SessionStart extends Notifier<DateTime> {
  @override
  DateTime build() => ref.read(clockProvider)();

  void restart() => state = ref.read(clockProvider)();
}

/// Which picture the cards show now: the parent's choice to begin with,
/// and the child can switch it on any card.
final cartoonProvider = NotifierProvider<CartoonStyle, bool>(CartoonStyle.new);

class CartoonStyle extends Notifier<bool> {
  @override
  bool build() => ref.watch(gameProvider.select((g) => g.settings.cartoon));

  void toggle() => state = !state;
}
