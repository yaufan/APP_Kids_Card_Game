import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/cards.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../../core/voice.dart';
import '../decks/decks_screen.dart';

/// 翻翻卡: one big card at a time. Tap it to turn it over: it says its
/// name and makes its sound; tap again to hear it again. The arrows go to
/// the next card, the button in the corner switches between the realistic
/// and the cartoon picture.
class FlipScreen extends ConsumerStatefulWidget {
  const FlipScreen({super.key, required this.deck});

  final String deck;

  @override
  ConsumerState<FlipScreen> createState() => _FlipScreenState();
}

class _FlipScreenState extends ConsumerState<FlipScreen> with SingleTickerProviderStateMixin {
  late final Sounds _sounds;
  late final Voice _voice;
  late final _flip = AnimationController(vsync: this, duration: const Duration(milliseconds: 520));
  var _index = 0;
  var _wiggle = 0;
  Timer? _soundLater;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _voice = ref.read(voiceProvider);
    _sounds.hold(this, Music.play);
  }

  @override
  void dispose() {
    _soundLater?.cancel();
    _flip.dispose();
    _sounds.release(this);
    super.dispose();
  }

  Deck get _deck => ref.read(cardBookProvider).deck(widget.deck)!;

  CardItem get _card => _deck.cards[_index];

  bool get _faceUp => _flip.value == 1;

  void _tapCard() {
    if (_flip.isAnimating) return;
    if (_faceUp) return _announce();
    _sounds.play('flip');
    _flip.forward().then((_) {
      if (!mounted) return;
      ref.read(gameProvider.notifier).change((g) => g.saw(_card.id));
      _announce();
    });
  }

  /// Says the card's name (and the English word, if the parent turned it
  /// on), then makes its sound.
  void _announce() {
    final c = _card;
    final s = ref.read(gameProvider).settings;
    setState(() => _wiggle++);
    if (s.voice) _voice.say(c.zh, en: s.english ? c.en : null);
    _soundLater?.cancel();
    final sound = c.sound;
    if (sound != null) {
      _soundLater = Timer(Duration(milliseconds: s.voice ? 1100 : 150), () {
        if (mounted) _sounds.play(sound);
      });
    }
  }

  void _go(int step) {
    _soundLater?.cancel();
    _voice.stop();
    final n = _deck.cards.length;
    setState(() {
      _index = (_index + step + n) % n;
      _flip.value = 0;
    });
  }

  void _switchStyle() => ref.read(cartoonProvider.notifier).toggle();

  @override
  Widget build(BuildContext context) {
    final deck = ref.watch(cardBookProvider).deck(widget.deck)!;
    final card = deck.cards[_index];
    final cartoon = ref.watch(cartoonProvider);
    final settings = ref.watch(gameProvider.select((g) => g.settings));
    final cover = ref.read(cardBookProvider).byId[DecksScreen.cover[deck.id]] ?? deck.cards.first;
    return Scaffold(
      body: SafeArea(
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 0),
            child: Row(children: [
              RoundButton(label: Strings.home, icon: Icons.home_rounded, onTap: () => context.canPop() ? context.pop() : context.go('/')),
              const SizedBox(width: 12),
              Container(width: 14, height: 14, decoration: BoxDecoration(color: Calm.deck(deck.id), shape: BoxShape.circle)),
              const SizedBox(width: 8),
              Text(deck.zh, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
              const Spacer(),
              AnimatedBuilder(
                animation: _flip,
                builder: (_, _) => _StyleSwitch(card: _faceUp ? card : cover, cartoon: cartoon, onTap: _switchStyle),
              ),
            ]),
          ),
          Expanded(
            child: LayoutBuilder(builder: (context, box) {
              final w = math.min(box.maxWidth * 0.84, (box.maxHeight - 30) / 1.32);
              return Center(
                child: Semantics(
                  container: true,
                  button: true,
                  label: _faceUp ? card.zh : Strings.flipMe,
                  excludeSemantics: true,
                  onTap: _tapCard,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    excludeFromSemantics: true,
                    onTap: _tapCard,
                    child: Wiggle(
                      trigger: _wiggle,
                      amount: 0.035,
                      child: AnimatedBuilder(
                        animation: _flip,
                        builder: (_, _) {
                          final t = Curves.easeInOut.transform(_flip.value);
                          final front = t >= 0.5;
                          final angle = t * math.pi;
                          return Transform(
                            alignment: Alignment.center,
                            transform: Matrix4.identity()
                              ..setEntry(3, 2, 0.0012)
                              ..rotateY(front ? angle - math.pi : angle),
                            child: SizedBox(
                              width: w,
                              height: w * 1.32,
                              child: front
                                  ? _Front(card: card, cartoon: cartoon, english: settings.english, width: w)
                                  : _Back(color: Calm.deck(deck.id), width: w),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
          Padding(padding: const EdgeInsets.symmetric(horizontal: 30), child: PageDots(count: deck.cards.length, at: _index)),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 18),
            child: Row(children: [
              RoundButton(label: Strings.previous, icon: Icons.arrow_back_rounded, sound: 'next', onTap: () => _go(-1)),
              const Spacer(),
              WideButton(label: Strings.find, icon: Icons.search_rounded, color: Colors.white, height: 58, onTap: () => context.push('/find/${deck.id}')),
              const Spacer(),
              RoundButton(label: Strings.next, icon: Icons.arrow_forward_rounded, color: Calm.teal, sound: 'next', onTap: () => _go(1)),
            ]),
          ),
        ]),
      ),
    );
  }
}

/// The face of the card: the picture, the name, the sound it makes.
class _Front extends StatelessWidget {
  const _Front({required this.card, required this.cartoon, required this.english, required this.width});

  final CardItem card;
  final bool cartoon;
  final bool english;
  final double width;

  @override
  Widget build(BuildContext context) => SoftCard(
        radius: width * 0.09,
        padding: EdgeInsets.fromLTRB(width * 0.08, width * 0.08, width * 0.08, width * 0.05),
        child: Column(children: [
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: CardPicture(card, cartoon: cartoon, key: ValueKey('${card.id}-$cartoon')),
            ),
          ),
          SizedBox(height: width * 0.03),
          Text(card.zh, style: TextStyle(fontSize: width * 0.15, fontWeight: FontWeight.w700, color: Calm.ink, height: 1.1)),
          if (card.says.isNotEmpty) ...[
            SizedBox(height: width * 0.025),
            Container(
              padding: EdgeInsets.symmetric(horizontal: width * 0.05, vertical: width * 0.015),
              decoration: BoxDecoration(color: Calm.tealSoft, borderRadius: BorderRadius.circular(width)),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                Icon(Icons.volume_up_rounded, color: Calm.teal, size: width * 0.07),
                SizedBox(width: width * 0.02),
                Text(card.says, style: TextStyle(fontSize: width * 0.065, fontWeight: FontWeight.w700, color: Calm.tealDeep)),
              ]),
            ),
          ],
          if (english) ...[
            SizedBox(height: width * 0.02),
            Text(card.en, style: TextStyle(fontSize: width * 0.06, color: Calm.inkSoft)),
          ],
        ]),
      );
}

/// The back of the card: the deck's colour with a sparkle.
class _Back extends StatelessWidget {
  const _Back({required this.color, required this.width});

  final Color color;
  final double width;

  @override
  Widget build(BuildContext context) => Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(width * 0.09),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color.lerp(color, Colors.white, 0.18)!, Color.lerp(color, Colors.black, 0.08)!],
          ),
          boxShadow: const [BoxShadow(color: Color(0x293E4A4A), blurRadius: 14, offset: Offset(0, 6))],
        ),
        padding: EdgeInsets.all(width * 0.06),
        child: CustomPaint(
          painter: _BackPattern(),
          child: Center(
            child: Container(
              width: width * 0.4,
              height: width * 0.4,
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.9), shape: BoxShape.circle),
              child: Icon(Icons.auto_awesome_rounded, color: color, size: width * 0.22),
            ),
          ),
        ),
      );
}

/// A thin white frame and a scatter of soft dots.
class _BackPattern extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final frame = Paint()
      ..color = Colors.white.withValues(alpha: 0.55)
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.012;
    canvas.drawRRect(RRect.fromRectAndRadius(Offset.zero & size, Radius.circular(size.width * 0.06)), frame);
    final dot = Paint()..color = Colors.white.withValues(alpha: 0.22);
    final r = math.Random(7);
    for (var i = 0; i < 26; i++) {
      final at = Offset(size.width * (0.08 + 0.84 * r.nextDouble()), size.height * (0.06 + 0.88 * r.nextDouble()));
      canvas.drawCircle(at, size.width * (0.012 + 0.02 * r.nextDouble()), dot);
    }
  }

  @override
  bool shouldRepaint(_BackPattern old) => false;
}

/// The corner button: a small picture of this card in the other style.
class _StyleSwitch extends StatelessWidget {
  const _StyleSwitch({required this.card, required this.cartoon, required this.onTap});

  final CardItem card;
  final bool cartoon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: cartoon ? Strings.toReal : Strings.toCartoon,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: 'switch',
          child: SizedBox(
            width: 66,
            height: 66,
            child: Stack(children: [
              Container(
                width: 62,
                height: 62,
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [BoxShadow(color: Color(0x223E4A4A), blurRadius: 10, offset: Offset(0, 4))],
                ),
                child: CardPicture(card, cartoon: !cartoon),
              ),
              Positioned(
                right: 0,
                bottom: 0,
                child: Container(
                  width: 26,
                  height: 26,
                  decoration: BoxDecoration(color: Calm.teal, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 2)),
                  child: const Icon(Icons.sync_rounded, color: Colors.white, size: 16),
                ),
              ),
            ]),
          ),
        ),
      );
}
