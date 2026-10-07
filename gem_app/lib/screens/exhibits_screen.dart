import 'dart:math';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../utils/constants.dart';
import 'menu_screen.dart';

class ExhibitsScreen extends StatefulWidget {
  const ExhibitsScreen({Key? key}) : super(key: key);

  @override
  State<ExhibitsScreen> createState() => _ExhibitsScreenState();
}

class _ExhibitsScreenState extends State<ExhibitsScreen> {
  final TextEditingController _searchController = TextEditingController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  String _selectedArtifact = 'tutankhamun';
  double _rotationX = 0.0;
  double _rotationY = 0.0;
  double _zoomLevel = 1.0;
  bool _is3DView = false;
  bool _showDetails = true;
  int _currentInfoTab = 0;

  // For tracking previous position in scale gesture
  Offset _previousFocalPoint = Offset.zero;

  // Artifacts Data
  final List<Map<String, dynamic>> artifacts = [
    {
      'id': 'tutankhamun',
      'title': 'Tutankhamun\'s Golden Mask',
      'description': 'The iconic gold funeral mask of the boy pharaoh Tutankhamun, discovered in his tomb in 1922',
      'era': 'New Kingdom, 18th Dynasty (c. 1323 BC)',
      'discovered': 'KV62, Valley of the Kings, 1922',
      'material': 'Solid gold with semi-precious stones',
      'dimensions': '54 cm high, 39.3 cm wide, 49 cm deep',
      'weight': '11 kg',
      'currentLocation': 'Grand Egyptian Museum, Gallery of Royal Treasures',
      'funFact': 'The mask\'s eyes are made of obsidian and quartz, giving it a lifelike appearance',
      'image': 'assets/images/tutankhamun_mask.png',
      'galleryImage': 'assets/images/tutankhamun_gallery.jpg',
      'resources': [
        {
          'title': 'Virtual Tour of Tomb',
          'url': 'https://artsandculture.google.com/story/tutankhamun-s-tomb/QgWBpYF1qelPJg',
          'icon': Icons.tour,
        },
        {
          'title': 'Scientific Analysis',
          'url': 'https://www.nature.com/articles/s41598-020-61198-6',
          'icon': Icons.science,
        },
        {
          'title': 'Historical Documentary',
          'url': 'https://www.youtube.com/watch?v=smv3C5cFGcQ',
          'icon': Icons.ondemand_video,
        },
        {
          'title': 'Interactive Timeline',
          'url': 'https://www.metmuseum.org/toah/hd/tuta/hd_tuta.htm',
          'icon': Icons.timeline,
        },
      ],
    },
    {
      'id': 'ramses',
      'title': 'Colossal Statue of Ramses II',
      'description': 'One of the largest surviving statues from ancient Egypt, depicting Pharaoh Ramses II',
      'era': 'New Kingdom, 19th Dynasty (c. 1279-1213 BC)',
      'discovered': 'Memphis, 1820',
      'material': 'Red granite',
      'dimensions': '10.5 meters tall (original height)',
      'weight': '83 tons',
      'currentLocation': 'Grand Egyptian Museum, Grand Atrium',
      'funFact': 'The statue was originally painted in bright colors, traces of which can still be seen',
      'image': 'assets/images/ramses_statue.png',
      'galleryImage': 'assets/images/ramses_gallery.jpg',
      'resources': [
        {
          'title': 'Archaeological Report',
          'url': 'https://www.academia.edu/Documents/in/Ramses_II_Statue',
          'icon': Icons.article,
        },
        {
          'title': 'Conservation Process',
          'url': 'https://www.getty.edu/conservation/publications_resources/newsletters/28_2/feature.html',
          'icon': Icons.construction,
        },
        {
          'title': 'Virtual Reconstruction',
          'url': 'https://sketchfab.com/3d-models/statue-of-ramses-ii',
          'icon': Icons.visibility,
        },
        {
          'title': 'Educational Resources',
          'url': 'https://www.britishmuseum.org/collection/galleries/egyptian-sculpture',
          'icon': Icons.school,
        },
      ],
    },
  ];

  // Interactive 3D Simulation Data
  final List<Map<String, dynamic>> _tutankhamun3DViews = [
    {'angle': 'Front View', 'rotation': 0.0, 'scale': 1.0},
    {'angle': 'Left Profile', 'rotation': 90.0, 'scale': 1.0},
    {'angle': 'Right Profile', 'rotation': 270.0, 'scale': 1.0},
    {'angle': 'Back View', 'rotation': 180.0, 'scale': 1.0},
    {'angle': 'Close-up Face', 'rotation': 0.0, 'scale': 1.8},
    {'angle': 'Crown Detail', 'rotation': 0.0, 'scale': 2.0},
  ];

  final List<Map<String, dynamic>> _ramses3DViews = [
    {'angle': 'Full Statue', 'rotation': 0.0, 'scale': 0.8},
    {'angle': 'Face Close-up', 'rotation': 0.0, 'scale': 2.0},
    {'angle': 'Left Side', 'rotation': 90.0, 'scale': 1.0},
    {'angle': 'Right Side', 'rotation': 270.0, 'scale': 1.0},
    {'angle': 'Hieroglyphics', 'rotation': 0.0, 'scale': 3.0},
    {'angle': 'Base Details', 'rotation': 0.0, 'scale': 2.5},
  ];

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      setState(() {});
    });
  }

  Future<void> _launchResource(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Could not open resource'),
          backgroundColor: AppColors.primaryGold,
        ),
      );
    }
  }

  void _toggle3DView() {
    setState(() {
      _is3DView = !_is3DView;
      if (_is3DView) {
        _rotationX = 0.0;
        _rotationY = 0.0;
        _zoomLevel = 1.0;
        _previousFocalPoint = Offset.zero;
      }
    });
  }

  void _resetView() {
    setState(() {
      _rotationX = 0.0;
      _rotationY = 0.0;
      _zoomLevel = 1.0;
      _previousFocalPoint = Offset.zero;
    });
  }

  // Gesture handling methods
  void _handleScaleStart(ScaleStartDetails details) {
    _previousFocalPoint = details.focalPoint;
  }

  void _handleScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      if (!_is3DView) return;

      // Handle zooming (scale change)
      if (details.scale != 1.0) {
        _zoomLevel = (_zoomLevel * details.scale).clamp(0.5, 3.0);
      }

      // Handle panning/rotation (focal point change)
      if (details.focalPointDelta != Offset.zero) {
        // Use the delta to calculate rotation
        _rotationX += details.focalPointDelta.dy * 0.01;
        _rotationY += details.focalPointDelta.dx * 0.01;
      }

      _previousFocalPoint = details.focalPoint;
    });
  }

  void _handleScaleEnd(ScaleEndDetails details) {
    // Reset previous focal point when gesture ends
    _previousFocalPoint = Offset.zero;
  }

  Widget _buildArtifactSelector() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.5),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Choose an Artifact',
            style: AppTextStyles.cardTitle.copyWith(fontSize: 18),
          ),
          const SizedBox(height: 12),

          // Artifact Cards
          Row(
            children: [
              Expanded(
                child: _buildArtifactCard(
                  'tutankhamun',
                  'Tutankhamun\'s Golden Mask',
                  'Solid Gold Masterpiece',
                  Icons.verified,
                  Colors.amber,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildArtifactCard(
                  'ramses',
                  'Colossal Statue of Ramses II',
                  'Granite Monument',
                  Icons.public,
                  Colors.deepOrange,
                ),
              ),
            ],
          ),

          // Coming Soon Indicator
          Container(
            margin: const EdgeInsets.only(top: 16),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.blue.withOpacity(0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.access_time, size: 16, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'More artifacts coming soon...',
                  style: TextStyle(color: Colors.blue, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1);
  }

  Widget _buildArtifactCard(String id, String title, String subtitle, IconData icon, Color color) {
    final isSelected = _selectedArtifact == id;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedArtifact = id;
          _resetView();
          _is3DView = false;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: isSelected ? color.withOpacity(0.2) : Colors.black.withOpacity(0.3),
          border: Border.all(
            color: isSelected ? color : Colors.transparent,
            width: 2,
          ),
          boxShadow: isSelected ? [
            BoxShadow(
              color: color.withOpacity(0.3),
              blurRadius: 10,
              spreadRadius: 2,
            ),
          ] : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.3),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, size: 20, color: color),
                ),
                const Spacer(),
                if (isSelected)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      'VIEWING',
                      style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                color: color,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ).animate().scale(duration: 300.ms),
    );
  }

  Widget _buildArtifactDisplay() {
    final artifact = artifacts.firstWhere((a) => a['id'] == _selectedArtifact);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.5),
            blurRadius: 15,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          // Title and Controls
          Row(
            children: [
              Expanded(
                child: Text(
                  artifact['title'] as String,
                  style: AppTextStyles.cardTitle.copyWith(fontSize: 22),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 12),
              // View Controls
              Row(
                children: [
                  Tooltip(
                    message: _is3DView ? 'Switch to 2D' : 'Switch to 3D',
                    child: IconButton(
                      onPressed: _toggle3DView,
                      icon: Icon(
                        _is3DView ? Icons.view_in_ar : Icons.view_in_ar_outlined,
                        color: AppColors.primaryGold,
                      ),
                    ),
                  ),
                  Tooltip(
                    message: 'Reset View',
                    child: IconButton(
                      onPressed: _resetView,
                      icon: Icon(Icons.replay, color: AppColors.primaryGold),
                    ),
                  ),
                  Tooltip(
                    message: _showDetails ? 'Hide Details' : 'Show Details',
                    child: IconButton(
                      onPressed: () {
                        setState(() {
                          _showDetails = !_showDetails;
                        });
                      },
                      icon: Icon(
                        _showDetails ? Icons.info : Icons.info_outline,
                        color: AppColors.primaryGold,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Interactive Display Area
          _buildInteractiveDisplay(artifact),

          if (_showDetails) ...[
            const SizedBox(height: 20),
            _buildArtifactDetails(artifact),
          ],
        ],
      ),
    ).animate().fadeIn(duration: 600.ms).slideY(begin: 0.1);
  }

  Widget _buildInteractiveDisplay(Map<String, dynamic> artifact) {
    return Container(
      height: 300,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.grey[900]!,
            Colors.black,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.8),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Stack(
        children: [
          // Interactive 3D Area
          Positioned.fill(
            child: GestureDetector(
              onScaleStart: _is3DView ? _handleScaleStart : null,
              onScaleUpdate: _is3DView ? _handleScaleUpdate : null,
              onScaleEnd: _is3DView ? _handleScaleEnd : null,
              child: Center(
                child: Transform(
                  alignment: Alignment.center,
                  transform: Matrix4.identity()
                    ..rotateX(_rotationX)
                    ..rotateY(_rotationY)
                    ..scale(_zoomLevel),
                  child: _buildArtifactVisualization(artifact),
                ),
              ),
            ),
          ),

          // 3D View Indicator
          if (_is3DView)
            Positioned(
              top: 12,
              left: 12,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.green),
                ),
                child: Row(
                  children: [
                    Icon(Icons.view_in_ar, size: 14, color: Colors.green),
                    const SizedBox(width: 6),
                    Text(
                      '3D INTERACTIVE VIEW',
                      style: TextStyle(color: Colors.green, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),

          // Interactive Controls Overlay
          Positioned(
            bottom: 12,
            right: 12,
            child: Column(
              children: [
                _buildControlButton(Icons.zoom_in, () {
                  setState(() {
                    _zoomLevel = (_zoomLevel + 0.2).clamp(0.5, 3.0);
                  });
                }),
                const SizedBox(height: 8),
                _buildControlButton(Icons.zoom_out, () {
                  setState(() {
                    _zoomLevel = (_zoomLevel - 0.2).clamp(0.5, 3.0);
                  });
                }),
                const SizedBox(height: 8),
                _buildControlButton(Icons.rotate_left, () {
                  setState(() {
                    _rotationY -= 0.3;
                  });
                }),
                const SizedBox(height: 8),
                _buildControlButton(Icons.rotate_right, () {
                  setState(() {
                    _rotationY += 0.3;
                  });
                }),
              ],
            ),
          ),

          // Pre-set View Angles
          Positioned(
            bottom: 12,
            left: 12,
            child: Container(
              height: 40,
              child: ListView(
                scrollDirection: Axis.horizontal,
                shrinkWrap: true,
                children: (_selectedArtifact == 'tutankhamun' ? _tutankhamun3DViews : _ramses3DViews).map((view) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        _rotationY = view['rotation'] * (pi / 180);
                        _zoomLevel = view['scale'];
                        _is3DView = true;
                      });
                    },
                    child: Container(
                      margin: const EdgeInsets.only(right: 8),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.white24),
                      ),
                      child: Text(
                        view['angle'],
                        style: TextStyle(color: Colors.white, fontSize: 10),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),

          // Instructions Overlay
          if (_is3DView)
            Positioned(
              top: 50,
              left: 0,
              right: 0,
              child: Column(
                children: [
                  Text(
                    '👆 Drag to rotate • 👌 Pinch to zoom',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                      shadows: [
                        Shadow(
                          color: Colors.black,
                          blurRadius: 3,
                          offset: const Offset(1, 1),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Tap view angles below for quick navigation',
                    style: TextStyle(
                      color: Colors.white60,
                      fontSize: 10,
                      shadows: [
                        Shadow(
                          color: Colors.black,
                          blurRadius: 2,
                          offset: const Offset(1, 1),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildControlButton(IconData icon, VoidCallback onPressed) {
    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white24),
      ),
      child: IconButton(
        onPressed: onPressed,
        icon: Icon(icon, size: 18, color: Colors.white),
        padding: EdgeInsets.zero,
      ),
    );
  }

  Widget _buildArtifactVisualization(Map<String, dynamic> artifact) {
    final isTutankhamun = artifact['id'] == 'tutankhamun';

    if (_is3DView) {
      // Simulated 3D effect with multiple layers and shadows
      return Stack(
        alignment: Alignment.center,
        children: [
          // Background glow
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.3),
                  Colors.transparent,
                ],
                stops: const [0.1, 1.0],
              ),
            ),
          ),

          // Main artifact with 3D effect
          Container(
            width: 180,
            height: 250,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.5),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.8),
                  blurRadius: 20,
                  offset: const Offset(10, 10),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.asset(
                artifact['image'] as String,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  // Fallback with decorative placeholder
                  return Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.8),
                          Colors.black,
                        ],
                      ),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            isTutankhamun ? Icons.masks : Icons.account_balance,
                            size: 60,
                            color: Colors.white.withOpacity(0.7),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            artifact['title'] as String,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.9),
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),

          // 3D Depth effect overlay
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.6),
                  ],
                ),
              ),
            ),
          ),
        ],
      );
    } else {
      // 2D Gallery View
      return Container(
        width: 280,
        height: 280,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.6),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Stack(
            children: [
              // Background Image
              Image.asset(
                artifact['galleryImage'] as String,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.8),
                          Colors.black,
                        ],
                      ),
                    ),
                  );
                },
              ),

              // Overlay with artifact image
              Center(
                child: Container(
                  width: 200,
                  height: 200,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.8),
                        blurRadius: 30,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: ClipOval(
                    child: Image.asset(
                      artifact['image'] as String,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          decoration: BoxDecoration(
                            color: (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.3),
                          ),
                          child: Icon(
                            isTutankhamun ? Icons.masks : Icons.account_balance,
                            size: 80,
                            color: Colors.white,
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ),

              // Gallery label
              Positioned(
                bottom: 20,
                left: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black.withOpacity(0.8),
                      ],
                    ),
                  ),
                  child: Column(
                    children: [
                      Icon(Icons.museum, color: AppColors.primaryGold, size: 20),
                      const SizedBox(height: 5),
                      Text(
                        'GEM Exhibition Display',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }
  }

  Widget _buildArtifactDetails(Map<String, dynamic> artifact) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Tab Selection
        Container(
          height: 40,
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: [
              _buildDetailTab('Information', 0, Icons.info),
              _buildDetailTab('Resources', 1, Icons.library_books),
              _buildDetailTab('Timeline', 2, Icons.timeline),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Tab Content
        _buildTabContent(artifact),
      ],
    );
  }

  Widget _buildDetailTab(String label, int index, IconData icon) {
    final isSelected = _currentInfoTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _currentInfoTab = index;
          });
        },
        child: Container(
          margin: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primaryGold.withOpacity(0.3) : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? AppColors.primaryGold : Colors.transparent,
            ),
          ),
          child: Center(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 16, color: isSelected ? AppColors.primaryGold : Colors.white70),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: TextStyle(
                    color: isSelected ? AppColors.primaryGold : Colors.white70,
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTabContent(Map<String, dynamic> artifact) {
    switch (_currentInfoTab) {
      case 0: // Information
        return _buildInformationTab(artifact);
      case 1: // Resources
        return _buildResourcesTab(artifact);
      case 2: // Timeline
        return _buildTimelineTab(artifact);
      default:
        return _buildInformationTab(artifact);
    }
  }

  Widget _buildInformationTab(Map<String, dynamic> artifact) {
    final isTutankhamun = artifact['id'] == 'tutankhamun';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          artifact['description'] as String,
          style: AppTextStyles.cardDescription.copyWith(fontSize: 15),
        ),

        const SizedBox(height: 16),

        // Key Facts Grid
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            _buildFactCard(Icons.history, 'Historical Era', artifact['era'] as String),
            _buildFactCard(Icons.location_on, 'Discovery Site', artifact['discovered'] as String),
            _buildFactCard(Icons.architecture, 'Material', artifact['material'] as String),
            _buildFactCard(Icons.straighten, 'Dimensions', artifact['dimensions'] as String),
            _buildFactCard(Icons.scale, 'Weight', artifact['weight'] as String),
            _buildFactCard(Icons.place, 'Current Location', artifact['currentLocation'] as String),
          ],
        ),

        const SizedBox(height: 20),

        // Fun Fact
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: (isTutankhamun ? Colors.amber : Colors.deepOrange).withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(Icons.emoji_events, color: isTutankhamun ? Colors.amber : Colors.deepOrange),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Did You Know?',
                      style: TextStyle(
                        color: isTutankhamun ? Colors.amber : Colors.deepOrange,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      artifact['funFact'] as String,
                      style: TextStyle(color: Colors.white, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFactCard(IconData icon, String title, String value) {
    return Container(
      width: 150,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.5),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: AppColors.primaryGold),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildResourcesTab(Map<String, dynamic> artifact) {
    final resources = artifact['resources'] as List<dynamic>;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Explore more about this artifact through these resources:',
          style: AppTextStyles.cardDescription,
        ),

        const SizedBox(height: 16),

        ...resources.map((resource) {
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => _launchResource(resource['url'] as String),
                borderRadius: BorderRadius.circular(10),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.white12),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppColors.primaryGold.withOpacity(0.2),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(resource['icon'] as IconData, color: AppColors.primaryGold),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              resource['title'] as String,
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              resource['url'] as String,
                              style: TextStyle(
                                color: Colors.white54,
                                fontSize: 11,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      Icon(Icons.open_in_new, color: Colors.white54, size: 18),
                    ],
                  ),
                ),
              ),
            ),
          );
        }).toList(),

        const SizedBox(height: 16),

        // QR Code for sharing
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Icon(Icons.qr_code_2, size: 40, color: Colors.black),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Scan to Share',
                      style: TextStyle(
                        color: Colors.blue,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Share this artifact with friends using the QR code',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTimelineTab(Map<String, dynamic> artifact) {
    final isTutankhamun = artifact['id'] == 'tutankhamun';
    final timelineEvents = isTutankhamun
        ? [
      {'year': '1341 BC', 'event': 'Tutankhamun born'},
      {'year': '1332 BC', 'event': 'Ascends to throne at age 9'},
      {'year': '1323 BC', 'event': 'Tutankhamun dies, mask created'},
      {'year': '1323 BC', 'event': 'Buried in Valley of the Kings'},
      {'year': '1922 AD', 'event': 'Discovered by Howard Carter'},
      {'year': '1925 AD', 'event': 'Mask first publicly displayed'},
      {'year': '2015 AD', 'event': 'Major conservation project'},
      {'year': '2023 AD', 'event': 'Moved to Grand Egyptian Museum'},
    ]
        : [
      {'year': '1279 BC', 'event': 'Ramses II begins reign'},
      {'year': '1250 BC', 'event': 'Statue commissioned for Memphis'},
      {'year': '1213 BC', 'event': 'Ramses II dies'},
      {'year': '332 BC', 'event': 'Statue damaged during Persian invasion'},
      {'year': '1820 AD', 'event': 'Rediscovered by archaeologists'},
      {'year': '1955 AD', 'event': 'Moved to Cairo Museum'},
      {'year': '2006 AD', 'event': 'Major restoration completed'},
      {'year': '2023 AD', 'event': 'Installed at GEM Grand Atrium'},
    ];

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              Icon(
                isTutankhamun ? Icons.masks : Icons.account_balance,
                color: AppColors.primaryGold,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Historical Timeline of ${artifact['title'] as String}',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Timeline visualization
        Container(
          height: 250,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: timelineEvents.length,
            itemBuilder: (context, index) {
              final event = timelineEvents[index];
              final bool isAncient = event['year']!.contains('BC');

              return Container(
                width: 120,
                margin: EdgeInsets.only(
                  left: index == 0 ? 0 : 12,
                  right: index == timelineEvents.length - 1 ? 0 : 12,
                ),
                child: Column(
                  children: [
                    // Timeline node
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        color: isAncient ? Colors.amber.withOpacity(0.3) : Colors.blue.withOpacity(0.3),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: isAncient ? Colors.amber : Colors.blue,
                          width: 2,
                        ),
                      ),
                      child: Center(
                        child: Text(
                          event['year']!,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),

                    // Timeline connector
                    Container(
                      width: 2,
                      height: 40,
                      color: Colors.white30,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                    ),

                    // Event description
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.white12),
                      ),
                      child: Text(
                        event['event']!,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),

        const SizedBox(height: 16),

        // Historical context
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.green.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(Icons.history_edu, color: Colors.green),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Historical Significance',
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isTutankhamun
                          ? 'The mask represents the pinnacle of Egyptian goldsmithing and provides insight into royal burial practices of the New Kingdom.'
                          : 'This statue exemplifies the monumental scale of Ramses II\'s building projects and his deification during his lifetime.',
                      style: TextStyle(color: Colors.white, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: MenuScreen(),
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/background.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            color: Colors.black.withOpacity(0.7),
            child: Column(
              children: [
                // Header with menu and title
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: Row(
                    children: [
                      IconButton(
                        onPressed: () => _scaffoldKey.currentState!.openDrawer(),
                        icon: Icon(
                          Icons.menu,
                          color: AppColors.textLight,
                          size: 28,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Text(
                          'Exhibits',
                          style: AppTextStyles.welcomeTitle.copyWith(
                            fontSize: 24,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Search Bar
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  child: Container(
                    decoration: BoxDecoration(
                      color: AppColors.inputBg,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: AppColors.primaryGold.withOpacity(0.3),
                      ),
                    ),
                    child: TextField(
                      controller: _searchController,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        hintText: 'Search artifacts...',
                        hintStyle: const TextStyle(color: Colors.white54),
                        prefixIcon: Icon(
                          Icons.search,
                          color: AppColors.primaryGold,
                        ),
                      ),
                    ),
                  ),
                ),

                // Main Content Area
                Expanded(
                  child: SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    child: Column(
                      children: [
                        const SizedBox(height: 16),
                        _buildArtifactSelector(),
                        _buildArtifactDisplay(),
                        const SizedBox(height: 30),

                        // Navigation Hint
                        Container(
                          margin: const EdgeInsets.symmetric(horizontal: 16),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.purple.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.purple.withOpacity(0.3)),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.touch_app, color: Colors.purple),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  'Tip: Switch between 2D/3D views, rotate, and zoom to explore artifacts in detail',
                                  style: TextStyle(
                                    color: Colors.white70,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 30),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}