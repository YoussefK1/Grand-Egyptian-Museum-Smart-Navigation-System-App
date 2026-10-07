import 'package:flutter_test/flutter_test.dart';
import 'package:gem_app/services/offline_router.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('offline router finds a route to the Tutankhamun gallery', () async {
    final r = await OfflineRouter.route('ENTRANCE', 'TUT_4', 'easiest');
    expect(r['found'], true);
    expect((r['minutes'] as num) > 0, true);
  });

  test('step-free mode never uses stairs', () async {
    final r = await OfflineRouter.route('ENTRANCE', 'G12', 'step_free');
    expect(r['found'], true);
    expect(r['uses_stairs'], false);
  });

  test('scenic mode climbs the Grand Staircase', () async {
    final r = await OfflineRouter.route('GRAND_HALL', 'GS_TOP', 'scenic');
    expect(r['uses_stairs'], true);
  });
}
