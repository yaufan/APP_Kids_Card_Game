import 'dart:math' as math;

import 'package:flutter/foundation.dart';
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

/// How much play time this sitting has used (docs/design.md 「每次玩多久」).
/// Only the play-time guard (RestGuard) adds to it; a parent letting play go
/// on starts a new sitting. It begins where the app left off when it was
/// closed and opened again within ten minutes ([SavedSitting]).
final sittingProvider = Provider<Sitting>((ref) {
  final saved = ref.read(savedGameProvider).sitting;
  return Sitting(saved != null && saved.goesOn(ref.read(clockProvider)()) ? saved.played : Duration.zero);
});

class Sitting {
  Sitting([this.played = Duration.zero]);

  Duration played;

  void restart() => played = Duration.zero;
}

/// Whether a card is being turned over and named, or a 找找看 question is
/// being asked and answered: when the play time runs out the rest waits for
/// it (at most a minute). The screen playing holds it, so a screen going
/// away cannot let go of the next screen's card or question; each new card
/// or question is a new [turn], so only the one being played when the time
/// ran out is finished.
final busyProvider = Provider<Busy>((ref) => Busy());

class Busy {
  Object? _owner;
  var _turn = 0;

  bool get busy => _owner != null;

  int get turn => _turn;

  /// [owner] starts a card or a question (one it is still playing goes on).
  void start(Object owner) {
    if (identical(_owner, owner)) return;
    _owner = owner;
    _turn++;
  }

  /// [owner]'s card or question is over (or it went away).
  void end(Object owner) {
    if (identical(_owner, owner)) _owner = null;
  }
}

/// Whether the parent gate is showing (pushed on top of a page): its time,
/// like parent mode's, is not the child's play time, and the play time does
/// not run out under a parent answering it.
final parentGateProvider = Provider<ParentGateShowing>((ref) => ParentGateShowing());

class ParentGateShowing extends ChangeNotifier {
  var _open = 0;

  bool get open => _open > 0;

  void opened() {
    _open++;
    notifyListeners();
  }

  void closed() {
    _open--;
    notifyListeners();
  }
}

/// Which picture the cards show now: the parent's choice to begin with,
/// and the child can switch it on any card.
final cartoonProvider = NotifierProvider<CartoonStyle, bool>(CartoonStyle.new);

class CartoonStyle extends Notifier<bool> {
  @override
  bool build() => ref.watch(gameProvider.select((g) => g.settings.cartoon));

  void toggle() => state = !state;
}
