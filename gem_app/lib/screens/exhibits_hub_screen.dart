import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/gem_widgets.dart';
import 'collections_screen.dart';
import 'exhibits_screen.dart';
import 'menu_screen.dart';

/// Exhibits tab = the original featured-artifact viewer + the new AI thematic collections.
class ExhibitsHubScreen extends StatefulWidget {
  const ExhibitsHubScreen({Key? key}) : super(key: key);

  @override
  State<ExhibitsHubScreen> createState() => _ExhibitsHubScreenState();
}

class _ExhibitsHubScreenState extends State<ExhibitsHubScreen> {
  int _tab = 1;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: const MenuScreen(),
      body: _tab == 0
          ? Stack(children: [
              const ExhibitsScreen(),
              Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: SafeArea(child: _switcher()),
              ),
            ])
          : SafeArea(
              child: GemBackground(
                child: Column(children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                    child: Row(children: [
                      IconButton(
                          onPressed: () => _scaffoldKey.currentState!.openDrawer(),
                          icon: Icon(Icons.menu, color: AppColors.textLight, size: 28)),
                      const SizedBox(width: 12),
                      Expanded(child: Text('Exhibits', style: AppTextStyles.welcomeTitle.copyWith(fontSize: 24))),
                    ]),
                  ),
                  _switcher(),
                  const Expanded(child: CollectionsScreen()),
                ]),
              ),
            ),
    );
  }

  Widget _switcher() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Align(
        alignment: Alignment.centerRight,
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          GemChip(label: 'Featured', selected: _tab == 0, icon: Icons.star, onTap: () => setState(() => _tab = 0)),
          const SizedBox(width: 8),
          GemChip(label: 'AI Collections', selected: _tab == 1, icon: Icons.auto_awesome, onTap: () => setState(() => _tab = 1)),
        ]),
      ),
    );
  }
}
