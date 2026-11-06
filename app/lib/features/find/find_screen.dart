import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/cards.dart';
import '../../core/find.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../../core/voice.dart';

/// 找找看: "小狗在哪裡？" among two cards (three or four if the parent
/// chose). A wrong card only says what it is; five found and a star.
class FindScreen extends ConsumerStatefulWidget {
  const FindScreen({super.key, required this.deck});

  final String deck;

  static const rounds = 5;

  @override
  ConsumerState<FindScreen> createState() => _FindScreenState();
}

class _FindScreenState extends ConsumerState<FindScreen> with SingleTickerProviderStateMixin {
  late final Sounds _sounds;
  late final Voice _voice;
  late final _star = AnimationController(vsync: this, duration: const Duration(milliseconds: 900));
  late FindRound _round;
  var _done = 0;
  String? _right;
  String? _named;
  final _wiggles = <String, int>{};
  var _finished = false;
  Timer? _later;
  Timer? _next;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _voice = ref.read(voiceProvider);
    _sounds.hold(this, Music.play);
    _deal();
    WidgetsBinding.instance.addPostFrameCallback((_) => _ask());
  }

  @override
  void dispose() {
    _later?.cancel();
    _next?.cancel();
    _star.dispose();
    _sounds.release(this);
    super.dispose();
  }

  Deck get _deck => ref.read(cardBookProvider).deck(widget.deck)!;

  @visibleForTesting
  String get debugTarget => _round.target.id;

  @visibleForTesting
  List<String> get debugChoices => [for (final c in _round.choices) c.id];

  void _deal({String? last}) {
    final g = ref.read(gameProvider);
    _round = FindRound.deal(_deck, g.settings.choices, ref.read(randomProvider), last: last, seen: g.seen.keys.toSet());
    _right = null;
    _named = null;
  }

  void _say(String zh, {String? en}) {
    final s = ref.read(gameProvider).settings;
    if (mounted && s.voice) _voice.say(zh, en: s.english ? en : null);
  }

  void _ask() => _say(Strings.whereIs(_round.target), en: _round.target.en);

  void _pick(CardItem c) {
    if (_right != null || _finished) return;
    final target = _round.target;
    if (c.id == target.id) {
      _sounds.play('right');
      setState(() {
        _right = c.id;
        _named = null;
      });
      ref.read(gameProvider.notifier).change((g) => g.foundCard(c.id));
      _say(Strings.rightIs(c), en: c.en);
      final sound = c.sound;
      if (sound != null) _later = Timer(const Duration(milliseconds: 1300), () => mounted ? _sounds.play(sound) : null);
      _next = Timer(const Duration(milliseconds: 2800), _advance);
      return;
    }
    _sounds.play('try');
    setState(() {
      _wiggles[c.id] = (_wiggles[c.id] ?? 0) + 1;
      _named = c.id;
    });
    _say(Strings.tryAgain(c, target));
  }

  void _advance() {
    if (!mounted) return;
    final last = _round.target.id;
    setState(() {
      _done++;
      if (_done >= FindScreen.rounds) {
        _finished = true;
      } else {
        _deal(last: last);
      }
    });
    if (_finished) {
      _sounds.play('star');
      _star.forward(from: 0);
      _say(Strings.allFound);
    } else {
      _ask();
    }
  }

  void _again() {
    setState(() {
      _done = 0;
      _finished = false;
      _deal(last: _round.target.id);
    });
    _ask();
  }

  @override
  Widget build(BuildContext context) {
    final cartoon = ref.watch(cartoonProvider);
    final target = _round.target;
    return Scaffold(
      body: SafeArea(
        child: Stack(children: [
          Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 10, 14, 0),
              child: Row(children: [
                RoundButton(label: Strings.back, icon: Icons.arrow_back_rounded, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 16),
                Expanded(child: PageDots(count: FindScreen.rounds, at: _finished ? -1 : _done, done: _done)),
                const SizedBox(width: 74),
              ]),
            ),
            const SizedBox(height: 18),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: SpeakBubble(text: _right != null ? Strings.rightIs(target) : Strings.whereIs(target), onTap: _ask),
            ),
            Expanded(
              child: LayoutBuilder(builder: (context, box) {
                final n = _round.choices.length;
                final cols = n == 2 || box.maxWidth > 700 && n <= 4 && box.maxWidth > box.maxHeight ? n : 2;
                final rows = (n / cols).ceil();
                final aspect = n == 2 ? 1.3 : 1.0;
                final w = math.min((box.maxWidth - 24 - cols * 20.0) / cols, ((box.maxHeight - 30) / rows - 20) / aspect).clamp(60.0, 320.0);
                return Center(
                  child: Wrap(alignment: WrapAlignment.center, spacing: 20, runSpacing: 20, children: [
                    for (final c in _round.choices)
                      _Choice(
                        key: ValueKey('choice-${c.id}'),
                        card: c,
                        cartoon: cartoon,
                        width: w,
                        height: w * aspect,
                        right: _right == c.id,
                        dim: _right != null && _right != c.id,
                        named: _named == c.id,
                        wiggle: _wiggles[c.id] ?? 0,
                        onTap: () => _pick(c),
                      ),
                  ]),
                );
              }),
            ),
            const SizedBox(height: 16),
          ]),
          if (_finished) _AllFound(star: _star, onAgain: _again, onBack: () => context.canPop() ? context.pop() : context.go('/')),
        ]),
      ),
    );
  }
}

class _Choice extends StatelessWidget {
  const _Choice({
    super.key,
    required this.card,
    required this.cartoon,
    required this.width,
    required this.height,
    required this.right,
    required this.dim,
    required this.named,
    required this.wiggle,
    required this.onTap,
  });

  final CardItem card;
  final bool cartoon;
  final double width;
  final double height;
  final bool right;
  final bool dim;
  final bool named;
  final int wiggle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: card.zh,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: Wiggle(
            trigger: wiggle,
            child: AnimatedScale(
              scale: right ? 1.06 : 1,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOutBack,
              child: AnimatedOpacity(
                opacity: dim ? 0.35 : 1,
                duration: const Duration(milliseconds: 300),
                child: SizedBox(
                  width: width,
                  height: height,
                  child: Stack(clipBehavior: Clip.none, children: [
                    Positioned.fill(
                      child: SoftCard(
                        radius: width * 0.12,
                        padding: EdgeInsets.all(width * 0.1),
                        border: right ? Border.all(color: Calm.gold, width: width * 0.035) : null,
                        child: CardPicture(card, cartoon: cartoon),
                      ),
                    ),
                    if (right)
                      Positioned(
                        right: -width * 0.05,
                        top: -width * 0.05,
                        child: Container(
                          width: width * 0.22,
                          height: width * 0.22,
                          decoration: BoxDecoration(color: Calm.gold, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 3)),
                          child: Icon(Icons.check_rounded, color: Colors.white, size: width * 0.15),
                        ),
                      ),
                    if (named)
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: width * 0.05,
                        child: Center(
                          child: Container(
                            padding: EdgeInsets.symmetric(horizontal: width * 0.08, vertical: width * 0.025),
                            decoration: BoxDecoration(color: Calm.tealSoft, borderRadius: BorderRadius.circular(width)),
                            child: Text(card.zh, style: TextStyle(fontSize: math.max(16, width * 0.1), fontWeight: FontWeight.w700, color: Calm.tealDeep)),
                          ),
                        ),
                      ),
                  ]),
                ),
              ),
            ),
          ),
        ),
      );
}

/// Five found: a big star, and play again or go back to the cards.
class _AllFound extends StatelessWidget {
  const _AllFound({required this.star, required this.onAgain, required this.onBack});

  final Animation<double> star;
  final VoidCallback onAgain;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) => Positioned.fill(
        child: ColoredBox(
          color: Calm.paper.withValues(alpha: 0.94),
          child: Center(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              ScaleTransition(
                scale: CurvedAnimation(parent: star, curve: Curves.elasticOut),
                child: const Icon(Icons.star_rounded, color: Calm.gold, size: 180),
              ),
              const Text(Strings.allFound, style: TextStyle(fontSize: 30, fontWeight: FontWeight.w700)),
              const SizedBox(height: 30),
              WideButton(label: Strings.again, icon: Icons.refresh_rounded, onTap: onAgain),
              const SizedBox(height: 16),
              WideButton(label: Strings.backToCards, icon: Icons.style_rounded, color: Colors.white, onTap: onBack),
            ]),
          ),
        ),
      );
}
