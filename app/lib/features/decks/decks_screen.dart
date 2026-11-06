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

/// The card box (the home screen): a big round button for each deck.
class DecksScreen extends ConsumerStatefulWidget {
  const DecksScreen({super.key});

  /// The decks in the free version (docs/design.md "以後上架和收費").
  static const free = {'animals', 'fruits'};

  /// The card on each deck's button.
  static const cover = {'animals': 'dog', 'fruits': 'banana', 'vehicles': 'car', 'body': 'hand', 'home': 'cup', 'clothes': 'tshirt'};

  @override
  ConsumerState<DecksScreen> createState() => _DecksScreenState();
}

class _DecksScreenState extends ConsumerState<DecksScreen> {
  late final Sounds _sounds;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.play);
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _open(Deck d) {
    final s = ref.read(gameProvider).settings;
    if (s.voice) ref.read(voiceProvider).say(d.zh, en: s.english ? d.en : null);
    context.push('/deck/${d.id}');
  }

  Future<void> _openParent() async {
    if (await showParentGate(context) && mounted) await context.push('/parent');
  }

  @override
  Widget build(BuildContext context) {
    final book = ref.watch(cardBookProvider);
    final full = ref.watch(gameProvider.select((g) => g.settings.full));
    final cartoon = ref.watch(cartoonProvider);
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(builder: (context, box) {
          final columns = box.maxWidth > 700 ? 3 : 2;
          final rows = (book.decks.length / columns).ceil();
          final size = [(box.maxWidth - 40) / columns - 24, (box.maxHeight - 110) / rows - 52, 220.0].reduce((a, b) => a < b ? a : b);
          return Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 14, 14, 0),
              child: Row(children: [
                const Text(Strings.cardBox, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
                const Spacer(),
                Semantics(
                  container: true,
                  button: true,
                  label: Strings.parent,
                  excludeSemantics: true,
                  onTap: _openParent,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: _openParent,
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: const BoxDecoration(color: Calm.paperDeep, shape: BoxShape.circle),
                      child: const Icon(Icons.lock_outline_rounded, color: Calm.inkSoft, size: 22),
                    ),
                  ),
                ),
              ]),
            ),
            Expanded(
              child: Center(
                child: Wrap(alignment: WrapAlignment.center, spacing: 24, runSpacing: 14, children: [
                  for (final d in book.decks)
                    _DeckButton(
                      deck: d,
                      cover: book.byId[DecksScreen.cover[d.id]] ?? d.cards.first,
                      cartoon: cartoon,
                      size: size,
                      locked: !full && !DecksScreen.free.contains(d.id),
                      onTap: () => _open(d),
                    ),
                ]),
              ),
            ),
          ]);
        }),
      ),
    );
  }
}

class _DeckButton extends StatelessWidget {
  const _DeckButton({required this.deck, required this.cover, required this.cartoon, required this.size, required this.locked, required this.onTap});

  final Deck deck;
  final CardItem cover;
  final bool cartoon;
  final double size;
  final bool locked;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = Calm.deck(deck.id);
    return Semantics(
      container: true,
      button: !locked,
      label: locked ? '${deck.zh}（${Strings.locked}）' : deck.zh,
      excludeSemantics: true,
      onTap: locked ? null : onTap,
      child: Pressable(
        onTap: locked ? null : onTap,
        child: Opacity(
          opacity: locked ? 0.45 : 1,
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Stack(children: [
              Container(
                width: size,
                height: size,
                padding: EdgeInsets.all(size * 0.15),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: color, width: size * 0.055),
                  boxShadow: const [BoxShadow(color: Color(0x1F3E4A4A), blurRadius: 14, offset: Offset(0, 6))],
                ),
                child: CardPicture(cover, cartoon: cartoon),
              ),
              if (locked)
                Positioned(
                  right: size * 0.04,
                  bottom: size * 0.04,
                  child: Container(
                    width: size * 0.28,
                    height: size * 0.28,
                    decoration: const BoxDecoration(color: Calm.inkSoft, shape: BoxShape.circle),
                    child: Icon(Icons.lock_rounded, color: Colors.white, size: size * 0.16),
                  ),
                ),
            ]),
            const SizedBox(height: 6),
            Text(deck.zh, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          ]),
        ),
      ),
    );
  }
}
