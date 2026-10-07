"""Shared vocabularies for the questionnaire, dataset and models."""

ERAS = [
    ("prehistoric_early", "Prehistoric & Early Dynastic", "Predynastic communities and the first pharaohs"),
    ("old_kingdom", "Old Kingdom (Pyramid Builders)", "The age of Khufu, Khafre and the Giza pyramids"),
    ("middle_kingdom", "Middle Kingdom", "Classical art, literature and the rebirth of Egypt"),
    ("new_kingdom", "New Kingdom (Empire)", "Hatshepsut, Akhenaten, Ramesses II and the Egyptian empire"),
    ("tutankhamun", "Tutankhamun's Treasures", "The complete collection of the boy king"),
    ("late_greco_roman", "Late, Ptolemaic & Roman Egypt", "Foreign rulers, animal cults and mummy portraits"),
]
ERA_IDS = [e[0] for e in ERAS]

INTERESTS = [
    ("royalty", "Pharaohs & Royalty", "crown"),
    ("gold_jewelry", "Gold & Jewelry", "diamond"),
    ("mummies_afterlife", "Mummies & the Afterlife", "mummy"),
    ("daily_life", "Daily Life & Society", "home"),
    ("art_statues", "Art & Statues", "art"),
    ("architecture", "Architecture & Monuments", "pyramid"),
    ("religion_gods", "Gods & Religion", "ankh"),
    ("war_weapons", "Warfare & Weapons", "sword"),
    ("writing_literature", "Writing & Literature", "scroll"),
    ("discovery_archaeology", "Discovery & Archaeology", "shovel"),
    ("ships_transport", "Boats & Chariots", "boat"),
    ("animals", "Sacred Animals", "paw"),
]
INTEREST_IDS = [i[0] for i in INTERESTS]

VISITOR_TYPES = [("solo", "Solo adult"), ("couple", "Couple / friends"), ("family_kids", "Family with children"),
                 ("student", "Student / researcher"), ("group", "Tour group")]
PACES = [("relaxed", "Relaxed - I like to take my time"), ("balanced", "Balanced"), ("fast", "Fast - highlights only")]
DEPTHS = [("highlights", "Highlights & masterpieces"), ("balanced", "A bit of everything"),
          ("deep", "Deep dive - hidden gems too")]
MOBILITY = [("full", "No restrictions"), ("avoid_stairs", "Avoid stairs"), ("wheelchair", "Wheelchair / step-free only")]
CROWD = [("avoid", "Avoid crowded areas if possible"), ("neutral", "Crowds don't bother me")]
TIME_OPTIONS = [60, 90, 120, 180, 240, 300]

WALK_SPEED_MPS = 1.1               # comfortable museum walking speed
PACE_VIEW_FACTOR = {"relaxed": 1.35, "balanced": 1.0, "fast": 0.7}
