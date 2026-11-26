import 'dart:io';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:card_world/core/sounds.dart';
import 'package:card_world/features/parent/parent_gate.dart';

import 'helpers.dart';

/// Privacy and the parent gate: no network, no pages opened by other apps,
/// parent mode only through the gate.
void main() {
  test('the app asks for no network and takes no links from other apps', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, isNot(contains('android.permission.INTERNET')));
    expect(manifest, contains('android:name="flutter_deeplinking_enabled" android:value="false"'));
    expect(File('ios/Runner/Info.plist').readAsStringSync(), contains('<key>FlutterDeepLinkingEnabled</key>\n\t<false/>'));
  });

  test('the phone\'s speech can be found (Android 11 and later)', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    final queries = RegExp(r'<queries>([\s\S]*?)</queries>').firstMatch(manifest)!.group(1)!;
    expect(queries, contains('<action android:name="android.intent.action.TTS_SERVICE" />'));
  });

  test('nothing goes into a backup: what the child played stays on this phone', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    final application = RegExp(r'<application[^>]*>').firstMatch(manifest)!.group(0)!;
    expect(application, contains('android:allowBackup="false"'));
    expect(application, contains('android:fullBackupContent="false"'));
    expect(application, contains('android:dataExtractionRules="@xml/data_extraction_rules"'));
    final rules = File('android/app/src/main/res/xml/data_extraction_rules.xml').readAsStringSync();
    for (final part in ['cloud-backup', 'device-transfer']) {
      final body = RegExp('<$part>([\\s\\S]*?)</$part>').firstMatch(rules)!.group(1)!;
      expect(body, contains('<exclude domain="root" path="." />'), reason: part);
      expect(body, isNot(contains('<include')), reason: part);
    }
  });

  test('the sounds play on the media volume and never take the focus from each other or the voice', () {
    for (final c in [SystemSounds.effectsContext, SystemSounds.musicContext]) {
      expect(c.android.usageType, anyOf(AndroidUsageType.media, AndroidUsageType.game));
      expect(c.android.audioFocus, AndroidAudioFocus.none);
      expect(c.iOS.category, AVAudioSessionCategory.ambient);
    }
    expect(SystemSounds.musicContext.android.contentType, AndroidContentType.music);
    expect(SystemSounds.effectsContext.android.contentType, AndroidContentType.sonification);
    final code = File('lib/core/sounds.dart').readAsStringSync();
    expect(code, isNot(contains('respectSilence')), reason: 'that is the ringer');
    expect(RegExp(r'AudioPool\.create\(').allMatches(code).length, RegExp(r'audioContext: effectsContext').allMatches(code).length);
    expect(code, contains('setAudioContext(musicContext)'));
  });

  test('the CI fails on a camera, microphone, contacts, photos or location permission', () {
    for (final f in ['../.github/workflows/app.yml', '../.github/workflows/release.yml']) {
      final check = RegExp(r"grep -E '([^']*)' permissions\.txt").firstMatch(File(f).readAsStringSync())!.group(1)!.split('|');
      expect(check, containsAll(['INTERNET', 'LOCATION', 'AD_ID', 'CAMERA', 'RECORD_AUDIO', 'READ_CONTACTS', 'READ_MEDIA_', 'READ_EXTERNAL_STORAGE']), reason: f);
    }
  });

  testWidgets('parent mode cannot be opened without the gate', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'no pass from the gate');
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/parent', reason: 'right after the gate');
    app.go('/');
    await app.settle();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up');
    await app.end();
  });
}
