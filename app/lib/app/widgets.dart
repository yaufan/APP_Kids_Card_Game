import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../core/cards.dart';
import '../core/providers.dart';
import 'theme.dart';

/// A card's picture in the chosen style.
class CardPicture extends StatelessWidget {
  const CardPicture(this.card, {super.key, required this.cartoon, this.fit = BoxFit.contain});

  final CardItem card;
  final bool cartoon;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) => SvgPicture.asset(card.art(cartoon: cartoon), fit: fit, excludeFromSemantics: true);
}

/// Shrinks a little while pressed and clicks.
class Pressable extends ConsumerStatefulWidget {
  const Pressable({super.key, required this.child, this.onTap, this.sound = 'tap'});

  final Widget child;
  final VoidCallback? onTap;
  final String? sound;

  @override
  ConsumerState<Pressable> createState() => _PressableState();
}

class _PressableState extends ConsumerState<Pressable> {
  var _down = false;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      excludeFromSemantics: true,
      onTapDown: enabled ? (_) => setState(() => _down = true) : null,
      onTapCancel: enabled ? () => setState(() => _down = false) : null,
      onTapUp: enabled ? (_) => setState(() => _down = false) : null,
      onTap: enabled
          ? () {
              final s = widget.sound;
              if (s != null) ref.read(soundsProvider).play(s);
              widget.onTap!();
            }
          : null,
      child: AnimatedScale(scale: _down ? 0.94 : 1, duration: const Duration(milliseconds: 90), child: widget.child),
    );
  }
}

/// A white rounded card with a soft shadow.
class SoftCard extends StatelessWidget {
  const SoftCard({super.key, this.child, this.color = Colors.white, this.radius = 26, this.padding = EdgeInsets.zero, this.border});

  final Widget? child;
  final Color color;
  final double radius;
  final EdgeInsets padding;
  final Border? border;

  @override
  Widget build(BuildContext context) => Container(
        padding: padding,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(radius),
          border: border,
          boxShadow: const [BoxShadow(color: Color(0x1F3E4A4A), blurRadius: 14, offset: Offset(0, 6))],
        ),
        child: child,
      );
}

/// A round button with an icon: white, or filled with [color].
class RoundButton extends StatelessWidget {
  const RoundButton({super.key, required this.label, required this.icon, this.onTap, this.color = Colors.white, this.size = 58, this.sound = 'tap'});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final Color color;
  final double size;
  final String? sound;

  @override
  Widget build(BuildContext context) {
    final filled = color != Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: const [BoxShadow(color: Color(0x223E4A4A), blurRadius: 10, offset: Offset(0, 4))],
          ),
          child: Icon(icon, size: size * 0.5, color: filled ? Colors.white : Calm.ink),
        ),
      ),
    );
  }
}

/// A wide rounded button with an icon and a word.
class WideButton extends StatelessWidget {
  const WideButton({super.key, required this.label, required this.icon, this.onTap, this.color = Calm.teal, this.height = 64, this.sound = 'tap'});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final Color color;
  final double height;
  final String? sound;

  @override
  Widget build(BuildContext context) {
    final light = color == Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          height: height,
          padding: EdgeInsets.symmetric(horizontal: height * 0.4),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(height / 2),
            boxShadow: const [BoxShadow(color: Color(0x223E4A4A), blurRadius: 10, offset: Offset(0, 4))],
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(icon, size: height * 0.46, color: light ? Calm.teal : Colors.white),
            const SizedBox(width: 10),
            Text(label, style: TextStyle(fontSize: height * 0.36, fontWeight: FontWeight.w700, color: light ? Calm.ink : Colors.white)),
          ]),
        ),
      ),
    );
  }
}

/// A speech bubble with a speaker: tap to hear it again.
class SpeakBubble extends StatelessWidget {
  const SpeakBubble({super.key, required this.text, this.onTap, this.size = 26});

  final String text;
  final VoidCallback? onTap;
  final double size;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: onTap != null,
        label: text,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: SoftCard(
            radius: 30,
            padding: const EdgeInsets.fromLTRB(12, 10, 22, 10),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Container(
                width: size * 1.7,
                height: size * 1.7,
                decoration: const BoxDecoration(color: Calm.teal, shape: BoxShape.circle),
                child: Icon(Icons.volume_up_rounded, color: Colors.white, size: size),
              ),
              const SizedBox(width: 12),
              Flexible(child: Text(text, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: Calm.ink))),
            ]),
          ),
        ),
      );
}

/// Shakes its child side to side once each time [trigger] changes.
class Wiggle extends StatefulWidget {
  const Wiggle({super.key, required this.trigger, required this.child, this.amount = 0.06});

  final int trigger;
  final Widget child;
  final double amount;

  @override
  State<Wiggle> createState() => _WiggleState();
}

class _WiggleState extends State<Wiggle> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));

  @override
  void didUpdateWidget(Wiggle old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final t = _c.value;
          final a = math.sin(t * math.pi * 4) * (1 - t) * widget.amount;
          return Transform.rotate(angle: a, child: child);
        },
        child: widget.child,
      );
}

/// Small dots: where we are among [count].
class PageDots extends StatelessWidget {
  const PageDots({super.key, required this.count, required this.at, this.done});

  final int count;
  final int at;

  /// When set, the dots before it are filled (for rounds).
  final int? done;

  @override
  Widget build(BuildContext context) {
    final size = count > 10 ? 7.0 : 11.0;
    return Wrap(alignment: WrapAlignment.center, spacing: size * 0.6, runSpacing: 4, children: [
      for (var i = 0; i < count; i++)
        AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: i == at ? size * 2.2 : size,
          height: size,
          decoration: BoxDecoration(
            color: i == at || (done != null && i < done!) ? Calm.teal : Calm.paperDeep,
            borderRadius: BorderRadius.circular(size),
          ),
        ),
    ]);
  }
}
