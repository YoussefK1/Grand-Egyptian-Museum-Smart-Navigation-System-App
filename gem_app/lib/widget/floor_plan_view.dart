import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'gem_widgets.dart';

/// Draws a schematic floor plan with the route (or tour path) on one floor.
/// [nodes] is the ordered list of route nodes {id,name,floor,x,y}. [markers] maps node id -> short label.
class FloorPlanView extends StatelessWidget {
  final List<Map<String, dynamic>> nodes;
  final int floor;
  final Map<String, String> markers;
  final String? startId;
  final String? goalId;
  final double height;

  const FloorPlanView({
    Key? key,
    required this.nodes,
    required this.floor,
    this.markers = const {},
    this.startId,
    this.goalId,
    this.height = 230,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.35),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white12),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: CustomPaint(
          painter: _PlanPainter(nodes, floor, markers, startId, goalId),
          child: const SizedBox.expand(),
        ),
      ),
    );
  }
}

class _PlanPainter extends CustomPainter {
  final List<Map<String, dynamic>> seq;
  final int floor;
  final Map<String, String> markers;
  final String? startId;
  final String? goalId;
  _PlanPainter(this.seq, this.floor, this.markers, this.startId, this.goalId);

  int _f(Map<String, dynamic> n) => (n['floor'] as num).toInt();
  double _x(Map<String, dynamic> n) => (n['x'] as num).toDouble();
  double _y(Map<String, dynamic> n) => (n['y'] as num).toDouble();

  @override
  void paint(Canvas canvas, Size size) {
    final pts = seq.where((n) => _f(n) == floor).toList();
    if (pts.isEmpty) {
      _text(canvas, 'No part of the route on this level', Offset(size.width / 2, size.height / 2),
          Colors.white54, 12, center: true);
      return;
    }
    double minX = _x(pts.first), maxX = minX, minY = _y(pts.first), maxY = minY;
    for (final n in pts) {
      if (_x(n) < minX) minX = _x(n);
      if (_x(n) > maxX) maxX = _x(n);
      if (_y(n) < minY) minY = _y(n);
      if (_y(n) > maxY) maxY = _y(n);
    }
    final spanX = (maxX - minX) < 80 ? 80.0 : (maxX - minX);
    final spanY = (maxY - minY) < 60 ? 60.0 : (maxY - minY);
    const pad = 34.0;
    final sx = (size.width - 2 * pad) / spanX;
    final sy = (size.height - 2 * pad) / spanY;
    final s = sx < sy ? sx : sy;
    final cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    Offset p(Map<String, dynamic> n) =>
        Offset(size.width / 2 + (_x(n) - cx) * s, size.height / 2 + (_y(n) - cy) * s);

    // faint grid
    final grid = Paint()
      ..color = Colors.white10
      ..strokeWidth = 1;
    for (double gx = 0; gx < size.width; gx += 32) {
      canvas.drawLine(Offset(gx, 0), Offset(gx, size.height), grid);
    }
    for (double gy = 0; gy < size.height; gy += 32) {
      canvas.drawLine(Offset(0, gy), Offset(size.width, gy), grid);
    }

    // path
    final line = Paint()
      ..color = AppColors.primaryGold
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;
    for (int i = 0; i < seq.length - 1; i++) {
      final a = seq[i], b = seq[i + 1];
      if (_f(a) == floor && _f(b) == floor && !(a['id'] == b['id'])) {
        canvas.drawLine(p(a), p(b), line);
      }
    }
    // nodes
    final drawn = <String>{};
    for (final n in pts) {
      final id = n['id'] as String;
      if (!drawn.add(id)) continue;
      final o = p(n);
      Color c = AppColors.secondaryGold;
      double r = 6;
      if (id == startId) {
        c = Colors.greenAccent.shade400;
        r = 9;
      } else if (id == goalId) {
        c = Colors.redAccent;
        r = 9;
      } else if (markers.containsKey(id)) {
        c = AppColors.accentGold;
        r = 11;
      }
      canvas.drawCircle(o, r, Paint()..color = c);
      canvas.drawCircle(o, r, Paint()
        ..color = Colors.black
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5);
      if (markers.containsKey(id)) {
        _text(canvas, markers[id]!, o, Colors.black, 11, center: true, bold: true);
      }
      String name = (n['name'] ?? '').toString();
      if (name.length > 24) name = '${name.substring(0, 22)}..';
      _text(canvas, name, o + Offset(0, r + 9), Colors.white70, 9, center: true);
    }
  }

  void _text(Canvas canvas, String t, Offset at, Color color, double fs,
      {bool center = false, bool bold = false}) {
    final tp = TextPainter(
      text: TextSpan(
          text: t,
          style: TextStyle(color: color, fontSize: fs, fontWeight: bold ? FontWeight.bold : FontWeight.normal)),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, center ? at - Offset(tp.width / 2, tp.height / 2) : at);
  }

  @override
  bool shouldRepaint(covariant _PlanPainter old) => true;
}

/// Floor tabs + plan for a list of route nodes.
class RoutePlanTabs extends StatefulWidget {
  final List<Map<String, dynamic>> nodes;
  final Map<String, String> markers;
  final String? startId;
  final String? goalId;
  const RoutePlanTabs({Key? key, required this.nodes, this.markers = const {}, this.startId, this.goalId})
      : super(key: key);

  @override
  State<RoutePlanTabs> createState() => _RoutePlanTabsState();
}

class _RoutePlanTabsState extends State<RoutePlanTabs> {
  int? _floor;

  @override
  Widget build(BuildContext context) {
    final floors = <int>[];
    for (final n in widget.nodes) {
      final f = (n['floor'] as num).toInt();
      if (!floors.contains(f)) floors.add(f);
    }
    floors.sort();
    if (floors.isEmpty) return const SizedBox.shrink();
    final current = (_floor != null && floors.contains(_floor)) ? _floor! : floors.first;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Wrap(spacing: 8, runSpacing: 6, children: [
        for (final f in floors)
          GemChip(label: floorName(f), selected: f == current, onTap: () => setState(() => _floor = f)),
      ]),
      const SizedBox(height: 8),
      FloorPlanView(
        nodes: widget.nodes,
        floor: current,
        markers: widget.markers,
        startId: widget.startId,
        goalId: widget.goalId,
      ),
    ]);
  }
}
