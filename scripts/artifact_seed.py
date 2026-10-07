"""
Seed records for the GEM artifact dataset.

source_tier values (be transparent about provenance in your report):
  confirmed_web   - object is explicitly named in the official GEM ticketing site / press coverage
                    / scholarly reviews of the museum that were consulted while building this dataset.
  prototype_app   - object comes from the team's first-version Flutter app (home / exhibits screens).
  representative  - a TYPE of object that belongs to that gallery theme (e.g. "Middle Kingdom coffin
                    with Coffin Texts"). Used so every gallery has enough data to train/cluster.
                    Verify the exact accession against the GEM catalogue before publishing.

Columns: name, zone_id, era_id, period, category, material, tags, popularity(1-10),
         view_minutes, kid_friendly(0-1), description, source_tier

Interest tags (12): royalty, gold_jewelry, mummies_afterlife, daily_life, art_statues, architecture,
religion_gods, war_weapons, writing_literature, discovery_archaeology, ships_transport, animals
"""

CW, PA, RP = "confirmed_web", "prototype_app", "representative"

SEED = [
    # ---------------------------------------------------------------- Entrance / Grand Hall
    ("Hanging Obelisk of Ramesses II", "ENTRANCE", "new_kingdom", "19th Dynasty, c. 1279-1213 BC", "Monument",
     "Granite", "architecture;royalty;religion_gods", 8, 6, 0.6,
     "The world's first hanging obelisk, relocated from Tanis to the museum entrance. Visitors can stand beneath it "
     "and look up to see the king's cartouches carved on the hidden base of the monument.", CW),
    ("Colossal Statue of Ramesses II", "GRAND_HALL", "new_kingdom", "19th Dynasty, c. 1279-1213 BC", "Statue",
     "Red granite", "royalty;art_statues;architecture", 10, 8, 0.9,
     "An 11 m, 83-ton red granite colossus of Ramesses II that greets visitors in the Grand Hall. Rediscovered at "
     "Memphis in 1820, it is one of the largest royal statues surviving from ancient Egypt.", CW),
    ("Column of King Merenptah", "GRAND_HALL", "new_kingdom", "19th Dynasty, c. 1213-1203 BC", "Monument",
     "Granite", "architecture;royalty;writing_literature", 5, 3, 0.3,
     "A monumental granite column inscribed with royal names and titles of Merenptah, son and successor of Ramesses II, "
     "standing in the Grand Hall beside the colossus.", CW),
    ("Ptolemaic Royal Statue (pair) in the Grand Hall", "GRAND_HALL", "late_greco_roman", "Ptolemaic Period", "Statue",
     "Granite", "royalty;art_statues", 5, 3, 0.4,
     "Two large Ptolemaic statues in the atrium show how Greek-era rulers presented themselves in traditional Egyptian "
     "royal style as pharaohs.", CW),

    # ---------------------------------------------------------------- Grand Staircase
    ("Royal Statue Group - Royal Image Landing", "GS_0", "middle_kingdom", "12th-13th Dynasty", "Statue",
     "Granite", "royalty;art_statues", 6, 4, 0.5,
     "Lowest landing of the staircase: royal statuary that shows how kings used monumental portraits to express power, "
     "divinity and the ideal of kingship.", CW),
    ("Colossal Statue of Senwosret I", "GS_0", "middle_kingdom", "12th Dynasty, c. 1971-1926 BC", "Statue",
     "Granite", "royalty;art_statues;religion_gods", 7, 4, 0.5,
     "A colossal granite statue of Senwosret I from the temple of Karnak, a masterpiece of Middle Kingdom royal sculpture "
     "with a calm idealised face.", CW),
    ("Shrine Elements Dedicated to the Gods", "GS_1", "new_kingdom", "18th-19th Dynasty", "Architecture",
     "Stone", "architecture;religion_gods", 5, 4, 0.3,
     "Carved doorways, naoi and temple elements dedicated by kings to the gods, displayed as 'Divine Houses' along the "
     "staircase to show how temples housed the divine.", CW),
    ("Statue of a God Presented by a King", "GS_2", "new_kingdom", "18th Dynasty", "Statue",
     "Granite", "religion_gods;royalty;art_statues", 6, 4, 0.5,
     "Divine and royal statues side by side in the 'Gods & Kings' section illustrate the relationship between the "
     "pharaoh and the deities who legitimised his rule.", CW),
    ("King List of the Subsidiary Staircase", "GS_2", "new_kingdom", "New Kingdom", "Inscription",
     "Stone", "writing_literature;royalty", 6, 5, 0.3,
     "A remarkable king list with a large informational panel on the side staircase, naming rulers in order and "
     "showing how Egyptians recorded their own history.", CW),
    ("Statue of Senwosret I (Side Staircase)", "GS_2", "middle_kingdom", "12th Dynasty", "Statue",
     "Stone", "royalty;art_statues", 5, 3, 0.4,
     "Statues of Senwosret I stand beside the king list on the side staircase, representing the founder-like image of a "
     "powerful Middle Kingdom ruler.", CW),
    ("Head of Akhenaten", "GS_3", "new_kingdom", "18th Dynasty, Amarna Period, c. 1353-1336 BC", "Statue",
     "Stone", "royalty;art_statues;religion_gods", 8, 4, 0.5,
     "A stone head of Akhenaten placed across the stairs from the other kings, suggesting a pharaoh apart. Its elongated "
     "features show the radical Amarna art style of the sun-worshipping king.", CW),
    ("Restoration Stela of Tutankhamun", "GS_3", "tutankhamun", "18th Dynasty, c. 1332-1323 BC", "Stela",
     "Stone", "religion_gods;royalty;writing_literature", 8, 5, 0.4,
     "The Restoration Stela, flanked by two statues of the king, records how Tutankhamun restored the traditional gods "
     "and temples after the Amarna upheaval and links the staircase to the Tutankhamun galleries.", CW),
    ("Funerary Monument - Journey to Eternity", "GS_3", "new_kingdom", "New Kingdom", "Funerary",
     "Stone", "mummies_afterlife;architecture", 5, 3, 0.3,
     "Monuments in the 'Journey to Eternity' section illustrate beliefs about death, burial and rebirth carved onto "
     "stone coffins, stelae and tomb architecture.", CW),
    ("Pyramid Panorama Window", "GS_TOP", "old_kingdom", "Old Kingdom (view of Giza)", "Viewpoint",
     "Glass", "architecture;discovery_archaeology", 9, 6, 1.0,
     "A floor-to-ceiling window at the top of the Grand Staircase frames a panoramic view of the Giza pyramids, linking "
     "the museum to the monuments of Khufu, Khafre and Menkaure.", CW),

    # ---------------------------------------------------------------- Khufu boats
    ("Solar Boat of Khufu", "BOATS", "old_kingdom", "4th Dynasty, c. 2500 BC", "Boat",
     "Cedar wood", "ships_transport;royalty;mummies_afterlife;religion_gods", 10, 15, 0.9,
     "A 43 m cedar boat found in a pit beside the Great Pyramid, believed to carry King Khufu with the sun god Ra in the "
     "afterlife. It is the oldest and largest wooden boat discovered in Egypt.", CW),
    ("Second Solar Boat of Khufu (under conservation)", "BOATS", "old_kingdom", "4th Dynasty, c. 2500 BC", "Boat",
     "Cedar wood", "ships_transport;discovery_archaeology;royalty", 7, 8, 0.7,
     "The second boat from the sealed pits at Giza is still being studied and restored, and visitors can watch "
     "conservators at work.", CW),
    ("Khufu Boat Rope and Reed Mat Fragments", "BOATS", "old_kingdom", "4th Dynasty", "Boat part",
     "Reed and rope", "ships_transport;discovery_archaeology;daily_life", 3, 2, 0.4,
     "Ropes, mats and tools found with the boats show how ancient shipwrights assembled the vessel without nails.", RP),

    # ---------------------------------------------------------------- Gallery 1 - Early Society
    ("Predynastic Painted Pottery Vessel", "G01", "prehistoric_early", "Naqada II, c. 3500-3200 BC", "Pottery",
     "Clay", "daily_life;art_statues", 4, 2, 0.5,
     "Buff clay vessels painted with boats, animals and spirals show the settled farming communities of the Nile Valley "
     "before the first pharaohs.", RP),
    ("Flint Knife with Ripple Flaking", "G01", "prehistoric_early", "Predynastic", "Tool",
     "Flint", "daily_life;war_weapons", 4, 2, 0.5,
     "A beautifully flaked flint blade shows the craft of Predynastic stone workers and the early development of "
     "prestige weapons.", RP),
    ("Palette for Grinding Eye Paint", "G01", "prehistoric_early", "Predynastic", "Tool",
     "Siltstone", "daily_life;art_statues", 4, 2, 0.5,
     "Slate palettes used to grind malachite for eye makeup became carved ceremonial objects as society grew more "
     "hierarchical.", RP),
    ("Early Dynastic Stone Vessel", "G01", "prehistoric_early", "1st-2nd Dynasty", "Vessel",
     "Stone", "daily_life;art_statues", 3, 2, 0.3,
     "Hard stone vessels carved by Early Dynastic craftsmen reflect royal workshops and elite funerary gifts.", RP),
    ("Animal Figurine of Predynastic Egypt", "G01", "prehistoric_early", "Predynastic", "Figurine",
     "Clay and ivory", "animals;daily_life", 4, 2, 0.8,
     "Small animal figures made of clay and ivory hint at early beliefs and the importance of cattle, hippopotami and "
     "birds in Nile life.", RP),
    ("Old Kingdom Agricultural Scene Relief", "G01", "old_kingdom", "5th Dynasty", "Relief",
     "Limestone", "daily_life;animals;art_statues", 5, 3, 0.6,
     "Painted limestone relief from a tomb chapel shows farming, herding and fishing, everyday work that fed the "
     "pyramid-building state.", RP),
    ("Statue of the Scribe Mitri", "G01", "old_kingdom", "Old Kingdom", "Statue",
     "Painted wood", "daily_life;writing_literature;art_statues", 6, 3, 0.6,
     "A painted wooden statue of the official Mitri, shown as a scribe with a lifelike face, representing the "
     "literate administrators who ran Old Kingdom Egypt.", PA),
    ("Servant Statuettes Grinding Grain and Brewing Beer", "G01", "old_kingdom", "5th-6th Dynasty", "Statuette",
     "Painted wood", "daily_life;art_statues", 5, 3, 0.8,
     "Tiny wooden servants grinding grain, baking bread and brewing beer were placed in tombs to supply the owner "
     "with food for eternity.", RP),

    # ---------------------------------------------------------------- Gallery 2 - Early Kingship
    ("Burial Equipment of Queen Hetepheres I", "G02", "old_kingdom", "4th Dynasty, c. 2600 BC", "Furniture",
     "Gilded wood", "royalty;gold_jewelry;mummies_afterlife;discovery_archaeology", 8, 7, 0.6,
     "Almost complete burial equipment of Queen Hetepheres, mother of Khufu, including gilded furniture and a canopy, "
     "found near the Great Pyramid and shown with objects never exhibited before.", CW),
    ("Silver Bracelets of Queen Hetepheres", "G02", "old_kingdom", "4th Dynasty", "Jewelry",
     "Silver and inlay", "gold_jewelry;royalty", 6, 3, 0.5,
     "Delicate silver bracelets inlaid with colourful stones belonged to the mother of Khufu, showing early royal "
     "jewelry design.", RP),
    ("Pyramid Builders' Royal Statue Head", "G02", "old_kingdom", "4th-5th Dynasty", "Statue",
     "Limestone", "royalty;art_statues;architecture", 6, 3, 0.5,
     "A carved royal head from the age of the Giza pyramids with the idealised features that expressed the divine "
     "kingship of the Old Kingdom.", RP),
    ("Early Dynastic King's Name Inscription (Serekh)", "G02", "prehistoric_early", "Early Dynastic Period", "Inscription",
     "Stone", "royalty;writing_literature", 4, 2, 0.3,
     "Carved royal names enclosed in the serekh frame show the first appearance of hieroglyphic writing in the service "
     "of kingship and state formation.", RP),
    ("Pyramid Complex Relief Fragment", "G02", "old_kingdom", "5th Dynasty", "Relief",
     "Limestone", "architecture;royalty;religion_gods", 5, 3, 0.4,
     "Relief fragments from a royal funerary temple depict the king with the gods and give clues to pyramid-complex "
     "ritual and decoration.", RP),
    ("Statue of King Pepi I (Copper Statue Type)", "G02", "old_kingdom", "6th Dynasty", "Statue",
     "Copper", "royalty;art_statues", 5, 3, 0.4,
     "Metal royal sculpture of the late Old Kingdom demonstrates early copper-working techniques and the continuing "
     "importance of royal portraiture.", RP),

    # ---------------------------------------------------------------- Gallery 3 - Early Beliefs
    ("Old Kingdom False Door Stela", "G03", "old_kingdom", "5th-6th Dynasty", "Funerary",
     "Limestone", "mummies_afterlife;religion_gods;writing_literature", 6, 3, 0.4,
     "A carved false door allowed the spirit of the tomb owner to receive offerings, expressing early beliefs about "
     "the afterlife and the cult of the dead.", RP),
    ("Pyramid Texts Inscription Fragment", "G03", "old_kingdom", "5th-6th Dynasty", "Inscription",
     "Limestone", "writing_literature;mummies_afterlife;religion_gods", 5, 3, 0.3,
     "Spells carved in royal pyramids, the oldest religious texts in the world, guided the dead king to the sky and "
     "the company of the gods.", RP),
    ("Early Funerary Offering Table", "G03", "old_kingdom", "Old Kingdom", "Funerary",
     "Limestone", "mummies_afterlife;religion_gods;daily_life", 4, 2, 0.3,
     "Offering tables carved with bread, beer and meat were set in front of tombs to feed the soul of the deceased "
     "for eternity.", RP),
    ("Predynastic Burial in Contracted Position", "G03", "prehistoric_early", "Predynastic", "Funerary",
     "Remains and pottery", "mummies_afterlife;discovery_archaeology", 5, 3, 0.4,
     "A reconstruction of an early grave shows the body naturally preserved in the desert sand, the observation that "
     "inspired later mummification.", RP),
    ("Early Amulets of Animal Gods", "G03", "old_kingdom", "Old Kingdom", "Amulet",
     "Faience", "religion_gods;animals;mummies_afterlife", 4, 2, 0.7,
     "Small amulets shaped like falcons, cows and jackals reflect the earliest animal-form deities and the protection "
     "they offered the living and the dead.", RP),

    # ---------------------------------------------------------------- Gallery 4 - Middle Kingdom Society
    ("Painted Wooden Soldiers of Mesehti (Egyptian Spearmen)", "G04", "middle_kingdom", "11th Dynasty, c. 2000 BC",
     "Model", "Painted wood", "war_weapons;daily_life;art_statues", 9, 6, 0.9,
     "Forty painted wooden Egyptian spearmen from the tomb of the nomarch Mesehti at Asyut, each face unique and each "
     "holding a lance and shield, a rare view of the army of the Middle Kingdom.", CW),
    ("Painted Wooden Nubian Archers of Mesehti", "G04", "middle_kingdom", "11th Dynasty, c. 2000 BC",
     "Model", "Painted wood", "war_weapons;daily_life;art_statues", 9, 5, 0.9,
     "Forty painted Nubian archers from the same tomb accompany the Egyptian spearmen, showing foreign soldiers "
     "serving in the Egyptian army.", CW),
    ("Model of Funerary Boat of Ukhhotep", "G04", "middle_kingdom", "12th Dynasty, found at Meir in 1885",
     "Model", "Painted wood", "ships_transport;mummies_afterlife;daily_life", 7, 4, 0.8,
     "A painted wooden model of a funerary boat discovered at Meir, showing the funeral journey of the nomarch "
     "Ukhhotep across the Nile.", PA),
    ("Model Workshop of Carpenters and Weavers", "G04", "middle_kingdom", "12th Dynasty", "Model",
     "Painted wood", "daily_life;art_statues", 6, 4, 0.9,
     "Tomb models of busy workshops with carpenters, weavers and brewers give a miniature view of craft production "
     "in a Middle Kingdom estate.", RP),
    ("Model Granary with Scribes Counting Grain", "G04", "middle_kingdom", "12th Dynasty", "Model",
     "Painted wood", "daily_life;writing_literature", 5, 3, 0.8,
     "A model granary with scribes recording the harvest shows the bureaucracy and taxation system of the Middle "
     "Kingdom.", RP),
    ("Middle Kingdom Cattle Counting Model", "G04", "middle_kingdom", "11th-12th Dynasty", "Model",
     "Painted wood", "daily_life;animals", 5, 3, 0.9,
     "A model of the owner inspecting his cattle illustrates wealth measured in livestock and the role of animals in "
     "provincial life.", RP),
    ("Hyksos Scarab Seal Collection", "G04", "middle_kingdom", "Second Intermediate Period", "Seal",
     "Steatite", "daily_life;writing_literature;discovery_archaeology", 4, 3, 0.4,
     "Scarab seals of Hyksos rulers from the Delta tell the story of foreign kings who governed part of Egypt during "
     "the Second Intermediate Period.", CW),

    # ---------------------------------------------------------------- Gallery 5 - Middle Kingdom Kingship
    ("Portrait of Senusret III", "G05", "middle_kingdom", "12th Dynasty, c. 1878-1839 BC", "Statue",
     "Granite", "royalty;art_statues", 8, 4, 0.5,
     "Psychologically realistic portraits of Senusret III show a tired, thoughtful king, a dramatic break from the "
     "idealised royal faces of earlier periods.", CW),
    ("Colossal Granite Statue of Senwosret I from Karnak (GEM 1706)", "G05", "middle_kingdom", "12th Dynasty",
     "Statue", "Granite", "royalty;art_statues;religion_gods", 8, 5, 0.6,
     "A colossal granite statue of Senwosret I from the temple of Karnak stands in the Middle Kingdom galleries, one "
     "of the largest royal sculptures of the era.", CW),
    ("Middle Kingdom Royal Sphinx", "G05", "middle_kingdom", "12th Dynasty", "Statue",
     "Granite", "royalty;animals;art_statues;religion_gods", 7, 4, 0.8,
     "A royal sphinx combining a lion's body with the king's head symbolises royal power guarding the sacred space of "
     "the temple.", RP),
    ("Royal Jewelry of a Middle Kingdom Princess", "G05", "middle_kingdom", "12th Dynasty", "Jewelry",
     "Gold and semi-precious stones", "gold_jewelry;royalty", 7, 4, 0.6,
     "Crowns, pectorals and bracelets of gold inlaid with carnelian and turquoise reveal the high point of Egyptian "
     "jewelry production under the Middle Kingdom.", RP),
    ("Pyramid Capstone of a Middle Kingdom King", "G05", "middle_kingdom", "12th-13th Dynasty", "Monument",
     "Granite", "architecture;royalty", 5, 3, 0.5,
     "A carved pyramidion shows that Middle Kingdom kings returned to pyramid building, with decoration of the sun's "
     "journey.", RP),
    ("Foundation Deposit of a Royal Temple", "G05", "middle_kingdom", "12th Dynasty", "Deposit",
     "Mixed", "architecture;religion_gods;discovery_archaeology", 4, 3, 0.4,
     "Models, tools and offerings buried under temple walls consecrated new royal buildings.", RP),
    ("Royal Stela Recording Nubian Campaigns", "G05", "middle_kingdom", "12th Dynasty", "Stela",
     "Granite", "war_weapons;royalty;writing_literature", 5, 3, 0.4,
     "A border stela proclaiming the limits of Egyptian territory in Nubia shows the king as a military leader.", RP),

    # ---------------------------------------------------------------- Gallery 6 - Middle Kingdom Beliefs
    ("Middle Kingdom Coffin with Coffin Texts", "G06", "middle_kingdom", "12th Dynasty", "Coffin",
     "Painted wood", "mummies_afterlife;religion_gods;writing_literature", 8, 5, 0.6,
     "A rectangular wooden coffin painted with eyes and covered in hieroglyphic spells known as Coffin Texts to guide "
     "the owner through the underworld.", CW),
    ("Mask and Canopic Box of a Middle Kingdom Official", "G06", "middle_kingdom", "12th Dynasty", "Funerary",
     "Cartonnage and wood", "mummies_afterlife;art_statues", 6, 3, 0.6,
     "A painted funerary mask and canopic box guarded the face and organs of a provincial official on his journey to "
     "eternity.", RP),
    ("Osiris Statuette of the Middle Kingdom", "G06", "middle_kingdom", "12th-13th Dynasty", "Statuette",
     "Wood", "religion_gods;mummies_afterlife", 5, 3, 0.5,
     "The god Osiris, ruler of the dead, appears in mummiform shape in growing popular devotion during the Middle "
     "Kingdom.", RP),
    ("Poetry and Literature on Papyrus (Middle Kingdom)", "G06", "middle_kingdom", "12th Dynasty", "Papyrus",
     "Papyrus", "writing_literature;daily_life", 6, 4, 0.3,
     "Papyrus fragments of stories and poetry remind visitors that the Middle Kingdom was the classical age of "
     "Egyptian literature.", RP),
    ("Hathor Cow Amulet and Jewelry Set", "G06", "middle_kingdom", "12th Dynasty", "Jewelry",
     "Gold and faience", "gold_jewelry;religion_gods;animals", 6, 3, 0.6,
     "Jewelry with a Hathor cow motif combined fashion with divine protection, and was worn by women of the court.", RP),
    ("Model Boats Sailing to Abydos", "G06", "middle_kingdom", "12th Dynasty", "Model",
     "Painted wood", "ships_transport;religion_gods;mummies_afterlife", 6, 3, 0.8,
     "A pair of model boats represents the pilgrimage to Abydos, the cult centre of Osiris, that every Egyptian "
     "hoped to make in life or death.", RP),

    # ---------------------------------------------------------------- Gallery 7 - New Kingdom Society
    ("Statue of the Scribe Paramessu (Ramesses I as Vizier)", "G07", "new_kingdom", "18th Dynasty", "Statue",
     "Stone", "writing_literature;royalty;art_statues", 6, 4, 0.5,
     "A scribe statue of Paramessu, the vizier who later became King Ramesses I, shows the route from official to "
     "founder of the Ramesside dynasty.", CW),
    ("Statuette of a Falcon", "G07", "late_greco_roman", "Late Period, found in 1893", "Statuette",
     "Gilt bronze", "animals;religion_gods;gold_jewelry", 7, 3, 0.8,
     "A gilt bronze votive statuette of a hawk discovered in 1893, dedicated to the falcon god Horus.", PA),
    ("New Kingdom Domestic Furniture - Stool and Headrest", "G07", "new_kingdom", "18th Dynasty", "Furniture",
     "Wood", "daily_life;art_statues", 5, 3, 0.6,
     "Folding stools, chairs and carved headrests give a close look at the furnishings in the homes of New Kingdom "
     "elites.", RP),
    ("Cosmetic Box and Mirror of a Noblewoman", "G07", "new_kingdom", "18th Dynasty", "Cosmetics",
     "Wood and bronze", "daily_life;gold_jewelry", 6, 3, 0.7,
     "A cosmetic box with kohl tubes, combs and a polished bronze mirror shows beauty routines in ancient Egypt.", RP),
    ("Workers' Village Ostraca and Tools", "G07", "new_kingdom", "19th Dynasty", "Tool",
     "Limestone and copper", "daily_life;writing_literature;discovery_archaeology", 5, 3, 0.5,
     "Pottery and limestone fragments with sketches and notes from the workers who built royal tombs reveal their "
     "daily life, strikes and humour.", RP),
    ("Amarna Period Relief of a Royal Family", "G07", "new_kingdom", "18th Dynasty, Amarna", "Relief",
     "Limestone", "royalty;religion_gods;art_statues;daily_life", 7, 4, 0.6,
     "A relief showing a royal family beneath the rays of the sun disc Aten shows the intimate, naturalistic style of "
     "the Amarna Period.", RP),
    ("Senet Game Board of the New Kingdom", "G07", "new_kingdom", "18th Dynasty", "Game",
     "Wood and ivory", "daily_life", 6, 3, 1.0,
     "A senet board game, played by all classes and believed to symbolise the journey to the afterlife, can be "
     "compared with the one from Tutankhamun's tomb.", RP),

    # ---------------------------------------------------------------- Gallery 8 - New Kingdom Kingship
    ("Statue of Queen Hatshepsut", "G08", "new_kingdom", "18th Dynasty, c. 1479-1458 BC", "Statue",
     "Granite", "royalty;art_statues", 9, 5, 0.6,
     "A statue of Queen Hatshepsut, the woman who ruled as pharaoh, shows her in royal regalia and expresses her "
     "claim to kingship.", CW),
    ("Thutmose III as King and Scribe", "G08", "new_kingdom", "18th Dynasty, c. 1479-1425 BC", "Statue",
     "Stone", "royalty;writing_literature;art_statues;war_weapons", 7, 4, 0.5,
     "A statue of the warrior-king Thutmose III shown with scribal equipment, combining the image of conqueror and "
     "learned ruler.", CW),
    ("Ramesses II Smiting Enemies Relief", "G08", "new_kingdom", "19th Dynasty", "Relief",
     "Limestone", "royalty;war_weapons;art_statues", 6, 3, 0.7,
     "A relief of the king striking down foreign enemies is the classic image of pharaonic power and propaganda "
     "after the battle of Kadesh.", RP),
    ("Royal Chariot Fittings of Thutmose IV", "G08", "new_kingdom", "18th Dynasty", "Chariot",
     "Wood and leather", "war_weapons;ships_transport;royalty", 6, 3, 0.8,
     "Chariot fittings show the new technology introduced by the Hyksos that made the New Kingdom army so powerful.", RP),
    ("Pharaoh's Khepresh War Crown and Regalia", "G08", "new_kingdom", "18th Dynasty", "Regalia",
     "Leather and gold", "royalty;war_weapons;gold_jewelry", 6, 3, 0.7,
     "The blue Khepresh crown and royal sceptres illustrate how New Kingdom pharaohs displayed royal and military "
     "authority.", RP),
    ("Diplomatic Amarna Letters Tablet", "G08", "new_kingdom", "18th Dynasty", "Tablet",
     "Clay", "writing_literature;royalty;daily_life", 5, 3, 0.5,
     "Cuneiform clay tablets of international correspondence show the New Kingdom as a diplomatic great power.", RP),

    # ---------------------------------------------------------------- Gallery 9 - New Kingdom Beliefs
    ("Winged Scarab Pectoral", "G09", "new_kingdom", "New Kingdom", "Jewelry",
     "Gold and semi-precious stones", "gold_jewelry;religion_gods;mummies_afterlife", 8, 4, 0.7,
     "A gold pectoral with a winged scarab inlaid with lapis and carnelian, symbol of the rising sun and rebirth, "
     "worn or buried to protect the body.", CW),
    ("Book of the Dead Papyrus", "G09", "new_kingdom", "18th-19th Dynasty", "Papyrus",
     "Papyrus", "mummies_afterlife;writing_literature;religion_gods", 8, 5, 0.6,
     "A painted papyrus with spells of the Book of the Dead and the weighing of the heart ceremony before Osiris.", RP),
    ("Set of Shabti Figures", "G09", "new_kingdom", "19th Dynasty", "Shabti",
     "Faience", "mummies_afterlife;religion_gods;daily_life", 7, 3, 0.9,
     "Small servant figures called shabtis were meant to work for the deceased in the field of reeds.", RP),
    ("Anthropoid Coffin of a Priest of Amun", "G09", "new_kingdom", "19th Dynasty", "Coffin",
     "Painted wood", "mummies_afterlife;religion_gods;art_statues", 7, 4, 0.7,
     "A human-shaped coffin painted with protective gods and a golden face for a priest of Amun at Thebes.", RP),
    ("Canopic Jars with Four Sons of Horus", "G09", "new_kingdom", "New Kingdom", "Funerary",
     "Limestone", "mummies_afterlife;religion_gods", 6, 3, 0.6,
     "Four jars with the heads of Imseti, Hapy, Duamutef and Qebehsenuef guarded the mummified liver, lungs, stomach "
     "and intestines.", RP),
    ("Statue of the God Amun", "G09", "new_kingdom", "18th Dynasty", "Statue",
     "Granite", "religion_gods;art_statues", 6, 3, 0.5,
     "A statue of Amun, king of the gods and patron of Thebes, associated with state religion and imperial power.", RP),
    ("Mummy of a New Kingdom Official", "G09", "new_kingdom", "New Kingdom", "Mummy",
     "Human remains and linen", "mummies_afterlife;discovery_archaeology", 8, 5, 0.4,
     "A mummy and its wrappings show how embalmers preserved the body and how modern CT scanning reveals what lies "
     "under the linen.", RP),
    ("Heart Scarab of a Noble", "G09", "new_kingdom", "18th Dynasty", "Amulet",
     "Green stone", "mummies_afterlife;religion_gods", 5, 2, 0.6,
     "A heart scarab placed on the mummy's chest carried a spell to stop the heart from testifying against its owner "
     "in the judgement.", RP),

    # ---------------------------------------------------------------- Tutankhamun galleries
    ("Golden Burial Mask of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty, c. 1323 BC", "Mask",
     "Solid gold with semi-precious stones and glass", "gold_jewelry;royalty;mummies_afterlife;art_statues", 10, 10, 0.9,
     "The iconic gold funerary mask of the boy king, lit as the centrepiece of the Tutankhamun galleries, weighing "
     "about 11 kg and inlaid with lapis lazuli, quartz and obsidian.", CW),
    ("Solid Gold Inner Coffin of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty", "Coffin",
     "Solid gold", "gold_jewelry;mummies_afterlife;royalty;religion_gods", 10, 8, 0.8,
     "The innermost of three nested coffins, made of solid gold in the form of the god Osiris, held the mummy of the "
     "king.", CW),
    ("Middle Coffin of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty", "Coffin",
     "Gilded wood with inlay", "mummies_afterlife;gold_jewelry;religion_gods", 8, 5, 0.7,
     "The middle coffin, covered with gold leaf and inlaid with glass, is part of a stepwise programme of protection "
     "and renewal.", CW),
    ("Outer Gilded Coffin of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty", "Coffin",
     "Gilded wood", "mummies_afterlife;gold_jewelry;religion_gods", 8, 5, 0.7,
     "The outer coffin, restored before going on view, shows the king as Osiris with feather patterns and protective "
     "winged goddesses.", CW),
    ("Quartzite Sarcophagus of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty", "Sarcophagus",
     "Quartzite", "mummies_afterlife;religion_gods;royalty", 7, 4, 0.6,
     "The stone sarcophagus with goddesses protecting the corners enclosed the three coffins in the burial chamber.", RP),
    ("Gilded Shrines of Tutankhamun (Nested Shrines)", "TUT_4", "tutankhamun", "18th Dynasty", "Shrine",
     "Gilded wood", "mummies_afterlife;religion_gods;gold_jewelry;architecture", 8, 6, 0.7,
     "A set of gilded wooden shrines nested one inside the other surrounded the sarcophagus, covered in funerary "
     "texts and divine figures.", CW),
    ("Canopic Shrine with Four Guardian Goddesses", "TUT_4", "tutankhamun", "18th Dynasty", "Shrine",
     "Gilded wood", "mummies_afterlife;religion_gods;gold_jewelry", 9, 6, 0.7,
     "A gilded shrine guarded by four goddesses (Isis, Nephthys, Neith and Selket) protects the calcite canopic chest "
     "that held the king's organs.", CW),
    ("Miniature Gold Canopic Coffins", "TUT_4", "tutankhamun", "18th Dynasty", "Funerary",
     "Gold and inlay", "mummies_afterlife;gold_jewelry;religion_gods", 8, 4, 0.7,
     "Four miniature coffins of gold inside the alabaster canopic chest contained the king's embalmed internal "
     "organs, among the most delicate objects in the collection.", CW),
    ("Golden Throne of Tutankhamun", "TUT_1", "tutankhamun", "18th Dynasty", "Furniture",
     "Gilded wood, silver, glass paste", "royalty;gold_jewelry;art_statues;daily_life", 10, 7, 0.9,
     "The gilded wooden throne, with a backrest showing Queen Ankhesenamun anointing the king, is one of the finest "
     "examples of royal furniture ever found.", CW),
    ("Six Chariots of Tutankhamun", "TUT_3", "tutankhamun", "18th Dynasty", "Chariot",
     "Wood, gold leaf, leather", "war_weapons;ships_transport;royalty", 9, 7, 0.9,
     "Six complete but dismantled chariots with different wheels and lashings, including golden ceremonial vehicles, "
     "show the king's role as warrior and hunter.", CW),
    ("Shields and Ceremonial Daggers of Tutankhamun", "TUT_3", "tutankhamun", "18th Dynasty", "Weapon",
     "Gold, iron, wood", "war_weapons;royalty;gold_jewelry", 9, 6, 0.8,
     "Court and combat gear including shields and two daggers, one with an iron blade made from meteoritic metal.", CW),
    ("Painted Chest with War and Hunting Scenes", "TUT_3", "tutankhamun", "18th Dynasty", "Furniture",
     "Painted wood", "war_weapons;animals;royalty;art_statues", 7, 4, 0.8,
     "A wooden chest painted with the king triumphing over Nubians and Asiatics and hunting wild animals, a rare "
     "example of royal painting.", RP),
    ("Ceremonial Bows and Arrows of Tutankhamun", "TUT_3", "tutankhamun", "18th Dynasty", "Weapon",
     "Wood and gold", "war_weapons;royalty", 6, 3, 0.7,
     "Bows decorated with gold and bark show the king's training in archery.", RP),
    ("Golden Fan and Ostrich Feather Fan", "TUT_3", "tutankhamun", "18th Dynasty", "Regalia",
     "Gold and feathers", "gold_jewelry;royalty;animals;daily_life", 6, 3, 0.8,
     "A golden fan with ostrich feather remains records a hunt in the desert and the king's royal image.", RP),
    ("Tutankhamun's Senet and Game Boxes", "TUT_3", "tutankhamun", "18th Dynasty", "Game",
     "Ebony and ivory", "daily_life;royalty", 7, 4, 1.0,
     "Game boxes for senet and related board games used for leisure and symbolic of the soul's journey.", RP),
    ("Child's Chair and Personal Furniture of the King", "TUT_3", "tutankhamun", "18th Dynasty", "Furniture",
     "Wood and ivory", "daily_life;royalty", 6, 3, 0.9,
     "Chairs, stools and headrests, some from the king's childhood, provide a human view of the pharaoh's daily life.", RP),
    ("Linen Clothing and Gold Sandals of Tutankhamun", "TUT_3", "tutankhamun", "18th Dynasty", "Textile",
     "Linen and gold", "daily_life;gold_jewelry;royalty", 7, 4, 0.7,
     "Tunics, gloves and gold sandals show what the king wore, and how fine linen and gold were combined in royal "
     "dress.", RP),
    ("Silver Trumpet of Tutankhamun", "TUT_3", "tutankhamun", "18th Dynasty", "Instrument",
     "Silver and gold", "daily_life;war_weapons;royalty", 6, 3, 0.9,
     "One of two trumpets found in the tomb, played in religious and military ceremony.", RP),
    ("Pectoral with Winged Scarab of Tutankhamun", "TUT_4", "tutankhamun", "18th Dynasty", "Jewelry",
     "Gold, silver, semi-precious stones", "gold_jewelry;religion_gods;royalty", 9, 4, 0.7,
     "A pectoral with a scarab bearing the sun disc in lapis and carnelian, one of many pieces of royal jewelry from "
     "the king's treasury.", RP),
    ("Anubis Shrine with Jackal on Sled", "TUT_4", "tutankhamun", "18th Dynasty", "Shrine",
     "Gilded wood and ebony", "animals;mummies_afterlife;religion_gods", 8, 4, 0.9,
     "A black jackal figure on a gilded shrine guarded the treasury and the entrance to the realm of the dead.", RP),
    ("Guardian Statues of the King (Sentinels)", "TUT_2", "tutankhamun", "18th Dynasty", "Statue",
     "Wood, bitumen, gold leaf", "royalty;art_statues;religion_gods;discovery_archaeology", 8, 4, 0.8,
     "Two life-size black and gold statues stood on either side of the burial chamber entrance as protectors of the "
     "king.", RP),
    ("Howard Carter's Excavation Archive and Photographs", "TUT_2", "tutankhamun", "1922", "Archive",
     "Paper and glass plate", "discovery_archaeology;writing_literature", 7, 5, 0.5,
     "Carter's notes, drawings and photographs tell the story of the discovery of KV62 in 1922 and the ten years it "
     "took to clear the tomb.", RP),
    ("Tomb Entrance Seals and Tomb Reconstruction", "TUT_2", "tutankhamun", "1922", "Reconstruction",
     "Mixed", "discovery_archaeology;architecture;mummies_afterlife", 7, 5, 0.8,
     "Reconstructions of the antechamber, annex, burial chamber and treasury of KV62 show how the tomb looked when "
     "Howard Carter first entered.", CW),
    ("Family Tree and Identity of Tutankhamun", "TUT_1", "tutankhamun", "18th Dynasty", "Display",
     "Digital and stone", "royalty;discovery_archaeology", 6, 4, 0.5,
     "A section on his name, parents and possible family tree, including Akhenaten, Nefertiti and Ankhesenamun.", CW),
    ("Golden Bed in the Form of Cow Goddess", "TUT_5", "tutankhamun", "18th Dynasty", "Furniture",
     "Gilded wood", "religion_gods;animals;mummies_afterlife;gold_jewelry", 7, 4, 0.8,
     "A ceremonial bed in the shape of a cow, possibly linked with Hathor or Mehetweret, used in rebirth ritual.", RP),
    ("Ushabti Figures of Tutankhamun", "TUT_5", "tutankhamun", "18th Dynasty", "Shabti",
     "Wood, calcite, faience", "mummies_afterlife;religion_gods", 7, 4, 0.8,
     "More than four hundred servant figures to do the king's work in the afterlife.", RP),
    ("Calcite Wishing Cup of Tutankhamun", "TUT_5", "tutankhamun", "18th Dynasty", "Vessel",
     "Calcite", "art_statues;writing_literature;religion_gods", 6, 3, 0.6,
     "A lotus-shaped alabaster cup with inscriptions wishing the king millions of years of life.", RP),
    ("Golden Shrine of Hathor Goddess Statue", "TUT_5", "tutankhamun", "18th Dynasty", "Shrine",
     "Gilded wood", "religion_gods;animals;gold_jewelry", 6, 3, 0.7,
     "A gilded statue of a deity protecting the king on his journey into the afterlife.", RP),
    ("Tutankhamun's Alabaster Lamps and Vessels", "TUT_5", "tutankhamun", "18th Dynasty", "Vessel",
     "Alabaster", "daily_life;art_statues", 5, 3, 0.6,
     "Translucent calcite vessels and lamps carved with floral decoration were used to light the tomb and hold "
     "ritual oils.", RP),
    ("Tutankhamun Statue as Harpooner on a Papyrus Raft", "TUT_5", "tutankhamun", "18th Dynasty", "Statue",
     "Gilded wood", "royalty;animals;ships_transport;religion_gods", 6, 3, 0.9,
     "The king stands on a papyrus raft in a harpooner pose, symbolically defeating chaos.", RP),

    # ---------------------------------------------------------------- Gallery 10 - Late Period Society
    ("Late Period Bronze Statuette of a Cat Goddess", "G10", "late_greco_roman", "Late Period", "Statuette",
     "Bronze", "animals;religion_gods;art_statues", 7, 3, 1.0,
     "Votive bronzes of cats dedicated to Bastet were made in thousands during the Late Period by pilgrims.", RP),
    ("Persian-Period Seal and Administrative Documents", "G10", "late_greco_roman", "27th Dynasty", "Seal",
     "Stone and papyrus", "writing_literature;daily_life", 4, 3, 0.3,
     "Seals and demotic documents show how Egyptians lived under Persian rule.", RP),
    ("Kushite King Portrait Head (25th Dynasty)", "G10", "late_greco_roman", "25th Dynasty", "Statue",
     "Stone", "royalty;art_statues", 6, 3, 0.5,
     "A portrait of a Nubian pharaoh wearing the double uraeus, the symbol of the Kushite kings of Egypt and Nubia.", RP),
    ("Late Period Household Items and Jewelry", "G10", "late_greco_roman", "Late Period", "Jewelry",
     "Faience and glass", "daily_life;gold_jewelry", 4, 3, 0.5,
     "Household objects and bead jewelry from a Late Period town give insight into everyday life.", RP),
    ("Egyptian Priests' Statues in Realistic Style", "G10", "late_greco_roman", "Late Period", "Statue",
     "Greywacke", "religion_gods;art_statues;daily_life", 5, 3, 0.4,
     "Realistic statues of priests with shaved heads and lifelike faces show a revival of older art.", RP),

    # ---------------------------------------------------------------- Gallery 11 - Late Period Kingship
    ("Dendera Treasure Hoard - Gold and Silver Falcon", "G11", "late_greco_roman", "Late/Ptolemaic Period", "Statuette",
     "Gold and silver", "gold_jewelry;animals;religion_gods", 9, 5, 0.8,
     "A hollow falcon made of gold and silver from the Dendera treasure hoards, hidden in the temple perhaps by "
     "priests; it may once have contained a mummified bird.", CW),
    ("Dendera Treasure Hoard - Outer Falcon Coffin", "G11", "late_greco_roman", "Late/Ptolemaic Period", "Coffin",
     "Gilded wood", "animals;mummies_afterlife;religion_gods;gold_jewelry", 7, 4, 0.8,
     "The 60 cm tall outer coffin of a falcon from the Dendera treasure shows how sacred animals were buried.", CW),
    ("Dendera Treasure Hoard - Sacred Ritual Vessels", "G11", "late_greco_roman", "Late/Ptolemaic Period", "Vessel",
     "Silver and gold", "gold_jewelry;religion_gods", 6, 3, 0.5,
     "Ritual vessels from the temple hoard of Dendera illustrate the wealth of the temple and its priests.", CW),
    ("Statue of a Ptolemaic King in Egyptian Dress", "G11", "late_greco_roman", "Ptolemaic Period", "Statue",
     "Granite", "royalty;art_statues", 6, 3, 0.5,
     "A Greek pharaoh shown as a traditional Egyptian king with nemes headcloth.", RP),
    ("Kushite Royal Objects of the 25th Dynasty", "G11", "late_greco_roman", "25th Dynasty", "Regalia",
     "Bronze and faience", "royalty;war_weapons;gold_jewelry", 5, 3, 0.4,
     "Royal objects from the Nubian pharaohs who ruled Egypt and reunited the Nile Valley.", RP),
    ("Rosetta-Style Decree Stela (Ptolemaic)", "G11", "late_greco_roman", "Ptolemaic Period", "Stela",
     "Granodiorite", "writing_literature;royalty;religion_gods", 7, 4, 0.5,
     "A priestly decree in hieroglyphic, demotic and Greek, the multilingual administration of Greek-ruled Egypt.", RP),

    # ---------------------------------------------------------------- Gallery 12 - Greco-Roman Beliefs
    ("Adult Crocodile Mummy", "G12", "late_greco_roman", "Graeco-Roman Period", "Mummy",
     "Mummified animal and linen", "animals;mummies_afterlife;religion_gods", 9, 4, 1.0,
     "A full-size adult crocodile mummy in contrast to most crocodile mummies that are of baby animals, dedicated "
     "to the crocodile god Sobek.", CW),
    ("Fayum Mummy Portrait", "G12", "late_greco_roman", "Roman Period", "Portrait",
     "Wood and encaustic", "art_statues;mummies_afterlife;daily_life", 8, 4, 0.7,
     "A realistic painted portrait attached to a mummy from the Roman Period, blending Greek painting with Egyptian "
     "burial customs.", RP),
    ("Statue of the Goddess Isis in Greco-Roman Style", "G12", "late_greco_roman", "Roman Period", "Statue",
     "Marble", "religion_gods;art_statues", 7, 3, 0.5,
     "Isis, worshipped across the Roman Empire, appears in a statue that merges Egyptian and Greek forms.", RP),
    ("Animal Mummies: Ibis, Cat and Falcon", "G12", "late_greco_roman", "Late to Roman Period", "Mummy",
     "Animal remains and linen", "animals;mummies_afterlife;religion_gods", 8, 4, 1.0,
     "Mummified ibis, cats and falcons were offerings to gods such as Thoth, Bastet and Horus.", RP),
    ("Roman-Period Painted Shroud", "G12", "late_greco_roman", "Roman Period", "Textile",
     "Linen", "mummies_afterlife;art_statues;religion_gods", 5, 3, 0.5,
     "A painted burial shroud with the deceased beside Osiris and Anubis, showing continuing funerary belief.", RP),
    ("Roman Mummy with Gilded Mask", "G12", "late_greco_roman", "Roman Period", "Mummy",
     "Human remains and cartonnage", "mummies_afterlife;gold_jewelry;religion_gods", 7, 4, 0.5,
     "A mummy decorated with a gilded cartonnage mask and elaborate wrapping, typical of Roman Egypt.", RP),
    ("Serapis Statue", "G12", "late_greco_roman", "Ptolemaic-Roman Period", "Statue",
     "Marble", "religion_gods;art_statues", 5, 3, 0.4,
     "The Greco-Egyptian god Serapis, created under the Ptolemies to unite two religions.", RP),
    ("Coptic-Roman Funerary Stela", "G12", "late_greco_roman", "Roman Period", "Stela",
     "Limestone", "mummies_afterlife;religion_gods;writing_literature", 4, 3, 0.3,
     "A funerary stela shows the late phase of ancient Egyptian belief as new religions arrived.", RP),
]
