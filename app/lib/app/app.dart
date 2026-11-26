import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/game.dart';
import '../core/providers.dart';
import '../features/decks/decks_screen.dart';
import '../features/find/find_screen.dart';
import '../features/flip/flip_screen.dart';
import '../features/parent/parent_gate.dart';
import '../features/parent/parent_screen.dart';
import '../features/rest/rest_screen.dart';
import 'strings.dart';
import 'theme.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final resting = ref.read(gameProvider).resting(ref.read(clockProvider)());
  final router = GoRouter(
    initialLocation: resting ? '/rest' : '/',
    // Always start here, whatever page another app asks the phone to open.
    overridePlatformDefaultLocation: true,
    redirect: (_, state) => state.matchedLocation == '/parent' && !ParentPass.take() ? '/' : null,
    routes: [
      GoRoute(path: '/', builder: (_, _) => const DecksScreen()),
      GoRoute(path: '/deck/:id', builder: (_, s) => FlipScreen(deck: s.pathParameters['id']!)),
      GoRoute(path: '/find/:id', builder: (_, s) => FindScreen(deck: s.pathParameters['id']!)),
      GoRoute(path: '/rest', builder: (_, _) => const RestScreen()),
      GoRoute(path: '/parent', builder: (_, _) => const ParentScreen()),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

class CardApp extends ConsumerWidget {
  const CardApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(gameProvider.select((g) => g.settings));
    ref.read(soundsProvider)
      ..music = settings.music
      ..effects = settings.sounds;
    return MaterialApp.router(
      title: Strings.appName,
      debugShowCheckedModeBanner: false,
      theme: CalmTheme.light(),
      locale: const Locale('zh', 'TW'),
      supportedLocales: const [Locale('zh', 'TW')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: ref.watch(routerProvider),
      builder: (_, child) => RestGuard(child: child ?? const SizedBox()),
    );
  }
}

/// Keeps the parent's play time (docs/design.md 「每次玩多久」): when the
/// sitting has used the minutes they set, the cards rest; an hour later (or
/// when a parent says so) play can go on. A card being turned over or a
/// 找找看 question being asked is finished first (at most a minute more).
///
/// Only play counts: not the parent gate or parent mode, not the rest, not
/// the app in the background (while it is out of sight the guard does
/// nothing, so a rest never starts there). Away for ten minutes or more
/// counts as a rest: a new sitting. A phone clock moved back gives no extra
/// time and does not end a rest early. The sitting is kept in the store, so
/// closing the app and opening it again soon goes on with it.
class RestGuard extends ConsumerStatefulWidget {
  const RestGuard({super.key, required this.child});

  final Widget child;

  static const check = Duration(seconds: 2);
  static const awayIsRest = SavedSitting.awayIsRest;

  /// How long a card or a question being played may go on after the time is up.
  static const finishRound = Duration(minutes: 1);

  /// The sitting is saved this often (and when the app goes out of sight).
  static const saveEvery = Duration(seconds: 30);

  @override
  ConsumerState<RestGuard> createState() => _RestGuardState();
}

class _RestGuardState extends ConsumerState<RestGuard> {
  Timer? _timer;
  AppLifecycleListener? _life;
  late final GoRouter _router;
  late final ParentGateShowing _gate;
  late final Sitting _sitting;
  late final DateTime Function() _clock;

  /// When the time not counted yet began, and whether it is play (looked at
  /// again whenever the page, the gate or the app being in sight changes, so
  /// a change is counted the moment it happens).
  late DateTime _from;
  var _playing = false;

  /// Since when the app is out of sight (null: in sight).
  DateTime? _away;

  /// The card or question being finished after the time ran out.
  int? _finishing;
  var _sinceSave = Duration.zero;

  DateTime get _now => _clock();

  String get _path => _router.routerDelegate.currentConfiguration.isEmpty ? '' : _router.state.matchedLocation;

  bool get _parent => _path.startsWith('/parent') || _gate.open;

  @override
  void initState() {
    super.initState();
    _clock = ref.read(clockProvider);
    _router = ref.read(routerProvider);
    _gate = ref.read(parentGateProvider);
    _sitting = ref.read(sittingProvider);
    _from = _now;
    _router.routerDelegate.addListener(_count);
    _gate.addListener(_count);
    _timer = Timer.periodic(RestGuard.check, (_) => _tick());
    _life = AppLifecycleListener(onHide: _hide, onShow: _show);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _count();
      _save();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _life?.dispose();
    _router.routerDelegate.removeListener(_count);
    _gate.removeListener(_count);
    super.dispose();
  }

  /// The time since the last count goes to what was being done until now (a
  /// clock moved back gives nothing), and counting starts afresh.
  void _count() {
    if (!mounted) return;
    final now = _now;
    final d = now.difference(_from);
    if (_playing && !d.isNegative) _sitting.played += d;
    if (!d.isNegative) _sinceSave += d;
    _from = now;
    final path = _path;
    _playing = _away == null && path.isNotEmpty && !_parent && path != '/rest';
  }

  void _tick() {
    if (!mounted) return;
    _count();
    if (_sinceSave >= RestGuard.saveEvery) _save();
    _check();
  }

  void _hide() {
    _count();
    _away = _now;
    _playing = false;
    // Parent mode and the gate close by themselves (ParentWatch); a pass
    // from the gate not used yet is used up, so a child opening the app
    // again has to pass the gate again.
    ParentPass.take();
    _save();
  }

  void _show() {
    final away = _away, now = _now;
    _away = null;
    // Ten minutes away is a rest; less is not play time either (and a clock
    // moved back meanwhile is not a rest).
    if (away != null && now.difference(away) >= RestGuard.awayIsRest) _sitting.restart();
    _from = now;
    _count();
    _check();
  }

  /// The sitting and when the app was last seen, for opening it again.
  void _save() {
    _sinceSave = Duration.zero;
    final now = _away ?? _now;
    final played = _sitting.played;
    ref.read(gameProvider.notifier).change((g) => g.restSince != null ? g : g.copyWith(sitting: SavedSitting(played, now)));
  }

  void _check() {
    // Nothing while the app is out of sight (its timer can go on in the
    // background), and nothing under a parent.
    if (!mounted || _away != null || _parent) return;
    final now = _now;
    final g = ref.read(gameProvider);
    final path = _path;
    final game = ref.read(gameProvider.notifier);
    final restSince = g.restSince;
    if (restSince != null) {
      // A phone clock moved back to before the rest began: the rest starts
      // again from now (so it is not over early, and it does end).
      if (restSince.isAfter(now)) game.change((g) => g.rest(now));
      if (ref.read(gameProvider).resting(now)) {
        if (path != '/rest') _router.go('/rest');
        return;
      }
      game.change((g) => g.playOn());
      _sitting.restart();
      _finishing = null;
      if (path == '/rest') _router.go('/');
      return;
    }
    if (path == '/rest') return;
    final over = _sitting.played - Duration(minutes: g.settings.minutes);
    if (over.isNegative) {
      _finishing = null;
      return;
    }
    // The card or question being played when the time ran out is finished
    // first (not the next one, and at most a minute more).
    final busy = ref.read(busyProvider);
    if (busy.busy && over < RestGuard.finishRound && (_finishing ?? busy.turn) == busy.turn) {
      _finishing = busy.turn;
      return;
    }
    _finishing = null;
    _sitting.restart();
    game.change((g) => g.rest(now));
    _router.go('/rest');
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
