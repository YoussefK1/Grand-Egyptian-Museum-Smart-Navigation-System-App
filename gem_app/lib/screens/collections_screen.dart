import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/app_nav.dart';
import '../utils/constants.dart';
import '../widgets/gem_widgets.dart';

const List<Color> _clusterColors = [
  Color(0xFFE6B800), Color(0xFF4FC3F7), Color(0xFFEF5350), Color(0xFF66BB6A), Color(0xFFAB47BC),
  Color(0xFFFF8A65), Color(0xFF26C6DA), Color(0xFFD4E157), Color(0xFFEC407A), Color(0xFF8D6E63),
  Color(0xFF7E57C2), Color(0xFF9CCC65), Color(0xFFFFCA28), Color(0xFF29B6F6),
];

Color clusterColor(int id) => _clusterColors[id % _clusterColors.length];

/// AI exhibition module: thematic artifact groups discovered with CLIP/TF-IDF embeddings + K-Means.
class CollectionsScreen extends StatefulWidget {
  const CollectionsScreen({Key? key}) : super(key: key);

  @override
  State<CollectionsScreen> createState() => _CollectionsScreenState();
}

class _CollectionsScreenState extends State<CollectionsScreen> {
  Map<String, dynamic>? _data;
  Map<String, dynamic>? _map;
  bool _showMap = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final d = await GemApi.collections();
      final m = await GemApi.collectionsMap();
      if (!mounted) return;
      setState(() {
        _data = d;
        _map = m;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Could not load collections: $e');
    }
  }

  void _about() {
    final m = Map<String, dynamic>.from((_data!['metrics'] ?? {}) as Map);
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.primaryDark,
        title: Text('How these groups were made', style: AppTextStyles.menuTitle),
        content: SingleChildScrollView(
          child: Text(
            'Every artifact (name + description, and its photo when available) is converted to an embedding '
            'vector (${m['embedder']}). K-Means groups similar vectors into ${m['kmeans_k']} thematic collections '
            '(silhouette ${m['kmeans_silhouette']}). DBSCAN flags one-of-a-kind pieces that belong to no dense theme.',
            style: const TextStyle(color: Colors.white70),
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(_error!, style: const TextStyle(color: Colors.redAccent))));
    }
    if (_data == null) return const Center(child: CircularProgressIndicator());
    final cols = (_data!['collections'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    return ListView(padding: const EdgeInsets.only(bottom: 100), children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 4),
        child: Row(children: [
          Expanded(
              child: Text('${cols.length} AI-discovered themes  |  ${_data!['embedder']}',
                  style: const TextStyle(color: Colors.white60, fontSize: 12))),
          IconButton(onPressed: _about, icon: Icon(Icons.info_outline, color: AppColors.primaryGold)),
        ]),
      ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(children: [
          GemChip(label: 'Groups', selected: !_showMap, icon: Icons.grid_view, onTap: () => setState(() => _showMap = false)),
          const SizedBox(width: 8),
          GemChip(label: 'Similarity map', selected: _showMap, icon: Icons.bubble_chart, onTap: () => setState(() => _showMap = true)),
        ]),
      ),
      const SizedBox(height: 8),
      if (_showMap) _mapView(cols) else ..._groupCards(cols),
    ]);
  }

  List<Widget> _groupCards(List<Map<String, dynamic>> cols) {
    return [
      for (final c in cols)
        GestureDetector(
          onTap: () => Navigator.push(
              context, MaterialPageRoute<void>(builder: (_) => CollectionDetailScreen(cluster: c))),
          child: GemCard(
            child: Row(children: [
              Container(
                  width: 8,
                  height: 64,
                  decoration: BoxDecoration(
                      color: clusterColor((c['cluster_id'] as num).toInt()), borderRadius: BorderRadius.circular(4))),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(c['label'] as String, style: AppTextStyles.cardTitle),
                  const SizedBox(height: 2),
                  Text('${c['size']} artifacts  |  e.g. ${c['representative_name']}',
                      maxLines: 1, overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white60, fontSize: 12)),
                  const SizedBox(height: 6),
                  Wrap(spacing: 6, runSpacing: 4, children: [
                    for (final k in (c['keywords'] as List).take(4))
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                            color: Colors.white10, borderRadius: BorderRadius.circular(10)),
                        child: Text('$k', style: const TextStyle(color: Colors.white70, fontSize: 10)),
                      ),
                  ]),
                ]),
              ),
              const Icon(Icons.chevron_right, color: Colors.white54),
            ]),
          ),
        ),
    ];
  }

  Widget _mapView(List<Map<String, dynamic>> cols) {
    final pts = (_map!['points'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    return GemCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Each dot is an artifact. Nearby dots are similar; X marks one-of-a-kind pieces.',
            style: TextStyle(color: Colors.white60, fontSize: 12)),
        const SizedBox(height: 10),
        Container(
          height: 320,
          decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(10)),
          child: LayoutBuilder(builder: (context, box) {
            return GestureDetector(
              onTapUp: (d) {
                Map<String, dynamic>? best;
                double bestDist = 24.0 * 24.0;
                for (final p in pts) {
                  final dx = 12 + (p['x'] as num).toDouble() * (box.maxWidth - 24) - d.localPosition.dx;
                  final dy = 12 + (p['y'] as num).toDouble() * (box.maxHeight - 24) - d.localPosition.dy;
                  final dist = dx * dx + dy * dy;
                  if (dist < bestDist) {
                    bestDist = dist;
                    best = p;
                  }
                }
                if (best != null) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text('${best['name']}'),
                      backgroundColor: clusterColor((best['cluster'] as num).toInt()),
                      duration: const Duration(seconds: 2)));
                }
              },
              child: CustomPaint(painter: _ScatterPainter(pts), size: Size.infinite),
            );
          }),
        ),
        const SizedBox(height: 10),
        Wrap(spacing: 10, runSpacing: 6, children: [
          for (final c in cols)
            Row(mainAxisSize: MainAxisSize.min, children: [
              Container(width: 10, height: 10, decoration: BoxDecoration(color: clusterColor((c['cluster_id'] as num).toInt()), shape: BoxShape.circle)),
              const SizedBox(width: 4),
              Text(c['label'] as String, style: const TextStyle(color: Colors.white70, fontSize: 10)),
            ]),
        ]),
      ]),
    );
  }
}

class _ScatterPainter extends CustomPainter {
  final List<Map<String, dynamic>> pts;
  _ScatterPainter(this.pts);

  @override
  void paint(Canvas canvas, Size size) {
    for (final p in pts) {
      final o = Offset(12 + (p['x'] as num).toDouble() * (size.width - 24),
          12 + (p['y'] as num).toDouble() * (size.height - 24));
      final c = clusterColor((p['cluster'] as num).toInt());
      if (p['outlier'] == true) {
        final paint = Paint()
          ..color = c
          ..strokeWidth = 2.5
          ..strokeCap = StrokeCap.round;
        canvas.drawLine(o + const Offset(-5, -5), o + const Offset(5, 5), paint);
        canvas.drawLine(o + const Offset(-5, 5), o + const Offset(5, -5), paint);
      } else {
        canvas.drawCircle(o, 5.5, Paint()..color = c);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _ScatterPainter old) => old.pts != pts;
}

class CollectionDetailScreen extends StatefulWidget {
  final Map<String, dynamic> cluster;
  const CollectionDetailScreen({Key? key, required this.cluster}) : super(key: key);

  @override
  State<CollectionDetailScreen> createState() => _CollectionDetailScreenState();
}

class _CollectionDetailScreenState extends State<CollectionDetailScreen> {
  Map<String, dynamic>? _detail;

  @override
  void initState() {
    super.initState();
    GemApi.collectionDetail((widget.cluster['cluster_id'] as num).toInt()).then((d) {
      if (mounted) setState(() => _detail = d);
    });
  }

  @override
  Widget build(BuildContext context) {
    final arts = _detail == null
        ? <Map<String, dynamic>>[]
        : (_detail!['artifacts'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    return Scaffold(
      body: GemBackground(
        child: SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                IconButton(onPressed: () => Navigator.pop(context), icon: Icon(Icons.arrow_back, color: AppColors.textLight)),
                Expanded(child: Text(widget.cluster['label'] as String, style: AppTextStyles.welcomeTitle.copyWith(fontSize: 20))),
              ]),
            ),
            Expanded(
              child: _detail == null
                  ? const Center(child: CircularProgressIndicator())
                  : ListView(padding: const EdgeInsets.only(bottom: 30), children: [
                      for (final a in arts)
                        GestureDetector(
                          onTap: () => showArtifactSheet(context, a),
                          child: GemCard(
                            child: Row(children: [
                              Expanded(
                                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                  Text(a['name'] as String, style: AppTextStyles.cardTitle.copyWith(fontSize: 15)),
                                  const SizedBox(height: 3),
                                  Text('${a['era']}  |  ${a['gallery']}',
                                      style: const TextStyle(color: Colors.white60, fontSize: 12)),
                                ]),
                              ),
                              const Icon(Icons.chevron_right, color: Colors.white54),
                            ]),
                          ),
                        ),
                    ]),
            ),
          ]),
        ),
      ),
    );
  }
}

/// Bottom sheet with details, "similar artifacts" (embedding neighbours) and a navigate button.
void showArtifactSheet(BuildContext context, Map<String, dynamic> a) {
  showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: AppColors.primaryDark,
    shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
    builder: (ctx) => _ArtifactSheet(artifact: a),
  );
}

class _ArtifactSheet extends StatefulWidget {
  final Map<String, dynamic> artifact;
  const _ArtifactSheet({Key? key, required this.artifact}) : super(key: key);

  @override
  State<_ArtifactSheet> createState() => _ArtifactSheetState();
}

class _ArtifactSheetState extends State<_ArtifactSheet> {
  List<Map<String, dynamic>> _similar = [];

  @override
  void initState() {
    super.initState();
    GemApi.similar(widget.artifact['artifact_id'] as String).then((s) {
      if (mounted) setState(() => _similar = s);
    });
  }

  @override
  Widget build(BuildContext context) {
    final a = widget.artifact;
    final img = (a['image_asset'] ?? '') as String;
    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.75,
      maxChildSize: 0.95,
      builder: (context, controller) => ListView(controller: controller, padding: const EdgeInsets.all(20), children: [
        if (img.isNotEmpty)
          ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.asset(img, height: 190, fit: BoxFit.cover,
                  errorBuilder: (c, e, s) => const SizedBox(height: 10))),
        const SizedBox(height: 12),
        Text(a['name'] as String, style: AppTextStyles.museumTitle.copyWith(fontSize: 20)),
        const SizedBox(height: 6),
        Wrap(spacing: 8, runSpacing: 6, children: [
          GemChip(label: '${a['era']}', selected: true),
          GemChip(label: '${a['category']}', selected: true),
          GemChip(label: '${a['material']}', selected: true),
        ]),
        const SizedBox(height: 12),
        Text(a['description'] as String, style: const TextStyle(color: Colors.white, height: 1.4)),
        const SizedBox(height: 10),
        Text('Where: ${a['gallery']}', style: TextStyle(color: AppColors.primaryGold)),
        const SizedBox(height: 12),
        GemButton(
          label: 'Navigate to this artifact',
          icon: Icons.navigation,
          onPressed: () {
            Navigator.pop(context);
            AppNav.navigateTo(NavTarget(startId: 'ENTRANCE', goalId: a['zone_id'] as String));
          },
        ),
        if (_similar.isNotEmpty) ...[
          const SizedBox(height: 18),
          Text('Similar artifacts (AI embedding neighbours)', style: AppTextStyles.cardTitle),
          const SizedBox(height: 6),
          for (final s in _similar.take(5))
            ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.auto_awesome, color: AppColors.primaryGold, size: 18),
              title: Text(s['name'] as String, style: const TextStyle(color: Colors.white)),
              subtitle: Text('similarity ${s['similarity']}  |  ${s['gallery']}',
                  style: const TextStyle(color: Colors.white54, fontSize: 11)),
            ),
        ],
      ]),
    );
  }
}
