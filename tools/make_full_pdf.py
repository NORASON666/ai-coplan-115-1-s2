# 共備簡報 → PDF：每頁投影片截圖＋該頁補充資料＋文末小組討論紀錄
# 用法：python tools/make_full_pdf.py <repo> <標題> <討論紀錄.md> <輸出.pdf> [主題標題 JSON]
import sys, json, base64, html, re, os
from pathlib import Path
from playwright.sync_api import sync_playwright
deck, title, disc, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
TOP = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
work = out.parent / (out.stem + "_tmp"); work.mkdir(parents=True, exist_ok=True)

def md2html(md):
    o = []
    for blk in re.split(r"\n\s*\n", md.strip()):
        b = blk.strip()
        m = re.match(r"^(#{1,4}) (.*)", b)
        if m and "\n" not in b:
            n = len(m.group(1)) + 1; t = m.group(2); t = t + "｜" + TOP[t] if t in TOP else t
            o.append(f"<h{n}>{html.escape(t)}</h{n}>"); continue
        if b.startswith(">"):
            o.append(f'<p class="note">{html.escape(re.sub(r"^> ?", "", b, flags=re.M))}</p>'); continue
        lines = b.split("\n")
        if re.match(r"^#{1,4} ", lines[0]):
            n = len(lines[0].split(" ")[0]) + 1
            o.append(f"<h{n}>{html.escape(lines[0].split(' ',1)[1])}</h{n}>"); lines = lines[1:]
        o.append("<p>" + "<br>".join(html.escape(x) for x in lines) + "</p>")
    return "\n".join(o)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + str(deck / "docs/index.html")); pg.wait_for_timeout(1500)
    pg.add_style_tag(content="#bar,#prog,#fwBtn,#timerBadge,#edgeGlow,.supbtn,.pops,.popbtn{display:none!important}#deck{transform:none!important}")
    side = pg.evaluate("SIDE")
    n = pg.evaluate("slides.length")
    imgs = []
    for i in range(n):
        pg.evaluate(f"show({i})"); pg.wait_for_timeout(350)
        f = work / f"s{i:03d}.jpg"; pg.locator("#deck").screenshot(path=str(f), type="jpeg", quality=82); imgs.append(f)
    parts = [f'<section class="cover"><h1>{html.escape(title)}</h1><p>簡報全頁＋各頁補充資料＋小組討論紀錄</p></section>']
    for i, f in enumerate(imgs):
        s = side[i]; data = base64.b64encode(f.read_bytes()).decode()
        parts.append(f'<section class="slide"><img src="data:image/jpeg;base64,{data}"></section>')
        if s.get("sup"):
            parts.append(f'<section class="sups"><h2>第 {html.escape(s["n"])} 頁｜補充資料</h2>{s["sup"]}</section>')
    parts.append(f'<section class="disc"><h1 class="dh">小組討論紀錄</h1>{md2html(disc.read_text(encoding="utf-8"))}</section>')
    css = """@page{size:A4 landscape;margin:10mm}body{font-family:'Noto Sans TC','PingFang TC',sans-serif;color:#1c2b45;margin:0}
section{page-break-after:always}section:last-child{page-break-after:auto}
.cover{height:180mm;display:flex;flex-direction:column;justify-content:center;align-items:center}.cover h1{font-size:30pt;margin:0 0 8mm}.cover p{font-size:14pt;color:#667}
.slide{height:189mm;display:flex;align-items:center;justify-content:center}.slide img{max-width:100%;max-height:189mm;border:1px solid #ccd}
.sups h2,.dh{font-size:15pt;border-bottom:2px solid #2b5797;padding-bottom:2mm;margin:0 0 4mm}
.sup{border:1px solid #ccd;border-radius:3mm;padding:3mm 4mm;margin-bottom:4mm;page-break-inside:avoid;font-size:10.5pt}
.sup h4{margin:1.5mm 0;font-size:12pt}.sup ul{margin:1mm 0 1mm 5mm;padding:0}.sup-k{display:flex;gap:2mm;font-size:9pt}
.kind{background:#e3edf9;color:#2b5797;border-radius:2mm;padding:0 2mm;font-weight:700}.ev{background:#eef1f5;color:#667;border-radius:2mm;padding:0 2mm}
.sup-src{font-size:9pt;color:#667;margin:1.5mm 0 0}.sup a{color:#2b5797}.code pre{white-space:pre-wrap;font-size:9pt;background:#f5f6f8;padding:2mm}.copy{display:none}
.sup b{color:#2b5797}.sup img{max-width:100%}
.disc{font-size:11pt}.disc h2{font-size:14pt;margin:6mm 0 2mm;color:#2b5797}.disc h2{font-size:16pt}.disc h3{font-size:14pt;margin:7mm 0 2mm;color:#fff;background:#2b5797;padding:1.5mm 3mm;border-radius:2mm}.disc h4{font-size:12pt;margin:4mm 0 1mm;color:#2b5797;border-left:3px solid #f0a020;padding-left:2mm}.disc p{margin:1mm 0 2mm;line-height:1.55}.note{color:#667;font-size:9.5pt}"""
    doc = work / "print.html"
    doc.write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style>" + "\n".join(parts), encoding="utf-8")
    pp = b.new_page(); pp.goto("file://" + str(doc)); pp.wait_for_timeout(1000)
    pp.pdf(path=str(out), format="A4", landscape=True, print_background=True)
    b.close()
print(out, len(imgs), "slides", sum(1 for s in side[:len(imgs)] if s.get("sup")), "with sup")
