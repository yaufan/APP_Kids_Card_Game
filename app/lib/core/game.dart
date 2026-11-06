/// What a parent set.
class Settings {
  const Settings({this.minutes = 10, this.cartoon = false, this.english = false, this.choices = 2, this.music = true, this.sounds = true, this.voice = true, this.full = true});

  /// How long one sitting may be before a rest (docs/design.md: the
  /// Health Promotion Administration asks for little screen time at two).
  final int minutes;

  /// The picture shown first: realistic (false) or cartoon.
  final bool cartoon;
  final bool english;

  /// Cards to choose from in 找找看 (2 to 4).
  final int choices;
  final bool music;
  final bool sounds;
  final bool voice;
  final bool full;

  static const minuteChoices = [5, 10, 15, 20, 30];

  Settings copyWith({int? minutes, bool? cartoon, bool? english, int? choices, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        minutes: minutes ?? this.minutes,
        cartoon: cartoon ?? this.cartoon,
        english: english ?? this.english,
        choices: choices ?? this.choices,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() =>
      {'minutes': minutes, 'cartoon': cartoon, 'english': english, 'choices': choices, 'music': music, 'sounds': sounds, 'voice': voice, 'full': full};

  factory Settings.fromJson(Map<String, dynamic> j) {
    final m = j['minutes'];
    final c = j['choices'];
    return Settings(
      minutes: m is int && minuteChoices.contains(m) ? m : 10,
      cartoon: j['cartoon'] as bool? ?? false,
      english: j['english'] as bool? ?? false,
      choices: c is int ? c.clamp(2, 4) : 2,
      music: j['music'] as bool? ?? true,
      sounds: j['sounds'] as bool? ?? true,
      voice: j['voice'] as bool? ?? true,
      full: j['full'] as bool? ?? true,
    );
  }
}

/// Everything kept: cards seen and found, the rest, the settings.
class Game {
  const Game({this.seen = const {}, this.found = const {}, this.recent = const [], this.restSince, this.settings = const Settings()});

  /// Times each card was turned over.
  final Map<String, int> seen;

  /// Times each card was found in 找找看.
  final Map<String, int> found;

  /// The last cards turned over, newest first (for "go and find it at home").
  final List<String> recent;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;
  final Settings settings;

  /// A rest lasts until a parent lets play go on, or an hour has passed.
  static const restLength = Duration(hours: 1);

  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  /// A card counts as known once found three times.
  bool knows(String id) => (found[id] ?? 0) >= 3;

  Game copyWith({Map<String, int>? seen, Map<String, int>? found, List<String>? recent, DateTime? restSince, bool clearRest = false, Settings? settings}) => Game(
        seen: seen ?? this.seen,
        found: found ?? this.found,
        recent: recent ?? this.recent,
        restSince: clearRest ? null : (restSince ?? this.restSince),
        settings: settings ?? this.settings,
      );

  Game saw(String id) => copyWith(seen: {...seen, id: (seen[id] ?? 0) + 1}, recent: [id, ...recent.where((r) => r != id)].take(12).toList());

  Game foundCard(String id) => copyWith(found: {...found, id: (found[id] ?? 0) + 1});

  Game rest(DateTime now) => copyWith(restSince: now);

  Game playOn() => copyWith(clearRest: true);

  Map<String, dynamic> toJson() => {
        'version': 1,
        'seen': seen,
        'found': found,
        'recent': recent,
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
        'settings': settings.toJson(),
      };

  factory Game.fromJson(Map<String, dynamic>? j) {
    if (j == null) return const Game();
    final recent = j['recent'], rest = j['restSince'];
    Map<String, int> counts(Object? o) => {if (o is Map) for (final e in o.entries) if (e.key is String && e.value is int) e.key as String: e.value as int};
    return Game(
      seen: counts(j['seen']),
      found: counts(j['found']),
      recent: [if (recent is List) for (final r in recent) if (r is String) r],
      restSince: rest is String ? DateTime.tryParse(rest) : null,
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
    );
  }
}
