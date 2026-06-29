/**
 * [trw_related_reads] v2 — dynamic related-reads / glovebox strip with RELATED-FIRST.
 *
 * Single engine for related-reading across the whole site (blog articles + service pages).
 * Card design = "glovebox" (Design B): hero thumbnail when the article has a featured image,
 * otherwise the branded TRW-seal card (never a blank thumbnail). Each page keeps its own
 * section alignment/sizing — the shortcode only emits the card grid.
 *
 * RELATED-FIRST: every candidate is scored by how many topic pillars it shares with the
 * current page. The current page's pillars come from the `topics` attr (service pages) or
 * from the registry by the current page's own ID (blog articles). Cards render related-first
 * (highest shared-pillar count first) for SEO + no-JS; the client then reshuffles WITHIN each
 * equal-score tier so the visible set varies per visit but stays relevant. Falls back to pure
 * random when nothing shares a pillar.
 *
 * AUTO-PULL: the $REG registry (page id => [pillar slugs]) is rewritten by the daily cron
 * (trw-ig-scheduler/blog/refresh_related_reading.py) from the live /blog/ list + topic_tags.json,
 * so a newly published article appears automatically with no manual step. Do not hand-edit the
 * block between RR_REGISTRY_START / RR_REGISTRY_END — the cron owns it.
 *
 * Variants: rel (blog .rel-card, default) | reads (.read-card) | svc (service .ac sizing).
 * Attrs: show(3 visible) pool(8 candidates) variant topics("pillar pillar") force("nohero" preview).
 */
add_shortcode('trw_related_reads', function ($atts) {
    $a = shortcode_atts(array('show' => 3, 'pool' => 8, 'variant' => 'rel', 'topics' => '', 'force' => ''), $atts);
    $show = max(1, intval($a['show']));
    $pooln = max($show, intval($a['pool']));
    $variant = in_array($a['variant'], array('reads', 'svc'), true) ? $a['variant'] : 'rel';
    $force_nohero = ($a['force'] === 'nohero');
    $emblem = 'https://therightworkshop.com/wp-content/uploads/2026/06/trw-emblem-orange-seal.png';

    // ===== REGISTRY — cron-maintained, do not hand-edit between the markers =====
    // RR_REGISTRY_START
    $REG = array(
        965 => array('servicing', 'ownership'),
        966 => array('workshop'),
        967 => array('car-insurance', 'ownership'),
        1220 => array('used-car', 'workshop'),
        1221 => array('brakes', 'driving-tips'),
        1223 => array('servicing', 'ownership'),
        5720 => array('coe', 'scrap-or-export', 'ownership'),
        5726 => array('scrap-or-export', 'coe', 'ownership', 'selling-your-car'),
    );
    // RR_REGISTRY_END
    // ===========================================================================

    $cur = get_the_ID();

    // current page pillars: explicit attr (service pages) else registry (articles)
    $cur_topics = array();
    if ($a['topics'] !== '') {
        $cur_topics = array_values(array_filter(array_map('trim', preg_split('/[\s,]+/', $a['topics']))));
    } elseif (isset($REG[$cur])) {
        $cur_topics = $REG[$cur];
    }

    // candidate ids = registry minus the current page
    $ids = array_values(array_filter(array_keys($REG), function ($id) use ($cur) {
        return intval($id) !== intval($cur);
    }));

    // score by shared pillars, shuffle for intra-tier variety, then stable-ish sort score desc
    $scored = array();
    foreach ($ids as $id) {
        $tp = isset($REG[$id]) ? $REG[$id] : array();
        $scored[] = array('id' => $id, 'score' => count(array_intersect($cur_topics, $tp)));
    }
    shuffle($scored);
    usort($scored, function ($x, $y) { return $y['score'] - $x['score']; });
    $pick = array_slice($scored, 0, $pooln);

    // ---- render config per variant ----
    $gid = 'trwRR_' . $variant;
    if ($variant === 'reads') { $gridcls = 'reads-grid'; $cardcls = 'read-card'; }
    elseif ($variant === 'svc') { $gridcls = 'ac-articles-grid rr-svc-grid'; $cardcls = 'rb-card'; }
    else { $gridcls = 'rel-grid'; $cardcls = 'rel-card'; }

    $brand = '<span class="rr-lockup"><span class="rr-seal"><img src="' . esc_url($emblem) . '" alt=""></span>'
           . '<span class="rr-brand"><span class="l1">The</span><br><span class="l2">Right</span><br><span class="l3">Workshop</span></span></span>';
    $news_kw = array('coe', 'erp', 'parf', 'vep', 'licence', 'license', 'mandatory', 'rates', 'hits', 'climb', 'consultation', 'rebate', 'schedule', 'fees');

    $out = '<div class="' . $gridcls . '" id="' . $gid . '">';
    foreach ($pick as $row) {
        $id = $row['id']; $rk = intval($row['score']);
        $url = get_permalink($id); $title = get_the_title($id);
        if (!$url) { continue; }
        $img = $force_nohero ? '' : get_the_post_thumbnail_url($id, 'medium_large');
        $slug = (string) get_post_field('post_name', $id);
        $is_news = false;
        foreach ($news_kw as $kw) { if (strpos($slug, $kw) !== false) { $is_news = true; break; } }
        $eyebrow = $is_news ? 'News' : 'Guide';
        $blurb = '';
        if (has_excerpt($id)) { $blurb = get_the_excerpt($id); }
        else { $rm = get_post_meta($id, 'rank_math_description', true); if ($rm) { $blurb = $rm; } }
        $blurb = $blurb ? wp_trim_words($blurb, 18, '&hellip;') : '';
        $data = ' data-rk="' . $rk . '"';

        if ($variant === 'reads') {
            $body = '<div class="read-body"><p class="read-cat">' . $eyebrow . '</p><h4>' . esc_html($title) . '</h4>'
                  . ($blurb ? '<p class="read-excerpt">' . esc_html($blurb) . '</p>' : '') . '</div>';
            if ($img) {
                $out .= '<a class="read-card" href="' . esc_url($url) . '"' . $data . ' style="text-decoration:none;color:inherit;display:block">'
                      . '<img class="read-img" loading="lazy" decoding="async" src="' . esc_url($img) . '" alt="' . esc_attr($title) . '">' . $body . '</a>';
            } else {
                $out .= '<a class="read-card rr-nohero" href="' . esc_url($url) . '"' . $data . ' style="text-decoration:none;color:inherit">'
                      . '<span class="rr-bloom"></span>' . $brand . $body . '</a>';
            }
        } else {
            // rel + svc share the same body markup (eyebrow + title + blurb + byline)
            $ey = ($variant === 'svc') ? 'rb-eyebrow' : 'rel-eyebrow';
            $bd = ($variant === 'svc') ? 'rb-body' : 'rel-body';
            $body = '<div class="' . $bd . '"><div class="' . $ey . '">' . $eyebrow . '</div><h4>' . esc_html($title) . '</h4>'
                  . ($blurb ? '<p>' . esc_html($blurb) . '</p>' : '') . '<div class="meta">The Right Workshop</div></div>';
            if ($img) {
                $out .= '<a class="' . $cardcls . '" href="' . esc_url($url) . '"' . $data . '>'
                      . '<img loading="lazy" decoding="async" src="' . esc_url($img) . '" alt="' . esc_attr($title) . '">' . $body . '</a>';
            } else {
                $out .= '<a class="' . $cardcls . ' rr-nohero" href="' . esc_url($url) . '"' . $data . '>'
                      . '<span class="rr-bloom"></span>' . $brand . $body . '</a>';
            }
        }
    }
    $out .= '</div>';

    // no-JS: server order is already related-first; hide beyond $show
    $out .= '<style>#' . $gid . ' .' . $cardcls . ':nth-child(n+' . ($show + 1) . '){display:none !important}</style>';
    // client: sort by data-rk desc, shuffle WITHIN equal-rk tier, re-append (related-first + per-visit variety)
    $out .= '<script>(function(){var g=document.getElementById("' . $gid . '");if(!g)return;'
          . 'var c=Array.prototype.slice.call(g.querySelectorAll(".' . $cardcls . '"));'
          . 'var b={};c.forEach(function(n){var r=n.getAttribute("data-rk")||"0";(b[r]=b[r]||[]).push(n);});'
          . 'var ks=Object.keys(b).sort(function(a,d){return d-a;});'
          . 'ks.forEach(function(k){var a=b[k];for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}'
          . 'a.forEach(function(n){g.appendChild(n);});});})();</script>';

    // one-time CSS (seal card + svc card + image guards)
    static $css_done = false;
    if (!$css_done) {
        $css_done = true;
        $css = '<style id="trw-rr-css">'
          . '#trwRR_rel a.rel-card>img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;height:auto}'
          . '#trwRR_reads a.read-card .read-img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;height:auto}'
          . '.rr-svc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}'
          . '.rr-svc-grid .rb-card{display:block;background:#fff;border:1px solid #ecebe4;border-radius:16px;overflow:hidden;color:#0D0D0D;text-decoration:none;transition:transform .15s ease,border-color .15s ease}'
          . '.rr-svc-grid .rb-card:hover{transform:translateY(-2px);border-color:#EF5927}'
          . '.rr-svc-grid .rb-card>img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;height:auto}'
          . '.rr-svc-grid .rb-body{padding:20px 22px 22px}'
          . '.rr-svc-grid .rb-eyebrow{font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#EF5927;margin-bottom:8px}'
          . '.rr-svc-grid .rb-card h4{font-size:17px;font-weight:800;line-height:1.3;color:#0D0D0D;margin:0 0 10px}'
          . '.rr-svc-grid .rb-card p{font-size:13px;color:#666;line-height:1.5;margin:0 0 10px}'
          . '.rr-svc-grid .rb-card .meta{font-size:12px;color:#999;font-weight:500}'
          . '@media(max-width:760px){.rr-svc-grid{grid-template-columns:1fr}}'
          . 'a.rr-nohero{position:relative;background:#FAF8F4;display:flex;flex-direction:column;justify-content:flex-end;min-height:300px;overflow:hidden}'
          . '.rr-nohero .rr-bloom{position:absolute;right:-34px;bottom:-34px;width:128px;height:128px;border-radius:50%;background:#FBEAE3;z-index:1}'
          . ".rr-nohero .rr-bloom::after{content:'';position:absolute;inset:26px;border-radius:50%;background:#fff;opacity:.5}"
          . '.rr-nohero .rr-lockup{position:absolute;top:20px;left:20px;display:flex;align-items:center;gap:11px;z-index:3}'
          . '.rr-nohero .rr-seal{width:60px;height:60px;border-radius:50%;background:#fff;border:2px solid #EF5927;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 13px rgba(239,89,39,.16);flex:0 0 60px}'
          . '.rr-nohero .rr-seal img{width:40px;height:auto;aspect-ratio:auto;margin:0;display:block;max-width:40px}'
          . '.rr-nohero .rr-brand{font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;text-transform:uppercase;font-size:14px;line-height:1.04;letter-spacing:-.005em}'
          . '.rr-nohero .rr-brand .l1,.rr-nohero .rr-brand .l3{font-weight:700;color:#0D0D0D}'
          . '.rr-nohero .rr-brand .l2{font-weight:900;color:#EF5927}'
          . '.rr-nohero .read-body,.rr-nohero .rel-body,.rr-nohero .rb-body{position:relative;z-index:3}'
          . '</style>';
        $out = $css . $out;
    }
    return $out;
});
