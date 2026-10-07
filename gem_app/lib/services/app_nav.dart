import 'package:flutter/foundation.dart';

/// A navigation request produced by other screens (tour, collections) and consumed by the Map tab.
class NavTarget {
  final String? startId;
  final String goalId;
  final String mode;
  const NavTarget({this.startId, required this.goalId, this.mode = 'easiest'});
}

class AppNav {
  static final ValueNotifier<NavTarget?> pending = ValueNotifier<NavTarget?>(null);
  static void Function(int index)? goToTab;

  /// Opens the Map tab (index 1) and asks it to compute a route.
  static void navigateTo(NavTarget target) {
    pending.value = target;
    goToTab?.call(1);
  }
}
