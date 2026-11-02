// fill_template.jsx — '틀' 그룹을 엑셀(CSV) 줄마다 복제해 글자·로고를 채우고 한 줄 10장씩 깐다.
//
// 틀 준비 (행사마다 한 번):
//   - 간판 1장(바탕·로고·글자)을 그룹으로 묶고 레이어 패널에서 이름을 '틀' 로.
//     크기가 다른 간판은 틀을 하나 더 만들어 '틀_2940x750' 처럼 이름을 붙이고, CSV '틀' 칸에 그 이름(또는 2940x750)을 적는다.
//     로고가 들어가며 배치가 달라지면 '틀_로고'(또는 '틀_2940x750_로고')를 만들어 두면 로고 있는 줄만 그 틀을 쓴다.
//   - 바뀌는 글자는 CSV 머리글과 같은 이름으로 (예: 부스번호, 국문, 영문). 같은 이름이 여러 개면 전부 채운다.
//   - 바뀌는 그림(로고 등)은 같은 이름의 칠·선 없는 사각형: 그 안에 비율 유지·가운데 정렬로 넣고 파일에 포함(embed).
//     CSV 칸 값은 파일 경로(CSV 위치 기준 상대경로 가능). 비어 있으면 아무것도 안 넣는다.
//   - '영역' 이라는 이름의 칠·선 없는 사각형: 이 안에 있는 글자는 폭을 넘으면 자동 축소.
//   - '수량' 칸은 장수(없으면 1).
// 실행: 파일 > 스크립트 > 기타 스크립트… → CSV 선택. 엑셀 기본 CSV·CSV UTF-8 둘 다 된다.
// 결과: '자동생성' 그룹. 엑셀 순서대로 한 줄 최대 10장. 크기가 같으면 틀이 달라도 이어 붙이고, 크기가 다른 간판만 따로 줄을 시작한다.
//       다시 돌리면 이전 '자동생성' 을 지우고 새로 만든다. 틀들은 숨김 처리된다.

var PER_ROW = 10;         // 출력소 한 번에 나오는 최대 장수
var ROW_GAP_MM = 69;      // 줄 사이 빈 간격 (문서 단위 mm). 부스간판 원본 줄 간격 151mm 와 맞춘 값
var BLOCK_GAP_MM = 300;   // 캔버스 아래가 차면 오른쪽에 새 10열 블록. 사이 간격
var MARGIN_MM = 30;       // 캔버스 가장자리 여백
var BREAK_RATIO = 0.5;    // 한 줄로 절반보다 더 줄여야 하면 띄어쓰기에서 두 줄로 나눈다 (원본 디자이너 기준)
var MM = 72 / 25.4;

function readCsv(file) {
    var encs = ["UTF-8", "CP949"], text = "";
    for (var i = 0; i < encs.length && !text; i++) {   // 인코딩이 틀리면 빈 문자열이 온다 (2026 실측)
        file.encoding = encs[i]; file.open("r"); text = file.read(); file.close();
    }
    text = text.replace(/^﻿/, "");
    var rows = [], row = [], cell = "", q = false;
    for (var k = 0; k < text.length; k++) {
        var c = text.charAt(k);
        if (q) {
            if (c == '"') { if (text.charAt(k + 1) == '"') { cell += '"'; k++; } else q = false; }
            else cell += c;
        } else if (c == '"') q = true;
        else if (c == ",") { row.push(cell); cell = ""; }
        else if (c == "\n" || c == "\r") {
            if (c == "\r" && text.charAt(k + 1) == "\n") k++;
            row.push(cell); rows.push(row); row = []; cell = "";
        } else cell += c;
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    var out = [];
    for (var r = 0; r < rows.length; r++) if (rows[r].join("").replace(/\s/g, "")) out.push(rows[r]);
    return out;
}

function collect(g, list) {              // 그룹 안 글자·영역을 깊이와 상관없이 모은다
    for (var i = 0; i < g.pageItems.length; i++) {
        var it = g.pageItems[i];
        if (it.parent !== g) continue;
        if (it.typename == "GroupItem") collect(it, list); else list.push(it);
    }
    return list;
}

function center(b) { return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]; }

function setText(tf, value, area) {
    var b0 = tf.visibleBounds, c0 = center(b0), h0 = b0[1] - b0[3];
    var size = tf.textRange.characterAttributes.size;
    tf.contents = value.replace(/\r\n|\n/g, "\r");
    if (area) {
        var maxW = area[2] - area[0], maxH = h0 * 1.15;
        var fit = function () { var b = tf.visibleBounds; return Math.min(1, maxW / (b[2] - b[0]), maxH / (b[1] - b[3])); };
        var r = fit();
        if (r < BREAK_RATIO && tf.contents.indexOf("\r") < 0 && tf.contents.indexOf(" ") > 0) {
            var s = tf.contents, mid = s.length / 2, best = -1;
            for (var i = 0; i < s.length; i++) if (s.charAt(i) == " " && (best < 0 || Math.abs(i - mid) < Math.abs(best - mid))) best = i;
            tf.contents = s.substring(0, best) + "\r" + s.substring(best + 1);
            r = fit();
        }
        if (r < 1) tf.textRange.characterAttributes.size = size * r * 0.995;
    }
    var c1 = center(tf.visibleBounds);
    tf.translate(c0[0] - c1[0], c0[1] - c1[1]);
}

// 캔버스(5779mm 정사각, 위치 고정) 경계. 대지는 캔버스 밖에 못 만들어서 임시 대지로 네 변을 이분 탐색한다.
// 오브젝트는 캔버스 밖으로도 옮겨지기 때문에 이걸 안 재면 대지 늘리기에서야 터진다 (2026-10-15 실측, 'AOoC').
function canvasBounds(doc) {
    var ab = doc.artboards[0].artboardRect, cx = (ab[0] + ab[2]) / 2, cy = (ab[1] + ab[3]) / 2, res = [];
    var mk = [function (v) { return [cx - v, cy + 1, cx, cy]; }, function (v) { return [cx, cy + v, cx + 1, cy]; },
              function (v) { return [cx, cy + 1, cx + v, cy]; }, function (v) { return [cx, cy, cx + 1, cy - v]; }];
    for (var s = 0; s < 4; s++) {
        var lo = 0, hi = 17000;
        while (hi - lo > 1) {
            var m = (lo + hi) / 2;
            try { doc.artboards.add(mk[s](m)); doc.artboards.remove(doc.artboards.length - 1); lo = m; } catch (e) { hi = m; }
        }
        res.push(lo);
    }
    return [cx - res[0], cy + res[1], cx + res[2], cy - res[3]];
}

function fillTemplate(doc, csvFile) {
    var cv = canvasBounds(doc);   // 임시 대지를 만들고 지우면 그 전에 잡은 오브젝트 참조가 끊긴다 → 맨 먼저 잰다
    // 출력용 간판은 CMYK 문서여야 한다. 부산(2026-10-15) 예시 원본이 RGB 문서라 CMYK 로고를 넣어도 RGB 로 바뀌었다.
    // 파일 > 문서 색상 모드 > CMYK (배경 그림까지 같이 바뀜, 실측). 캔버스를 잰 다음에 해야 되돌려지지 않는다.
    if (doc.documentColorSpace != DocumentColorSpace.CMYK) app.executeMenuCommand("doc-color-cmyk");
    var tpls = {}, names = [];
    for (var i = 0; i < doc.groupItems.length; i++) {
        var g = doc.groupItems[i];
        if (/^틀(_|$)/.test(g.name) && !tpls[g.name]) { tpls[g.name] = g; names.push(g.name); }
    }
    if (!names.length) throw new Error("'틀' 이라는 이름의 그룹이 없습니다.");
    var rows = readCsv(csvFile);
    if (rows.length < 2) throw new Error("CSV 가 비었거나 읽지 못했습니다: " + csvFile.fsName);
    var head = rows[0], col = {};
    for (var j = 0; j < head.length; j++) { head[j] = head[j].replace(/^\s+|\s+$/g, ""); col[head[j]] = j; }
    function val(r, name) { return name in col ? String(rows[r][col[name]] || "").replace(/^\s+|\s+$/g, "") : ""; }

    // 줄마다 틀 고르기 + 검사 (여기까지는 문서를 안 바꾼다)
    var groups = {}, order = [], seq = [], total = 0, errs = [];
    for (var r = 1; r < rows.length; r++) {
        var t = val(r, "틀") || "틀";
        if (!/^틀/.test(t)) t = "틀_" + t.replace(/\s+/g, "").replace(/×|\*/g, "x").replace(/mm$/i, "");
        if (val(r, "로고") && tpls[t + "_로고"]) t = t + "_로고";
        if (!tpls[t]) { errs.push((r + 1) + "번째 줄: '" + t + "' 틀이 없습니다"); continue; }
        var q = "수량" in col ? parseInt(val(r, "수량"), 10) : 1;
        if (isNaN(q) || q < 0) { errs.push((r + 1) + "번째 줄 수량이 숫자가 아닙니다: " + val(r, "수량")); continue; }
        if (!groups[t]) { groups[t] = []; order.push(t); }
        for (var k = 0; k < q; k++) { groups[t].push(r); seq.push({ r: r, t: t }); }
        total += q;
    }
    for (var o = 0; o < order.length; o++) {
        var tn = order[o], its = collect(tpls[tn], []), need = {}, imgs = [];
        for (i = 0; i < its.length; i++) {
            var nm = its[i].name;
            if (!nm || nm == "영역") continue;
            if (its[i].typename == "TextFrame") need[nm] = 1;
            else if (its[i].typename == "PathItem" && nm in col) imgs.push(nm);
        }
        for (var f in need) if (!(f in col)) errs.push("'" + tn + "' 의 '" + f + "' 글자에 맞는 CSV 칸이 없습니다");
        for (i = 0; i < imgs.length; i++) for (k = 0; k < groups[tn].length; k++) {
            var path = val(groups[tn][k], imgs[i]);
            if (path && !resolve(path, csvFile).exists) errs.push((groups[tn][k] + 1) + "번째 줄 " + imgs[i] + " 파일 없음: " + path);
        }
    }
    if (errs.length) throw new Error(dedupe(errs).slice(0, 15).join("\n"));

    // 배치 계산: 크기가 같은 간판은 틀이 달라도(로고2·와이드 등) 엑셀 순서 그대로 10장씩 붙여 한 줄.
    // 크기가 다른 간판만 따로 줄을 시작한다. 아래가 차면 오른쪽 새 블록.
    // (2026-10-15 부산: 틀별로 줄을 나눴더니 같은 크기 06·14 가 맨 아래 한 장씩 떨어졌다 — ASURA님 지적 "10개 붙여서 두라 했는데")
    var hidden = {};
    for (i = 0; i < names.length; i++) { hidden[names[i]] = tpls[names[i]].hidden; tpls[names[i]].hidden = false; }
    var tb0 = {}, bySize = {}, sizeOrder = [], lines = [];
    for (i = 0; i < order.length; i++) tb0[order[i]] = bounds(tpls[order[i]]);
    for (i = 0; i < seq.length; i++) {
        var b = tb0[seq[i].t], key = Math.round((b[2] - b[0]) * 10) + "x" + Math.round((b[1] - b[3]) * 10);
        if (!bySize[key]) { bySize[key] = { items: [], w: b[2] - b[0], h: b[1] - b[3] }; sizeOrder.push(key); }
        bySize[key].items.push(seq[i]);
    }
    for (o = 0; o < sizeOrder.length; o++) {
        var S = bySize[sizeOrder[o]];
        for (k = 0; k < S.items.length; k += PER_ROW) lines.push({ items: S.items.slice(k, k + PER_ROW), w: S.w, h: S.h });
    }
    var mg = MARGIN_MM * MM, gap = ROW_GAP_MM * MM;
    function plan(left, top) {
        var x = left, y = top, bw = 0, placed = 0, pos = [];
        for (var l = 0; l < lines.length; l++) {
            var L = lines[l];
            if (y - L.h < cv[3] + mg && y < top) { x += bw + BLOCK_GAP_MM * MM; y = top; bw = 0; }
            if (y - L.h < cv[3] + mg || x + L.w * L.items.length > cv[2] - mg) return { ok: false, placed: placed };
            pos.push([x, y]); placed += L.items.length;
            bw = Math.max(bw, L.w * L.items.length); y -= L.h + gap;
        }
        return { ok: true, pos: pos };
    }
    var fb = tb0[order[0]], at = plan(fb[0], fb[1]);   // 첫 틀 자리에서 시작
    if (!at.ok) at = plan(cv[0] + mg, cv[1] - mg);                   // 모자라면 캔버스 왼쪽 위부터
    if (!at.ok) {
        for (i = 0; i < names.length; i++) tpls[names[i]].hidden = hidden[names[i]];
        throw new Error("이 파일 캔버스에는 최대 " + at.placed + "장까지 들어갑니다 (요청 " + total + "장).\nCSV 를 나눠서 파일별로 돌리세요.");
    }

    try { doc.pageItems.getByName("자동생성").remove(); } catch (e) {}   // 검사 통과 뒤에만 이전 결과 삭제
    var out = tpls[order[0]].layer.groupItems.add(); out.name = "자동생성";
    var n = 0;
    for (var l = 0; l < lines.length; l++) {
        var L = lines[l];
        for (k = 0; k < L.items.length; k++, n++) {
            r = L.items[k].r;
            var tpl = tpls[L.items[k].t], tb = tb0[L.items[k].t];
            var d = tpl.duplicate(out, ElementPlacement.PLACEATEND);
            d.name = ""; d.hidden = false;
            var ci = collect(d, []), areas = [];       // 영역이 여럿이면(두 회사 반반) 글자가 들어 있는 영역을 쓴다
            for (i = 0; i < ci.length; i++) if (ci[i].name == "영역") areas.push(ci[i].visibleBounds);
            for (i = 0; i < ci.length; i++) {
                var it = ci[i];
                if (!it.name || it.name == "영역") continue;
                if (it.typename == "TextFrame") {
                    var c = center(it.visibleBounds), area = null;
                    for (var a = 0; a < areas.length && !area; a++)
                        if (c[0] > areas[a][0] && c[0] < areas[a][2] && c[1] < areas[a][1] && c[1] > areas[a][3]) area = areas[a];
                    setText(it, String(rows[r][col[it.name]] || ""), area);
                    it.name = "";
                } else if (it.typename == "PathItem" && it.name in col) {
                    var pth = val(r, it.name);
                    if (pth) placeImage(it, resolve(pth, csvFile));
                    it.name = "";
                }
            }
            d.translate(at.pos[l][0] + k * L.w - tb[0], at.pos[l][1] - tb[1]);
        }
    }
    for (i = 0; i < names.length; i++) tpls[names[i]].hidden = true;
    var ob = null;                        // 대지는 배치 계산 결과로 잡는다 (장마다 다시 재지 않음)
    for (l = 0; l < lines.length; l++) {
        var cb = [at.pos[l][0], at.pos[l][1], at.pos[l][0] + lines[l].w * lines[l].items.length, at.pos[l][1] - lines[l].h];
        ob = ob ? [Math.min(ob[0], cb[0]), Math.max(ob[1], cb[1]), Math.max(ob[2], cb[2]), Math.min(ob[3], cb[3])] : cb;
    }
    var ab = doc.artboards[doc.artboards.getActiveArtboardIndex()], ar = ab.artboardRect, m = 20 * MM;
    ab.artboardRect = [Math.min(ar[0], ob[0] - m), Math.max(ar[1], ob[1] + m), Math.max(ar[2], ob[2] + m), Math.min(ar[3], ob[3] - m)];
    return n;
}

function resolve(p, csvFile) {            // 절대경로 또는 CSV 위치 기준 상대경로
    var f = File(p);
    return f.exists ? f : File(csvFile.parent.fsName + "/" + p);
}

function dedupe(a) { var seen = {}, o = []; for (var i = 0; i < a.length; i++) if (!seen[a[i]]) { seen[a[i]] = 1; o.push(a[i]); } return o; }

function bounds(g) {                     // 클리핑 그룹은 가려진 바깥 장식까지 재지 않게 클리핑 사각형으로 잰다.
    if (g.typename != "GroupItem") return g.visibleBounds;   // 묶음 그룹(간판 + 위 번호 라벨)은 자식들의 합으로 잰다.
    if (g.clipped)
        for (var i = 0; i < g.pathItems.length; i++) if (g.pathItems[i].clipping) return g.pathItems[i].geometricBounds;
    var ch = kids(g), u = null;
    for (i = 0; i < ch.length; i++) {
        var b = bounds(ch[i]);
        u = u ? [Math.min(u[0], b[0]), Math.max(u[1], b[1]), Math.max(u[2], b[2]), Math.min(u[3], b[3])] : b;
    }
    return u || g.visibleBounds;
}

function kids(g) { var a = []; for (var i = 0; i < g.pageItems.length; i++) if (g.pageItems[i].parent === g) a.push(g.pageItems[i]); return a; }

function placeImage(box, file) {          // 사각형 안에 비율 유지·가운데, 파일에 포함
    if (/\.(ai|eps|pdf|svg)$/i.test(file.name)) file = rasterizeVector(file);
    var parent = box.parent, before = kids(parent);
    var p = parent.placedItems.add();
    p.file = file;
    p.move(box, ElementPlacement.PLACEBEFORE);
    p.embed();                            // embed 하면 p 는 새 오브젝트(RasterItem)로 바뀐다
    var after = kids(parent), it = null;
    for (var i = 0; i < after.length && !it; i++) {
        var isNew = true;
        for (var j = 0; j < before.length; j++) if (after[i] === before[j]) isNew = false;
        if (isNew) it = after[i];
    }
    var bb = box.geometricBounds, ib = it.geometricBounds;
    var s = Math.min((bb[2] - bb[0]) / (ib[2] - ib[0]), (bb[1] - bb[3]) / (ib[1] - ib[3])) * 100;
    it.resize(s, s, true, true, true, true, s, Transformation.CENTER);
    ib = it.geometricBounds;
    it.translate((bb[0] + bb[2]) / 2 - (ib[0] + ib[2]) / 2, (bb[1] + bb[3]) / 2 - (ib[1] + ib[3]) / 2);
}

// CMYK 변환은 여기서 하지 않는다. 로고 파일을 넣기 전에 excel_to_csv.to_cmyk_tiff 로 CMYK TIFF 로 바꿔 둔다.
// 일러 안에서 바꾸려다 실패했다(2026-10-15 부산): 메뉴 명령 "Colors8" 은 스크립트에서 안 먹었고(전부 RGB),
// d.rasterize 로 CMYK 래스터화했더니 일러가 응답 없음(메모리 13GB) → ASURA님이 강제 종료.

// 벡터 로고(ai·eps·pdf·svg)는 직접 열어 흰 바탕을 치우고 고해상도 투명 PNG 로 뽑아 넣는다.
// .ai 를 그대로 place→embed 하면 그림이 깨졌다 (2026-10-15 신화CNS 심볼 조각남·S 잘림, 양사로고 글자 두 겹).
// 원본 로고 파일은 저장하지 않고 닫는다.
var LOGO_PX = 5000, rasterCache = {};
function rasterizeVector(file) {
    if (rasterCache[file.fsName]) return rasterCache[file.fsName];
    var cur = app.activeDocument, ui = app.userInteractionLevel;
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    var d = app.open(file), out;
    try {
        for (var l = 0; l < d.layers.length; l++) d.layers[l].locked = false;
        var ab = d.artboards[0].artboardRect, aw = ab[2] - ab[0], ah = ab[1] - ab[3], all = [];
        for (var i = 0; i < d.pageItems.length; i++) all.push(d.pageItems[i]);
        for (i = 0; i < all.length; i++) {          // 대지를 거의 다 덮는 흰색·투명 바탕 사각형 제거
            var it = all[i];
            if (it.typename != "PathItem" || !isBlank(it)) continue;
            var b = it.geometricBounds;
            if (b[2] - b[0] > aw * 0.9 && b[1] - b[3] > ah * 0.9) { it.locked = false; it.remove(); }
        }
        var vb = d.visibleBounds, o = new ExportOptionsPNG24();
        o.transparency = true; o.antiAliasing = true; o.artBoardClipping = false;
        o.horizontalScale = o.verticalScale = Math.min(776, LOGO_PX / (vb[2] - vb[0]) * 100);
        out = File(Folder.temp.fsName + "/ft_logo_" + (new Date().getTime()) + "_" + Math.floor(Math.random() * 1e6) + ".png");
        d.exportFile(out, ExportType.PNG24, o);
    } finally {
        d.close(SaveOptions.DONOTSAVECHANGES);
        cur.activate();
        app.userInteractionLevel = ui;
    }
    rasterCache[file.fsName] = out;
    return out;
}

function isBlank(p) {
    if (!p.filled) return !p.stroked;
    var c = p.fillColor;
    if (c.typename == "CMYKColor") return c.cyan + c.magenta + c.yellow + c.black < 1;
    if (c.typename == "RGBColor") return c.red + c.green + c.blue > 760;
    if (c.typename == "GrayColor") return c.gray < 1;
    return false;
}

if (!$.global.FT_NO_MAIN) {
    try {
        var csv = File.openDialog("간판 목록 CSV 선택", "*.csv");
        if (csv) alert(fillTemplate(app.activeDocument, csv) + "장 생성 완료");
    } catch (e) {
        alert(e.message);
    }
}
