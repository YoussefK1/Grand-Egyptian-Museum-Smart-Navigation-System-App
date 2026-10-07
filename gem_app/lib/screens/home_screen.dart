import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';
import '../utils/constants.dart';
import 'menu_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  // VIDEO PLAYER CONTROLLER
  late VideoPlayerController _videoPlayerController;
  late ChewieController _chewieController;
  bool _isVideoInitialized = false;

  // Collection data with image paths
  final List<Map<String, String>> collections = [
    {
      'id': '1',
      'title': 'Model of Funerary Boat of Ukhhotep',
      'desc': 'A painted wooden model of a funerary boat discovered in Meir in 1885.',
      'image': 'assets/images/collection1.png'
    },
    {
      'id': '2',
      'title': 'The Golden Burial Mask of Tutankhamun',
      'desc': 'Preserved remains of ancient pharaohs',
      'image': 'assets/images/collection2.png'
    },
    {
      'id': '3',
      'title': 'Statuette of a Falcon',
      'desc': 'This gilt bronze votive statuette of a hawk was discovered in 1893.',
      'image': 'assets/images/collection3.png'
    },
    {
      'id': '4',
      'title': 'Obelisk of King Ramesses II',
      'desc': 'Placed in a square of 30,000 m2.',
      'image': 'assets/images/collection4.png'
    },
    {
      'id': '5',
      'title': 'Statue of the Scribe Mitri',
      'desc': 'This painted wooden statue belongs to Mitri.',
      'image': 'assets/images/collection5.png'
    },
  ];

  // Events data with image paths
  final List<Map<String, String>> events = [
    {
      'id': '1',
      'title': 'GEM Talks Series: From Past to Present',
      'desc': 'Azza Fahmy and Amina Ghali',
      'image': 'assets/images/event1.png'
    },
    {
      'id': '2',
      'title': 'RiseUp Summit 2025',
      'desc': 'Youth RiseUp Event',
      'image': 'assets/images/event2.png'
    },
    {
      'id': '3',
      'title': 'GEM Talks Series',
      'desc': 'From Inspiration to Masterpiece',
      'image': 'assets/images/event3.png'
    },
    {
      'id': '4',
      'title': 'Al Mashrafia 2025',
      'desc': 'Egyptian Ramadan Nights',
      'image': 'assets/images/event4.png'
    },
    {
      'id': '5',
      'title': 'Um Kalthoum',
      'desc': 'A musical homage to the timeless legacy of Um Kulthoum.',
      'image': 'assets/images/event5.png'
    },
  ];

  @override
  void initState() {
    super.initState();
    // Initialize video player
    _initializeVideoPlayer();
  }

  Future<void> _initializeVideoPlayer() async {
    try {
      _videoPlayerController = VideoPlayerController.asset(
        'assets/videos/mixed_reality.mp4',
      );

      await _videoPlayerController.initialize();

      _chewieController = ChewieController(
        videoPlayerController: _videoPlayerController,
        autoPlay: false,
        looping: false,
        autoInitialize: true,
        showControls: true,
        placeholder: Container(
          color: Colors.grey[800],
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.play_circle_filled,
                  size: 60,
                  color: AppColors.primaryGold,
                ),
                const SizedBox(height: 10),
                Text(
                  'Mixed Reality Experience',
                  style: AppTextStyles.cardTitle.copyWith(fontSize: 18),
                ),
              ],
            ),
          ),
        ),
        materialProgressColors: ChewieProgressColors(
          playedColor: AppColors.primaryGold,
          handleColor: AppColors.primaryGold,
          backgroundColor: Colors.grey[700]!,
          bufferedColor: Colors.grey[600]!,
        ),
      );

      setState(() {
        _isVideoInitialized = true;
      });
    } catch (e) {
      print('Error initializing video: $e');
      // Fallback to placeholder if video fails
      setState(() {
        _isVideoInitialized = false;
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    if (_isVideoInitialized) {
      _videoPlayerController.dispose();
      _chewieController.dispose();
    }
    super.dispose();
  }

  Future<void> _launchMixedRealityWebsite() async {
    const url = 'https://gem.eg';
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Could not launch website'),
          backgroundColor: AppColors.primaryGold,
        ),
      );
    }
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
                          'Discover GEM',
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
                        hintText: 'Search Here',
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
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 16),

                          // Collections Section
                          _buildSectionTitle('Collection'),
                          const SizedBox(height: 12),
                          SizedBox(
                            height: 210, // INCREASED HEIGHT
                            child: ListView.builder(
                              scrollDirection: Axis.horizontal,
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              itemCount: collections.length,
                              itemBuilder: (context, index) {
                                return _buildCollectionCard(collections[index]);
                              },
                            ),
                          ),
                          const SizedBox(height: 28),

                          // Mixed Reality Experience Section
                          _buildSectionTitle('Explore Grand Egyptian Museum'),
                          const SizedBox(height: 12),
                          _buildVideoSection(),
                          const SizedBox(height: 28),

                          // Events Section
                          _buildSectionTitle('Events'),
                          const SizedBox(height: 12),
                          _buildEventsGrid(),
                          const SizedBox(height: 30),
                        ],
                      ),
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

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Text(
        title,
        style: AppTextStyles.sectionTitle,
      ),
    );
  }

  Widget _buildCollectionCard(Map<String, String> collection) {
    return Container(
      width: 165, // SLIGHTLY WIDER
      margin: const EdgeInsets.only(right: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // IMAGE
          Container(
            height: 110, // REDUCED IMAGE HEIGHT
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
              color: Colors.grey[800],
            ),
            child: Stack(
              children: [
                // Your actual image
                ClipRRect(
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                  child: Image.asset(
                    collection['image']!,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                    errorBuilder: (context, error, stackTrace) {
                      // Fallback if image doesn't exist
                      return Center(
                        child: Text(
                          collection['id']!,
                          style: const TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      );
                    },
                  ),
                ),
                // Optional overlay with ID
                Container(
                  alignment: Alignment.topLeft,
                  padding: const EdgeInsets.all(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.primaryGold.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      collection['id']!,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          // TEXT CONTENT - FIXED HEIGHTS
          Padding(
            padding: const EdgeInsets.all(8), // REDUCED PADDING
            child: SizedBox(
              height: 80, // FIXED HEIGHT FOR TEXT AREA
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // TITLE
                  SizedBox(
                    height: 40, // FIXED HEIGHT
                    child: Text(
                      collection['title']!,
                      style: AppTextStyles.cardTitle.copyWith(
                        fontSize: 12, // SMALLER FONT
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  // DESCRIPTION
                  SizedBox(
                    height: 32, // FIXED HEIGHT
                    child: Text(
                      collection['desc']!,
                      style: AppTextStyles.cardDescription.copyWith(
                        fontSize: 10, // SMALLER FONT
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: AppColors.cardBg,
          border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            // VIDEO PLAYER REPLACEMENT
            Container(
              height: 165,
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(12),
                  topRight: Radius.circular(12),
                ),
                color: Colors.grey[800],
              ),
              child: _isVideoInitialized
                  ? Chewie(controller: _chewieController)
                  : Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.play_circle_filled,
                      size: 55,
                      color: AppColors.primaryGold,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Mixed Reality Experience',
                      style: AppTextStyles.cardTitle.copyWith(fontSize: 17),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Tap to play video',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
            // Button
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              child: ElevatedButton(
                onPressed: _launchMixedRealityWebsite,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGold,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.open_in_new, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Learn More Online',
                      style: AppTextStyles.buttonText.copyWith(fontSize: 15),
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

  Widget _buildEventsGrid() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 0.82, // ADJUSTED ASPECT RATIO
        ),
        itemCount: events.length,
        itemBuilder: (context, index) {
          return _buildEventCard(events[index]);
        },
      ),
    );
  }

  Widget _buildEventCard(Map<String, String> event) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // EVENT IMAGE
          Container(
            height: 90, // REDUCED HEIGHT
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(10),
                topRight: Radius.circular(10),
              ),
              color: Colors.grey[800],
            ),
            child: ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(10),
                topRight: Radius.circular(10),
              ),
              child: Image.asset(
                event['image']!,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                errorBuilder: (context, error, stackTrace) {
                  return Center(
                    child: Text(
                      event['id']!,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          // EVENT TEXT - FIXED HEIGHTS
          Padding(
            padding: const EdgeInsets.all(8), // REDUCED PADDING
            child: SizedBox(
              height: 70, // FIXED HEIGHT FOR TEXT
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  SizedBox(
                    height: 36, // FIXED HEIGHT
                    child: Text(
                      event['title']!,
                      style: AppTextStyles.cardTitle.copyWith(
                        fontSize: 12, // SMALLER FONT
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  SizedBox(
                    height: 26, // FIXED HEIGHT
                    child: Text(
                      event['desc']!,
                      style: AppTextStyles.cardDescription.copyWith(
                        fontSize: 10, // SMALLER FONT
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}