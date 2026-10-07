import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../utils/constants.dart';
import '../widgets/gem_widgets.dart';
import '../widgets/indoor_navigation_panel.dart';
import 'menu_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({Key? key}) : super(key: key);

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  // Launch Google Maps with directions
  Future<void> _launchGoogleMapsDirections() async {
    const gemCoordinates = '29.9855,31.1325'; // Approximate GEM coordinates
    final url = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$gemCoordinates&travelmode=driving');

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Could not launch Google Maps'),
          backgroundColor: AppColors.primaryGold,
        ),
      );
    }
  }

  // Launch general Google Maps to GEM location
  Future<void> _openGEMInGoogleMaps() async {
    const gemCoordinates = '29.9855,31.1325';
    final url = Uri.parse('https://www.google.com/maps/search/?api=1&query=$gemCoordinates');

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: const MenuScreen(),
      body: SafeArea(
        child: GemBackground(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => _scaffoldKey.currentState!.openDrawer(),
                      icon: Icon(Icons.menu, color: AppColors.textLight, size: 28),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text('Navigation', style: AppTextStyles.welcomeTitle.copyWith(fontSize: 24)),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 90),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 8),
                        _buildSectionTitle('Indoor Navigation'),
                        const SizedBox(height: 8),
                        const IndoorNavigationPanel(),
                        const SizedBox(height: 20),
                        _buildSectionTitle('Getting Here'),
                        const SizedBox(height: 12),
                        _buildTransportationSection(),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Text(
        title,
        style: AppTextStyles.sectionTitle,
      ),
    );
  }

  Widget _buildTransportationSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: AppColors.cardBg,
          border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // By Car
              _buildTransportCard(
                icon: Icons.directions_car,
                title: 'By Car',
                description: 'Exit onto Cairo/Alex Desert Rd, head towards El Remayoh Sq., and enter Gate 2',
                buttonText: 'Get Directions',
                onPressed: _launchGoogleMapsDirections,
              ),
              const SizedBox(height: 16),

              // By Metro
              _buildTransportCard(
                icon: Icons.train,
                title: 'By Metro',
                description: 'Coming Soon - Planned metro line extension to GEM',
                buttonText: 'View Map',
                onPressed: _openGEMInGoogleMaps,
                isComingSoon: true,
              ),

              const SizedBox(height: 12),

              // Open in Google Maps Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _openGEMInGoogleMaps,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[800],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  icon: FaIcon(FontAwesomeIcons.google, size: 18),
                  label: Text(
                    'Open in Google Maps',
                    style: AppTextStyles.buttonText.copyWith(fontSize: 14),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTransportCard({
    required IconData icon,
    required String title,
    required String description,
    required String buttonText,
    required VoidCallback onPressed,
    bool isComingSoon = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: AppColors.primaryGold, size: 22),
              const SizedBox(width: 10),
              Text(
                title,
                style: AppTextStyles.cardTitle.copyWith(fontSize: 16),
              ),
              if (isComingSoon) ...[
                const SizedBox(width: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.blue[800],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'Coming Soon',
                    style: TextStyle(color: Colors.white, fontSize: 10),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: AppTextStyles.cardDescription,
          ),
          const SizedBox(height: 12),
          if (!isComingSoon)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onPressed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGold,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                ),
                child: Text(
                  buttonText,
                  style: AppTextStyles.buttonText.copyWith(fontSize: 14),
                ),
              ),
            ),
        ],
      ),
    );
  }

}
