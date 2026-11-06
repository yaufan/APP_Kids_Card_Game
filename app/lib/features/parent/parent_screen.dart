import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/version.dart';
import '../../core/game.dart';
import '../../core/providers.dart';

/// Parent mode (after the gate): play time, the cards, sounds, what the
/// child has played, ideas for playing together.
class ParentScreen extends ConsumerWidget {
  const ParentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final s = g.settings;
    final book = ref.watch(cardBookProvider);
    final game = ref.read(gameProvider.notifier);
    final now = ref.read(clockProvider)();

    Widget section(String title, List<Widget> children) => Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: const TextStyle(fontSize: 15, color: Calm.inkSoft, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                ...children,
              ]),
            ),
          ),
        );

    Widget toggle(String label, bool value, void Function(bool) set, {Key? key}) =>
        SwitchListTile(key: key, contentPadding: EdgeInsets.zero, title: Text(label, style: const TextStyle(fontSize: 17)), value: value, onChanged: set);

    Widget chips<T>(List<T> values, T selected, String Function(T) name, void Function(T) pick, String keyPrefix) => Wrap(spacing: 8, runSpacing: 8, children: [
          for (final v in values)
            ChoiceChip(
              key: ValueKey('$keyPrefix-$v'),
              label: Text(name(v), style: const TextStyle(fontSize: 16)),
              selected: v == selected,
              onSelected: (_) => pick(v),
              selectedColor: Calm.tealSoft,
              showCheckmark: false,
            ),
        ]);

    const note = TextStyle(fontSize: 14, height: 1.5, color: Calm.inkSoft);

    return Scaffold(
      backgroundColor: Calm.parentBg,
      appBar: AppBar(
        backgroundColor: Calm.parentBg,
        title: const Text(Strings.parentTitle),
        leading: IconButton(icon: const Icon(Icons.close_rounded), tooltip: Strings.back, onPressed: () => context.canPop() ? context.pop() : context.go('/')),
      ),
      body: ListView(padding: const EdgeInsets.fromLTRB(16, 8, 16, 32), children: [
        section(Strings.playTime, [
          chips<int>(Settings.minuteChoices, s.minutes, Strings.minutes, (m) => game.settings((x) => x.copyWith(minutes: m)), 'minutes'),
          const SizedBox(height: 10),
          const Text(Strings.playTimeNote, style: note),
          if (g.resting(now)) ...[
            const SizedBox(height: 10),
            const Text(Strings.resting, style: TextStyle(fontSize: 16)),
            const SizedBox(height: 6),
            FilledButton(
              key: const ValueKey('play-on'),
              onPressed: () {
                game.change((g) => g.playOn());
                ref.read(sessionStartProvider.notifier).restart();
                context.go('/');
              },
              child: const Text(Strings.playOn),
            ),
          ],
        ]),
        section(Strings.cardsSection, [
          const Text(Strings.firstPicture, style: TextStyle(fontSize: 17)),
          RadioGroup<bool>(
            groupValue: s.cartoon,
            onChanged: (v) => game.settings((x) => x.copyWith(cartoon: v)),
            child: const Column(children: [
              RadioListTile<bool>(key: ValueKey('style-real'), contentPadding: EdgeInsets.zero, value: false, title: Text(Strings.realPicture, style: TextStyle(fontSize: 16))),
              RadioListTile<bool>(key: ValueKey('style-cartoon'), contentPadding: EdgeInsets.zero, value: true, title: Text(Strings.cartoonPicture, style: TextStyle(fontSize: 16))),
            ]),
          ),
          const Text(Strings.pictureNote, style: note),
          const SizedBox(height: 4),
          toggle(Strings.english, s.english, (v) => game.settings((x) => x.copyWith(english: v)), key: const ValueKey('english')),
          const SizedBox(height: 4),
          const Text(Strings.choices, style: TextStyle(fontSize: 17)),
          const SizedBox(height: 8),
          chips<int>(const [2, 3, 4], s.choices, Strings.cards, (n) => game.settings((x) => x.copyWith(choices: n)), 'choices'),
        ]),
        section(Strings.sound, [
          toggle(Strings.music, s.music, (v) => game.settings((x) => x.copyWith(music: v)), key: const ValueKey('music')),
          toggle(Strings.effects, s.sounds, (v) => game.settings((x) => x.copyWith(sounds: v)), key: const ValueKey('effects')),
          toggle(Strings.voice, s.voice, (v) => game.settings((x) => x.copyWith(voice: v)), key: const ValueKey('voice')),
        ]),
        section(Strings.progress, [
          for (final d in book.decks) ...[
            Row(children: [
              Container(width: 12, height: 12, decoration: BoxDecoration(color: Calm.deck(d.id), shape: BoxShape.circle)),
              const SizedBox(width: 8),
              Text(d.zh, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  Strings.deckLine(d.cards.where((c) => g.seen.containsKey(c.id)).length, d.cards.where((c) => g.knows(c.id)).length, d.cards.length),
                  style: const TextStyle(fontSize: 15),
                ),
              ),
            ]),
            if (d.cards.any((c) => g.knows(c.id)))
              Padding(
                padding: const EdgeInsets.only(left: 20, top: 4),
                child: Text(d.cards.where((c) => g.knows(c.id)).map((c) => c.zh).join('、'), style: note),
              ),
            const SizedBox(height: 10),
          ],
          const Text(Strings.knownNote, style: note),
        ]),
        section(Strings.together, [
          for (final t in Strings.tips)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Padding(padding: EdgeInsets.only(top: 3), child: Icon(Icons.favorite_rounded, size: 16, color: Calm.teal)),
                const SizedBox(width: 8),
                Expanded(child: Text(t, style: const TextStyle(fontSize: 16, height: 1.45))),
              ]),
            ),
        ]),
        section(Strings.fullVersion, [
          const Text(Strings.fullNote, style: note),
          toggle(Strings.fullSwitch, s.full, (v) => game.settings((x) => x.copyWith(full: v)), key: const ValueKey('full')),
        ]),
        section(Strings.about, [
          const Text(Strings.privacy, style: TextStyle(fontSize: 15, height: 1.5)),
          const SizedBox(height: 6),
          Text(Strings.version(appVersion), style: note),
        ]),
      ]),
    );
  }
}
