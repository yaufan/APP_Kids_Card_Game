import 'dart:math' as math;

import 'cards.dart';

/// One round of 找找看: the card asked for, among [choices].
class FindRound {
  const FindRound(this.target, this.choices);

  final CardItem target;
  final List<CardItem> choices;

  /// Asks for a card from [deck], preferably one already turned over
  /// ([seen]), and never the one asked for last time; the others are
  /// different cards from the same deck, and the places are shuffled.
  factory FindRound.deal(Deck deck, int count, math.Random r, {String? last, Set<String> seen = const {}}) {
    final n = count.clamp(2, math.min(4, deck.cards.length)).toInt();
    final seenHere = [for (final c in deck.cards) if (seen.contains(c.id) && c.id != last) c];
    final pool = seenHere.length >= 3 ? seenHere : [for (final c in deck.cards) if (c.id != last) c];
    final target = pool[r.nextInt(pool.length)];
    final others = [for (final c in deck.cards) if (c.id != target.id) c]..shuffle(r);
    final choices = [target, ...others.take(n - 1)]..shuffle(r);
    return FindRound(target, choices);
  }
}
