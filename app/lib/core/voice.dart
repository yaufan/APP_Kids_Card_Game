import 'package:flutter/widgets.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Reads out the instructions and the characters, for children who cannot
/// read yet: Taiwanese Mandarin for what is said, English for a letter's
/// name and its word ("A, apple"). It uses the phone's own speech; parents
/// can turn it off.
abstract interface class Voice {
  /// Says [zh] in Mandarin, then [en] (if any) in English. Completes when
  /// the words have been said (or were cut off by a newer line or a stop).
  Future<void> say(String zh, {String? en});
  Future<void> stop();
}

class SystemVoice implements Voice {
  SystemVoice() {
    // Nothing is said while the app is out of sight, and a line being said
    // stops when it goes.
    _life = AppLifecycleListener(
      onHide: () {
        _away = true;
        stop();
      },
      onShow: () => _away = false,
    );
  }

  late final AppLifecycleListener _life;
  FlutterTts? _tts;
  Future<FlutterTts>? _setUp;
  String? _language;
  var _away = false;

  /// Counts the lines asked for (and the stops): only the newest is said.
  var _turn = 0;

  /// The engine, set up once. Every line waits for the whole set-up, so a
  /// line asked for while the first one is still setting up is not cut off
  /// by the first one's late stop(): only the newest line is said.
  Future<FlutterTts> _engine() => _setUp ??= () async {
        final tts = _tts = FlutterTts();
        await tts.awaitSpeakCompletion(true);
        await tts.setSpeechRate(0.45);
        await tts.setPitch(1.2);
        return tts;
      }();

  Future<void> _use(FlutterTts tts, String language) async {
    if (_language == language) return;
    _language = language;
    await tts.setLanguage(language);
  }

  @override
  Future<void> say(String zh, {String? en}) async {
    final turn = ++_turn;
    if (_away) return;
    try {
      final tts = await _engine();
      // A newer line, or a stop, while this one waited.
      if (turn != _turn) return;
      await tts.stop();
      if (zh.isNotEmpty) {
        await _use(tts, 'zh-TW');
        if (turn != _turn) return;
        await tts.speak(zh);
      }
      if (en == null || en.isEmpty || turn != _turn) return;
      await _use(tts, 'en-US');
      if (turn != _turn) return;
      await tts.speak(en);
    } catch (_) {
      // No speech engine (tests, or a phone without one): the words on
      // screen and the pictures are enough.
    }
  }

  @override
  Future<void> stop() async {
    _turn++;
    try {
      await _tts?.stop();
    } catch (_) {}
  }

  void dispose() => _life.dispose();
}

class SilentVoice implements Voice {
  const SilentVoice();

  @override
  Future<void> say(String zh, {String? en}) async {}

  @override
  Future<void> stop() async {}
}

/// Remembers what was said, and when it was stopped (tests): [log] has
/// both, a stop as "(stop)".
class RecordingVoice implements Voice {
  final said = <String>[];
  final log = <String>[];
  var stops = 0;

  @override
  Future<void> say(String zh, {String? en}) async {
    final line = en == null ? zh : '$zh|$en';
    said.add(line);
    log.add(line);
  }

  @override
  Future<void> stop() async {
    stops++;
    log.add('(stop)');
  }
}
