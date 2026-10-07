import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/app_nav.dart';
import '../utils/constants.dart';
import '../widgets/floor_plan_view.dart';
import '../widgets/gem_widgets.dart';
import 'menu_screen.dart';

enum _Phase { loading, asking, generating, result }

class TourScreen extends StatefulWidget {
  const TourScreen({Key? key}) : super(key: key);

  @override
  State<TourScreen> createState() => _TourScreenState();
}

class _TourScreenState extends State<TourScreen> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  _Phase _phase = _Phase.loading;
  List<Map<String, dynamic>> _questions = [];
  List<Map<String, dynamic>> _zones = [];
  final Map<String, dynamic> _answers = {
    'time_minutes': 120,
    'eras': <String>[],
    'interests': <String>[],
    'visitor_type': 'solo',
    'pace': 'balanced',
    'depth': 'balanced',
    'mobility': 'full',
    'crowd': 'neutral',
    'start': 'ENTRANCE',
  };
  int _step = 0;
  Map<String, dynamic>? _plan;
  String? _error;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final q = await GemApi.questionnaire();
    final z = await GemApi.zones();
    z.sort((a, b) => (a['name'] as String).compareTo(b['name'] as String));
    if (!mounted) return;
    setState(() {
      _questions = (q['questions'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
      _zones = z;
      _phase = _Phase.asking;
    });
  }

  int get _totalSteps => _questions.length + 1; // + start location

  bool _isSelected(String qid, dynamic value) {
    final a = _answers[qid];
    if (a is List) return a.contains(value);
    return a == value;
  }

  void _toggle(Map<String, dynamic> q, dynamic value) {
    final id = q['id'] as String;
    setState(() {
      if (q['type'] == 'multi') {
        final list = List<String>.from(_answers[id] as List);
        final v = value.toString();
        if (list.contains(v)) {
          list.remove(v);
        } else {
          final max = (q['max'] as num?)?.toInt() ?? 99;
          if (list.length < max) list.add(v);
        }
        _answers[id] = list;
      } else {
        _answers[id] = value;
      }
    });
  }

  Future<void> _generate() async {
    setState(() {
      _phase = _Phase.generating;
      _error = null;
    });
    try {
      final plan = await GemApi.recommendTour(Map<String, dynamic>.from(_answers));
      if (!mounted) return;
      setState(() {
        _plan = plan;
        _phase = _Phase.result;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Could not create a tour: $e';
        _phase = _Phase.asking;
      });
    }
  }

  void _restart() {
    setState(() {
      _plan = null;
      _step = 0;
      _phase = _Phase.asking;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: const MenuScreen(),
      body: SafeArea(
        child: GemBackground(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
              child: Row(children: [
                IconButton(
                  onPressed: () => _scaffoldKey.currentState!.openDrawer(),
                  icon: Icon(Icons.menu, color: AppColors.textLight, size: 28),
                ),
                const SizedBox(width: 12),
                Expanded(child: Text('My AI Tour', style: AppTextStyles.welcomeTitle.copyWith(fontSize: 24))),
                if (_phase == _Phase.result)
                  IconButton(
                      onPressed: _restart,
                      tooltip: 'New tour',
                      icon: Icon(Icons.refresh, color: AppColors.primaryGold)),
              ]),
            ),
            Expanded(child: _body()),
          ]),
        ),
      ),
    );
  }

  Widget _body() {
    switch (_phase) {
      case _Phase.loading:
        return const Center(child: CircularProgressIndicator());
      case _Phase.generating:
        return Center(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text('Our AI is designing your tour...', style: AppTextStyles.cardTitle),
          ]),
        );
      case _Phase.asking:
        return _questionView();
      case _Phase.result:
        return _resultView();
    }
  }

  // ------------------------------------------------------------------ questionnaire
  Widget _questionView() {
    final last = _step == _totalSteps - 1;
    Widget content;
    String title;
    String? subtitle;
    if (!last) {
      final q = _questions[_step];
      title = q['title'] as String;
      subtitle = q['subtitle'] as String?;
      final opts = (q['options'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
      content = Wrap(spacing: 10, runSpacing: 10, children: [
        for (final o in opts)
          GemChip(
            label: o['label'] as String,
            selected: _isSelected(q['id'] as String, o['value'] is num ? o['value'] : o['value'].toString()),
            onTap: () => _toggle(q, o['value'] is num ? o['value'] : o['value'].toString()),
          ),
      ]);
    } else {
      title = 'Where are you now?';
      subtitle = 'Your tour starts from this point';
      content = DropdownButtonFormField<String>(
        isExpanded: true,
        value: _zones.any((z) => z['id'] == _answers['start']) ? _answers['start'] as String : null,
        dropdownColor: AppColors.primaryDark,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.inputBg,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        items: [
          for (final z in _zones)
            DropdownMenuItem<String>(
                value: z['id'] as String,
                child: Text('${z['name']}  -  ${floorName(z['floor'])}', overflow: TextOverflow.ellipsis)),
        ],
        onChanged: (v) => setState(() => _answers['start'] = v ?? 'ENTRANCE'),
      );
    }

    return Column(children: [
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Question ${_step + 1} of $_totalSteps', style: const TextStyle(color: Colors.white54, fontSize: 12)),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: (_step + 1) / _totalSteps,
              minHeight: 6,
              backgroundColor: Colors.white12,
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryGold),
            ),
          ),
        ]),
      ),
      Expanded(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title, style: AppTextStyles.sectionTitle),
            if (subtitle != null) ...[
              const SizedBox(height: 4),
              Text(subtitle, style: const TextStyle(color: Colors.white60)),
            ],
            const SizedBox(height: 18),
            content,
            if (_error != null) ...[
              const SizedBox(height: 14),
              Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ],
          ]),
        ),
      ),
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 86),
        child: Row(children: [
          if (_step > 0)
            Expanded(
                child: GemButton(label: 'Back', outlined: true, onPressed: () => setState(() => _step--))),
          if (_step > 0) const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: GemButton(
              label: last ? 'Create my tour' : 'Next',
              icon: last ? Icons.auto_awesome : Icons.arrow_forward,
              onPressed: last ? _generate : () => setState(() => _step++),
            ),
          ),
        ]),
      ),
    ]);
  }

  // ------------------------------------------------------------------ result
  Widget _resultView() {
    final plan = _plan!;
    final stops = (plan['stops'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    final nodes = <Map<String, dynamic>>[];
    final markers = <String, String>{};
    for (int i = 0; i < stops.length; i++) {
      final leg = Map<String, dynamic>.from(stops[i]['leg'] as Map);
      for (final n in (leg['nodes'] as List)) {
        final m = Map<String, dynamic>.from(n as Map);
        if (nodes.isEmpty || nodes.last['id'] != m['id']) nodes.add(m);
      }
      markers[stops[i]['zone_id'] as String] = '${i + 1}';
    }
    final profile = Map<String, dynamic>.from(_answers);
    final brk = plan['suggested_break'];
    return ListView(padding: const EdgeInsets.only(bottom: 100), children: [
      if (plan['offline_demo'] == true)
        GemCard(
          child: Row(children: [
            const Icon(Icons.cloud_off, color: Colors.orangeAccent),
            const SizedBox(width: 10),
            const Expanded(
                child: Text(
                    'Server not reachable - showing the closest ready-made demo tour. Start the backend '
                    '(see README) for fully personalised AI tours.',
                    style: TextStyle(color: Colors.white70, fontSize: 12))),
          ]),
        ),
      GemCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(plan['title'] as String, style: AppTextStyles.museumTitle),
          const SizedBox(height: 2),
          Text(plan['subtitle'] as String, style: const TextStyle(color: Colors.white70)),
          const SizedBox(height: 12),
          Wrap(spacing: 8, runSpacing: 8, children: [
            GemChip(label: '${(plan['total_minutes'] as num).round()} min total', icon: Icons.timer, selected: true),
            GemChip(label: '${plan['n_stops']} stops', icon: Icons.place, selected: true),
            GemChip(label: '${plan['n_artifacts']} artifacts', icon: Icons.museum, selected: true),
            GemChip(
                label: '${(plan['walking_distance_m'] as num).round()} m walking',
                icon: Icons.directions_walk,
                selected: true),
          ]),
          const SizedBox(height: 14),
          RoutePlanTabs(nodes: nodes, markers: markers),
        ]),
      ),
      for (int i = 0; i < stops.length; i++) _stopCard(i, stops[i], profile),
      if (brk != null)
        GemCard(
          child: Row(children: [
            Icon(Icons.coffee, color: AppColors.primaryGold),
            const SizedBox(width: 10),
            Expanded(
                child: Text('${(brk as Map)['suggestion']}  (${brk['zone_name']})',
                    style: const TextStyle(color: Colors.white70, fontSize: 13))),
          ]),
        ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: GemButton(label: 'Change my answers', icon: Icons.tune, outlined: true, onPressed: _restart),
      ),
    ]);
  }

  Widget _stopCard(int index, Map<String, dynamic> stop, Map<String, dynamic> profile) {
    final arts = (stop['artifacts'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    final leg = Map<String, dynamic>.from(stop['leg'] as Map);
    final steps = (leg['steps'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    final prevId = index == 0 ? (_plan!['visitor'] as Map)['start'] as String : null;
    return GemCard(
      padding: EdgeInsets.zero,
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          initiallyExpanded: index == 0,
          iconColor: AppColors.primaryGold,
          collapsedIconColor: Colors.white54,
          leading: CircleAvatar(
              radius: 15,
              backgroundColor: AppColors.primaryGold,
              child: Text('${index + 1}', style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold))),
          title: Text(stop['zone_name'] as String, style: AppTextStyles.cardTitle),
          subtitle: Text(
              '${floorName(stop['floor'])}  |  +${(stop['arrive_at_min'] as num).round()} min  |  stay ${(stop['dwell_min'] as num).round()} min',
              style: const TextStyle(color: Colors.white60, fontSize: 12)),
          childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
          expandedCrossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final a in arts) _artifactTile(a, profile),
            const SizedBox(height: 8),
            Text('How to get here (${(leg['minutes'] as num)} min walk)',
                style: TextStyle(color: AppColors.primaryGold, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            for (final s in steps)
              if (s['kind'] != 'start' && s['kind'] != 'arrive')
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Text('- ${s['text']}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                ),
            const SizedBox(height: 8),
            GemButton(
              label: 'Navigate here',
              icon: Icons.navigation,
              outlined: true,
              onPressed: () => AppNav.navigateTo(NavTarget(
                  startId: prevId ?? (leg['nodes'] as List).first['id'] as String,
                  goalId: stop['zone_id'] as String,
                  mode: (_plan!['navigation_mode'] == 'step_free') ? 'step_free' : 'easiest')),
            ),
          ],
        ),
      ),
    );
  }

  Widget _artifactTile(Map<String, dynamic> a, Map<String, dynamic> profile) {
    final img = (a['app_image_asset'] ?? '') as String;
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.35),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (img.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(right: 10),
            child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.asset(img, width: 56, height: 56, fit: BoxFit.cover,
                    errorBuilder: (c, e, s) => const SizedBox(width: 56, height: 56))),
          ),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(a['name'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
            const SizedBox(height: 2),
            Text('${a['era']}  |  ${a['category']}  |  ${a['minutes']} min',
                style: const TextStyle(color: Colors.white54, fontSize: 11)),
            const SizedBox(height: 4),
            Text(a['description'] as String,
                maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white70, fontSize: 12)),
            const SizedBox(height: 4),
            for (final w in (a['why'] as List))
              Text('* $w', style: TextStyle(color: AppColors.accentGold, fontSize: 11)),
            const SizedBox(height: 4),
            Row(children: [
              Text('AI match ${a['match']}%', style: const TextStyle(color: Colors.white54, fontSize: 11)),
              const Spacer(),
              InkWell(
                onTap: () => _rate(profile, a['artifact_id'] as String, 5),
                child: const Padding(padding: EdgeInsets.all(4), child: Icon(Icons.thumb_up_alt_outlined, size: 18, color: Colors.white70)),
              ),
              InkWell(
                onTap: () => _rate(profile, a['artifact_id'] as String, 1),
                child: const Padding(padding: EdgeInsets.all(4), child: Icon(Icons.thumb_down_alt_outlined, size: 18, color: Colors.white70)),
              ),
            ]),
          ]),
        ),
      ]),
    );
  }

  void _rate(Map<String, dynamic> profile, String id, int rating) {
    GemApi.feedback(profile, id, rating);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(rating >= 4 ? 'Thanks! We will show you more like this.' : 'Thanks - noted.'),
      backgroundColor: AppColors.primaryGold,
      duration: const Duration(seconds: 2),
    ));
  }
}
