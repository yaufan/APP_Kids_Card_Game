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
import '../parent/parent_gate.dart';

/// The play time is up: a quiet night sky, and something just seen to go
/// and find at home ("眼睛休息一下，我們去找找家裡的杯子吧！"). Only a
/// parent (through the gate) or an hour's wait lets play go on.
class RestScreen extends ConsumerStatefulWidget {
  const RestScreen({super.key});

  /// Decks whose cards are found at home (or on oneself).
  static const atHome = {'home', 'fruits', 'clothes', 'body'};

  /// The card to go and find: the last one seen that is at home.
  static CardItem pick(CardBook book, List<String> recent) {
    for (final id in recent) {
      final c = book.byId[id];
      if (c != null && atHome.contains(c.deck)) return c;
    }
    return book.byId['cup'] ?? book.decks.first.cards.first;
  }

  @override
  ConsumerState<RestScreen> createState() => _RestScreenState();
}

class _RestScreenState extends ConsumerState<RestScreen> {
  late final Sounds _sounds;
  late final CardItem _card;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.rest);
    _card = RestScreen.pick(ref.read(cardBookProvider), ref.read(gameProvider).recent);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _sounds.play('rest');
      if (ref.read(gameProvider).settings.voice) ref.read(voiceProvider).say(Strings.restLine(_card).replaceAll('\n', ''));
    });
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  Future<void> _parent() async {
    if (!await showParentGate(context) || !mounted) return;
    ref.read(gameProvider.notifier).change((g) => g.playOn());
    ref.read(sessionStartProvider.notifier).restart();
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    final cartoon = ref.watch(cartoonProvider);
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Color(0xFFEDEAF4), Calm.paper]),
        ),
        child: SafeArea(
          child: LayoutBuilder(builder: (context, box) {
            final sky = math.min(box.maxWidth - 48, box.maxHeight * 0.42);
            final thumb = math.min(170.0, box.maxHeight * 0.2);
            return Column(children: [
              const SizedBox(height: 20),
              ClipRRect(
                borderRadius: BorderRadius.circular(34),
                child: SizedBox(width: sky, height: sky * 0.86, child: const CustomPaint(painter: NightSky())),
              ),
              const SizedBox(height: 22),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Text(Strings.restLine(_card), textAlign: TextAlign.center, style: const TextStyle(fontSize: 24, height: 1.5, fontWeight: FontWeight.w700)),
              ),
              const SizedBox(height: 18),
              Stack(clipBehavior: Clip.none, children: [
                SoftCard(radius: 28, padding: EdgeInsets.all(thumb * 0.12), child: SizedBox(width: thumb, height: thumb, child: CardPicture(_card, cartoon: cartoon))),
                Positioned(
                  left: -12,
                  top: -12,
                  child: Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(color: Calm.teal, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 3)),
                    child: const Icon(Icons.home_rounded, color: Colors.white, size: 24),
                  ),
                ),
              ]),
              const Spacer(),
              Align(
                alignment: Alignment.bottomRight,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(0, 0, 18, 16),
                  child: Semantics(
                    container: true,
                    button: true,
                    label: Strings.parent,
                    excludeSemantics: true,
                    onTap: _parent,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: _parent,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.8), borderRadius: BorderRadius.circular(22)),
                        child: const Row(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.lock_outline_rounded, color: Calm.inkSoft, size: 20),
                          SizedBox(width: 6),
                          Text(Strings.parent, style: TextStyle(fontSize: 16, color: Calm.inkSoft)),
                        ]),
                      ),
                    ),
                  ),
                ),
              ),
            ]);
          }),
        ),
      ),
    );
  }
}

/// A sleepy night: a crescent moon, stars, clouds and "z z z".
class NightSky extends CustomPainter {
  const NightSky();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width, h = size.height;
    canvas.drawRect(
      Offset.zero & size,
      Paint()..shader = const LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Color(0xFF26325C), Color(0xFF55508C)]).createShader(Offset.zero & size),
    );
    final star = Paint()..color = const Color(0xFFFFF4C8);
    final r = math.Random(11);
    for (var i = 0; i < 26; i++) {
      final at = Offset(w * r.nextDouble(), h * 0.7 * r.nextDouble());
      canvas.drawCircle(at, w * (0.004 + 0.007 * r.nextDouble()), star..color = const Color(0xFFFFF4C8).withValues(alpha: 0.5 + 0.5 * r.nextDouble()));
    }
    // The moon: a circle with a bite taken out.
    final c = Offset(w * 0.5, h * 0.44);
    final moon = Path.combine(
      PathOperation.difference,
      Path()..addOval(Rect.fromCircle(center: c, radius: w * 0.2)),
      Path()..addOval(Rect.fromCircle(center: c + Offset(w * 0.1, -h * 0.07), radius: w * 0.18)),
    );
    canvas.drawCircle(c, w * 0.26, Paint()..color = const Color(0x22FFE9A0));
    canvas.drawPath(moon, Paint()..color = const Color(0xFFF6D77A));
    // Sleepy z's.
    for (final (i, s) in [0.05, 0.065, 0.08].indexed) {
      final tp = TextPainter(
        text: TextSpan(text: 'z', style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: w * s, fontWeight: FontWeight.w700)),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(w * (0.7 + i * 0.07), h * (0.24 - i * 0.08)));
    }
    // Clouds along the bottom.
    final cloud = Paint()..color = Colors.white.withValues(alpha: 0.95);
    for (final (x, y, rr) in [(0.05, 1.0, 0.16), (0.24, 0.97, 0.13), (0.42, 1.02, 0.15), (0.62, 0.98, 0.14), (0.82, 1.0, 0.16), (1.0, 0.97, 0.13)]) {
      canvas.drawCircle(Offset(w * x, h * y), w * rr, cloud);
    }
  }

  @override
  bool shouldRepaint(NightSky old) => false;
}
