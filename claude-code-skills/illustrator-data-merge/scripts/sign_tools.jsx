// sign_tools.jsx — 부스간판 세트 후반 작업 도구 (2026-10-21 부산 사이버보안 콘퍼런스에서 실측으로 다듬은 것).
// fill_template.jsx 를 먼저 불러야 한다(kids·bounds·collect·center·setText·placeImage 를 쓴다):
//   $.global.FT_NO_MAIN = true; $.evalFile(File(".../fill_template.jsx")); $.evalFile(File(".../sign_tools.jsx"));
// 들어 있는 것:
//   stSqueeze(w, opt)          정면 틀 → 좁은 틀(옆간판 2435 등)을 '잘라 당기기'로 만든다
//   stInfo(card)               간판 한 장의 번호·이름·글자·로고 요약 (전후 대조용)
//   stReorder(res, lastNames)  간판을 번호순으로 다시 놓는다(크기별 줄, 10장씩)
//   stTitle(layer, ...)        묶음 제목(이름 + 크기·재질·수량 줄)
//   stTwoFaceWing(layer, ...)  둥글게 양면 날개 = 한 면 그림 + 180도 돌린 한 면
// ExtendScript(ES3) 주의 — 전부 실측으로 터진 것: Array.indexOf 없음 · 겹친 삼항식(a?0:b?1:2) 오계산 →
// 구간 판정은 if 로 · 한 줄 코드 중간에 // 주석을 넣으면 뒤가 통째로 주석이 된다(test_tools.py 가 문법을 잡는다).

var ST_MM = 72 / 25.4;

// ── 잘라 당기기 ─────────────────────────────────────────────────────────────
// 늘이거나 줄이지(scale) 않는다. 두 세로선 cut1·cut2(간판 왼쪽 끝에서 mm)를 기준으로
// 가운데 구간은 D, 오른쪽 구간은 2D 만큼 왼쪽으로 옮긴다(D = (지금 폭 - 새 폭)/2).
// 구간을 가로지르는 선(테두리)은 꼭짓점만 옮겨 모서리 모양이 그대로 남는다. 배경 그림은 클리핑이 잘라 준다.
// cut 선은 제목 홈·글자·장식을 피해서 고른다(부산: 홈 115~185, 'AI시대' 글자 24~74 → cut 92·238).
// opt = { cut1, cut2, width(새 폭 mm), logo:[x0,x1], area:[x0,x1], tagScale(0~100, 왼쪽 작은 문구 축소, 없으면 안 함) }
function stClipOf(w) {
    var k = kids(w);
    for (var i = 0; i < k.length; i++)
        if (k[i].typename == "GroupItem" && k[i].clipped)
            for (var j = 0; j < k[i].pathItems.length; j++) if (k[i].pathItems[j].clipping) return k[i].pathItems[j];
    return null;
}
function stZone(x, x0, c1, c2) {
    var m = (x - x0) / ST_MM;
    if (m <= c1) return 0;
    if (m <= c2) return 1;
    return 2;
}
function stShift(x, x0, c1, c2, d) { return -stZone(x, x0, c1, c2) * d * ST_MM; }
function stMovePts(p, x0, c1, c2, d) {
    var n = 0;
    for (var i = 0; i < p.pathPoints.length; i++) {
        var q = p.pathPoints[i], s = stShift(q.anchor[0], x0, c1, c2, d);
        if (!s) continue;
        q.anchor = [q.anchor[0] + s, q.anchor[1]];
        q.leftDirection = [q.leftDirection[0] + s, q.leftDirection[1]];
        q.rightDirection = [q.rightDirection[0] + s, q.rightDirection[1]];
        n++;
    }
    return n;
}
function stSq(it, x0, c1, c2, d) {
    if (it.name == "__st_holder__") return 0;          // 로고·글자 칸 묶음은 따로 다시 잡는다 (=== 비교가 안 돼서 이름표로 건너뜀)
    var b = it.geometricBounds, n = 0;
    if (stZone(b[0], x0, c1, c2) == stZone(b[2], x0, c1, c2)) { var s = stShift(b[0], x0, c1, c2, d); if (s) it.translate(s, 0); return 0; }
    if (it.typename == "GroupItem") { var k = kids(it); for (var i = 0; i < k.length; i++) n += stSq(k[i], x0, c1, c2, d); }
    else if (it.typename == "PathItem") n += stMovePts(it, x0, c1, c2, d);
    else if (it.typename == "CompoundPathItem") { for (var j = 0; j < it.pathItems.length; j++) n += stMovePts(it.pathItems[j], x0, c1, c2, d); }
    else if (it.typename == "RasterItem") { n += 0; }
    else it.translate(stShift((b[0] + b[2]) / 2, x0, c1, c2, d), 0);
    return n;
}
function stSqueeze(w, opt) {
    var clip = stClipOf(w);
    if (!clip) throw new Error("stSqueeze: 클리핑된 간판 그룹이 없음");
    var cb = clip.geometricBounds, x0 = cb[0], d = ((cb[2] - cb[0]) / ST_MM - opt.width) / 2;
    var all = collect(w, []), area = null, logo = null, i;
    for (i = 0; i < all.length; i++) { if (all[i].name == "영역") area = all[i]; if (all[i].name == "로고") logo = all[i]; }
    if (!area || !logo) throw new Error("stSqueeze: '로고'·'영역' 상자가 없음");
    var holder = area.parent; holder.name = "__st_holder__";
    var k = kids(w), moved = 0;
    for (i = 0; i < k.length; i++) moved += stSq(k[i], x0, opt.cut1, opt.cut2, d);
    holder.name = "";
    if (opt.tagScale)
        for (i = 0; i < all.length; i++)
            if (all[i].typename == "TextFrame" && /^AI시대/.test(all[i].contents)) all[i].resize(opt.tagScale, opt.tagScale, true, true, true, true, opt.tagScale, Transformation.LEFT);
    var tg = null, hk = kids(holder);
    for (i = 0; i < hk.length; i++) if (hk[i].typename == "GroupItem") tg = hk[i];
    logo.width = (opt.logo[1] - opt.logo[0]) * ST_MM; logo.left = x0 + opt.logo[0] * ST_MM;
    area.width = (opt.area[1] - opt.area[0]) * ST_MM; area.left = x0 + opt.area[0] * ST_MM;
    if (tg) { var tb = tg.visibleBounds; tg.translate(x0 + (opt.area[0] + opt.area[1]) / 2 * ST_MM - (tb[0] + tb[2]) / 2, 0); }
    var nb = stClipOf(w).geometricBounds;
    return { moved: moved, width: Math.round((nb[2] - nb[0]) / ST_MM * 10) / 10 };
}

// ── 간판 찾기 (묶음 이름에 기대지 않는다) ──────────────────────────────────
// ASURA님이 손보면서 '자동생성' 묶음을 풀고 레이어 이름을 바꿨다(부산 10-23). 그래서 모양으로 찾는다:
//   간판 = [클리핑된 간판 그룹 + 번호 라벨]을 묶은 그룹, 그 밖의 '맨 위 클리핑 그룹' = 다른 출력물(데스크 띠지 등).
//   이름이 '제목_…' 이거나 '기업부스날개' 인 묶음은 빼고, 레이어 직속과 '자동생성' 묶음 안을 모두 본다.
function stClipPathOf(g) { for (var j = 0; j < g.pathItems.length; j++) if (g.pathItems[j].clipping && g.pathItems[j].parent === g) return g.pathItems[j]; return null; }
function stFindSigns(doc) {
    var signs = [], others = [], pools = [];
    for (var l = 0; l < doc.layers.length; l++) pools.push(doc.layers[l]);
    for (var p = 0; p < pools.length; p++) {
        var k = kids(pools[p]);
        for (var i = 0; i < k.length; i++) {
            var it = k[i];
            if (it.typename != "GroupItem" || /^제목_/.test(it.name) || it.name == "기업부스날개") continue;
            if (it.name == "자동생성") { pools.push(it); continue; }
            if (it.clipped) { others.push(it); continue; }
            if (stClipOf(it)) signs.push(it);
        }
    }
    return { signs: signs, others: others };
}

// ── 간판 한 장 요약 ─────────────────────────────────────────────────────────
function stWalk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") stWalk(k[i], fn); } }
function stInfo(card) {
    var r = { card: card, name: "", num: "", nums: [], txt: [], logos: [], rgb: 0 };
    stWalk(card, function (it) {
        if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) {
            if (/^\d+$/.test(it.contents)) { r.nums.push(it.contents); r.num = it.contents; }
            else { r.txt.push(it.contents.replace(/\r/g, "/")); if (/[가-힣]/.test(it.contents) && !r.name) r.name = it.contents.replace(/\r/g, " "); }
        }
        if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * ST_MM) {
            r.logos.push(it); if (it.imageColorSpace != ImageColorSpace.CMYK) r.rgb++;
        }
    });
    r.b = bounds(card); r.w = Math.round((r.b[2] - r.b[0]) / ST_MM * 10) / 10;
    var lb = [];
    for (var i = 0; i < r.logos.length; i++) { var b = r.logos[i].geometricBounds; lb.push(Math.round((b[2] - b[0]) / ST_MM * 10) / 10 + "x" + Math.round((b[1] - b[3]) / ST_MM * 10) / 10); }
    r.key = r.nums.join("/") + " | " + r.txt.join(" ; ") + " | " + lb.join(" ; ");   // 자리와 무관한 내용 키
    return r;
}

// ── 번호순 다시 놓기 ────────────────────────────────────────────────────────
// 크기(폭)가 같은 간판끼리 한 묶음, 묶음마다 지금 줄 위치(위쪽 값)를 그대로 써서 10장씩 다시 놓는다.
// lastNames: 맨 끝으로 보낼 국문 이름 목록(예: 존이 다른 공공협력존 ["국제식물검역인증원"]). 같은 번호는 지금 순서 유지(08 안랩 2장).
// 돌려주는 값: 줄마다 번호 문자열 목록. 내용(stInfo.key)이 바뀌면 throw.
function stReorder(res, lastNames, perRow) {
    perRow = perRow || 10;
    var cards = kids(res), groups = {}, gkeys = [], before = {}, i, j;
    for (i = 0; i < cards.length; i++) {
        var r = stInfo(cards[i]), gk = String(Math.round(r.w));
        var last = false; for (j = 0; j < (lastNames || []).length; j++) if (r.name == lastNames[j]) last = true;
        r.sort = (last ? 1000 : 0) + (parseInt(r.num, 10) || 0) + i / 1000;
        before[r.key] = (before[r.key] || 0) + 1;
        if (!groups[gk]) { groups[gk] = []; gkeys.push(gk); }
        groups[gk].push(r);
    }
    var lines = [];
    for (var g = 0; g < gkeys.length; g++) {
        var G = groups[gkeys[g]], x0 = 1e9, tops = [], pitch = G[0].b[2] - G[0].b[0];
        for (i = 0; i < G.length; i++) {
            x0 = Math.min(x0, G[i].b[0]);
            var t = Math.round(G[i].b[1]), seen = false;
            for (j = 0; j < tops.length; j++) if (tops[j] == t) seen = true;
            if (!seen) tops.push(t);
        }
        tops.sort(function (a, b) { return b - a; });
        var need = Math.ceil(G.length / perRow);
        if (tops.length < need) throw new Error("stReorder: 폭 " + gkeys[g] + " 묶음 줄 " + tops.length + "개 < 필요 " + need);
        G.sort(function (a, b) { return a.sort - b.sort; });
        for (i = 0; i < G.length; i++) {
            G[i].card.translate(x0 + (i % perRow) * pitch - G[i].b[0], tops[Math.floor(i / perRow)] - G[i].b[1]);
            if (i % perRow == 0) lines.push([]);
            lines[lines.length - 1].push((G[i].sort >= 1000 ? "끝" : "") + G[i].num);
        }
    }
    var after = kids(res), now = {};
    for (i = 0; i < after.length; i++) { var k2 = stInfo(after[i]).key; now[k2] = (now[k2] || 0) + 1; }
    for (var key in before) if (before[key] != now[key]) throw new Error("stReorder: 내용이 달라짐 " + key);
    return lines;
}

// ── 묶음 제목 ───────────────────────────────────────────────────────────────
// 2025 참고판 이름: 조립부스간판 / 기본부스간판 옆날개 / 기업부스날개. lines 예: ["2930x750mm / 현수막 / 상하단 바미싱", "각 1EA · 총 24EA"]
// 맨 아래가 bottom 에 오게. font 는 간판 번호 라벨 글꼴을 넘기면 통일된다.
function stText(parent, s, size, font) {
    var t = parent.textFrames.add(); t.contents = s;
    if (font) t.textRange.characterAttributes.textFont = font;
    t.textRange.characterAttributes.size = size;
    var k = new CMYKColor(); k.black = 100; t.textRange.characterAttributes.fillColor = k;
    return t;
}
function stTitle(layer, name, lines, x, bottom, font) {
    var g = layer.groupItems.add(); g.name = "제목_" + name;
    var items = [stText(g, name, 60, font)], y = 0, i;
    for (i = 0; i < lines.length; i++) items.push(stText(g, lines[i], 26, font));
    for (i = 0; i < items.length; i++) {
        var b = items[i].visibleBounds;
        items[i].translate(x - b[0], y - b[1]);
        y -= (b[1] - b[3]) + (i == 0 ? 4 : 2) * ST_MM;
    }
    var gb = g.visibleBounds; g.translate(0, bottom - gb[3]);
    return g;
}

// ── 둥글게 양면 날개 ────────────────────────────────────────────────────────
// 현수막 한 장을 반으로 접어 기둥 하나를 감싼다 → 아래 = 한 면 그대로, 위 = 같은 면 180도.
// tif 는 render_artboard_tif.py 로 뽑은 한 면(예: 450x3230 실물). 다른 파일 디자인을 벡터로 복제하면
// 반투명 그림·스크린 겹침이 빠졌다(부산 3회) → 그림으로 넣는다. faceW = 한 면 폭(문서 mm, 1/10 이면 45).
function stEmbed(parent, file) {
    var pre = kids(parent), p = parent.placedItems.add(); p.file = file; p.embed();
    var post = kids(parent);
    for (var i = 0; i < post.length; i++) { var isNew = true; for (var j = 0; j < pre.length; j++) if (post[i] === pre[j]) isNew = false; if (isNew) return post[i]; }
    return null;
}
function stTwoFaceWing(layer, tif, x, top, faceW, name) {
    var wing = layer.groupItems.add(); wing.name = name || "기업부스날개";
    var lower = stEmbed(wing, tif), upper = stEmbed(wing, tif), parts = [lower, upper];
    for (var i = 0; i < 2; i++) { var b = parts[i].geometricBounds, k = faceW * ST_MM / (b[2] - b[0]) * 100; parts[i].resize(k, k, true, true, true, true, k, Transformation.TOPLEFT); }
    upper.rotate(180);
    var ub = upper.geometricBounds; upper.translate(x - ub[0], top - ub[1]); ub = upper.geometricBounds;
    var lb = lower.geometricBounds; lower.translate(x - lb[0], ub[3] - lb[1]);
    return wing;
}

// ── 출력 파일 마무리: 줄 그룹 + CS6 저장 (ASURA님 10-23) ─────────────────────
// 간판은 한 장씩 그룹 그대로, 그 위에 한 줄(최대 10장)씩 한 그룹. 같은 줄 = 위쪽 높이와 폭(정면 293 / 옆 243.5)이 같은 것.
// 인쇄업체가 열 수 있게 Illustrator CS6(=ILLUSTRATOR16) 로 저장: PDF 호환 ✔ · ICC 포함 ✘ · 압축 ✔.
function stGroupRows(items, prefix, perRow) {
    perRow = perRow || 10;
    var rows = {}, keys = [], i, j, n = 0;
    for (i = 0; i < items.length; i++) {
        var b = bounds(items[i]), k = Math.round(b[1] / ST_MM) + "_" + Math.round((b[2] - b[0]) / ST_MM);
        if (!rows[k]) { rows[k] = []; keys.push(k); }
        rows[k].push({ it: items[i], x: b[0] });
    }
    for (i = 0; i < keys.length; i++) {
        var R = rows[keys[i]];
        R.sort(function (a, b) { return a.x - b.x; });
        for (j = 0; j < R.length; j += perRow) {
            var g = R[j].it.layer.groupItems.add(); g.name = (prefix || "줄") + "_" + (++n);
            for (var q = j; q < Math.min(j + perRow, R.length); q++) R[q].it.move(g, ElementPlacement.PLACEATEND);
        }
    }
    return n;
}
function stCS6Options() {
    var o = new IllustratorSaveOptions();
    o.compatibility = Compatibility.ILLUSTRATOR16;
    o.pdfCompatible = true; o.embedICCProfile = false; o.compressed = true;
    return o;
}
