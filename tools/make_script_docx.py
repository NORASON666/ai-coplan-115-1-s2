# 產生場次二講稿 docx：時間表＋逐頁講稿（頁碼與簡報畫面一致）
# 用法：python tools/make_script_docx.py <輸出路徑>
import sys, re, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import content as c
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

OUT = sys.argv[1]
D = c._disp(c.S)
def mins(n):
    m = re.search(r"｜(\d+) 分鐘", n or ""); s = re.search(r"｜(\d+) 秒", n or "")
    return int(m.group(1)) if m else (0.5 if s else 0)
def title(d):
    if d["t"] == "cover": return "封面"
    if d["t"] == "closing": return "結尾"
    return d.get("title") or d.get("kicker") or d["t"]
SEG = [("開場", "s2-0", "s2-ag"), ("上週回顧", "s2-1", "36"), ("討論 1：案例① 第 3 題", "19", "s2-4"),
       ("評量觀念", "68", "72"), ("三種作業改造法", "73", "s2-ex3"), ("討論 2、3：案例④⑤", "s2-5", "78"),
       ("討論 4：案例⑥（視時間）", "s2-9", "81"), ("收斂", "77", "83"), ("小組產出總表", "84", "84"), ("收尾", "85", "87")]
order = [d["pg"] for d in c.S]
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Noto Sans TC"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans TC")
doc.add_heading("AI 工具衝擊下的作業與評量｜場次二講稿", 0)
doc.add_paragraph("2026-11-13（五）09:30–11:30　西湖國小活動中心二樓會議室\n簡報：https://norason666.github.io/ai-coplan-115-1-s2/　手機討論板：is.gd/coplan1113（簡報上按 B）\n頁碼＝簡報右下角頁碼。標「可略」的頁時間不夠就跳過；🗣＝討論頁。")
doc.add_heading("時間表", 1)
tb = doc.add_table(rows=1, cols=5); tb.style = "Light Grid Accent 1"
for i, h in enumerate(["段落", "頁", "必要（分）", "可略（分）", "預計時刻"]): tb.rows[0].cells[i].text = h
t = datetime.datetime(2026, 11, 13, 9, 30)
for name, a, b in SEG:
    seg = c.S[order.index(a): order.index(b) + 1]
    must = sum(mins(d.get("notes")) for d in seg if not d.get("notes", "").startswith("（"))
    opt = sum(mins(d.get("notes")) for d in seg if d.get("notes", "").startswith("（"))
    if "視時間" in name: must, opt = 0, must + opt
    end = t + datetime.timedelta(minutes=must)
    r = tb.add_row().cells
    r[0].text, r[1].text = name, f"{D[a]}–{D[b]}" if a != b else D[a]
    r[2].text, r[3].text = f"{must:g}", f"{opt:g}" if opt else ""
    r[4].text = f"{t:%H:%M}–{end:%H:%M}"; t = end
doc.add_paragraph(f"必要內容約到 {t:%H:%M}，到 11:30 還有約 {int((datetime.datetime(2026,11,13,11,30)-t).seconds/60)} 分鐘彈性：先給討論延長，其次案例⑥，最後才用可略頁。")
doc.add_heading("逐頁講稿", 1)
for d in c.S:
    n = d.get("notes", "")
    if d["pg"] in ("88", "89", "90"): continue
    h = doc.add_heading(f"第 {D[d['pg']]} 頁｜{title(d)}", 2)
    tags = []
    if d.get("talk"): tags.append("🗣 " + d["talk"])
    if n.startswith("（"): tags.append(n[1:n.index("）")])
    if d.get("board"): tags.append(f"按 B＝主題 {d['board']}")
    if tags:
        p = doc.add_paragraph(); r = p.add_run("　".join(tags)); r.bold = True; r.font.color.rgb = RGBColor(0xD9, 0x62, 0x2B)
    if d.get("pops"):
        doc.add_paragraph("🔍 彈出：" + "、".join(x[0] for x in d["pops"]))
    body = re.sub(r"^（[^）]*）", "", n)
    for line in body.split("\n"):
        if line.strip(): doc.add_paragraph(line.strip())
doc.save(OUT); print("saved", OUT)
