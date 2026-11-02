"""족자봉 출력 시트의 사진 이미지 실물 해상도 감사 — 1/10 시트라 '시트 ppi ÷ 10' 이 실물 ppi 다.
계기: 2026-10-27 굿모닝 재전달분 "해상도 깨지는거 있는지 확인 잘해"(ASURA님). 같은 점검에서 새 문서 래스터효과 해상도가
72ppi(실물 7ppi)로 굳어 빛 고리 글로우가 빠진 것을 찾았다 → build.jsx 가 300 으로 고정.
xref 0 항목은 사진이 아니라 그라데이션(셰이딩)이라 뺀다(확대해도 매끈함). 기준 미만 항목은 실물 100ppi 로 확대해 눈으로 본다.
사용: python res_audit.py <시트.ai> [기준ppi=40]"""
import sys, fitz

path = sys.argv[1]; LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 40
p = fitz.open(path, filetype="pdf")[0]; area = p.rect.width * p.rect.height
rows = []
for inf in p.get_image_info(xrefs=True):
    b = fitz.Rect(inf["bbox"]); vis = b & p.rect
    if inf["xref"] == 0 or vis.is_empty or min(inf["width"], inf["height"]) < 8: continue   # 그라데이션 / 여백맞춤 가장자리 늘림 띠
    ppi = min(inf["width"] / (b.width / 72 * 10), inf["height"] / (b.height / 72 * 10))
    rows.append((ppi, vis.width * vis.height / area * 100, inf["width"], inf["height"], b.x0 / 72 * 25.4, b.y0 / 72 * 25.4))
rows.sort()
low = [r for r in rows if r[0] < LIMIT]
for r in rows:
    print(f"{'★' if r[0] < LIMIT else ' '} 실물 {r[0]:5.0f}ppi  {r[2]}x{r[3]}px  시트의 {r[1]:4.1f}%  위치 {r[4]:.0f},{r[5]:.0f}mm")
print(f"사진 {len(rows)}개, {LIMIT:.0f}ppi 미만 {len(low)}개 — 미만 항목은 실물 100ppi 로 확대해 눈으로 확인" if low else f"RES_OK 사진 {len(rows)}개 모두 {LIMIT:.0f}ppi 이상")
