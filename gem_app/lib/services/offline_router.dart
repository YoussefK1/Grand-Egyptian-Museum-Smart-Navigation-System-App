import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

/// On-device routing over the bundled museum graph (assets/data/nav_graph.json).
/// Same cost model as the Python backend, so the app keeps working without a server.
class OfflineRouter {
  static Map<String, Map<String, dynamic>>? _zones;
  static final Map<String, List<Map<String, dynamic>>> _adj = {};
  static Map<String, dynamic> floors = {};

  static const double _walkSpeed = 1.1;

  static Future<void> _load() async {
    if (_zones != null) return;
    final raw = await rootBundle.loadString('assets/data/nav_graph.json');
    final data = jsonDecode(raw) as Map<String, dynamic>;
    floors = Map<String, dynamic>.from(data['floors'] as Map);
    final zones = <String, Map<String, dynamic>>{};
    for (final z in (data['zones'] as List)) {
      final m = Map<String, dynamic>.from(z as Map);
      zones[m['id'] as String] = m;
      _adj[m['id'] as String] = [];
    }
    for (final e in (data['edges'] as List)) {
      final m = Map<String, dynamic>.from(e as Map);
      final a = m['a'] as String;
      final b = m['b'] as String;
      final len = (m['length_m'] as num).toDouble();
      final lv = (m['levels'] as num).toInt();
      final kind = m['kind'] as String;
      _adj[a]!.add({'to': b, 'kind': kind, 'length': len, 'levels': lv});
      _adj[b]!.add({'to': a, 'kind': kind, 'length': len, 'levels': lv});
    }
    _zones = zones;
  }

  static Future<List<Map<String, dynamic>>> zones() async {
    await _load();
    return _zones!.values.toList();
  }

  static double? _cost(Map<String, dynamic> e, String mode) {
    final kind = e['kind'] as String;
    final len = e['length'] as double;
    if (kind == 'stairs') {
      switch (mode) {
        case 'step_free':
          return null;
        case 'easiest':
          return len * 2.2;
        case 'scenic':
          return len * 0.6;
        case 'avoid_stairs':
          return len * 8.0;
        default:
          return len;
      }
    }
    if (kind == 'elevator') {
      switch (mode) {
        case 'shortest':
          return len;
        case 'scenic':
          return len + 60.0;
        default:
          return len + 14.0;
      }
    }
    return len;
  }

  static String _floorLabel(int f) => (floors['$f'] ?? 'Level $f').toString();

  static Future<Map<String, dynamic>> route(String start, String goal, String mode) async {
    await _load();
    final zones = _zones!;
    if (!zones.containsKey(start) || !zones.containsKey(goal)) {
      return {'found': false, 'message': 'Unknown location'};
    }
    final dist = <String, double>{for (final k in zones.keys) k: double.infinity};
    final prev = <String, String>{};
    final prevEdge = <String, Map<String, dynamic>>{};
    final open = <String>{start};
    dist[start] = 0;
    while (open.isNotEmpty) {
      String u = open.first;
      for (final n in open) {
        if (dist[n]! < dist[u]!) u = n;
      }
      open.remove(u);
      if (u == goal) break;
      for (final e in _adj[u]!) {
        final c = _cost(e, mode);
        if (c == null) continue;
        final v = e['to'] as String;
        final nd = dist[u]! + c;
        if (nd < dist[v]!) {
          dist[v] = nd;
          prev[v] = u;
          prevEdge[v] = e;
          open.add(v);
        }
      }
    }
    if (dist[goal]!.isInfinite) {
      return {'found': false, 'message': 'No route found for this mode.'};
    }
    final path = <String>[goal];
    while (path.first != start) {
      path.insert(0, prev[path.first]!);
    }
    final steps = <Map<String, dynamic>>[];
    int fl(String id) => (zones[id]!['floor'] as num).toInt();
    steps.add({
      'kind': 'start',
      'text': 'Start at ${zones[start]!['name']} (${_floorLabel(fl(start))}).',
      'from_id': start, 'to_id': start, 'distance_m': 0.0, 'seconds': 0.0,
      'floor_from': fl(start), 'floor_to': fl(start), 'turn': 'straight',
    });
    double totalM = 0, totalS = 0;
    bool usesStairs = false;
    int i = 0;
    while (i < path.length - 1) {
      final a = path[i];
      final b = path[i + 1];
      final e = prevEdge[b]!;
      final kind = e['kind'] as String;
      if (kind == 'elevator' || kind == 'stairs') {
        int j = i;
        double dsum = 0;
        while (j < path.length - 1 && (prevEdge[path[j + 1]]!['kind'] as String) == kind) {
          dsum += prevEdge[path[j + 1]]!['length'] as double;
          j++;
        }
        final end = path[j];
        final fa = fl(a);
        final fb = fl(end);
        final dir = fb > fa ? 'up' : 'down';
        final levels = (fb - fa).abs();
        if (kind == 'elevator') {
          final secs = 30.0 + 6.0 * levels;
          totalS += secs;
          steps.add({
            'kind': 'elevator',
            'text': 'Take the elevator $dir to ${_floorLabel(fb)} (step-free).',
            'from_id': a, 'to_id': end, 'distance_m': 0.0, 'seconds': secs,
            'floor_from': fa, 'floor_to': fb, 'turn': 'straight',
          });
        } else {
          usesStairs = true;
          final secs = 40.0 * levels;
          totalM += dsum;
          totalS += secs;
          steps.add({
            'kind': 'stairs',
            'text': 'Go $dir the stairs to ${zones[end]!['name']} ($levels level${levels == 1 ? '' : 's'}).',
            'from_id': a, 'to_id': end, 'distance_m': dsum, 'seconds': secs,
            'floor_from': fa, 'floor_to': fb, 'turn': 'straight',
          });
        }
        i = j;
        continue;
      }
      final len = e['length'] as double;
      totalM += len;
      totalS += len / _walkSpeed;
      steps.add({
        'kind': 'walk',
        'text': 'Head to ${zones[b]!['name']} (~${len.round()} m)${kind == 'outdoor' ? ' (outdoors)' : ''}.',
        'from_id': a, 'to_id': b, 'distance_m': len, 'seconds': len / _walkSpeed,
        'floor_from': fl(a), 'floor_to': fl(b), 'turn': 'straight',
      });
      i++;
    }
    steps.add({
      'kind': 'arrive',
      'text': 'You have arrived at ${zones[goal]!['name']}.',
      'from_id': goal, 'to_id': goal, 'distance_m': 0.0, 'seconds': 0.0,
      'floor_from': fl(goal), 'floor_to': fl(goal), 'turn': 'straight',
    });
    final floorsVisited = <int>[];
    for (final id in path) {
      final f = fl(id);
      if (floorsVisited.isEmpty || floorsVisited.last != f) floorsVisited.add(f);
    }
    return {
      'found': true,
      'mode': mode,
      'start': start,
      'goal': goal,
      'start_name': zones[start]!['name'],
      'goal_name': zones[goal]!['name'],
      'distance_m': double.parse(totalM.toStringAsFixed(1)),
      'minutes': double.parse((totalS / 60.0).toStringAsFixed(1)),
      'floors_visited': floorsVisited,
      'uses_stairs': usesStairs,
      'nodes': [
        for (final id in path)
          {'id': id, 'name': zones[id]!['name'], 'floor': fl(id), 'x': zones[id]!['x'], 'y': zones[id]!['y']}
      ],
      'steps': steps,
    };
  }
}
