import 'package:flutter/material.dart';
import '../utils/constants.dart';

/// Dark museum background used by every screen.
class GemBackground extends StatelessWidget {
  final Widget child;
  const GemBackground({Key? key, required this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        image: DecorationImage(image: AssetImage('assets/images/background.jpg'), fit: BoxFit.cover),
      ),
      child: Container(color: Colors.black.withOpacity(0.72), child: child),
    );
  }
}

class GemCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;
  final EdgeInsets margin;
  const GemCard({
    Key? key,
    required this.child,
    this.padding = const EdgeInsets.all(14),
    this.margin = const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primaryGold.withOpacity(0.3)),
      ),
      child: child,
    );
  }
}

class GemButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback? onPressed;
  final bool outlined;
  const GemButton({Key? key, required this.label, this.icon, this.onPressed, this.outlined = false})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final style = outlined
        ? OutlinedButton.styleFrom(
            foregroundColor: AppColors.primaryGold,
            side: BorderSide(color: AppColors.primaryGold),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16))
        : ElevatedButton.styleFrom(
            backgroundColor: AppColors.primaryGold,
            foregroundColor: Colors.black,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16));
    final text = Text(label, style: const TextStyle(fontWeight: FontWeight.w600));
    if (outlined) {
      return icon == null
          ? OutlinedButton(onPressed: onPressed, style: style, child: text)
          : OutlinedButton.icon(onPressed: onPressed, style: style, icon: Icon(icon, size: 18), label: text);
    }
    return icon == null
        ? ElevatedButton(onPressed: onPressed, style: style, child: text)
        : ElevatedButton.icon(onPressed: onPressed, style: style, icon: Icon(icon, size: 18), label: text);
  }
}

class GemChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final IconData? icon;
  const GemChip({Key? key, required this.label, this.selected = false, this.onTap, this.icon}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? AppColors.primaryGold.withOpacity(0.25) : Colors.white.withOpacity(0.06),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: selected ? AppColors.primaryGold : Colors.white24),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: selected ? AppColors.primaryGold : Colors.white70),
            const SizedBox(width: 6),
          ],
          Flexible(
            child: Text(label,
                style: TextStyle(
                    color: selected ? AppColors.accentGold : Colors.white70,
                    fontSize: 13,
                    fontWeight: selected ? FontWeight.w600 : FontWeight.w400)),
          ),
        ]),
      ),
    );
  }
}

String floorName(dynamic f) {
  final n = (f as num).toInt();
  switch (n) {
    case -1:
      return 'Lower Level';
    case 0:
      return 'Ground';
    case 4:
      return 'Galleries Level';
    default:
      return 'Staircase L$n';
  }
}
