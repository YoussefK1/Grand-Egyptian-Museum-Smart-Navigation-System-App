import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/server_settings.dart';
import 'chat_screen.dart';

class MenuScreen extends StatelessWidget {
  const MenuScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppColors.primaryDark.withOpacity(0.98),
      width: MediaQuery.of(context).size.width * 0.8,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with Logo
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // GEM Logo
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white.withOpacity(0.1),
                      border: Border.all(
                        color: AppColors.primaryGold,
                        width: 2,
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Image.asset(
                        'assets/images/gem_logo.png',
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Explore GEM',
                    style: AppTextStyles.menuTitle,
                  ),
                ],
              ),
            ),

            // Divider
            const Divider(
              color: Colors.white24,
              height: 1,
              indent: 20,
              endIndent: 20,
            ),

            // Menu Items
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildMenuItem('Manage Account', Icons.person_outline, () {
                      Navigator.pop(context);
                      // Navigate to account management
                    }),
                    _buildMenuItem('Saved Exhibits', Icons.bookmark_border, () {
                      Navigator.pop(context);
                      // Navigate to saved exhibits
                    }),
                    _buildMenuItem('Saved Tours', Icons.map_outlined, () {
                      Navigator.pop(context);
                      // Navigate to saved tours
                    }),

                    const SizedBox(height: 24),

                    _buildMenuItem('AI Chat Assistant', Icons.smart_toy_outlined, () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute<void>(builder: (_) => const ChatScreen()));
                    }),
                    _buildMenuItem('Server address (AI backend)', Icons.settings_outlined, () {
                      Navigator.pop(context);
                      showServerSettings(context);
                    }),
                    _buildMenuItem('Help & Support', Icons.help_outline, () {
                      Navigator.pop(context);
                      // Navigate to help
                    }),
                    _buildMenuItem('About GEM', Icons.info_outline, () {
                      Navigator.pop(context);
                      // Navigate to about
                    }),
                  ],
                ),
              ),
            ),

            // Footer
            Container(
              padding: const EdgeInsets.all(24.0),
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.3),
                border: Border(
                  top: BorderSide(
                    color: AppColors.primaryGold.withOpacity(0.3),
                    width: 1,
                  ),
                ),
              ),
              child: Column(
                children: [
                  Text(
                    'GRAND EGYPTIAN MUSEUM',
                    style: AppTextStyles.museumTitle.copyWith(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Cairo, Egypt',
                    style: AppTextStyles.cardDescription.copyWith(fontSize: 14),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '© 2026 All Rights Reserved Built At UFE By Youssef & Omar',
                    style: AppTextStyles.cardDescription.copyWith(fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem(String title, IconData icon, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppColors.primaryGold, size: 24),
      title: Text(
        title,
        style: AppTextStyles.menuItem,
      ),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 4),
      horizontalTitleGap: 8,
      minLeadingWidth: 0,
    );
  }
}