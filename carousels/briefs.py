"""16 carousel content briefs. Maps queue id -> (mode_name, content_data dict).

Keep mode-default hero photos for V1 ship; Ed can swap per-topic photos in v2.
"""

# Verified working Unsplash URLs (mode defaults)
HERO_A = "https://images.unsplash.com/photo-1676018366904-c083ed678e60?w=1600&q=85"  # workshop+mechanic
HERO_B = "https://images.unsplash.com/photo-1597386601945-8980df52c3dc?w=1600&q=85"  # dashboard
HERO_C = "https://images.unsplash.com/photo-1650179172998-035ba1b497b9?w=1600&q=85"  # engine close-up
HERO_D = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=85"  # car at night
HERO_E = "https://images.unsplash.com/photo-1761040100230-8c8e6fc64638?w=1600&q=85"  # brake caliper


# ============================================================================
# BRIEF SET — keyed by queue id
# ============================================================================
BRIEFS = {

# --- COST OF WAITING — MODE B — Brake fluid ($80 → $3,400) ---
"newseries-cow-mode-b-2026-05-02-20": ("mode_b", {
    "eyebrow_top": "COST OF WAITING",
    "series_eyebrow": "DECODED BY THE RIGHT WORKSHOP",
    "hero_url": HERO_B,
    "chip": "$80 → $3,400",
    "hero_eyebrow": "BRAKE FLUID · DECODED",
    "hero_title_html": "$80 service.<br/><span style='color:#F4A93A;'>Skipped twice.</span>",
    "hero_body": "Brake fluid degrades on a schedule. Ignore it long enough and the disc warps, the caliper sticks, and the small bill becomes a big one.",

    "diag_eyebrow": "WHAT'S ACTUALLY HAPPENING",
    "diag_title_html": "Fluid <span class='accent'>fails</span> first.",
    "diag_left_num": "2 yrs",
    "diag_left_body": "Brake fluid absorbs water from the air. Boiling point drops. Brakes go spongy in heat.",
    "diag_right_title": "Then it spreads",
    "diag_right_body": "Wet fluid corrodes the caliper. Caliper sticks. Disc warps from uneven heat.",
    "diag_footer": "<strong>One skipped flush</strong> turns a $80 service into a $3,400 brake job.",

    "tier_eyebrow": "THE COST CURVE",
    "tier_title_html": "Service.<br/>Disc.<br/><span class='accent'>Caliper.</span>",
    "tier_rows": [
        {"range": "$80", "label": "ON SCHEDULE", "body": "Brake fluid flush every 2 years. Done in an hour.", "color": "#F4A93A"},
        {"range": "$420", "label": "DISC WARPED", "body": "Skipped one flush. Caliper held heat. Disc warped.", "color": "#EFE6D4"},
        {"range": "$3,400", "label": "FULL REBUILD", "body": "Skipped twice. Caliper seized, disc + pads + lines.", "color": "#C73E2C"},
    ],

    "cost_eyebrow": "PRICE OF NOT WAITING",
    "cost_title_html": "Flush now,<br/>or rebuild later.",
    "cost_left_label": "FLUSH ON TIME",
    "cost_left_amt": "$80",
    "cost_left_body": "Brake fluid flush every 2 years. Drive home the same day. No drama.",
    "cost_right_label": "REBUILT TWICE",
    "cost_right_amt": "$3,400+",
    "cost_right_body": "New disc, new caliper, new pads, new lines. Tow if it locks up.",
    "cost_note": "Free brake-fluid moisture test when you book.",

    "cta_eyebrow": "BOOK YOUR BRAKE FLUID FLUSH",
    "cta_title_html": "Service on time.<br/><span class='accent'>Pay once.</span>",
}),

# --- DRIVER'S MANUAL — MODE A — What I wish I knew at 23 ---
"newseries-dm-mode-a-2026-05-03-11": ("mode_a", {
    "eyebrow_top": "DRIVER'S MANUAL",
    "hero_url": HERO_A,
    "chip": "5 LESSONS",
    "sub": "BEFORE YOU SIGN THE PAPERS",
    "title_html": "What I wish<br/>I knew <span class='accent'>at 23.</span>",
    "body_html": "COE expires. Tyres age out. Service stamps matter at resale. <strong>Five things every first-time driver should know</strong> before signing the loan papers.",

    "items": [
        {"label": "LESSON ONE", "num": "01", "title_html": "COE is<br/><span class='accent'>not magic.</span>",
         "body": "It's a 10-year permit. The car can outlast it physically. Plan the year-9 decision now, not at year-10.",
         "watch": "Most owners forget COE renewal pricing — it can double the car's running cost."},
        {"label": "LESSON TWO", "num": "02", "title_html": "Tyres<br/><span class='accent'>age out.</span>",
         "body": "Even with low mileage, rubber hardens after 5–6 years. Sidewall cracks before tread wears.",
         "watch": "Watch for: \"plenty of tread left\" — that's a tread reading, not an age reading."},
        {"label": "LESSON THREE", "num": "03", "title_html": "Service stamps<br/><span class='accent'>matter.</span>",
         "body": "At resale, a complete service book adds $1,500–$3,000 vs no records. Keep every receipt.",
         "watch": "Workshops with proper book stamps cost a little more. Worth it at trade-in."},
    ],

    "tell_eyebrow": "THE LESSON",
    "tell_title_html": "The cheap parts<br/>aren't <span class='accent'>the cheap parts.</span>",
    "tell_body_html_1": "First-time drivers focus on monthly payments. Five-year owners focus on total cost — fuel, service, COE, resale.",
    "tell_body_html_2": "<strong>The cheapest car is the one you understood before you signed.</strong>",

    "cta_eyebrow": "SAVE THIS · BOOK YOUR PRE-DECISION CHECK",
    "cta_title_html": "Bookmark<br/>this for your<br/><span class='accent'>next car.</span>",
}),

# --- BEHIND THE BADGE — VEZEL — MODE A ---
"newseries-bbtb-vezel-mode-a-2026-05-03-20": ("mode_a", {
    "eyebrow_top": "BEHIND THE BADGE",
    "hero_url": HERO_A,
    "chip": "HONDA VEZEL",
    "sub": "HONEST TAKE",
    "title_html": "Honda Vezel.<br/><span class='accent'>Honest</span> take.",
    "body_html": "The hybrid sips fuel. The CVT cabin is quiet. <strong>But the rear wheel bearings start whining around 80,000 km</strong>, and the infotainment is dated. Buy it for the running cost. Budget for the bearings.",

    "items": [
        {"label": "WHAT WORKS", "num": "01", "title_html": "Fuel<br/><span class='accent'>economy.</span>",
         "body": "Hybrid drivetrain regularly returns 18–22 km/L in Singapore traffic. Half the running cost of a petrol-only SUV.",
         "watch": "Watch for: hybrid battery health beyond 150,000 km — get a battery report at every service."},
        {"label": "WHAT WORKS", "num": "02", "title_html": "Cabin<br/><span class='accent'>comfort.</span>",
         "body": "CVT is whisper-quiet at city speeds. Rear seats fold flat. Resale stays strong year on year.",
         "watch": "Watch for: brake regen feel — slightly grabby; not a fault, just the system."},
        {"label": "WHAT FAILS", "num": "03", "title_html": "Rear<br/><span class='accent'>bearings.</span>",
         "body": "Whining noise starts around 80,000 km. Loudest at 60–80 km/h on smooth roads. Plan a $400 per-side bearing job.",
         "watch": "Watch for: a noise that disappears in a corner — that's the bearing, not the tyre."},
    ],

    "tell_eyebrow": "THE TELL",
    "tell_title_html": "Buy for the<br/>running cost.<br/><span class='accent'>Budget for bearings.</span>",
    "tell_body_html_1": "The Vezel is a smart choice for a Singapore driver who wants a hybrid SUV without paying European prices.",
    "tell_body_html_2": "<strong>It is not maintenance-free.</strong> But it is predictable, and predictable is what cheap-to-own actually means.",

    "cta_eyebrow": "SERVICING A VEZEL? · WE SEE THEM EVERY WEEK",
    "cta_title_html": "Drop us a<br/><span class='accent'>message.</span>",
}),

# --- WARNING LIGHT — MODE C — Check engine light ---
"newseries-wl-mode-c-2026-05-04-11": ("mode_c", {
    "eyebrow_top": "WARNING LIGHT DECODED",
    "hero_url": HERO_C,
    "hero_chip": "$30 → $3,000",
    "hero_eyebrow": "CHECK ENGINE · DECODED",
    "hero_title_html": "Check<br/>engine.<br/>Don't<br/><span class='accent'>panic.</span>",
    "hero_body": "It can be a $30 oxygen sensor or a $3,000 catalytic converter. <strong>The OBD scanner tells the difference in two minutes.</strong>",

    "tl_eyebrow": "STEADY VS FLASHING",
    "tl_title_html": "Read the<br/><span class='accent'>colour first.</span>",
    "tl_rows": [
        {"label": "STEADY", "label_body": "YOU HAVE TIME", "body": "Drive normally. Book a scan within the week. Most steady codes are sensor-related.", "accent": False},
        {"label": "FLASHING", "label_body": "PULL OVER", "body": "Misfire detected. Continued driving cooks the catalyst. Stop, tow, scan.", "accent": True},
        {"label": "ON + OFF", "label_body": "INTERMITTENT", "body": "A loose gas cap can do this. Tighten, drive 2 cycles, light may clear itself.", "accent": False},
    ],

    "cost_eyebrow": "THE COST CURVE",
    "cost_title_html": "$30 sensor.<br/><span class='accent'>$3,000 cat.</span>",
    "cost_left_label": "QUICK FIX",
    "cost_left_amt": "$30",
    "cost_left_body": "O₂ sensor or gas cap. Plug-and-play. Light clears, drive on.",
    "cost_right_label": "WORST CASE",
    "cost_right_amt": "$3,000",
    "cost_right_body": "Catalytic converter melt. Misfire ignored too long. Replace cat + plugs + coils.",
    "cost_note": "Free OBD diagnostic when you book.",

    "list_eyebrow": "WHAT WE READ FIRST",
    "list_title_html": "Read the<br/><span class='accent'>code.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>P0420 / P0430</strong> — catalyst efficiency. Sensor or cat-related. Often sensor first."},
        {"n": "2", "body": "<strong>P0171 / P0174</strong> — fuel mixture too lean. Vacuum leak or MAF sensor."},
        {"n": "3", "body": "<strong>P0300 series</strong> — misfire codes. Plugs, coils, injectors. Pull over if light flashes."},
        {"n": "4", "body": "<strong>P0440 / P0455</strong> — evaporative system. Often a loose gas cap. Cheap fix."},
    ],

    "rule_eyebrow": "THE RULE",
    "rule_title_html": "2 mins.",
    "rule_sub": "the OBD scanner tells the difference.",
    "rule_body_1": "A $30 fault and a $3,000 fault display the same warning light. The scanner is the only thing that knows which one you have.",
    "rule_body_2": "<strong>Free diagnostic when you book.</strong>",

    "cta_eyebrow": "BOOK A FREE OBD SCAN",
    "cta_title_html": "Don't guess.<br/><span class='accent'>Scan.</span>",
}),

# --- STRAIGHT TALK — MODE C — Bring receipts ---
"newseries-st-mode-c-2026-05-04-15": ("mode_c", {
    "eyebrow_top": "STRAIGHT TALK",
    "hero_url": HERO_C,
    "hero_chip": "BRING RECEIPTS",
    "hero_eyebrow": "BEFORE YOU SAY YES",
    "hero_title_html": "Bring<br/>receipts.<br/>Walk away<br/><span class='accent'>clean.</span>",
    "hero_body": "Get the quote in writing. Ask for the part number. Compare with one other shop. <strong>If the workshop refuses to quote, that is the quote.</strong>",

    "tl_eyebrow": "THE 3 ASKS",
    "tl_title_html": "Three asks.<br/><span class='accent'>One quote.</span>",
    "tl_rows": [
        {"label": "ASK 1", "label_body": "QUOTE IN WRITING", "body": "On a printed slip or PDF, not on a napkin. Itemised. Dated.", "accent": False},
        {"label": "ASK 2", "label_body": "PART NUMBER", "body": "Brand and OEM number. So you can verify it's the right part for your VIN.", "accent": False},
        {"label": "ASK 3", "label_body": "SECOND OPINION", "body": "Send the quote to one other workshop. 30-second sanity check.", "accent": True},
    ],

    "cost_eyebrow": "THE PRICE OF NOT ASKING",
    "cost_title_html": "Receipt now.<br/><span class='accent'>Argument later.</span>",
    "cost_left_label": "WITH RECEIPT",
    "cost_left_amt": "$0",
    "cost_left_body": "Cost to ask. Honest workshops want you to compare — they win on transparency.",
    "cost_right_label": "WITHOUT",
    "cost_right_amt": "$300+",
    "cost_right_body": "Average markup on undocumented quotes. Plus the dispute when something fails early.",
    "cost_note": "If a workshop refuses to put the quote in writing, that is the quote.",

    "list_eyebrow": "RED FLAGS · WALK AWAY IF YOU SEE THESE",
    "list_title_html": "Four<br/><span class='accent'>red flags.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>\"Trust me, fair price.\"</strong> Trust is built with paperwork, not adjectives."},
        {"n": "2", "body": "<strong>\"Original brand.\"</strong> Ask which brand. \"Original\" is not a brand."},
        {"n": "3", "body": "<strong>One round number for everything.</strong> Real quotes itemise parts vs labour vs consumables."},
        {"n": "4", "body": "<strong>\"We already disposed of the old part.\"</strong> Honest shops keep it for you to inspect."},
    ],

    "rule_eyebrow": "THE RULE",
    "rule_title_html": "In writing.",
    "rule_sub": "or it's not a quote.",
    "rule_body_1": "An honest workshop wants their quote on paper. They want you to compare. They want the second opinion to confirm them.",
    "rule_body_2": "<strong>The shop afraid of comparison is the shop you should compare with someone else.</strong>",

    "cta_eyebrow": "WANT A SECOND-OPINION QUOTE?",
    "cta_title_html": "Send us<br/>the receipt.<br/><span class='accent'>We'll check.</span>",
}),

# --- DRIVER'S MANUAL — MODE B — Read the dipstick ---
"newseries-dm-mode-b-2026-05-05-11": ("mode_b", {
    "eyebrow_top": "DRIVER'S MANUAL",
    "series_eyebrow": "DECODED BY THE RIGHT WORKSHOP",
    "hero_url": HERO_B,
    "chip": "2 MIN HABIT",
    "hero_eyebrow": "DIPSTICK · DECODED",
    "hero_title_html": "Read the dipstick.<br/><span style='color:#F4A93A;'>Read the future.</span>",
    "hero_body": "Pull it out. Wipe. Dip again. <strong>The dipstick tells you what the dashboard cannot.</strong> Two-minute habit. Saves engines.",

    "diag_eyebrow": "WHAT YOU'RE READING",
    "diag_title_html": "Three <span class='accent'>signals.</span><br/>Two minutes.",
    "diag_left_num": "Level",
    "diag_left_body": "Should sit between the MIN and MAX marks. Low = leak or burn. High = dangerous, can warp seals.",
    "diag_right_title": "Colour & feel",
    "diag_right_body": "Golden-amber and slick = healthy. Black and gritty = overdue. Milky = coolant in the oil.",
    "diag_footer": "<strong>The dipstick reads the engine's health.</strong> The dashboard only reports failure.",

    "tier_eyebrow": "READ THE COLOUR",
    "tier_title_html": "What the<br/>colour <span class='accent'>tells you.</span>",
    "tier_rows": [
        {"range": "Amber", "label": "HEALTHY", "body": "Golden-amber, slightly translucent. Drive normally. Service at the next interval.", "color": "#F4A93A"},
        {"range": "Black", "label": "OVERDUE", "body": "Coal-black, opaque. Additives spent, sludge forming. Book a service this week.", "color": "#EFE6D4"},
        {"range": "Milky", "label": "COOLANT MIX", "body": "Cream-tan colour. Coolant leaking into oil. Stop driving. Book diagnostic now.", "color": "#C73E2C"},
    ],

    "cost_eyebrow": "PRICE OF KNOWING",
    "cost_title_html": "Two minutes.<br/><span class='accent'>Or a rebuild.</span>",
    "cost_left_label": "READ IT MONTHLY",
    "cost_left_amt": "2 min",
    "cost_left_body": "30-second habit while filling fuel. Catches every level + colour change before it kills the engine.",
    "cost_right_label": "DON'T READ IT",
    "cost_right_amt": "$8,000",
    "cost_right_body": "Engine seizure from running low or contaminated. By the time the dashboard knows, the damage is done.",
    "cost_note": "Free dipstick reading on every TRW visit — bring it in if unsure.",

    "cta_eyebrow": "TWO-MINUTE HABIT · SAVES ENGINES",
    "cta_title_html": "Read it<br/>this week.<br/><span class='accent'>Every week.</span>",
}),

# --- BEHIND THE BADGE — VEZEL — MODE B ---
"newseries-bbtb-vezel-mode-b-2026-05-05-20": ("mode_b", {
    "eyebrow_top": "BEHIND THE BADGE",
    "series_eyebrow": "DECODED BY THE RIGHT WORKSHOP",
    "hero_url": HERO_B,
    "chip": "HONDA VEZEL",
    "hero_eyebrow": "VEZEL HYBRID · THE HONEST LIST",
    "hero_title_html": "What works.<br/><span style='color:#F4A93A;'>What fails.</span>",
    "hero_body": "Vezel hybrid. <strong>What works:</strong> the fuel economy, the boot space, the resale price. <strong>What fails:</strong> rear wheel bearings, infotainment, hybrid battery beyond 150,000 km. Know before you buy.",

    "diag_eyebrow": "ECONOMY",
    "diag_title_html": "The case <span class='accent'>for</span><br/>buying one.",
    "diag_left_num": "18-22",
    "diag_left_body": "km/L in real Singapore traffic. Half the fuel cost of a petrol SUV.",
    "diag_right_title": "Resale strong",
    "diag_right_body": "Holds value year on year. Hybrid stigma is gone — buyers actively seek them.",
    "diag_footer": "<strong>The Vezel is a sensible buy.</strong> Just don't pretend it's bullet-proof.",

    "tier_eyebrow": "WHAT FAILS · BY MILEAGE",
    "tier_title_html": "Plan for these.<br/><span class='accent'>They're coming.</span>",
    "tier_rows": [
        {"range": "80k", "label": "REAR BEARINGS", "body": "Whining at 60–80 km/h. Plan ~$400 per side. Don't ignore — bearings can seize.", "color": "#F4A93A"},
        {"range": "120k", "label": "BRAKE HOSES", "body": "Coastal humidity rusts them. Soft pedal feel. Replace as a pair.", "color": "#EFE6D4"},
        {"range": "150k+", "label": "HYBRID BATTERY", "body": "Capacity drop. Get a battery health report. $2,800 to refurbish, $4,500 new.", "color": "#C73E2C"},
    ],

    "cost_eyebrow": "TOTAL COST OF OWNERSHIP",
    "cost_title_html": "Buy smart.<br/><span class='accent'>Maintain smarter.</span>",
    "cost_left_label": "ON SCHEDULE",
    "cost_left_amt": "$1,200/yr",
    "cost_left_body": "Hybrid service, brake fluid, oil. Plus 1 bigger ticket every 30k km.",
    "cost_right_label": "IGNORED",
    "cost_right_amt": "$5,000+",
    "cost_right_body": "Bearing failure, hybrid battery degradation, brake corrosion. All compound.",
    "cost_note": "We service Vezels every week — message us for a Vezel-specific quote.",

    "cta_eyebrow": "SERVICING A VEZEL?",
    "cta_title_html": "Send us a<br/><span class='accent'>message.</span>",
}),

# --- WARNING LIGHT — MODE D — I drove on the red light ---
"newseries-wl-mode-d-2026-05-06-11": ("mode_d", {
    "eyebrow_top": "WARNING LIGHT DECODED",
    "hero_photo": HERO_D,
    "hero_caption": "Stranded · 11 pm · home, 2 km away",
    "hero_sticky_html": "Coolant temp light.<br/>Drove ten more minutes.<br/><strong>New head gasket: $2,800.</strong>",
    "hero_eyebrow": "GUEST DIARY · LAST FRIDAY",
    "hero_title_html": "I drove on<br/>the <span class='accent'>red light.</span>",
    "hero_body": "Coolant temp glowed for ten minutes. I thought I could make it home. <strong>I did not.</strong> New head gasket: $2,800. The light was not the warning. It was the verdict.",

    "grid_eyebrow": "THE TEN MINUTES I IGNORED",
    "grid_title_html": "Ten minutes.<br/>One <span class='accent'>head gasket.</span>",
    "grid_items": [
        {"label": "amber light first", "sublabel": "min 0–3 · safe", "color": "#F4D960"},
        {"label": "red light at min 4", "sublabel": "min 4 · pull over now", "color": "#F4A93A"},
        {"label": "steam at min 10", "sublabel": "min 10 · too late", "color": "#C73E2C"},
    ],
    "grid_body": "<strong>Heat damage compounds in seconds.</strong> Past the red line, every minute warps something different.",

    "inv_eyebrow": "THE INVOICE I DID NOT WANT",
    "inv_title_html": "What ten<br/>minutes <span class='accent'>cost.</span>",
    "inv_rows": [
        {"label": "Head gasket kit", "amt": "$520"},
        {"label": "Machining + skim", "amt": "$680"},
        {"label": "Labour (12 hrs)", "amt": "$1,200"},
        {"label": "Coolant + fluids", "amt": "$220"},
        {"label": "Tow + diagnostic", "amt": "$180"},
    ],
    "inv_total_amt": "$2,800",
    "inv_body": "If I had pulled over at minute four, the bill would have been $80 of coolant.",

    "list_eyebrow": "FOUR SIGNS · I IGNORED ALL OF THEM",
    "list_title_html": "Small signals.<br/><span class='accent'>Big bills.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>Temp gauge creeping past mid-line.</strong> Cooling system can't keep up."},
        {"n": "2", "body": "<strong>Sweet smell from the vents.</strong> Coolant leaking onto a hot surface."},
        {"n": "3", "body": "<strong>White smoke from the exhaust.</strong> Coolant entering the cylinders."},
        {"n": "4", "body": "<strong>Heater blows cold even when set to hot.</strong> Coolant level too low to circulate."},
    ],

    "lesson_eyebrow": "THE LESSON",
    "lesson_title_html": "When the temp light<br/>comes on,<br/><span class='accent'>pull over.</span>",
    "lesson_body_1": "Engines tolerate a lot — under-fuelling, hard driving, missed services. They do not tolerate overheating.",
    "lesson_body_2": "— A guest diary from a customer who said we could share his story so someone else doesn't repeat it.",

    "cta_eyebrow": "FREE COOLING SYSTEM CHECK",
    "cta_title_html": "If the temp<br/>light is on,<br/><span class='accent'>pull over.</span>",
}),

# --- STRAIGHT TALK — MODE D — 4-line honest test ---
"newseries-st-mode-d-2026-05-06-15": ("mode_d", {
    "eyebrow_top": "STRAIGHT TALK",
    "hero_photo": HERO_D,
    "hero_caption": "On the bench · before you say yes",
    "hero_sticky_html": "Show the part.<br/>Show the wear.<br/>Show the spec.<br/><strong>Show the price.</strong>",
    "hero_eyebrow": "THE 4-LINE HONEST TEST",
    "hero_title_html": "Save this.<br/>Use it before<br/>any <span class='accent'>quote.</span>",
    "hero_body": "Four asks. Honest workshops answer all four. <strong>Save this for your next quote.</strong>",

    "grid_eyebrow": "THE FOUR LINES",
    "grid_title_html": "Four asks.<br/><span class='accent'>One yes.</span>",
    "grid_items": [
        {"label": "show the part", "sublabel": "old + new on the bench", "color": "#1A1A1A"},
        {"label": "show the wear", "sublabel": "what failed and why", "color": "#1A1A1A"},
        {"label": "show the price", "sublabel": "itemised, in writing", "color": "#C73E2C"},
    ],
    "grid_body": "<strong>Honest workshops welcome the questions.</strong> Upsell shops change the topic.",

    "inv_eyebrow": "WHAT AN HONEST QUOTE LOOKS LIKE",
    "inv_title_html": "Itemised.<br/><span class='accent'>Always.</span>",
    "inv_rows": [
        {"label": "Brake pads (OEM)", "amt": "$220"},
        {"label": "Pad fitting kit", "amt": "$45"},
        {"label": "Labour (1.5 hrs)", "amt": "$120"},
        {"label": "Brake fluid top-up", "amt": "$28"},
    ],
    "inv_total_amt": "$413",
    "inv_body": "Round numbers without itemisation are not quotes. They are guesses with confidence.",

    "list_eyebrow": "DODGE PATTERNS · WALK AWAY IF YOU HEAR ANY",
    "list_title_html": "Four lies.<br/>Four <span class='accent'>walk-aways.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>\"We already disposed of the old part.\"</strong> Honest shops save it for you to see."},
        {"n": "2", "body": "<strong>\"All the same lah.\"</strong> Brand and grade always matter — that's why they exist."},
        {"n": "3", "body": "<strong>\"Trust me, good price.\"</strong> Trust is built with paperwork, not promises."},
        {"n": "4", "body": "<strong>\"Pay first, I tell you what's wrong.\"</strong> Diagnostic comes before quote, not the other way around."},
    ],

    "lesson_eyebrow": "THE LESSON",
    "lesson_title_html": "Four asks.<br/>Four <span class='accent'>answers.</span>",
    "lesson_body_1": "A workshop that can show the part, the wear, the spec, and the price is a workshop. A workshop that cannot is a sales floor with a hoist.",
    "lesson_body_2": "<strong>Save this card. Use it before your next quote.</strong>",

    "cta_eyebrow": "WANT A SECOND-OPINION QUOTE?",
    "cta_title_html": "Send us<br/>your quote.<br/><span class='accent'>We'll check.</span>",
}),

# --- DRIVER'S MANUAL — MODE C — On the PIE watch the gauges ---
"newseries-dm-mode-c-2026-05-07-11": ("mode_c", {
    "eyebrow_top": "DRIVER'S MANUAL",
    "hero_url": HERO_C,
    "hero_chip": "PRE-TRIP READY",
    "hero_eyebrow": "ON THE PIE · WATCH THE GAUGES",
    "hero_title_html": "Long pulls.<br/><span class='accent'>Weak parts.</span><br/>Revealed.",
    "hero_body": "Coolant temp creeping up. Oil pressure dropping. RPM spiking. <strong>The expressway exposes weak parts.</strong> Long pulls reveal what short trips hide.",

    "tl_eyebrow": "THE 3 GAUGES THAT MATTER",
    "tl_title_html": "Three<br/><span class='accent'>gauges.</span><br/>Three signals.",
    "tl_rows": [
        {"label": "TEMP", "label_body": "COOLANT", "body": "Stays in the middle. If it creeps past two-thirds on a flat road, cooling system is struggling.", "accent": False},
        {"label": "OIL", "label_body": "PRESSURE", "body": "Drops a little when warm — normal. Drops below the marker line — pull off, check level.", "accent": True},
        {"label": "RPM", "label_body": "TACHOMETER", "body": "Sudden spikes at steady speed = transmission slipping. CVT belts and torque converters fail this way.", "accent": False},
    ],

    "cost_eyebrow": "PRE-TRIP CHECK",
    "cost_title_html": "$80 now.<br/><span class='accent'>$3,000 stranded.</span>",
    "cost_left_label": "PRE-TRIP",
    "cost_left_amt": "$80",
    "cost_left_body": "Coolant level + oil + tyres + battery test. Done in 30 minutes before a long drive.",
    "cost_right_label": "STRANDED",
    "cost_right_amt": "$3,000+",
    "cost_right_body": "Tow off the expressway + transmission rebuild + lost weekend.",
    "cost_note": "Long-drive ready? Book a pre-trip check.",

    "list_eyebrow": "BEFORE THE PIE · 4-MIN CHECKLIST",
    "list_title_html": "Four<br/><span class='accent'>checks.</span><br/>Four minutes.",
    "list_items": [
        {"n": "1", "body": "<strong>Coolant reservoir level.</strong> Between MIN and MAX. Cold engine only."},
        {"n": "2", "body": "<strong>Oil dipstick.</strong> Pull. Wipe. Dip. Should sit at the upper mark."},
        {"n": "3", "body": "<strong>Tyre pressure all four + spare.</strong> Cold pressure as per door sticker."},
        {"n": "4", "body": "<strong>Brake feel on the slip road.</strong> Pedal should feel firm, not spongy."},
    ],

    "rule_eyebrow": "THE RULE",
    "rule_title_html": "Glance.",
    "rule_sub": "every 30 km, check the gauges.",
    "rule_body_1": "On the expressway, your eyes go further down the road. Every 30 km, drag them back to the dashboard for a half-second check.",
    "rule_body_2": "<strong>That half-second is the cheapest insurance you'll ever buy.</strong>",

    "cta_eyebrow": "BOOK A PRE-TRIP CHECK",
    "cta_title_html": "Long drive?<br/><span class='accent'>Quick check.</span>",
}),

# --- BEHIND THE BADGE — VEZEL — MODE C ---
"newseries-bbtb-vezel-mode-c-2026-05-07-20": ("mode_c", {
    "eyebrow_top": "BEHIND THE BADGE",
    "hero_url": HERO_C,
    "hero_chip": "HONDA VEZEL",
    "hero_eyebrow": "FIND THE RIGHT WORKSHOP",
    "hero_title_html": "Right car.<br/>Right<br/><span class='accent'>workshop.</span>",
    "hero_body": "Hybrid systems need workshops that understand them. <strong>Wrong hands, wrong parts, wrong diagnosis.</strong> We service Vezels every week. We know what wears, when, and what to do.",

    "tl_eyebrow": "WHAT VEZEL OWNERS GET WRONG",
    "tl_title_html": "Same car.<br/><span class='accent'>Different</span> mistakes.",
    "tl_rows": [
        {"label": "WRONG OIL", "label_body": "0W-20 ONLY", "body": "Vezel hybrid demands 0W-20 synthetic. Generic 5W-30 hurts fuel economy + thermal limits.", "accent": False},
        {"label": "WRONG COOLANT", "label_body": "TYPE 2 BLUE", "body": "Honda Type 2 only. Mixing green or pink coolant clogs the hybrid radiator within a year.", "accent": True},
        {"label": "WRONG SCAN", "label_body": "HONDA HDS", "body": "Generic OBD reads engine codes only. Hybrid system needs Honda HDS to read battery + inverter.", "accent": False},
    ],

    "cost_eyebrow": "WORKSHOP MATCH MATTERS",
    "cost_title_html": "Right shop.<br/><span class='accent'>Right cost.</span>",
    "cost_left_label": "HYBRID-SAVVY",
    "cost_left_amt": "$420",
    "cost_left_body": "Vezel-specific service. Right oil. Right coolant. Hybrid battery report included.",
    "cost_right_label": "GENERIC SHOP",
    "cost_right_amt": "$1,200",
    "cost_right_body": "Wrong oil = future repair. Wrong scan = missed warning. You pay it back later.",
    "cost_note": "Servicing a Vezel? We see them every week.",

    "list_eyebrow": "ASK YOUR WORKSHOP",
    "list_title_html": "Four<br/><span class='accent'>questions.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>Do you stock 0W-20 Honda spec?</strong> Not just a 0W-20 from any brand."},
        {"n": "2", "body": "<strong>Do you have Honda HDS or equivalent?</strong> Or just a generic scanner."},
        {"n": "3", "body": "<strong>Can you do a hybrid battery health report?</strong> Should be standard on a Vezel."},
        {"n": "4", "body": "<strong>Have you replaced rear bearings on a Vezel before?</strong> Vezel-specific knowledge matters."},
    ],

    "rule_eyebrow": "THE RULE",
    "rule_title_html": "Vezel-savvy.",
    "rule_sub": "or generic — there is no \"close enough.\"",
    "rule_body_1": "Hybrid drivetrains are unforgiving. Wrong oil viscosity costs you fuel economy. Wrong coolant clogs the radiator. Wrong scanner misses the early signal.",
    "rule_body_2": "<strong>Find a workshop that knows your specific car. Not a generalist.</strong>",

    "cta_eyebrow": "BOOK A VEZEL SERVICE",
    "cta_title_html": "Drop us<br/>a Vezel<br/><span class='accent'>message.</span>",
}),

# --- STRAIGHT TALK — MODE E — Honest vs upsell side by side ---
"newseries-st-mode-e-2026-05-13-11": ("mode_e", {
    "eyebrow_top": "STRAIGHT TALK",
    "file_meta": "<span>FILE / ST.QUOTE.COMPARE</span><span style='opacity:1;'>SEVERITY / HIGH</span><span>ACTION / GET 2 QUOTES</span><span>USE / BEFORE PAY</span>",
    "file_subtitle": "Honest workshop vs upsell workshop.",
    "hero_url": HERO_E,
    "pins": [
        {"label": "A", "desc": "OEM PART", "pos": "top:30px;left:50px;", "desc_pos": "top:30px;left:96px;"},
        {"label": "B", "desc": "WEAR PATTERN", "pos": "top:140px;left:160px;", "desc_pos": "top:140px;left:206px;"},
        {"label": "C", "desc": "FAILURE POINT", "pos": "top:80px;right:80px;", "desc_pos": "top:80px;right:128px;"},
        {"label": "D", "desc": "INVOICE", "pos": "bottom:60px;right:140px;", "desc_pos": "bottom:60px;right:188px;"},
    ],
    "pic_eyebrow": "DECODED · QUOTE COMPARISON",
    "pic_title_html": "Same car. Same part.<br/><span class='accent'>Two quotes.</span>",
    "pic_body": "The honest workshop shows you the part. The upsell one tells you a story. <strong>Know the difference before you say yes.</strong>",

    "tab1_eyebrow": "QUOTE COMPARISON · BRAKE JOB",
    "tab1_title_html": "Read the<br/>quote, not<br/>the rumour.",
    "tab1_cols": ["Honest workshop", "Upsell workshop", "Diff"],
    "tab1_rows": [
        {"key": "A", "c1": "Pads", "c2": "OEM brand<br/>part number", "c3": "\"good brand\"<br/>no part number", "c4": "+verifiable"},
        {"key": "B", "c1": "Labour", "c2": "1.5 hrs<br/>itemised", "c3": "all-in lump<br/>no breakdown", "c4": "+itemised"},
        {"key": "C", "c1": "Old part", "c2": "shown to you<br/>on the bench", "c3": "\"already disposed\"", "c4": "+evidence"},
        {"key": "D", "c1": "Total", "c2": "$413<br/>printed receipt", "c3": "$680<br/>verbal only", "c4": "+saved $267"},
    ],

    "grid_eyebrow": "ASK BEFORE PAY",
    "grid_title_html": "Four asks.<br/><span class='accent'>Two minutes.</span>",
    "grid_cells": [
        {"label": "ASK 1", "big": "PART", "body": "Show me the new part. Show me the brand. Show me the OEM number.", "accent": False},
        {"label": "ASK 2", "big": "WEAR", "body": "Show me the old part. Show me where it failed. Tell me what caused it.", "accent": False},
        {"label": "ASK 3", "big": "PRICE", "body": "Itemise parts. Itemise labour. Itemise consumables. On paper.", "accent": False},
        {"label": "ASK 4", "big": "RECEIPT", "body": "Printed receipt. Dated. Signed. Workshop stamp.", "accent": True},
    ],

    "list_eyebrow": "DODGE PATTERNS · WALK AWAY IF YOU HEAR THESE",
    "list_title_html": "Four<br/><span class='accent'>red flags.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>\"All the same brand lah.\"</strong> No, brand and grade matter. Always."},
        {"n": "2", "body": "<strong>\"Pay first, scan first.\"</strong> Diagnostic before quote, not the other way."},
        {"n": "3", "body": "<strong>\"We disposed of the old part.\"</strong> Honest shops keep it for you to see."},
        {"n": "4", "body": "<strong>\"Trust me, fair price.\"</strong> Trust is built with paper, not adjectives."},
    ],

    "tab2_eyebrow": "WHAT TO SAVE FROM EVERY VISIT",
    "tab2_title_html": "Build your<br/><span class='accent'>service book.</span>",
    "tab2_cols": ["Document", "Why", "Resale value"],
    "tab2_rows": [
        {"key": "1", "c1": "Itemised receipt", "c2": "Proves what was done", "c3": "+$300 at trade-in"},
        {"key": "2", "c1": "Old part photo", "c2": "Verifies the work", "c3": "+$150 trust"},
        {"key": "3", "c1": "Workshop stamp", "c2": "Service book entry", "c3": "+$500 trade-in"},
        {"key": "4", "c1": "OEM part number", "c2": "Quality verifiable", "c3": "+future repairs"},
    ],

    "cta_eyebrow": "WANT A SECOND-OPINION QUOTE?",
    "cta_title_html": "Drop us<br/>your quote.<br/><span class='accent'>We'll check.</span>",
}),

# --- COST OF WAITING — MODE E — Service interval numbers ---
"newseries-cow-mode-e-2026-05-13-15": ("mode_e", {
    "eyebrow_top": "COST OF WAITING",
    "file_meta": "<span>FILE / COW.SERVICE.INTERVAL</span><span style='opacity:1;'>SEVERITY / MEDIUM</span><span>ACTION / SERVICE BY DATE</span><span>FREQ / ANNUAL</span>",
    "file_subtitle": "Manufacturer service intervals · summary card.",
    "hero_url": HERO_E,
    "pins": [
        {"label": "A", "desc": "ENGINE OIL", "pos": "top:30px;left:50px;", "desc_pos": "top:30px;left:96px;"},
        {"label": "B", "desc": "BRAKE FLUID", "pos": "top:140px;left:160px;", "desc_pos": "top:140px;left:206px;"},
        {"label": "C", "desc": "TIMING BELT", "pos": "top:80px;right:80px;", "desc_pos": "top:80px;right:128px;"},
        {"label": "D", "desc": "COOLANT", "pos": "bottom:60px;right:140px;", "desc_pos": "bottom:60px;right:188px;"},
    ],
    "pic_eyebrow": "DECODED · MAINTENANCE INTERVALS",
    "pic_title_html": "Forget these numbers.<br/><span class='accent'>Big problem.</span>",
    "pic_body": "Manufacturers publish service intervals because oils, belts and fluids degrade on a schedule. <strong>Forget them, and the cost curve goes vertical.</strong>",

    "tab1_eyebrow": "INTERVAL TABLE · SINGAPORE DRIVING",
    "tab1_title_html": "The numbers<br/>that matter.",
    "tab1_cols": ["Interval", "Trigger", "Skip cost"],
    "tab1_rows": [
        {"key": "A", "c1": "Engine oil", "c2": "7,500 km<br/>or 6 months", "c3": "First or second", "c4": "$8,000 rebuild"},
        {"key": "B", "c1": "Brake fluid", "c2": "2 yrs or<br/>40,000 km", "c3": "Either", "c4": "$3,400 caliper"},
        {"key": "C", "c1": "Timing belt", "c2": "100,000 km<br/>or 7 yrs", "c3": "Either", "c4": "$4,000 valves"},
        {"key": "D", "c1": "Coolant", "c2": "5 yrs or<br/>100,000 km", "c3": "Either", "c4": "$2,800 head"},
    ],

    "grid_eyebrow": "WHEN TO SERVICE · BY DRIVING STYLE",
    "grid_title_html": "Adjust by<br/><span class='accent'>conditions.</span>",
    "grid_cells": [
        {"label": "CITY MAINLY", "big": "EARLIER", "body": "Stop-go traffic ages oil faster. Service at 6,000 km, not 7,500.", "accent": False},
        {"label": "EXPRESSWAY", "big": "ON TIME", "body": "Highway driving is easier on engines. Stick to the manufacturer interval.", "accent": False},
        {"label": "SHORT TRIPS", "big": "EARLIER", "body": "Engine never reaches full temperature. Sludge builds. 5,000 km service.", "accent": False},
        {"label": "RIDESHARE", "big": "MUCH EARLIER", "body": "12+ hrs/day driving. Service every 4,000 km — engine works for a living.", "accent": True},
    ],

    "list_eyebrow": "WHY THE INTERVALS EXIST",
    "list_title_html": "Four<br/><span class='accent'>reasons.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>Engine oil oxidises.</strong> After 7,500 km, additives are spent and sludge starts forming."},
        {"n": "2", "body": "<strong>Brake fluid absorbs water.</strong> After 2 yrs, boiling point drops, brakes go spongy in heat."},
        {"n": "3", "body": "<strong>Timing belts harden.</strong> After 100,000 km, snap risk rises sharply — and it bends valves."},
        {"n": "4", "body": "<strong>Coolant pH shifts.</strong> Acidic coolant corrodes the radiator and water pump from inside."},
    ],

    "tab2_eyebrow": "SERVICE STAMPS = RESALE",
    "tab2_title_html": "Document<br/><span class='accent'>everything.</span>",
    "tab2_cols": ["Item", "What to keep", "Resale value"],
    "tab2_rows": [
        {"key": "1", "c1": "Oil change", "c2": "Itemised receipt", "c3": "+$300 trade-in"},
        {"key": "2", "c1": "Brake flush", "c2": "Workshop stamp", "c3": "+$200 trade-in"},
        {"key": "3", "c1": "Timing belt", "c2": "OEM part receipt", "c3": "+$1,500 trade-in"},
        {"key": "4", "c1": "Major service", "c2": "Full service book", "c3": "+$3,000 trade-in"},
    ],

    "cta_eyebrow": "BOOK YOUR NEXT SERVICE",
    "cta_title_html": "Service<br/>on schedule.<br/><span class='accent'>Always cheaper.</span>",
}),

# --- DRIVER'S MANUAL — MODE D — My first car 230k km ---
"newseries-dm-mode-d-2026-05-13-20": ("mode_d", {
    "eyebrow_top": "DRIVER'S MANUAL",
    "hero_photo": HERO_D,
    "hero_caption": "First car · 2008 Civic · 230,000 km",
    "hero_sticky_html": "Five lessons.<br/>Ten years.<br/><strong>Wish I'd known<br/>before I signed.</strong>",
    "hero_eyebrow": "GUEST DIARY · A DECADE WITH ONE CAR",
    "hero_title_html": "My first car.<br/>230,000 km.<br/>Many <span class='accent'>lessons.</span>",
    "hero_body": "COE expires. Tyres age out. Service stamps matter at resale. <strong>Five things every first-time driver should know</strong> before signing the loan papers.",

    "grid_eyebrow": "THE THREE THINGS THAT BIT ME FIRST",
    "grid_title_html": "Three lessons.<br/><span class='accent'>Three big bills.</span>",
    "grid_items": [
        {"label": "year 2 · tyres age out", "sublabel": "low mileage didn't matter", "color": "#1A1A1A"},
        {"label": "year 5 · timing belt", "sublabel": "$1,800 surprise", "color": "#1A1A1A"},
        {"label": "year 9 · COE call", "sublabel": "renew or scrap?", "color": "#C73E2C"},
    ],
    "grid_body": "<strong>Every car has a lifetime curve.</strong> The first surprise teaches you to plan the next one.",

    "inv_eyebrow": "WHAT 10 YEARS ACTUALLY COST",
    "inv_title_html": "First car.<br/><span class='accent'>Real numbers.</span>",
    "inv_rows": [
        {"label": "COE (10 yrs)", "amt": "$48,000"},
        {"label": "Servicing (annual)", "amt": "$12,000"},
        {"label": "Tyres (3 sets)", "amt": "$2,400"},
        {"label": "Big repairs", "amt": "$6,800"},
        {"label": "Insurance + road tax", "amt": "$18,000"},
    ],
    "inv_total_amt": "$87,200",
    "inv_body": "Plus the $58,000 I paid to buy it. <strong>Total over 10 years: $145,000 / 230,000 km = $0.63 per km.</strong>",

    "list_eyebrow": "FIVE LESSONS · IN ORDER OF IMPORTANCE",
    "list_title_html": "Five things<br/>I'd tell <span class='accent'>23-year-old me.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>The cheapest car is the one you understand.</strong> Buy what you can service, not what you can flex."},
        {"n": "2", "body": "<strong>Service stamps are money.</strong> Skip a stamp, lose $500 at resale. Every time."},
        {"n": "3", "body": "<strong>Plan the COE decision at year 8.</strong> Not at year 10. Not the day before expiry."},
        {"n": "4", "body": "<strong>Tyres age out before they wear out.</strong> Low-mileage car ≠ safe tyres."},
    ],

    "lesson_eyebrow": "THE LESSON",
    "lesson_title_html": "The car you<br/><span class='accent'>understand</span><br/>is the cheap one.",
    "lesson_body_1": "Owning a car for ten years is owning every system on it for ten years. The owner's manual is the most expensive book you'll never read.",
    "lesson_body_2": "— A guest diary from a 2008 Civic owner who sold his 230k-km baby last month and started over.",

    "cta_eyebrow": "BOOK YOUR FIRST-CAR HEALTH CHECK",
    "cta_title_html": "Bookmark<br/>this for your<br/><span class='accent'>next car.</span>",
}),

# --- BEHIND THE BADGE — VEZEL — MODE D ---
"newseries-bbtb-vezel-mode-d-2026-05-14-15": ("mode_d", {
    "eyebrow_top": "BEHIND THE BADGE",
    "hero_photo": HERO_D,
    "hero_caption": "Vezel · workshop · weekly visitor",
    "hero_sticky_html": "Bearings: 80k.<br/>Brake hose: 120k.<br/><strong>Hybrid battery: 150k+.</strong>",
    "hero_eyebrow": "VEZEL NOTES · FROM THE WORKSHOP FLOOR",
    "hero_title_html": "Vezel notes.<br/>From the<br/><span class='accent'>workshop floor.</span>",
    "hero_body": "Owners come in for the same things. <strong>Bearings around 80k. Brake hose corrosion in coastal areas. Hybrid battery health beyond 150k.</strong> Know what to ask for at your next service.",

    "grid_eyebrow": "THREE VEZELS · THREE STORIES",
    "grid_title_html": "Same car.<br/>Three<br/><span class='accent'>different bills.</span>",
    "grid_items": [
        {"label": "85k km · whining", "sublabel": "rear bearing · $400 fix", "color": "#1A1A1A"},
        {"label": "118k km · spongy", "sublabel": "brake hose · $260 fix", "color": "#1A1A1A"},
        {"label": "162k km · slow charge", "sublabel": "battery refurb · $2,800", "color": "#C73E2C"},
    ],
    "grid_body": "<strong>The Vezel is predictable.</strong> Predictable means you can budget. Budget means you don't get blindsided.",

    "inv_eyebrow": "TYPICAL 5-YEAR VEZEL OWNERSHIP",
    "inv_title_html": "What it<br/>actually <span class='accent'>costs.</span>",
    "inv_rows": [
        {"label": "Yearly servicing", "amt": "$1,200"},
        {"label": "Brake fluid (yr 2)", "amt": "$80"},
        {"label": "Bearings (yr 3-4)", "amt": "$800"},
        {"label": "Brake hoses (yr 5)", "amt": "$260"},
        {"label": "Hybrid health checks", "amt": "$200"},
    ],
    "inv_total_amt": "$7,540",
    "inv_body": "<strong>Plus fuel.</strong> Vezel hybrid does 18-22 km/L — half the running cost of a petrol SUV. Budget for the bearings, save on the fuel.",

    "list_eyebrow": "ASK AT YOUR NEXT SERVICE",
    "list_title_html": "Four<br/><span class='accent'>questions.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>Hybrid battery health report.</strong> State of charge, capacity, cell balance. Should be standard on Vezels."},
        {"n": "2", "body": "<strong>Rear wheel bearing inspection.</strong> Listen at 60-80 km/h on a smooth road. Easy catch."},
        {"n": "3", "body": "<strong>Brake hose visual.</strong> Look for surface corrosion. Coastal cars get it earlier."},
        {"n": "4", "body": "<strong>Honda HDS scan, not generic.</strong> Hybrid system needs the right diagnostic tool."},
    ],

    "lesson_eyebrow": "THE LESSON",
    "lesson_title_html": "Predictable.<br/>Not <span class='accent'>maintenance-free.</span>",
    "lesson_body_1": "The Vezel rewards owners who plan. Bearings come at 80k. Hybrid health needs checking past 150k. Brake fluid every 2 years. Same routine, year after year.",
    "lesson_body_2": "— Notes from servicing 200+ Vezels at TRW. Patterns repeat.",

    "cta_eyebrow": "SERVICING A VEZEL?",
    "cta_title_html": "We see them<br/><span class='accent'>weekly.</span>",
}),

# --- BEHIND THE BADGE — VEZEL — MODE E ---
"newseries-bbtb-vezel-mode-e-2026-05-14-20": ("mode_e", {
    "eyebrow_top": "BEHIND THE BADGE",
    "file_meta": "<span>FILE / BTB.VEZEL.SPEC</span><span style='opacity:1;'>HONDA / VEZEL HYBRID</span><span>YEARS / 2014-2024</span><span>SG / COMMON</span>",
    "file_subtitle": "Honda Vezel · the spec card.",
    "hero_url": HERO_E,
    "pins": [
        {"label": "A", "desc": "1.5L HYBRID", "pos": "top:30px;left:50px;", "desc_pos": "top:30px;left:96px;"},
        {"label": "B", "desc": "CVT", "pos": "top:140px;left:160px;", "desc_pos": "top:140px;left:206px;"},
        {"label": "C", "desc": "FRONT WHEEL DRIVE", "pos": "top:80px;right:80px;", "desc_pos": "top:80px;right:128px;"},
        {"label": "D", "desc": "REAR BEARINGS", "pos": "bottom:60px;right:140px;", "desc_pos": "bottom:60px;right:188px;"},
    ],
    "pic_eyebrow": "DECODED · HONDA VEZEL HYBRID",
    "pic_title_html": "The Vezel<br/><span class='accent'>spec card.</span>",
    "pic_body": "Engine: 1.5L hybrid. CVT. Front-wheel drive. <strong>Resale: strong. Running cost: low. Quirks: known.</strong>",

    "tab1_eyebrow": "SPEC SHEET · WHAT WEARS WHEN",
    "tab1_title_html": "Read the<br/>numbers.<br/>Plan ahead.",
    "tab1_cols": ["Mileage", "Common issue", "Fix range"],
    "tab1_rows": [
        {"key": "A", "c1": "60-80k", "c2": "Brake pads<br/>front", "c3": "$220 / pair", "c4": "wear by use"},
        {"key": "B", "c1": "80k", "c2": "Rear wheel<br/>bearings whining", "c3": "$400 / side", "c4": "common"},
        {"key": "C", "c1": "120k", "c2": "Brake hoses<br/>(coastal)", "c3": "$260 / pair", "c4": "humidity"},
        {"key": "D", "c1": "150k+", "c2": "Hybrid battery<br/>capacity drop", "c3": "$2,800 refurb", "c4": "monitor"},
    ],

    "grid_eyebrow": "OWNERSHIP MATRIX",
    "grid_title_html": "Buy for<br/>this. <span class='accent'>Plan</span> for that.",
    "grid_cells": [
        {"label": "FUEL ECONOMY", "big": "18-22", "body": "km/L in Singapore traffic. Half the running cost of a petrol SUV.", "accent": False},
        {"label": "RESALE", "big": "STRONG", "body": "Holds value year on year. Hybrid stigma is gone.", "accent": False},
        {"label": "REPAIRS", "big": "PREDICTABLE", "body": "Same wear items, same mileages. You can budget.", "accent": False},
        {"label": "HYBRID BATTERY", "big": "MONITOR", "body": "Past 150k, plan for refurb. Standard health checks catch it.", "accent": True},
    ],

    "list_eyebrow": "OWNERS GUIDE · 5-MIN VERSION",
    "list_title_html": "Five things<br/>to <span class='accent'>watch.</span>",
    "list_items": [
        {"n": "1", "body": "<strong>Listen at 60-80 km/h.</strong> Whining = rear wheel bearing. Catch early at 80k."},
        {"n": "2", "body": "<strong>Press the brake hard at idle.</strong> Spongy = brake hose. Common after coastal driving."},
        {"n": "3", "body": "<strong>Check fuel economy monthly.</strong> Sudden drop = hybrid battery starting to fade."},
        {"n": "4", "body": "<strong>0W-20 oil only.</strong> Honda spec. Generic 5W-30 hurts efficiency and longevity."},
    ],

    "tab2_eyebrow": "VEZEL SERVICE · 5-YEAR PLAN",
    "tab2_title_html": "Plan ahead.<br/><span class='accent'>Pay less.</span>",
    "tab2_cols": ["Year", "Service", "Cost"],
    "tab2_rows": [
        {"key": "1", "c1": "Yr 1-2", "c2": "Standard service", "c3": "$1,200 / yr"},
        {"key": "2", "c1": "Yr 2", "c2": "Brake fluid flush", "c3": "$80"},
        {"key": "3", "c1": "Yr 3-4", "c2": "Rear bearings", "c3": "$400 / side"},
        {"key": "4", "c1": "Yr 5+", "c2": "Hybrid battery health", "c3": "$200 / report"},
    ],

    "cta_eyebrow": "NEED A VEZEL SERVICE?",
    "cta_title_html": "Drop us<br/>a Vezel<br/><span class='accent'>message.</span>",
}),

}
