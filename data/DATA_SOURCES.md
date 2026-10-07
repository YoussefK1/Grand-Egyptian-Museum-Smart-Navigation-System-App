# Dataset card - GEM artifact & museum dataset

Built in October 2026 from the museum's official ticketing site (https://visit-gem.com -> tickets.gem.eg), press and
scholarly coverage of the museum, and the team's first-version app (`home_screen.dart`, `exhibits_screen.dart`).

## Files
| File | Rows | Description |
|---|---|---|
| `artifacts.csv` | 126 | One row per object: id, name, zone_id, gallery, floor, era_id, period, category, material, interest_tags, popularity (1-10), view_minutes, kid_friendly, crowd_level, description, keywords, image_url/image_file, app_image_asset, **source_tier** |
| `zones.csv` | 50 | Navigation nodes (entrance, halls, 12 main galleries, 5 Tutankhamun galleries, boats museum, lifts, stairs, restrooms, cafe, shop, 4 cave galleries) with floor, schematic x/y |
| `edges.csv` | 72 | Connections (walk / outdoor / stairs / elevator) with length in metres |
| `questionnaire.json` | 8 questions | Tour-customisation questions served to the app |
| `visitor_profiles.csv` | 3,000 | **Synthetic** visitor questionnaire answers |
| `tour_training_data.csv.gz` | 378,000 | **Synthetic** (visitor x artifact) feature rows with relevance grade 0-3 used to train XGBoost |

## What was verified from the website / press (`source_tier = confirmed_web`, 43 rows)
Opening hours, areas included in a visit (Tutankhamun Galleries, Main Galleries, Grand Hall, Grand Stairs, Khufu's Boats Museum,
commercial area, gardens), visitor rules (from the official ticketing site); structure of the 12 Main Galleries (4 periods x
Society/Kingship/Beliefs; Galleries 1-3 Prehistoric-First Intermediate, 4-6 Middle Kingdom/Second Intermediate, 7-9 New Kingdom,
10-12 Third Intermediate/Late/Graeco-Roman); named objects: Ramesses II colossus, Hanging Obelisk, Merenptah column,
Ptolemaic statues, Restoration Stela, Akhenaten head, Senwosret I statues, king list, Hatshepsut, Thutmose III, Mesehti soldiers,
Hetepheres burial equipment, Khufu solar boats, Dendera treasure falcon, adult crocodile mummy, and the Tutankhamun galleries'
mask, three coffins, canopic shrine, throne, six chariots, shields and daggers.

## What is NOT verified (`source_tier = representative`, 80 rows)
Typical object types for each gallery theme (e.g. "Middle Kingdom coffin with Coffin Texts", "Set of shabti figures"). They give every
gallery enough data for training and clustering, but **exact accession numbers/locations must be checked against the GEM catalogue
before publication.** Sources also disagree on the theme order inside galleries 4-12 (assumed Society -> Kingship -> Beliefs, as
officially confirmed for galleries 1-3).

## Other caveats
* `popularity`, `view_minutes`, `kid_friendly`, `crowd_level` are analyst estimates, not museum statistics.
* `interest_tags` are manual labels (12 interest categories).
* No photos are bundled except the 5 from the prototype app; `image_url` is empty - fill it (and run `scripts/fetch_images.py`)
  to enable CLIP image embeddings. Respect the museum's image-use terms (personal/non-commercial use only on its ticketing site).
* Visitor/training data is simulated by `scripts/simulate_visitors.py` (hidden utility = era match + interest overlap + popularity + family/student/
  mobility/crowd effects + personal noise). It is a stand-in until real feedback is collected.

## Main sources consulted
* Official ticketing website: https://visit-gem.com/en/home (opening hours, visit contents, rules)
* The Past: "The Grand Egyptian Museum: Visiting the Main galleries" and "The Grand Egyptian Museum" (gallery structure, objects)
* Antiquity (Cambridge): "Truly Grand Egyptian Museum" (gallery grid, Gallery 02 Hetepheres, Senwosret I GEM 1706)
* EnterpriseAM "Inside the GEM", Wanderlust, Khaleej Times, d5mag / ATELIER BRUCKNER, The Collector (Tutankhamun galleries)
* Team prototype app (collection items: Ukhhotep boat, falcon statuette, Mitri scribe, Ramesses II obelisk)
