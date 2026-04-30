"""21 carousel briefs. Each brief = (mode, series_meta, slides_spec).

slides_spec is a list of (layout_func_name, kwargs_dict). Each renders one slide.
Slide 1 is ALWAYS the original slide.png from the queue entry — NOT included here.
We only describe slides 2..N here.
"""

# Verified Unsplash + local Vezel photos
P_ENGINE = "https://images.unsplash.com/photo-1650179172998-035ba1b497b9?w=1600&q=85"
P_DASH   = "https://images.unsplash.com/photo-1597386601945-8980df52c3dc?w=1600&q=85"
P_SHOP   = "https://images.unsplash.com/photo-1676018366904-c083ed678e60?w=1600&q=85"
P_BRAKE  = "/Users/admin/the-right-workshop/assets/stock-photos/ig-carousels/brake-assembly-abs-pexels-34277926.jpg"
P_NIGHT  = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=85"
# Local Vezel photos (canonical/ folder) — runner converts file paths to data URIs
P_VEZEL_CLEAN = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/vezel-clean.png"
P_VEZEL_B     = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/vezel-b.png"
P_VEZEL_C     = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/vezel-c.png"
P_VEZEL_D     = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/vezel-d.png"
P_VEZEL_E     = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/vezel-e.png"

# Local Singapore nano-banana photos for Mode D + Mode A topic-context
NB = "/Users/admin/the-right-workshop/assets/nano-banana-generated/blog"
P_SG_QUESTIONS  = f"{NB}/nb_post_12-questions_v1.png"     # mechanic + questions
P_SG_FIRST_CAR  = f"{NB}/nb_post7_coe_renewal_v1.png"     # COE renewal (SG)
P_SG_RECEIPT    = f"{NB}/nb_post_read-quote_v1.png"       # reading workshop quote
P_SG_BRAKES     = f"{NB}/nb_post5_brake_pads_v1.png"      # brake pads
P_SG_COOLANT    = f"{NB}/nb_post6_coolant_radiator_v1.png"  # coolant / overheat
P_SG_RAIN       = f"{NB}/nb_post10_rain_driving_v1.png"   # rain driving SG
P_SG_OIL        = f"{NB}/nb_servicing_oilpour_v2.png"     # oil pour
P_SG_USED       = f"{NB}/nb_post9_used_car_inspection_v1.png"  # used car inspection
P_SG_DEALER_INDEP = f"{NB}/nb_post_dealer-vs-indep_v1.png"  # dealer vs independent
P_SG_FIRST_SVC  = f"{NB}/nb_post_first-service_v2.png"    # first service


# series_meta values match the canonical mode templates
S_WLD = "Warning Light Decoded"
S_COW = "Cost of Waiting"
S_ST  = "Straight Talk"
S_DM  = "Driver's Manual"
S_BBTB = "Behind the Badge"


BRIEFS = {

# CoW Mode C — Skip the Oil
"newseries-cow-mode-c-2026-05-04-20": ("mode_c", S_COW, [
    ("c_list_punch", {"eyebrow": "What each skip costs",
        "h1_html": "Each cycle<br><span class='accent'>matters.</span>",
        "items": [
            {"title": "SKIP 1 · ADDITIVES GONE", "body": "Detergents and antiwear additives are spent. Engine still runs, but unprotected."},
            {"title": "SKIP 2 · METAL ON METAL", "body": "Bearings start scoring. Filings appear in the pan. Damage is silent."},
            {"title": "SKIP 3 · SEIZED", "body": "Engine locks. Tow + rebuild. $8,000+. The cheap end of the curve is gone."},
        ],
        "footer_stat": "<span class='num'>3</span>SKIPS · GAME OVER"}),
    ("c_stat_callout", {"big_stat_html": "$<span class='accent'>50</span>",
        "eyebrow": "On schedule",
        "h1_html": "$50 SERVICE.<br>$5,000<br><span class='accent'>REBUILD.</span>",
        "body_html": "100x cost gap. Same car. Same engine. Same owner. <strong>The cheapest engine fix is the next oil change.</strong>",
        "footer_stat": "<span class='num'>100</span>X COST GAP"}),
    ("c_list_punch", {"eyebrow": "Signs you're overdue",
        "h1_html": "Black, thin,<br><span class='accent'>burning.</span>",
        "items": [
            {"title": "DIPSTICK BLACK", "body": "Oil should be golden-amber. Coal-black means sludge."},
            {"title": "ENGINE TICKS AT IDLE", "body": "Lifters aren't getting clean oil. Service this week."},
            {"title": "BURNING SMELL", "body": "Old oil's flash point is dropping. Time's up."},
            {"title": "SERVICE STICKER OLD", "body": "If you can't remember the last service, it's overdue."},
        ],
        "footer_stat": "<span class='num'>4</span>SIGNS"}),
    ("c_cta", {"h1_html": "Service<br>on time.<br><span class='accent'>Pay once.</span>",
        "body_html": "Drop us your model and last service date. We'll tell you what's due, what's optional, and what to skip.",
        "footer_stat": "BOOK NOW"}),
]),

# ─────────────────────────────────────────────────────────
# MODE B — CREAM MAGAZINE
# ─────────────────────────────────────────────────────────

# WLD Mode B — Battery Light (slide 1: cover already says "The red one matters most.")
"newseries-wl-mode-b-2026-05-02-11": ("mode_b", S_WLD, [
    ("b_pullquote", {"kicker_label": "What it actually means",
        "h1_html": "It's not the<br><em>battery.</em>",
        "body_html": "9 of 10 battery-light cases trace back to a failing alternator. The battery just delivers what the alternator made — and that supply is gone. <strong>The light is the warning. The stall is the verdict.</strong>"}),
    ("b_numbered_list", {"kicker_label": "How long you have",
        "h1_html": "Drive less.<br>Drive home.<br><em>Don't drive far.</em>",
        "items": [
            {"title": "First 30 minutes", "body": "Battery alone can carry the car. You may still make it home if you drive direct."},
            {"title": "30 to 60 minutes", "body": "Power steering goes heavy. Dashboard dims. Don't merge onto the PIE."},
            {"title": "Past 60 minutes", "body": "Engine cuts mid-traffic. Stranded. Tow required."},
        ]}),
    ("b_two_column", {"kicker_label": "The cost split",
        "h1_html": "Catch it now,<br>or pay <em>later.</em>",
        "left_label": "Catch it now", "left_value": "$300", "left_body": "Alternator replaced. Battery tested. Belt checked. Drive home the same day.",
        "right_label": "Stranded", "right_value": "$1,500+", "right_body": "Tow + alternator + new battery + missed appointments + the bad afternoon.",
        "footer_note": "Free OBD scan + alternator load test when you book."}),
    ("b_cta", {"kicker_label": "If the light comes on",
        "h1_html": "Come<br><em>straight in.</em>",
        "body": "We diagnose alternators on the spot. Free OBD load test if you book the same day."}),
]),

# CoW Mode B — Brake fluid $80 → $3,400
"newseries-cow-mode-b-2026-05-02-20": ("mode_b", S_COW, [
    ("b_pullquote", {"kicker_label": "What's actually happening",
        "h1_html": "Fluid <em>fails</em><br>first.",
        "body_html": "Brake fluid absorbs water from the air on a 2-year curve. Boiling point drops. Brakes go spongy in heat. <strong>One skipped flush turns an $80 service into a $3,400 brake job.</strong>"}),
    ("b_photo_caption", {"kicker_label": "Where the damage shows up", "photo_url": P_BRAKE,
        "photo_caption_text": "WET FLUID · CALIPER · WARPED DISC",
        "h1_html": "From flush to <em>full rebuild.</em>",
        "body_html": "Wet fluid corrodes the caliper from inside. Caliper sticks. Disc warps from uneven heat. <strong>Each skip raises the next bill by 5x.</strong>"}),
    ("b_numbered_list", {"kicker_label": "The cost curve",
        "h1_html": "Service.<br>Disc.<br><em>Caliper.</em>",
        "items": [
            {"title": "$80 — flush on schedule", "body": "Brake fluid every 2 years. Done in an hour. Brakes feel sharp, all season."},
            {"title": "$420 — disc warped", "body": "Skipped one flush. Caliper held heat. Disc warped. Pulse through the pedal."},
            {"title": "$3,400 — full rebuild", "body": "Skipped twice. Caliper seized. New disc, new caliper, new pads, new lines."},
        ]}),
    ("b_two_column", {"kicker_label": "The price of staying cheap",
        "h1_html": "Flush now,<br>or rebuild <em>later.</em>",
        "left_label": "Flush on time", "left_value": "$80", "left_body": "Brake fluid flush every 2 years. Drive home the same day. No drama.",
        "right_label": "Rebuilt twice", "right_value": "$3,400", "right_body": "New disc, new caliper, new pads, new lines. Tow if it locks up.",
        "footer_note": "Free brake-fluid moisture test when you book."}),
    ("b_cta", {"kicker_label": "Book your brake-fluid flush",
        "h1_html": "Service<br>on time.<br><em>Pay once.</em>",
        "body": "We test moisture content before we flush. We show you the strip. Then we do the work."}),
]),

# DM Mode B — Read the dipstick
"newseries-dm-mode-b-2026-05-05-11": ("mode_b", S_DM, [
    ("b_pullquote", {"kicker_label": "Two-minute habit",
        "h1_html": "What the dashboard<br><em>can't tell you.</em>",
        "body_html": "Pull. Wipe. Dip. The dipstick reads the engine's health every time you fill fuel. <strong>The dashboard only reports failure — by then, the damage is done.</strong>"}),
    ("b_photo_caption", {"kicker_label": "What you're looking for", "photo_url": P_ENGINE,
        "photo_caption_text": "DIPSTICK · LEVEL · COLOUR · FEEL",
        "h1_html": "Three signals.<br><em>Two minutes.</em>",
        "body_html": "Level: between MIN and MAX. Colour: golden-amber and slick = healthy. Feel: smooth, not gritty. <strong>That's the engine's monthly check-up.</strong>"}),
    ("b_numbered_list", {"kicker_label": "Read the colour",
        "h1_html": "What the<br>colour <em>tells you.</em>",
        "items": [
            {"title": "Golden-amber", "body": "Healthy. Drive normally. Service at the next manufacturer interval."},
            {"title": "Coal-black", "body": "Overdue. Additives spent. Sludge forming. Book a service this week."},
            {"title": "Cream / milky", "body": "Coolant in the oil. Stop driving. Book a diagnostic now — head gasket suspected."},
        ]}),
    ("b_cta", {"kicker_label": "Read it this week",
        "h1_html": "Two minutes.<br><em>Saves engines.</em>",
        "body": "Free dipstick reading on every TRW visit. Bring it in if anything looks off."}),
]),

# BtB Vezel Mode B — honest list
"newseries-bbtb-vezel-mode-b-2026-05-05-20": ("mode_b", S_BBTB, [
    ("b_pullquote", {"kicker_label": "The honest list",
        "h1_html": "What works.<br><em>What fails.</em>",
        "body_html": "Vezel hybrid. <strong>What works:</strong> the fuel economy, the boot space, the resale price. <strong>What fails:</strong> rear wheel bearings, infotainment, hybrid battery beyond 150,000 km. Know before you buy."}),
    ("b_photo_caption", {"kicker_label": "Buy for this", "photo_url": P_VEZEL_B,
        "photo_caption_text": "RU-GEN HYBRID · SG'S MOST-COMMON SUV",
        "h1_html": "Half the running<br>cost. <em>Twice the<br>resale.</em>",
        "body_html": "18–22 km/L in real Singapore traffic. Holds value year on year. Hybrid stigma is gone — buyers actively seek them now."}),
    ("b_numbered_list", {"kicker_label": "Plan for these — they're coming",
        "h1_html": "What fails.<br><em>By mileage.</em>",
        "items": [
            {"title": "80,000 km — rear bearings", "body": "Whining at 60–80 km/h on smooth roads. Plan ~$400 per side. Don't ignore."},
            {"title": "120,000 km — brake hoses", "body": "Coastal humidity rusts them from outside. Soft pedal feel. Replace as a pair."},
            {"title": "150,000 km+ — hybrid battery", "body": "Capacity drop. Get a battery health report at every service. $2,800 to refurb."},
        ]}),
    ("b_cta", {"kicker_label": "Servicing a Vezel?",
        "h1_html": "Send us<br>a <em>message.</em>",
        "body": "We service Vezels every week. Drop us a model + mileage and we'll send a quote with the right parts."}),
]),


# ─────────────────────────────────────────────────────────
# MODE A — EDITORIAL DARK
# ─────────────────────────────────────────────────────────

# ST Mode A — Three Questions (slide 1 cover: "Ask the three questions.")
"newseries-st-mode-a-2026-05-02-15": ("mode_a", S_ST, [
    ("a_numbered_card", {"photo_url": P_SG_QUESTIONS, "num": 1, "label": "Question one",
        "h1_html": "Show me<br>the <em>part.</em>",
        "body_html": "The old part out. The new part in. <strong>Side by side, on the bench.</strong> If they cannot show it, they did not change it.",
        "watch_text": "Watch for: 'we already disposed of it.'"}),
    ("a_numbered_card", {"photo_url": P_SG_QUESTIONS, "num": 2, "label": "Question two",
        "h1_html": "Show me<br>the <em>spec.</em>",
        "body_html": "OEM? Aftermarket? Brand? Grade? <strong>Every part has a spec sheet.</strong> An honest mechanic talks brand and grade — not just 'good one' or 'original.'",
        "watch_text": "Watch for: 'all the same lah.'"}),
    ("a_numbered_card", {"photo_url": P_SG_QUESTIONS, "num": 3, "label": "Question three",
        "h1_html": "Show me<br>the <em>price.</em>",
        "body_html": "Itemised. <strong>Parts vs labour vs consumables.</strong> A real quote breaks it down. A fishy quote bundles everything into one round number.",
        "watch_text": "Watch for: 'trust me, fair price.'"}),
    ("a_quote", {"photo_url": P_SG_QUESTIONS, "kicker": "The tell",
        "quote_html": "If they dodge any of the three, <em>walk away</em>.",
        "attrib": "TRW workshop floor"}),
    ("a_cta", {"photo_url": P_SG_QUESTIONS,
        "h1_html": "Bring the<br>questions.<br><em>Get straight<br>answers.</em>",
        "body_html": "We answer all three before we lift the hood. Free second-opinion quote if you have one in hand."}),
]),

# DM Mode A — What I wish I knew at 23
"newseries-dm-mode-a-2026-05-03-11": ("mode_a", S_DM, [
    ("a_numbered_card", {"photo_url": P_SG_FIRST_CAR, "num": 1, "label": "Lesson one",
        "h1_html": "COE is<br><em>not magic.</em>",
        "body_html": "It's a 10-year permit. The car can outlast it physically. <strong>Plan the year-9 decision now</strong>, not at year-10.",
        "watch_text": "COE renewal pricing can double a car's lifetime running cost."}),
    ("a_numbered_card", {"photo_url": P_SG_FIRST_CAR, "num": 2, "label": "Lesson two",
        "h1_html": "Tyres<br><em>age out.</em>",
        "body_html": "Even with low mileage, rubber hardens after 5–6 years. <strong>Sidewall cracks before tread wears.</strong>",
        "watch_text": "'Plenty of tread' is a tread reading, not an age reading."}),
    ("a_numbered_card", {"photo_url": P_SG_FIRST_CAR, "num": 3, "label": "Lesson three",
        "h1_html": "Service stamps<br><em>matter.</em>",
        "body_html": "At resale, a complete service book adds <strong>$1,500–$3,000</strong> vs no records. Keep every receipt.",
        "watch_text": "Workshops with proper book stamps cost a little more. Worth it at trade-in."}),
    ("a_quote", {"photo_url": P_SG_FIRST_CAR, "kicker": "The lesson",
        "quote_html": "The cheapest car is the one you <em>understand</em> before you signed.",
        "attrib": "Five years owning a Civic"}),
    ("a_cta", {"photo_url": P_SG_FIRST_CAR,
        "h1_html": "Bookmark<br>this for your<br><em>next car.</em>",
        "body_html": "Pre-decision check before you sign. We pull diagnostic, COE history, and resale comps so you know what you're buying."}),
]),

# BtB Vezel Mode A — honest take
"newseries-bbtb-vezel-mode-a-2026-05-03-20": ("mode_a", S_BBTB, [
    ("a_numbered_card", {"photo_url": P_VEZEL_CLEAN, "num": 1, "label": "What works",
        "h1_html": "Fuel<br><em>economy.</em>",
        "body_html": "Hybrid drivetrain returns 18–22 km/L in Singapore traffic. <strong>Half the running cost</strong> of a petrol-only SUV.",
        "watch_text": "Watch for: hybrid battery health past 150,000 km — get a battery report at every service."}),
    ("a_numbered_card", {"photo_url": P_VEZEL_CLEAN, "num": 2, "label": "What works",
        "h1_html": "Cabin<br><em>comfort.</em>",
        "body_html": "CVT is whisper-quiet at city speeds. Rear seats fold flat. <strong>Resale stays strong year on year.</strong>",
        "watch_text": "Brake regen is slightly grabby — not a fault, just the system."}),
    ("a_numbered_card", {"photo_url": P_VEZEL_CLEAN, "num": 3, "label": "What fails",
        "h1_html": "Rear<br><em>bearings.</em>",
        "body_html": "Whining starts around 80,000 km. Loudest at 60–80 km/h on smooth roads. <strong>Plan a $400 per-side bearing job.</strong>",
        "watch_text": "If the noise disappears in a corner — that's the bearing, not the tyre."}),
    ("a_quote", {"photo_url": P_VEZEL_CLEAN, "kicker": "The tell",
        "quote_html": "Buy for the running cost. <em>Budget for the bearings</em>.",
        "attrib": "TRW workshop floor"}),
    ("a_cta", {"photo_url": P_VEZEL_CLEAN,
        "h1_html": "Servicing<br>a Vezel?<br><em>We see them<br>every week.</em>",
        "body_html": "Drop us a model year + mileage and we'll send a quote with the right parts. Vezel-specific knowledge included."}),
]),


# ─────────────────────────────────────────────────────────
# MODE C — POSTER BOLD
# ─────────────────────────────────────────────────────────

# WLD Mode C — Check engine light
"newseries-wl-mode-c-2026-05-04-11": ("mode_c", S_WLD, [
    ("c_stat_callout", {"big_stat_html": "2<span class='accent'>min</span>", "eyebrow": "OBD scan",
        "h1_html": "the SCANNER<br>tells the<br><span class='accent'>truth.</span>",
        "body_html": "A $30 sensor and a $3,000 catalytic converter throw the same warning light. <strong>The OBD scanner is the only thing that knows which one you have.</strong>",
        "footer_stat": "<span class='num'>$30</span> v <span class='num'>$3,000</span>"}),
    ("c_list_punch", {"eyebrow": "Steady vs flashing",
        "h1_html": "Read the<br><span class='accent'>colour first.</span>",
        "items": [
            {"title": "STEADY · YOU HAVE TIME", "body": "Drive normally. Book a scan within the week. Most steady codes are sensor-related."},
            {"title": "FLASHING · PULL OVER", "body": "Misfire detected. Continued driving cooks the catalyst. Stop, tow, scan."},
            {"title": "ON + OFF · INTERMITTENT", "body": "A loose gas cap can do this. Tighten, drive 2 cycles, light may clear itself."},
        ],
        "footer_stat": "<span class='num'>'26</span>OBD CHEAT SHEET"}),
    ("c_photo_headline", {"photo_url": P_ENGINE,
        "badge_year_html": "FREE · DIAG", "badge_tag": "$0 SCAN ON BOOK",
        "h1_html": "DON'T<br>GUESS.<br><span class='accent'>SCAN.</span>",
        "tagline_html": "<strong>$30 fix or $3,000 fix</strong> — the scanner reads it in two minutes. Free with any TRW booking.",
        "footer_stat": "<span class='num'>2</span>MIN DIAGNOSTIC"}),
    ("c_cta", {"h1_html": "Book a<br><span class='accent'>free<br>OBD scan.</span>",
        "body_html": "Drop your model + the code (if you have one). We confirm the fault and the fix range before you commit.",
        "footer_stat": "FREE OBD"}),
]),

# ST Mode C — Bring receipts
"newseries-st-mode-c-2026-05-04-15": ("mode_c", S_ST, [
    ("c_list_punch", {"eyebrow": "The 3 asks",
        "h1_html": "Three asks.<br><span class='accent'>One quote.</span>",
        "items": [
            {"title": "QUOTE IN WRITING", "body": "On a printed slip or PDF, not a napkin. Itemised. Dated. Workshop stamp."},
            {"title": "PART NUMBER", "body": "Brand and OEM number. So you can verify it's the right part for your VIN."},
            {"title": "SECOND OPINION", "body": "Send the quote to one other workshop. 30-second sanity check."},
        ],
        "footer_stat": "<span class='num'>$0</span>TO ASK"}),
    ("c_stat_callout", {"big_stat_html": "$<span class='accent'>300</span>",
        "eyebrow": "average markup",
        "h1_html": "ON QUOTES<br>WITHOUT<br><span class='accent'>RECEIPTS.</span>",
        "body_html": "Plus the dispute when something fails early. <strong>Honest workshops want you to compare</strong> — they win on transparency.",
        "footer_stat": "<span class='num'>'26</span>QUOTE AUDIT"}),
    ("c_list_punch", {"eyebrow": "Red flags · walk away",
        "h1_html": "Four<br><span class='accent'>red flags.</span>",
        "items": [
            {"title": "TRUST ME · FAIR PRICE", "body": "Trust is built with paperwork, not adjectives."},
            {"title": "ORIGINAL BRAND", "body": "Ask which brand. 'Original' is not a brand."},
            {"title": "ONE ROUND NUMBER", "body": "Real quotes itemise parts vs labour vs consumables."},
            {"title": "ALREADY DISPOSED", "body": "Honest shops save the old part for you to inspect."},
        ],
        "footer_stat": "<span class='num'>x4</span>WALK-AWAYS"}),
    ("c_cta", {"h1_html": "Send us<br>your<br><span class='accent'>receipt.</span>",
        "body_html": "We'll second-opinion any quote in writing. <strong>Free check.</strong> No commitment.",
        "footer_stat": "SECOND OPINION"}),
]),

# DM Mode C — On the PIE watch the gauges
"newseries-dm-mode-c-2026-05-07-11": ("mode_c", S_DM, [
    ("c_list_punch", {"eyebrow": "Three gauges that matter",
        "h1_html": "Glance.<br><span class='accent'>Every 30 km.</span>",
        "items": [
            {"title": "TEMP · COOLANT", "body": "Stays in the middle. Past two-thirds on a flat road = cooling system struggling."},
            {"title": "OIL · PRESSURE", "body": "Drops a little when warm — normal. Below the marker line — pull off, check level."},
            {"title": "RPM · TACHOMETER", "body": "Sudden spikes at steady speed = transmission slipping. CVT belts fail this way."},
        ],
        "footer_stat": "<span class='num'>3</span>GAUGE CHECK"}),
    ("c_stat_callout", {"big_stat_html": "<span class='accent'>$80</span><br>v $3,000",
        "eyebrow": "PRE-TRIP CHECK",
        "h1_html": "PRE-TRIP<br>NOW.<br><span class='accent'>STRANDED LATER.</span>",
        "body_html": "Coolant level + oil + tyres + battery test. <strong>Done in 30 minutes.</strong> Catches what the dashboard misses.",
        "footer_stat": "<span class='num'>30</span>MIN PRE-TRIP"}),
    ("c_photo_headline", {"photo_url": P_ENGINE,
        "badge_year_html": "PIE · READY", "badge_tag": "Long-drive check",
        "h1_html": "LONG PULLS.<br>WEAK PARTS.<br><span class='accent'>REVEALED.</span>",
        "tagline_html": "The expressway exposes weak parts. Long pulls reveal what short trips hide. <strong>Book before, not after.</strong>",
        "footer_stat": "<span class='num'>'26</span>PIE READY"}),
    ("c_cta", {"h1_html": "Book a<br><span class='accent'>pre-trip<br>check.</span>",
        "body_html": "30 minutes. Coolant, oil, tyres, battery. The cheapest insurance for a long drive.",
        "footer_stat": "BOOK NOW"}),
]),

# BtB Vezel Mode C — Find the right Vezel workshop
"newseries-bbtb-vezel-mode-c-2026-05-07-20": ("mode_c", S_BBTB, [
    ("c_list_punch", {"eyebrow": "What Vezel owners get wrong",
        "h1_html": "Same car.<br><span class='accent'>Different<br>mistakes.</span>",
        "items": [
            {"title": "WRONG OIL", "body": "0W-20 synthetic only. Generic 5W-30 hurts fuel economy + thermal limits."},
            {"title": "WRONG COOLANT", "body": "Honda Type 2 only. Mixing green or pink coolant clogs the hybrid radiator within a year."},
            {"title": "WRONG SCAN", "body": "Generic OBD reads engine codes only. Hybrid system needs Honda HDS to read battery + inverter."},
        ],
        "footer_stat": "<span class='num'>3</span>WRONGS"}),
    ("c_stat_callout", {"big_stat_html": "$<span class='accent'>420</span>",
        "eyebrow": "Vezel-savvy service",
        "h1_html": "RIGHT<br>SHOP.<br><span class='accent'>RIGHT COST.</span>",
        "body_html": "Vezel-specific service. Right oil. Right coolant. Hybrid battery report included. <strong>Generic shops cost you 3x in future repairs.</strong>",
        "footer_stat": "<span class='num'>'26</span>VEZEL SVC"}),
    ("c_photo_headline", {"photo_url": P_VEZEL_C,
        "badge_year_html": "WEEKLY · '26", "badge_tag": "TRW Vezel-savvy",
        "h1_html": "RIGHT CAR.<br>RIGHT<br><span class='accent'>WORKSHOP.</span>",
        "tagline_html": "Hybrid systems are unforgiving. <strong>Wrong hands, wrong parts, wrong diagnosis.</strong> We service Vezels every week.",
        "footer_stat": "<span class='num'>200+</span>VEZELS SERVICED"}),
    ("c_cta", {"h1_html": "Book a<br><span class='accent'>Vezel<br>service.</span>",
        "body_html": "Drop us your model year + mileage. Honda HDS scan, hybrid battery report, the right 0W-20 oil — standard.",
        "footer_stat": "VEZEL HOTLINE"}),
]),


# ─────────────────────────────────────────────────────────
# MODE D — POLAROID ZINE
# ─────────────────────────────────────────────────────────

# WLD Mode D — Drove on red light
"newseries-wl-mode-d-2026-05-06-11": ("mode_d", S_WLD, [
    ("d_polaroid_text", {"photo_url": P_SG_COOLANT, "photo_caption": "min 4 · pull over now",
        "sticky_lines": ["min 0–3:", "amber light. safe.", "min 4:", "red light.", "min 10: too late."],
        "kicker_stamp": "Heat damage", "kicker_date": "compounds in seconds",
        "h1_html": "Past the <span class='underline'>red line</span>.",
        "lead_text": "Every minute past red warps something different. Heads, gaskets, valves. By minute 10, the bill is in the thousands."}),
    ("d_handwritten_list", {"kicker_stamp": "4 signs · I ignored all 4",
        "h1_html": "Small signals. <span class='underline'>Big bills</span>.",
        "items": [
            {"title": "Temp gauge creeping past mid-line", "body": "Cooling system can't keep up. Pull over within 5 km."},
            {"title": "Sweet smell from the vents", "body": "Coolant leaking onto a hot surface. Smell is the warning."},
            {"title": "White smoke from the exhaust", "body": "Coolant entering the cylinders. Engine is drinking it."},
            {"title": "Heater blows cold even when set to hot", "body": "Coolant level too low to circulate through the heater core."},
        ]}),
    ("d_sticky_quote", {"kicker_stamp": "The lesson",
        "sticky_html": "When the temp light comes on,<br><em>pull over</em>.",
        "attrib": "Customer who learned the $2,800 way"}),
    ("d_cta", {"kicker_stamp": "Free cooling-system check",
        "h1_html": "If the temp light is on,<br><span class='underline'>pull over</span>.",
        "body_html": "Bring it on a tow if you must. We'd rather see it on a flatbed than on a head-gasket invoice.",
        "swipe": "book"}),
]),

# ST Mode D — 4-line honest test
"newseries-st-mode-d-2026-05-06-15": ("mode_d", S_ST, [
    ("d_handwritten_list", {"kicker_stamp": "Use before any quote",
        "h1_html": "Four asks. <span class='underline'>One yes</span>.",
        "items": [
            {"title": "Show me the part", "body": "Old part out, new part in. Side by side, on the bench."},
            {"title": "Show me the wear", "body": "What failed, and why. A photo or the part itself."},
            {"title": "Show me the spec", "body": "OEM brand, part number, grade. On paper."},
            {"title": "Show me the price", "body": "Itemised. Parts vs labour vs consumables. Receipt before you pay."},
        ]}),
    ("d_polaroid_text", {"photo_url": P_SG_RECEIPT, "photo_caption": "old part · on the bench",
        "sticky_lines": ["if you can't", "see it,", "<em>they didn't</em>", "<em>change it</em>."],
        "kicker_stamp": "Bench rule", "kicker_date": "Always",
        "h1_html": "On the <span class='underline'>bench</span>.",
        "lead_text": "The old part stays on the bench until you see it. Honest workshops keep it. Upsell shops 'already disposed of it.'"}),
    ("d_sticky_quote", {"kicker_stamp": "The lesson",
        "sticky_html": "Honest workshops welcome <em>questions</em>. Upsell shops change the topic.",
        "attrib": "TRW workshop floor"}),
    ("d_cta", {"kicker_stamp": "Save this card",
        "h1_html": "Send us your <span class='underline'>quote</span>.",
        "body_html": "We'll second-opinion any quote in writing. We use the same four asks. Honest reply, every time.",
        "swipe": "book"}),
]),

# CoW Mode D — One year too long
"newseries-cow-mode-d-2026-05-06-20": ("mode_d", S_COW, [
    ("d_handwritten_list", {"kicker_stamp": "4 signs · I ignored all 4",
        "h1_html": "Small noises. <span class='underline'>Big bills</span>.",
        "items": [
            {"title": "Squeal at low speed", "body": "Pad wear indicator hitting the rotor. $180 problem at this stage."},
            {"title": "Pulse through the pedal", "body": "Rotor warping from heat cycling. $420 if you book this week."},
            {"title": "One side pulling harder", "body": "Caliper sticking. Heat building on one wheel. $680 in caliper rebuild."},
            {"title": "Grinding I felt in my teeth", "body": "Metal on metal. Past pads. Now a $1,500 brake job — minimum."},
        ]}),
    ("d_polaroid_text", {"photo_url": P_SG_BRAKES, "photo_caption": "8 months of squeals",
        "sticky_lines": ["$180 service.", "Skipped twice.", "<em>Now $1,500</em>.", "Lesson learned."],
        "kicker_stamp": "Guest diary", "kicker_date": "Last Tuesday",
        "h1_html": "I waited <span class='underline'>one year</span> too long.",
        "lead_text": "The squeal in March was a $180 problem. I made it a $1,500 problem. Eight months. Same brakes. Same car."}),
    ("d_sticky_quote", {"kicker_stamp": "The lesson",
        "sticky_html": "Brakes do not get better on their own. The squeal is the <em>cheapest warning</em> you'll ever get.",
        "attrib": "Customer who shared his story so you don't repeat it"}),
    ("d_cta", {"kicker_stamp": "If it squeals",
        "h1_html": "Come <span class='underline'>straight in</span>.",
        "body_html": "Squeal-stage brake jobs are an hour and $180. Grind-stage brake jobs are a weekend and $1,500. Catch it early.",
        "swipe": "book"}),
]),

# DM Mode D — My first car 230k
"newseries-dm-mode-d-2026-05-13-20": ("mode_d", S_DM, [
    ("d_polaroid_text", {"photo_url": P_SG_FIRST_CAR, "photo_caption": "first car · 2008 Civic · 230,000 km",
        "sticky_lines": ["10 years.", "5 lessons.", "<em>Wish I'd known</em>", "before I signed."],
        "kicker_stamp": "Owner diary", "kicker_date": "Since 2014",
        "h1_html": "230,000 km. <span class='underline'>Many lessons</span>.",
        "lead_text": "COE expires. Tyres age out. Service stamps matter at resale. Five things every first-time driver should know before signing the loan papers."}),
    ("d_handwritten_list", {"kicker_stamp": "5 lessons · in order of importance",
        "h1_html": "What I'd tell <span class='underline'>23-year-old me</span>.",
        "items": [
            {"title": "The cheapest car is the one you understand", "body": "Buy what you can service, not what you can flex."},
            {"title": "Service stamps are money", "body": "Skip a stamp, lose $500 at resale. Every time."},
            {"title": "Plan the COE decision at year 8", "body": "Not at year 10. Not the day before expiry."},
            {"title": "Tyres age out before they wear out", "body": "Low-mileage car ≠ safe tyres. Check the date code."},
        ]}),
    ("d_sticky_quote", {"kicker_stamp": "The lesson",
        "sticky_html": "The car you <em>understand</em><br>is the cheap one.",
        "attrib": "10 years and 230,000 km of being wrong"}),
    ("d_cta", {"kicker_stamp": "Bookmark for your next car",
        "h1_html": "Pre-decision <span class='underline'>check</span>.",
        "body_html": "We pull diagnostic, service history, and resale comps before you sign. So you know what you're buying.",
        "swipe": "book"}),
]),

# BtB Vezel Mode D — Vezel notes from workshop floor
"newseries-bbtb-vezel-mode-d-2026-05-14-15": ("mode_d", S_BBTB, [
    ("d_polaroid_text", {"photo_url": P_VEZEL_D, "photo_caption": "Vezel · weekly visitor",
        "sticky_lines": ["Bearings: 80k.", "Brake hose: 120k.", "<em>Hybrid bat: 150k+</em>"],
        "kicker_stamp": "Workshop notes", "kicker_date": "From the floor",
        "h1_html": "Same car. <span class='underline'>Same patterns</span>.",
        "lead_text": "Owners come in for the same things. Bearings around 80k. Brake hose corrosion in coastal areas. Hybrid battery health beyond 150k. Predictable, if you know."}),
    ("d_handwritten_list", {"kicker_stamp": "Ask at your next service",
        "h1_html": "Four <span class='underline'>questions</span>.",
        "items": [
            {"title": "Hybrid battery health report", "body": "State of charge, capacity, cell balance. Should be standard on every Vezel service."},
            {"title": "Rear wheel bearing inspection", "body": "Listen at 60–80 km/h on a smooth road. Whining = bearing. Easy catch."},
            {"title": "Brake hose visual", "body": "Look for surface corrosion. Coastal cars get it earlier."},
            {"title": "Honda HDS scan, not generic", "body": "Hybrid system needs the right diagnostic tool. Generic OBD misses half."},
        ]}),
    ("d_sticky_quote", {"kicker_stamp": "The lesson",
        "sticky_html": "Predictable. Not <em>maintenance-free</em>.",
        "attrib": "200+ Vezels serviced at TRW"}),
    ("d_cta", {"kicker_stamp": "Servicing a Vezel?",
        "h1_html": "We see them <span class='underline'>weekly</span>.",
        "body_html": "Drop us a model year + mileage and we'll send a Vezel-specific quote — right oil, right coolant, hybrid battery report.",
        "swipe": "book"}),
]),


# ─────────────────────────────────────────────────────────
# MODE E — SPEC SHEET
# ─────────────────────────────────────────────────────────

# WLD Mode E — ABS off (slide 1 already shows ABS diagram + headline)
"newseries-wl-mode-e-2026-05-08-11": ("mode_e", S_WLD, [
    ("e_spec_table", {"file_id": "FILE / WL.ABS.SENSOR", "file_label": "Anti-lock braking system",
        "eyebrow": "Spec table · what happens when ABS is on",
        "h1_html": "Read the spec,<br><span class='accent'>not the rumour.</span>",
        "body_html": "Brakes still work. Anti-lock is disabled. <strong>Skid risk in wet weather.</strong> Most causes: dirty wheel sensor or broken wire after a kerb hit.",
        "cells": [
            {"k": "Severity", "v": "Med", "u": "not pull-over"},
            {"k": "Common cause", "v": "Sensor", "u": "dirty / broken"},
            {"k": "Diag. cost", "v": "$60-90", "u": "OBD + visual"},
            {"k": "Fix range", "v": "$120-360", "u": "per wheel"},
        ]}),
    ("e_data_grid", {"eyebrow": "Severity by driving condition",
        "h1_html": "Not the same risk<br>in every <span class='accent'>condition.</span>",
        "items": [
            {"k": "DRY · LOW SPEED", "v": "Low", "u": "Brakes still stop the car. Take it to a workshop within the week."},
            {"k": "DRY · EXPRESSWAY", "v": "Med", "u": "Hard braking can lock a wheel. Leave more gap."},
            {"k": "WET · LOW SPEED", "v": "Med", "u": "Standing water + locked wheel = slide. Brake gently."},
            {"k": "WET · EXPRESSWAY", "v": "High", "u": "Drive home, then book. Don't push speeds in rain."},
        ]}),
    ("e_pinned_photo", {"photo_url": P_BRAKE,
        "pins": [{"label": "A · WHEEL HUB", "pos": "top:230px;left:120px;"}, {"label": "B · ABS SENSOR", "pos": "top:380px;left:140px;"}, {"label": "C · BRAKE DISC", "pos": "top:330px;right:180px;"}, {"label": "D · WIRING", "pos": "top:480px;right:160px;"}],
        "eyebrow": "Diagnostic pin map",
        "h1_html": "From light<br>to <span class='accent'>part.</span>",
        "body_html": "OBD code first. Visual check. Resistance test. Road test to confirm. <strong>Free diagnostic when you book.</strong>"}),
    ("e_cta", {"h1_html": "If the ABS<br>light is on,<br><span class='accent'>come scan.</span>",
        "body_html": "Free OBD diagnostic with any TRW booking. We trace the code to the part before we quote."}),
]),

# ST Mode E — Honest vs upsell
"newseries-st-mode-e-2026-05-13-11": ("mode_e", S_ST, [
    ("e_spec_table", {"file_id": "FILE / ST.QUOTE.COMPARE", "file_label": "Honest vs upsell · brake job",
        "eyebrow": "Spec compare · same car, two quotes",
        "h1_html": "Read the<br>quote, not<br><span class='accent'>the rumour.</span>",
        "body_html": "The honest workshop shows you the part. The upsell one tells you a story. <strong>Know the difference before you say yes.</strong>",
        "cells": [
            {"k": "Pads", "v": "OEM", "u": "with part #"},
            {"k": "Labour", "v": "1.5h", "u": "itemised"},
            {"k": "Old part", "v": "Shown", "u": "on bench"},
            {"k": "Total", "v": "$413", "u": "v $680 upsell"},
        ]}),
    ("e_data_grid", {"eyebrow": "Four asks · ask before pay",
        "h1_html": "Four asks.<br><span class='accent'>Two minutes.</span>",
        "items": [
            {"k": "ASK 1", "v": "PART", "u": "Show me the new part. Show me the brand. Show me the OEM number."},
            {"k": "ASK 2", "v": "WEAR", "u": "Show me the old part. Show me where it failed. Tell me what caused it."},
            {"k": "ASK 3", "v": "PRICE", "u": "Itemise parts. Itemise labour. Itemise consumables. On paper."},
            {"k": "ASK 4", "v": "RECEIPT", "u": "Printed receipt. Dated. Signed. Workshop stamp."},
        ]}),
    ("e_spec_table", {"file_id": "FILE / ST.RECEIPT.SAVE", "file_label": "What to save · every visit",
        "eyebrow": "Build your service book",
        "h1_html": "Document<br><span class='accent'>everything.</span>",
        "body_html": "Service stamps add <strong>$1,500–$3,000</strong> at resale. Old part photos prove the work. Workshop stamps prove the shop. Save them all.",
        "cells": [
            {"k": "Receipt", "v": "+$300", "u": "trade-in"},
            {"k": "Old-part photo", "v": "+$150", "u": "trust"},
            {"k": "Workshop stamp", "v": "+$500", "u": "trade-in"},
            {"k": "OEM part #", "v": "Future", "u": "verifiable"},
        ]}),
    ("e_cta", {"h1_html": "Send us<br>your quote.<br><span class='accent'>We'll check.</span>",
        "body_html": "Free second-opinion on any quote. Itemised reply. No commitment."}),
]),

# CoW Mode E — Service interval numbers
"newseries-cow-mode-e-2026-05-13-15": ("mode_e", S_COW, [
    ("e_spec_table", {"file_id": "FILE / COW.SERVICE.INTERVAL", "file_label": "Service intervals · summary",
        "eyebrow": "Decoded · maintenance intervals",
        "h1_html": "Forget these numbers.<br><span class='accent'>Big problem.</span>",
        "body_html": "Manufacturers publish service intervals because oils, belts and fluids degrade on a schedule. <strong>Forget them, and the cost curve goes vertical.</strong>",
        "cells": [
            {"k": "Engine oil", "v": "7,500", "u": "km / 6 mo"},
            {"k": "Brake fluid", "v": "2 yrs", "u": "or 40,000 km"},
            {"k": "Timing belt", "v": "100k", "u": "km / 7 yrs"},
            {"k": "Coolant", "v": "5 yrs", "u": "or 100,000 km"},
        ]}),
    ("e_data_grid", {"eyebrow": "Adjust by driving conditions",
        "h1_html": "When to service.<br>By <span class='accent'>conditions.</span>",
        "items": [
            {"k": "CITY MAINLY", "v": "EARLIER", "u": "Stop-go ages oil faster. Service at 6,000 km, not 7,500."},
            {"k": "EXPRESSWAY", "v": "ON TIME", "u": "Highway driving is easier on engines. Stick to manufacturer interval."},
            {"k": "SHORT TRIPS", "v": "EARLIER", "u": "Engine never reaches full temp. Sludge builds. 5,000 km service."},
            {"k": "RIDESHARE", "v": "MUCH EARLIER", "u": "12+ hrs/day driving. Service every 4,000 km."},
        ]}),
    ("e_spec_table", {"file_id": "FILE / COW.SKIP.COST", "file_label": "Cost of skipping · by part",
        "eyebrow": "Why intervals exist",
        "h1_html": "On schedule.<br><span class='accent'>Always cheaper.</span>",
        "body_html": "Engine oil oxidises. Brake fluid absorbs water. Timing belts harden. Coolant turns acidic. <strong>Each one fails on its own clock.</strong>",
        "cells": [
            {"k": "Skip oil", "v": "$8,000", "u": "engine rebuild"},
            {"k": "Skip fluid", "v": "$3,400", "u": "caliper job"},
            {"k": "Skip belt", "v": "$4,000", "u": "valve job"},
            {"k": "Skip coolant", "v": "$2,800", "u": "head gasket"},
        ]}),
    ("e_cta", {"h1_html": "Service<br>on schedule.<br><span class='accent'>Always cheaper.</span>",
        "body_html": "Drop us your model + mileage and last service date. We'll tell you what's due, what's optional, and what to skip."}),
]),

# BtB Vezel Mode E — Vezel spec card (slide 1 already has Vezel pinned photo + spec table)
"newseries-bbtb-vezel-mode-e-2026-05-14-20": ("mode_e", S_BBTB, [
    ("e_spec_table", {"file_id": "FILE / BTB.VEZEL.WEAR", "file_label": "Wear card · what / when",
        "eyebrow": "Spec sheet · what wears when",
        "h1_html": "Read the<br>numbers.<br><span class='accent'>Plan ahead.</span>",
        "cells": [
            {"k": "60-80k", "v": "Pads", "u": "$220 / pair"},
            {"k": "80k", "v": "Bearings", "u": "$400 / side"},
            {"k": "120k", "v": "Brake hoses", "u": "$260 / pair"},
            {"k": "150k+", "v": "Hybrid bat.", "u": "$2,800 refurb"},
        ],
        "body_html": "Every Vezel goes through the same wear curve. Same parts, same mileages. <strong>Predictable means you can budget.</strong>"}),
    ("e_data_grid", {"eyebrow": "Ownership matrix",
        "h1_html": "Buy for this.<br><span class='accent'>Plan</span> for that.",
        "items": [
            {"k": "FUEL ECONOMY", "v": "18-22", "u": "km/L · half the running cost of a petrol SUV"},
            {"k": "RESALE", "v": "STRONG", "u": "Holds value year on year. Hybrid stigma is gone."},
            {"k": "REPAIRS", "v": "PREDICTABLE", "u": "Same wear items, same mileages. You can budget."},
            {"k": "HYBRID BAT.", "v": "MONITOR", "u": "Past 150k, plan for refurb. Health checks catch it."},
        ]}),
    ("e_pinned_photo", {"photo_url": P_VEZEL_E,
        "pins": [{"label": "A · LED HEADLAMP", "pos": "top:230px;left:120px;"}, {"label": "B · 16/17″ ALLOY", "pos": "top:400px;left:140px;"}, {"label": "C · ROOFLINE", "pos": "top:330px;right:140px;"}, {"label": "D · I-DCD HYBRID", "pos": "top:520px;right:160px;"}],
        "eyebrow": "Pin map · the Vezel, measured",
        "h1_html": "The Vezel,<br><span class='accent'>measured.</span>",
        "body_html": "27.4 km/L on the JC08 cycle. 152 PS combined system. <strong>~38,000 in service across SG.</strong> The most-popular B-segment SUV in the region."}),
    ("e_cta", {"h1_html": "Need a<br>Vezel<br><span class='accent'>service?</span>",
        "body_html": "Drop us a model year + mileage. We'll send a Vezel-specific quote with the right oil, coolant, and a hybrid battery health report."}),
]),

}
