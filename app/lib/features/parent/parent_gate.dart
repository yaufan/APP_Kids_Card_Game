import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/game.dart';
import '../../core/providers.dart';

/// A question a grown-up answers easily but a 2 to 4 year old cannot read:
/// the numbers are written out in Chinese characters (as in 畫畫小鎮).
class ParentGateChallenge {
  ParentGateChallenge(this.a, this.b);

  factory ParentGateChallenge.random([math.Random? random]) {
    final r = random ?? math.Random();
    return ParentGateChallenge(3 + r.nextInt(7), 3 + r.nextInt(7));
  }

  final int a;
  final int b;

  static const _digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];

  String get question => Strings.gateQuestion(_digits[a], _digits[b]);

  int get answer => a + b;

  bool check(String typed) => int.tryParse(typed.trim()) == answer;
}

/// Completes with true only for a right answer; with [pass] the answer also
/// lets parent mode open (once).
Future<bool> showParentGate(BuildContext context, {bool pass = true}) async {
  final ok = await Navigator.of(context).push<bool>(
    MaterialPageRoute(fullscreenDialog: true, builder: (_) => const ParentGatePage()),
  );
  if ((ok ?? false) && pass) ParentPass.grant();
  return ok ?? false;
}

/// Parent mode opens only right after the gate was answered: the router
/// takes the pass, so nothing else (a link from another app) can open it.
abstract final class ParentPass {
  static var _open = false;

  static void grant() => _open = true;

  /// Whether parent mode may open now (once per right answer).
  static bool take() {
    final open = _open;
    _open = false;
    return open;
  }
}

/// Closes a parent page (the gate, parent mode) when the app goes to the
/// background or after five minutes without a touch, so a child picking up
/// the phone later has to pass the gate again.
class ParentWatch extends StatefulWidget {
  const ParentWatch({super.key, required this.onClose, required this.child});

  static const idle = Duration(minutes: 5);

  final VoidCallback onClose;
  final Widget child;

  @override
  State<ParentWatch> createState() => _ParentWatchState();
}

class _ParentWatchState extends State<ParentWatch> {
  Timer? _idle;
  AppLifecycleListener? _life;
  var _closed = false;

  @override
  void initState() {
    super.initState();
    _life = AppLifecycleListener(onHide: _close);
    _wake();
  }

  @override
  void dispose() {
    _idle?.cancel();
    _life?.dispose();
    super.dispose();
  }

  void _wake() {
    _idle?.cancel();
    _idle = Timer(ParentWatch.idle, _close);
  }

  void _close() {
    if (_closed || !mounted) return;
    _closed = true;
    _idle?.cancel();
    ParentPass.take();
    widget.onClose();
  }

  @override
  Widget build(BuildContext context) => Listener(behavior: HitTestBehavior.translucent, onPointerDown: (_) => _wake(), child: widget.child);
}

/// Full screen, so a child cannot tap past it. Three wrong answers in a row
/// and it waits: a minute, then five, then fifteen (kept in the game, so
/// closing the app does not open it; a right answer starts again at one).
class ParentGatePage extends ConsumerStatefulWidget {
  const ParentGatePage({super.key, this.random});

  final math.Random? random;

  @override
  ConsumerState<ParentGatePage> createState() => _ParentGatePageState();
}

class _ParentGatePageState extends ConsumerState<ParentGatePage> {
  late var _challenge = ParentGateChallenge.random(widget.random);
  late final ParentGateShowing _showing;
  var _typed = '';
  var _wrong = false;
  var _shownLocked = false;
  Timer? _tick;

  @override
  void initState() {
    super.initState();
    _showing = ref.read(parentGateProvider)..opened();
    _tick = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      _rebase();
      // The seconds count down, and the question comes back when it opens.
      if (_shownLocked || _left > Duration.zero) setState(() {});
    });
  }

  @override
  void dispose() {
    _tick?.cancel();
    _showing.closed();
    super.dispose();
  }

  DateTime get _now => ref.read(clockProvider)();

  /// How long the gate is still locked.
  Duration get _left {
    final now = _now;
    return ref.read(gameProvider).gate.at(now).left(now);
  }

  /// A phone clock moved back to before the lock began: the lock starts
  /// again from now (so it does end).
  void _rebase() {
    final now = _now;
    final lock = ref.read(gameProvider).gate;
    final seen = lock.at(now);
    if (!identical(seen, lock)) ref.read(gameProvider.notifier).change((g) => g.copyWith(gate: seen));
  }

  void _key(String k) {
    _rebase();
    if (_left > Duration.zero) return;
    setState(() {
      _wrong = false;
      if (k == '⌫') {
        if (_typed.isNotEmpty) _typed = _typed.substring(0, _typed.length - 1);
        return;
      }
      if (_typed.length >= 2) return;
      _typed += k;
    });
    if (_typed.length < '${_challenge.answer}'.length) return;
    final game = ref.read(gameProvider.notifier);
    if (_challenge.check(_typed)) {
      game.change((g) => g.copyWith(gate: const GateLock()));
      Navigator.of(context).pop(true);
      return;
    }
    final now = _now;
    game.change((g) => g.copyWith(gate: g.gate.miss(now)));
    setState(() {
      _wrong = true;
      _typed = '';
      _challenge = ParentGateChallenge.random(widget.random);
    });
  }

  @override
  Widget build(BuildContext context) {
    ref.watch(gameProvider.select((g) => g.gate));
    final left = _left;
    final locked = _shownLocked = left > Duration.zero;
    final need = '${_challenge.answer}'.length;
    Widget box(int i) => Container(
          width: 60,
          height: 70,
          margin: const EdgeInsets.only(right: 12),
          alignment: Alignment.center,
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(16), border: Border.all(color: i < _typed.length ? Calm.teal : Calm.paperDeep, width: 2.5)),
          child: Text(i < _typed.length ? _typed[i] : '', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w700)),
        );
    Widget key(String k) => Semantics(
          key: ValueKey('gate-key-$k'),
          container: true,
          button: true,
          label: k == '⌫' ? Strings.backspace : k,
          excludeSemantics: true,
          child: Pressable(
            onTap: locked ? null : () => _key(k),
            child: Container(
              height: 64,
              alignment: Alignment.center,
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18), border: Border.all(color: Calm.paperDeep)),
              child: k == '⌫' ? const Icon(Icons.backspace_outlined, color: Calm.inkSoft) : Text(k, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
            ),
          ),
        );
    final page = Scaffold(
      backgroundColor: Calm.parentBg,
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: ListView(padding: const EdgeInsets.all(20), children: [
              Row(children: [
                const Expanded(
                  child: SoftCard(
                    padding: EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                    child: Text(Strings.callParent, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                  ),
                ),
                const SizedBox(width: 8),
                RoundButton(label: Strings.cancel, icon: Icons.close_rounded, onTap: () => Navigator.of(context).pop(false)),
              ]),
              const SizedBox(height: 18),
              Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Row(children: [
                    Icon(Icons.lock_outline_rounded, size: 18, color: Calm.inkSoft),
                    SizedBox(width: 8),
                    Text(Strings.parentGateTitle, style: TextStyle(fontSize: 15, color: Calm.inkSoft)),
                  ]),
                  const SizedBox(height: 10),
                  Text(locked ? Strings.gateWait(left) : _challenge.question, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 18),
                  if (!locked) Row(children: [for (var i = 0; i < need; i++) box(i)]),
                  const SizedBox(height: 14),
                  Text(_wrong ? Strings.wrongAnswer : Strings.gateRules, style: TextStyle(fontSize: 14, color: _wrong ? const Color(0xFFD9655A) : Calm.inkSoft)),
                ]),
              ),
              const SizedBox(height: 22),
              GridView.count(
                crossAxisCount: 3,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.7,
                children: [
                  for (final k in ['1', '2', '3', '4', '5', '6', '7', '8', '9']) key(k),
                  const SizedBox.shrink(),
                  key('0'),
                  key('⌫'),
                ],
              ),
            ]),
          ),
        ),
      ),
    );
    return ParentWatch(onClose: () => Navigator.of(context).pop(false), child: page);
  }
}
