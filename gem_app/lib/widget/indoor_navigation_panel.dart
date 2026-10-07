import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/app_nav.dart';
import '../utils/constants.dart';
import 'floor_plan_view.dart';
import 'gem_widgets.dart';

/// Indoor navigation: choose where you are and where you want to go, get the easiest route.
class IndoorNavigationPanel extends StatefulWidget {
  const IndoorNavigationPanel({Key? key}) : super(key: key);

  @override
  State<IndoorNavigationPanel> createState() => _IndoorNavigationPanelState();
}

class _IndoorNavigationPanelState extends State<IndoorNavigationPanel> {
  List<Map<String, dynamic>> _zones = [];
  String? _start = 'ENTRANCE';
  String? _goal;
  String _mode = 'easiest';
  bool _loadingZones = true;
  bool _busy = false;
  Map<String, dynamic>? _route;
  String? _error;

  static const _modes = <String, String>{
    'easiest': 'Easiest',
    'shortest': 'Shortest',
    'step_free': 'Step-free',
  };

  @override
  void initState() {
    super.initState();
    AppNav.pending.addListener(_consumePending);
    _loadZones();
  }

  @override
  void dispose() {
    AppNav.pending.removeListener(_consumePending);
    super.dispose();
  }

  Future<void> _loadZones() async {
    final z = await GemApi.zones();
    z.sort((a, b) {
      final fa = (a['floor'] as num).toInt(), fb = (b['floor'] as num).toInt();
      if (fa != fb) return fb.compareTo(fa);
      return (a['name'] as String).compareTo(b['name'] as String);
    });
    if (!mounted) return;
    setState(() {
      _zones = z;
      _loadingZones = false;
    });
    _consumePending();
  }

  void _consumePending() {
    final t = AppNav.pending.value;
    if (t == null || _zones.isEmpty) return;
    AppNav.pending.value = null;
    setState(() {
      if (t.startId != null) _start = t.startId;
      _goal = t.goalId;
      _mode = _modes.containsKey(t.mode) ? t.mode : 'easiest';
    });
    _find();
  }

  Future<void> _find() async {
    if (_start == null || _goal == null) {
      setState(() => _error = 'Choose both your location and a destination.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final r = await GemApi.route(_start!, _goal!, _mode);
    if (!mounted) return;
    setState(() {
      _busy = false;
      if (r['found'] == true) {
        _route = r;
      } else {
        _route = null;
        _error = (r['message'] ?? 'No route found').toString();
      }
    });
  }

  Future<void> _quick(String type) async {
    if (_start == null) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    Map<String, dynamic>? best;
    for (final z in _zones.where((z) => z['type'] == type)) {
      final r = await GemApi.route(_start!, z['id'] as String, _mode);
      if (r['found'] == true && (best == null || (r['minutes'] as num) < (best['minutes'] as num))) {
        best = r;
      }
    }
    if (!mounted) return;
    setState(() {
      _busy = false;
      if (best != null) {
        _route = best;
        _goal = best['goal'] as String;
      } else {
        _error = 'Nothing of that type found.';
      }
    });
  }

  IconData _stepIcon(String kind, String turn) {
    switch (kind) {
      case 'start':
        return Icons.my_location;
      case 'arrive':
        return Icons.flag;
      case 'elevator':
        return Icons.elevator;
      case 'stairs':
        return Icons.stairs;
      default:
        if (turn == 'left') return Icons.turn_left;
        if (turn == 'right') return Icons.turn_right;
        return Icons.arrow_upward;
    }
  }

  Widget _dropdown(String label, String? value, ValueChanged<String?> onChanged) {
    return DropdownButtonFormField<String>(
      isExpanded: true,
      value: (value != null && _zones.any((z) => z['id'] == value)) ? value : null,
      dropdownColor: AppColors.primaryDark,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white70),
        filled: true,
        fillColor: AppColors.inputBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: BorderSide(color: AppColors.primaryGold.withOpacity(0.3))),
      ),
      items: [
        for (final z in _zones)
          DropdownMenuItem<String>(
            value: z['id'] as String,
            child: Text('${z['name']}  -  ${floorName(z['floor'])}', overflow: TextOverflow.ellipsis),
          ),
      ],
      onChanged: onChanged,
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingZones) {
      return const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()));
    }
    final r = _route;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      GemCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _dropdown('I am at', _start, (v) => setState(() => _start = v)),
          const SizedBox(height: 10),
          _dropdown('I want to go to', _goal, (v) => setState(() => _goal = v)),
          const SizedBox(height: 12),
          Wrap(spacing: 8, runSpacing: 8, children: [
            for (final e in _modes.entries)
              GemChip(
                  label: e.value,
                  selected: _mode == e.key,
                  icon: e.key == 'step_free' ? Icons.accessible : null,
                  onTap: () => setState(() => _mode = e.key)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(
                child: GemButton(
                    label: _busy ? 'Finding route...' : 'Find route',
                    icon: Icons.alt_route,
                    onPressed: _busy ? null : _find)),
          ]),
          const SizedBox(height: 10),
          Wrap(spacing: 8, runSpacing: 8, children: [
            GemChip(label: 'Nearest restroom', icon: Icons.wc, onTap: () => _quick('restroom')),
            GemChip(label: 'Nearest cafe', icon: Icons.restaurant, onTap: () => _quick('food')),
            GemChip(label: 'Museum store', icon: Icons.shopping_bag, onTap: () => _quick('shop')),
          ]),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: Colors.redAccent)),
          ],
        ]),
      ),
      if (r != null) ...[
        GemCard(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('${r['start_name']}  >  ${r['goal_name']}', style: AppTextStyles.cardTitle),
            const SizedBox(height: 8),
            Wrap(spacing: 8, runSpacing: 6, children: [
              GemChip(label: '${r['minutes']} min', icon: Icons.timer, selected: true),
              GemChip(label: '${(r['distance_m'] as num).round()} m', icon: Icons.straighten, selected: true),
              GemChip(
                  label: r['uses_stairs'] == true ? 'Uses stairs' : 'Step-free',
                  icon: r['uses_stairs'] == true ? Icons.stairs : Icons.accessible,
                  selected: true),
            ]),
            const SizedBox(height: 12),
            RoutePlanTabs(
              nodes: (r['nodes'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList(),
              startId: r['start'] as String?,
              goalId: r['goal'] as String?,
            ),
          ]),
        ),
        GemCard(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Directions', style: AppTextStyles.cardTitle),
            const SizedBox(height: 8),
            for (final raw in (r['steps'] as List))
              Builder(builder: (context) {
                final s = Map<String, dynamic>.from(raw as Map);
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Icon(_stepIcon(s['kind'] as String, (s['turn'] ?? 'straight') as String),
                        color: AppColors.primaryGold, size: 22),
                    const SizedBox(width: 10),
                    Expanded(child: Text(s['text'] as String, style: const TextStyle(color: Colors.white, fontSize: 14))),
                  ]),
                );
              }),
          ]),
        ),
      ],
      if (GemApi.offline)
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Text('Offline mode: routes are computed on this device.',
              style: TextStyle(color: Colors.white54, fontSize: 12)),
        ),
    ]);
  }
}
