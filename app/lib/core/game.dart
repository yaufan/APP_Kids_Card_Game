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

/// The sitting being played, kept so that closing the app and opening it
/// again soon goes on with it (docs/design.md 「每次玩多久」): the play time
/// it has used, and when the app was last seen.
class SavedSitting {
  const SavedSitting(this.played, this.seen);

  final Duration played;
  final DateTime seen;

  /// Away from the app this long counts as a rest: a new sitting.
  static const awayIsRest = Duration(minutes: 10);

  /// Whether the app opened at [now] goes on with this sitting: back within
  /// ten minutes (a phone clock moved back counts as back at once).
  bool goesOn(DateTime now) => now.difference(seen) < awayIsRest;

  Map<String, dynamic> toJson() => {'played': played.inSeconds, 'seen': seen.toIso8601String()};

  static SavedSitting? fromJson(Object? j) {
    if (j is! Map) return null;
    final p = j['played'], s = j['seen'];
    final seen = s is String ? DateTime.tryParse(s) : null;
    if (p is! int || p < 0 || seen == null) return null;
    return SavedSitting(Duration(seconds: p), seen);
  }
}

/// The parent gate's lock (kept, so closing the app does not open it):
/// wrong answers in a row, how often it has locked since the last right
/// answer (each lock is longer: one minute, then five, then fifteen), and
/// since when it is locked.
class GateLock {
  const GateLock({this.misses = 0, this.locks = 0, this.since});

  final int misses;
  final int locks;
  final DateTime? since;

  static const maxMisses = 3;
  static const steps = [Duration(minutes: 1), Duration(minutes: 5), Duration(minutes: 15)];

  /// How long the lock lasts.
  Duration get length => steps[(locks - 1).clamp(0, steps.length - 1)];

  /// How long it is still locked at [now] (zero: open). A phone clock moved
  /// back to before the lock began counts as locked just now (see [at]).
  Duration left(DateTime now) {
    final s = since;
    if (s == null) return Duration.zero;
    final passed = now.isBefore(s) ? Duration.zero : now.difference(s);
    final l = length - passed;
    return l.isNegative ? Duration.zero : l;
  }

  /// The lock as seen at [now]: a phone clock moved back to before it began
  /// starts it again from [now], so it ends at the latest [length] later
  /// (never a lock that does not end).
  GateLock at(DateTime now) {
    final s = since;
    return s != null && now.isBefore(s) ? GateLock(misses: misses, locks: locks, since: now) : this;
  }

  /// A wrong answer: the third in a row locks the gate.
  GateLock miss(DateTime now) => misses + 1 < maxMisses ? GateLock(misses: misses + 1, locks: locks, since: since) : GateLock(locks: locks + 1, since: now);

  Map<String, dynamic> toJson() => {'misses': misses, 'locks': locks, if (since != null) 'since': since!.toIso8601String()};

  factory GateLock.fromJson(Object? j) {
    if (j is! Map) return const GateLock();
    final m = j['misses'], l = j['locks'], s = j['since'];
    return GateLock(misses: m is int ? m.clamp(0, maxMisses - 1) : 0, locks: l is int ? l.clamp(0, 99) : 0, since: s is String ? DateTime.tryParse(s) : null);
  }
}

/// Everything kept: cards seen and found, the rest, the sitting, the
/// parent gate's lock, the settings.
class Game {
  const Game({this.seen = const {}, this.found = const {}, this.recent = const [], this.restSince, this.sitting, this.gate = const GateLock(), this.settings = const Settings()});

  /// Times each card was turned over.
  final Map<String, int> seen;

  /// Times each card was found in 找找看.
  final Map<String, int> found;

  /// The last cards turned over, newest first (for "go and find it at home").
  final List<String> recent;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;

  /// The sitting being played (null: none kept).
  final SavedSitting? sitting;
  final GateLock gate;
  final Settings settings;

  /// A rest lasts until a parent lets play go on, or an hour has passed.
  static const restLength = Duration(hours: 1);

  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  /// A card counts as known once found three times.
  bool knows(String id) => (found[id] ?? 0) >= 3;

  Game copyWith({
    Map<String, int>? seen,
    Map<String, int>? found,
    List<String>? recent,
    DateTime? restSince,
    bool clearRest = false,
    SavedSitting? sitting,
    bool clearSitting = false,
    GateLock? gate,
    Settings? settings,
  }) =>
      Game(
        seen: seen ?? this.seen,
        found: found ?? this.found,
        recent: recent ?? this.recent,
        restSince: clearRest ? null : (restSince ?? this.restSince),
        sitting: clearSitting ? null : (sitting ?? this.sitting),
        gate: gate ?? this.gate,
        settings: settings ?? this.settings,
      );

  Game saw(String id) => copyWith(seen: {...seen, id: (seen[id] ?? 0) + 1}, recent: [id, ...recent.where((r) => r != id)].take(12).toList());

  Game foundCard(String id) => copyWith(found: {...found, id: (found[id] ?? 0) + 1});

  /// The play time ran out: the rest begins, the sitting is over.
  Game rest(DateTime now) => copyWith(restSince: now, clearSitting: true);

  Game playOn() => copyWith(clearRest: true);

  Map<String, dynamic> toJson() => {
        'version': 1,
        'seen': seen,
        'found': found,
        'recent': recent,
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
        if (sitting != null) 'sitting': sitting!.toJson(),
        'gate': gate.toJson(),
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
      sitting: SavedSitting.fromJson(j['sitting']),
      gate: GateLock.fromJson(j['gate']),
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
    );
  }
}
