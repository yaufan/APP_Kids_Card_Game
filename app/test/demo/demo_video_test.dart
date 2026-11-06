// Records a demo video of 小卡認天下 being played: a scripted child (a white
// dot where the finger is) with a caption under the phone screen; the music
// and sounds the app asked for are written down and mixed in afterwards by
// tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:card_world/app/app.dart';
import 'package:card_world/app/strings.dart';
import 'package:card_world/core/providers.dart';
import 'package:card_world/core/sounds.dart';
import 'package:card_world/core/store.dart';
import 'package:card_world/core/voice.dart';
import 'package:card_world/features/find/find_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers.dart' show book, loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and sounds asked for, with the frame they were asked at.
class _Track implements Sounds {
  _Track(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    var now = DateTime(2026, 11, 6, 10);
    final track = _Track(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    storeProvider.overrideWithValue(MemoryStore()),
                    cardBookProvider.overrideWithValue(book),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(5)),
                    clockProvider.overrideWithValue(() => now),
                  ],
                  child: const CardApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFF3B7F75),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text,
                      textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Future<void> label(String l) => touch(tester.getCenter(find.bySemanticsLabel(l).first));
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await touch(tester.getCenter(find.byKey(ValueKey('gate-key-$d'))));
        await frames(3);
      }
    }

    Future<void> flip(String name) async {
      await label(Strings.flipMe);
      await seconds(2.6);
    }

    // The card box.
    mark('box');
    caption.value = '小卡認天下：2 歲起，一張一張翻卡片\n認識身邊的東西和名字';
    await seconds(3.5);

    // Turning cards over.
    mark('flip');
    caption.value = '點一下，卡片翻過來\n念出名字，會叫的動物就叫';
    await label('動物');
    await seconds(1.5);
    await flip('小狗');
    caption.value = '再點一下，再聽一次';
    await label('小狗');
    await seconds(2.4);

    mark('style');
    caption.value = '右上角的小圖：真實版和卡通版\n小朋友當下就能自己切換';
    await seconds(1);
    await label(Strings.toCartoon);
    await seconds(2.2);
    await label('小狗');
    await seconds(2);
    await label(Strings.toReal);
    await seconds(2);

    mark('next');
    caption.value = '左右箭頭換下一張';
    for (final name in ['小貓', '兔子', '牛']) {
      await label(Strings.next);
      await seconds(0.8);
      await flip(name);
    }

    // Finding.
    mark('find');
    caption.value = '找找看：「小狗在哪裡？」\n兩張卡片選一張（家長可以改成三張、四張）';
    await label(Strings.find);
    await seconds(2.4);
    final state = tester.state(find.byType(FindScreen)) as dynamic;
    for (var round = 0; round < FindScreen.rounds; round++) {
      final target = state.debugTarget as String;
      if (round == 0) {
        final wrong = (state.debugChoices as List<String>).firstWhere((id) => id != target);
        caption.value = '點錯了也沒關係：只說「這是${book.byId[wrong]!.zh}喔」\n不扣分、不催促';
        await label(book.byId[wrong]!.zh);
        await seconds(2.6);
      }
      caption.value = round == 0 ? '找到了！' : '找找看（${round + 1}／5）';
      await label(book.byId[target]!.zh);
      await seconds(3.2);
      if (round == 0) await seconds(0.6);
    }
    caption.value = '找到五個，一顆大星星';
    await seconds(2.5);
    await label(Strings.backToCards);
    await seconds(1);
    await label(Strings.home);
    await seconds(1.2);

    // Vehicles and fruit.
    mark('vehicles');
    caption.value = '交通工具：車子會發出自己的聲音\n6 組卡片，每組 20 張';
    await label('交通工具');
    await seconds(1.2);
    await flip('汽車');
    await label(Strings.next);
    await seconds(0.6);
    await flip('公車');
    await label(Strings.home);
    await seconds(1);
    caption.value = '水果、身體、家裡的東西、衣服';
    await label('水果');
    await seconds(1.2);
    await flip('蘋果');
    await label(Strings.home);
    await seconds(1.5);

    // Time for a rest.
    mark('rest');
    now = now.add(const Duration(minutes: 10, seconds: 1));
    caption.value = '家長設定的時間到了：溫柔地休息\n請小朋友去找找家裡剛剛看過的東西';
    await seconds(6);

    // Parent mode.
    mark('parent');
    caption.value = '家長答對題目，才能再玩或進家長模式';
    await label(Strings.parent);
    await seconds(1.2);
    await gate();
    await seconds(1.5);
    await label(Strings.parent);
    await seconds(1);
    await gate();
    await seconds(1);
    caption.value = '家長模式：每次玩多久、一開始的畫風、英文\n找找看幾張卡片、看小朋友認得哪些';
    await seconds(3);
    await tester.drag(find.byType(ListView), const Offset(0, -700));
    await seconds(3);
    caption.value = '';
    mark('end');
    await seconds(0.5);

    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF3E4A4A).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
