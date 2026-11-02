// 부산 사이버보안 부스간판 틀 만들기 (2026-10-15, 일회성)
// 원본 부스간판.ai 를 열어 '부스간판_자동생성.ai' 로 다른 이름 저장 → 그 안에서만 고친다(원본 불변).
// 아이시큐 예시 간판 → '틀'(로고+국문+영문), '틀_로고2'(로고 2개 좌우), '틀_와이드'(양사로고 1개 넓게).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, log = [];
var DIR = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var doc = app.open(File(WORK + "원본_부스간판_예시안_1015.ai"));   // 2026-10-21 결과 파일이 부스간판.ai 로 이름이 바뀌며 원본 예시안은 작업기록 폴더로
doc.saveAs(File(WORK + "부스간판_틀.ai"));         // 틀은 작업기록 폴더에 따로 둔다. 결과 파일엔 간판만 (ASURA님: 중복 정리)
// 원본 예시안이 RGB 문서다 → 틀을 만들기 전에 CMYK 로 (그래야 아래에서 넣는 CMYK 색이 그대로 남는다)
if (doc.documentColorSpace != DocumentColorSpace.CMYK) app.executeMenuCommand("doc-color-cmyk");
log.push("문서 색상 " + doc.documentColorSpace);
var L = doc.layers.getByName("Layer 1");

function kids(g) { var a = []; for (var i = 0; i < g.pageItems.length; i++) if (g.pageItems[i].parent === g) a.push(g.pageItems[i]); return a; }
function clipRect(g) { for (var i = 0; i < g.pathItems.length; i++) if (g.pathItems[i].clipping) return g.pathItems[i].geometricBounds; }
function hasText(g, s) {                          // g 안(깊이 무관)에서 s 를 담은 글자
    for (var i = 0; i < g.textFrames.length; i++) if (g.textFrames[i].contents.indexOf(s) >= 0) return g.textFrames[i];
    var ch = kids(g);
    for (i = 0; i < ch.length; i++) if (ch[i].typename == "GroupItem") { var t = hasText(ch[i], s); if (t) return t; }
    return null;
}
function box(parent, name, cr, x, y, w, h) {      // cr 기준 상대 mm (왼쪽 위 원점)
    var r = parent.pathItems.rectangle(cr[1] - y * MM, cr[0] + x * MM, w * MM, h * MM);
    r.filled = false; r.stroked = false; r.name = name; return r;
}

var signs = kids(L), blank = null, example = null;
for (var i = 0; i < signs.length; i++) {
    if (signs[i].typename != "GroupItem" || !signs[i].clipped) continue;
    if (hasText(signs[i], "ISECU")) example = signs[i]; else if (hasText(signs[i], "company name")) blank = signs[i];
}
var bcr = clipRect(blank);

// 기본 틀: 예시 간판을 빈 간판 자리로 복제
var tpl = example.duplicate(L, ElementPlacement.PLACEATBEGINNING);
tpl.translate(bcr[0] - clipRect(tpl)[0], bcr[1] - clipRect(tpl)[1]);
tpl.name = "틀";
var cr = clipRect(tpl);
var ko = hasText(tpl, "아이시큐"), en = hasText(tpl, "ISECU"), no = hasText(tpl, "a-01");
ko.name = "국문"; en.name = "영문"; no.name = "부스번호";
var textGroup = ko.parent, logoGroup = null, kk = kids(textGroup.parent);
for (i = 0; i < kk.length; i++) if (kk[i] !== textGroup) logoGroup = kk[i];
var holder = textGroup.parent;                     // 로고+글자 묶음 그룹
log.push("logo group bounds(mm rel): " + ((logoGroup.geometricBounds[0] - cr[0]) / MM) + ", w " + ((logoGroup.geometricBounds[2] - logoGroup.geometricBounds[0]) / MM));
logoGroup.remove();
box(holder, "로고", cr, 39.5, 31.5, 95, 26);        // 예시 아이시큐 로고 자리(가운데 87mm, 폭 87mm)를 조금 넉넉히
box(holder, "영역", cr, 153, 28, 100, 34);          // 글자 묶음 가운데 203mm, 폭 100mm 넘으면 축소

// 로고 2개 좌우 (신화씨엔에스: illumio | 신화CNS)
var t2 = tpl.duplicate(L, ElementPlacement.PLACEATBEGINNING);
t2.translate(0, -200 * MM); t2.name = "틀_로고2";
var cr2 = clipRect(t2), h2 = hasText(t2, "아이시큐").parent.parent;
hasText(t2, "아이시큐").parent.remove();
var kk2 = kids(h2); for (i = 0; i < kk2.length; i++) kk2[i].remove();
box(h2, "로고", cr2, 30, 31.5, 108, 26);
box(h2, "로고2", cr2, 155, 31.5, 108, 26);
var line = h2.pathItems.add(); line.setEntirePath([[cr2[0] + 146.5 * MM, cr2[1] - 31 * MM], [cr2[0] + 146.5 * MM, cr2[1] - 58 * MM]]);
line.filled = false; line.stroked = true; line.strokeWidth = 0.75;
var gc = new CMYKColor(); gc.black = 40; line.strokeColor = gc;

// 한 부스 두 회사 반반 (제이콥시스템 | 정원엔시스): 반쪽마다 로고 + 국문 + 영문, 가운데 구분선.
// 처음엔 합본 로고 파일 한 장을 넓게 넣었는데 여백·세로선 때문에 작고 어색했다 → ASURA님 "이건 뭐여 로고도 아니고"(2026-10-15).
// 요청서에 붙은 2025 우리아이티 예시(시스코 | 우리아이티 각각 로고+이름)와 같은 형식.
var t3 = tpl.duplicate(L, ElementPlacement.PLACEATBEGINNING);
t3.translate(0, -400 * MM); t3.name = "틀_2사";
var cr3 = clipRect(t3), tg3 = hasText(t3, "아이시큐").parent, h3 = tg3.parent;
var kk3 = kids(h3); for (i = 0; i < kk3.length; i++) if (kk3[i] !== tg3) kk3[i].remove();   // 로고·영역 상자 치우고 글자 묶음만 남김
function centerTo(g, relX) { var b = g.visibleBounds; g.translate(cr3[0] + relX * MM - (b[0] + b[2]) / 2, 0); }
var tg3b = tg3.duplicate(h3, ElementPlacement.PLACEATEND);
hasText(tg3b, "아이시큐").name = "국문2"; hasText(tg3b, "ISECU").name = "영문2";
centerTo(tg3, 110); centerTo(tg3b, 238);
box(h3, "로고", cr3, 26, 33, 52, 22);  box(h3, "영역", cr3, 82, 28, 58, 34);
box(h3, "로고2", cr3, 153, 33, 52, 22); box(h3, "영역", cr3, 209, 28, 58, 34);
var line3 = h3.pathItems.add(); line3.setEntirePath([[cr3[0] + 146.5 * MM, cr3[1] - 31 * MM], [cr3[0] + 146.5 * MM, cr3[1] - 58 * MM]]);
line3.filled = false; line3.stroked = true; line3.strokeWidth = 0.75; line3.strokeColor = gc;

// 번호 도형 연두색 틀 (2026-10-16 국제식물검역인증원 비고: "부스번호 기입되는 도형 색깔을 하늘색 말고 연두색으로")
var t4 = tpl.duplicate(L, ElementPlacement.PLACEATBEGINNING);
t4.translate(0, -600 * MM); t4.name = "틀_연두";
var nb = hasText(t4, "a-01").visibleBounds, ncx = (nb[0] + nb[2]) / 2, ncy = (nb[1] + nb[3]) / 2, recolored = 0;
var green = new CMYKColor(); green.cyan = 50; green.magenta = 0; green.yellow = 100; green.black = 0;
for (i = 0; i < t4.pathItems.length; i++) {
    var pi = t4.pathItems[i], pb = pi.geometricBounds;
    if (pi.filled && !pi.clipping && pb[0] < ncx && pb[2] > ncx && pb[1] > ncy && pb[3] < ncy && pb[2] - pb[0] < 40 * MM) { pi.fillColor = green; recolored++; }
}
log.push("연두 번호 도형 " + recolored + "개 (C50 Y100)");

// 간판 위 검정 번호 라벨 (현수막 출력할 때 알아보게 — ASURA님 2026-10-15 "번호 위에 검정 텍스트 있어야 한다").
// 간판은 클리핑 그룹이라 안에 넣으면 가려진다 → 바깥 묶음 그룹(틀 이름)을 만들어 간판 + 라벨을 같이 넣는다.
// 라벨 오른쪽 끝 = 배지 오른쪽 끝, 간판 위 3mm. 글자·크기는 배지 번호와 같게, 색만 검정.
function wrap(sign, name) {
    var w = L.groupItems.add(); w.name = name; sign.name = "";
    sign.move(w, ElementPlacement.PLACEATEND);
    var badge = hasText(sign, "a-01"), crw = clipRect(sign), bb = badge.visibleBounds;
    var t = w.textFrames.add(); t.contents = "01"; t.name = "부스번호";
    t.textRange.characterAttributes.textFont = badge.textRange.characterAttributes.textFont;
    t.textRange.characterAttributes.size = badge.textRange.characterAttributes.size;
    var k = new CMYKColor(); k.black = 100; t.textRange.characterAttributes.fillColor = k;
    t.textRange.paragraphAttributes.justification = Justification.RIGHT;
    var tb = t.visibleBounds;
    t.translate(bb[2] - tb[2], crw[1] + 3 * MM - tb[3]);
    return w;
}
wrap(tpl, "틀"); wrap(t2, "틀_로고2"); wrap(t3, "틀_2사"); wrap(t4, "틀_연두");

// 원본 예시 2개는 이 파일에서만 치운다 (원본 파일엔 그대로 있음)
blank.remove(); example.remove();
doc.save();
log.push("templates ok");
doc.close(SaveOptions.DONOTSAVECHANGES);
var f = File(Folder.temp.fsName + "/bsg_tpl.txt"); f.encoding = "UTF-8"; f.open("w"); f.write(log.join("\n")); f.close();
