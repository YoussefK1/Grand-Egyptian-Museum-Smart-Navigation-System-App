import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'offline_router.dart';

/// Talks to the FastAPI backend (backend/main.py). Every call has an on-device fallback so the app
/// still demonstrates all three modules when the server is not running.
class GemApi {
  /// Android emulator -> host machine is 10.0.2.2. Use your PC's LAN IP for a real phone, or change it
  /// at runtime from the menu (Settings -> Server address). Build-time override:
  ///   flutter run --dart-define=GEM_API=http://192.168.1.20:8000
  static String baseUrl =
      const String.fromEnvironment('GEM_API', defaultValue: 'http://10.0.2.2:8000');

  /// True when the last tour/route/collection answer came from the bundled data, not the server.
  static bool offline = false;
  static const Duration _timeout = Duration(seconds: 10);

  static Uri _uri(String path, [Map<String, String>? q]) {
    final u = Uri.parse('$baseUrl$path');
    return q == null ? u : u.replace(queryParameters: q);
  }

  static dynamic _decode(http.Response r) {
    if (r.statusCode >= 400) {
      throw Exception('HTTP ${r.statusCode}: ${r.body}');
    }
    return jsonDecode(utf8.decode(r.bodyBytes));
  }

  static Future<dynamic> _get(String path, [Map<String, String>? q]) async {
    final r = await http.get(_uri(path, q)).timeout(_timeout);
    return _decode(r);
  }

  static Future<dynamic> _post(String path, Map<String, dynamic> body) async {
    final r = await http
        .post(_uri(path),
            headers: {'Content-Type': 'application/json'}, body: jsonEncode(body))
        .timeout(_timeout);
    return _decode(r);
  }

  static Future<Map<String, dynamic>> _asset(String name) async {
    final raw = await rootBundle.loadString('assets/data/$name');
    return jsonDecode(raw) as Map<String, dynamic>;
  }

  static Future<bool> ping() async {
    try {
      final h = await _get('/health');
      offline = false;
      return h['status'] == 'ok';
    } catch (_) {
      offline = true;
      return false;
    }
  }

  // ------------------------------------------------------------------ questionnaire
  static Future<Map<String, dynamic>> questionnaire() async {
    try {
      return Map<String, dynamic>.from(await _get('/api/questionnaire') as Map);
    } catch (_) {
      return _asset('questionnaire.json');
    }
  }

  // ------------------------------------------------------------------ 1) tour customisation (XGBoost)
  static Future<Map<String, dynamic>> recommendTour(Map<String, dynamic> profile) async {
    try {
      final r = Map<String, dynamic>.from(await _post('/api/tour/recommend', profile) as Map);
      offline = false;
      return r;
    } catch (_) {
      offline = true;
      final raw = await rootBundle.loadString('assets/data/demo_tours.json');
      final tours = (jsonDecode(raw) as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
      Map<String, dynamic> best = tours.first;
      double bestScore = -1e9;
      for (final t in tours) {
        final p = Map<String, dynamic>.from(t['profile'] as Map);
        double s = 0;
        final pe = ((p['eras'] ?? []) as List).map((e) => e.toString()).toSet();
        final pi = ((p['interests'] ?? []) as List).map((e) => e.toString()).toSet();
        final ue = ((profile['eras'] ?? []) as List).map((e) => e.toString()).toSet();
        final ui = ((profile['interests'] ?? []) as List).map((e) => e.toString()).toSet();
        s += 2.0 * pe.intersection(ue).length + 2.0 * pi.intersection(ui).length;
        final pt = (p['time_minutes'] as num).toDouble();
        final ut = ((profile['time_minutes'] ?? 120) as num).toDouble();
        s -= (pt - ut).abs() / 60.0;
        if ((p['mobility'] ?? 'full') == (profile['mobility'] ?? 'full')) s += 3;
        if ((p['visitor_type'] ?? 'solo') == (profile['visitor_type'] ?? 'solo')) s += 1.5;
        if (s > bestScore) {
          bestScore = s;
          best = t;
        }
      }
      final plan = Map<String, dynamic>.from(best['plan'] as Map);
      plan['offline_demo'] = true;
      return plan;
    }
  }

  // ------------------------------------------------------------------ 2) navigation
  static Future<List<Map<String, dynamic>>> zones() async {
    try {
      final r = await _get('/api/nav/zones', {'limit': '200'});
      return (r['zones'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } catch (_) {
      final z = await OfflineRouter.zones();
      return z.where((e) => e['type'] != 'elevator' && e['type'] != 'stairs').toList();
    }
  }

  static Future<Map<String, dynamic>> route(String start, String goal, String mode) async {
    try {
      final r = await _get('/api/nav/route', {'start': start, 'goal': goal, 'mode': mode});
      offline = false;
      return Map<String, dynamic>.from(r as Map);
    } catch (_) {
      offline = true;
      return OfflineRouter.route(start, goal, mode);
    }
  }

  // ------------------------------------------------------------------ 3) AI collections
  static Future<Map<String, dynamic>> collections() async {
    try {
      final r = Map<String, dynamic>.from(await _get('/api/collections') as Map);
      final info = Map<String, dynamic>.from(await _get('/api/model/info') as Map);
      r['metrics'] = info['clustering'];
      return r;
    } catch (_) {
      final a = await _asset('collections.json');
      return {
        'embedder': (a['metrics'] as Map)['embedder'],
        'k': (a['metrics'] as Map)['kmeans_k'],
        'collections': a['collections'],
        'metrics': a['metrics'],
      };
    }
  }

  static Future<Map<String, dynamic>> collectionDetail(int id) async {
    try {
      return Map<String, dynamic>.from(await _get('/api/collections/$id') as Map);
    } catch (_) {
      final a = await _asset('collections.json');
      return Map<String, dynamic>.from((a['details'] as Map)['$id'] as Map);
    }
  }

  static Future<Map<String, dynamic>> collectionsMap() async {
    try {
      return Map<String, dynamic>.from(await _get('/api/collections/map') as Map);
    } catch (_) {
      final a = await _asset('collections.json');
      return {'points': a['points'], 'clusters': a['clusters']};
    }
  }

  static Future<List<Map<String, dynamic>>> similar(String artifactId) async {
    try {
      final r = await _get('/api/artifacts/$artifactId/similar');
      return (r as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } catch (_) {
      return [];
    }
  }

  static Future<void> feedback(Map<String, dynamic> profile, String artifactId, int rating) async {
    try {
      await _post('/api/feedback', {'profile': profile, 'artifact_id': artifactId, 'rating': rating});
    } catch (_) {/* best effort */}
  }
}
