# 產生 site/index.html：content.py（版面）＋ slides.json（講稿）＋ supplements.json（補充資料）
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import S, SHOT, ILL
import content as content_mod

BASE = os.path.dirname(__file__)
notes = {s["n"]: s["notes"] for s in json.load(open(os.path.join(BASE, "slides.json")))}
sup_path = os.path.join(BASE, "supplements.json")
SUP = json.load(open(sup_path)) if os.path.exists(sup_path) else {}
ILL_EXT = {}
for f in os.listdir(os.path.join(BASE, "..", "docs", ILL)) if os.path.isdir(os.path.join(BASE, "..", "docs", ILL)) else []:
    ILL_EXT[os.path.splitext(f)[0]] = f


def e(s):
    # 跳脫後支援 **粗體** 與換行
    s = html.escape(s or "")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s.replace("\n", "<br>")


def ill(name):
    f = ILL_EXT.get(name)
    return f'<img class="ill" src="{ILL}{f}" alt="">' if f else f'<div class="ill missing">插圖 {name} 製作中</div>'


def head(d):
    k = f'<div class="kicker">{e(d["kicker"])}</div>' if d.get("kicker") else ""
    cls = "title sr" if d.get("hide_title") else "title"
    t = f'<h2 class="{cls}"><span>{e(d["title"])}</span></h2>' if d.get("title") else ""
    return k + t


def foot(d):
    out = ""
    if d.get("rel"):
        out += f'<div class="rel"><span class="tag">{e(d["rel"][0])}</span><span>{e(d["rel"][1])}</span></div>'
    if d.get("foot"):
        out += f'<p class="foot">{e(d["foot"])}</p>'
    if d.get("link"):
        out += f'<a class="link" href="{html.escape(d["link"])}" target="_blank" rel="noopener">{html.escape(d["link"])}</a>'
    if d.get("dl"):
        out += f'<a class="dl big" href="{html.escape(d["dl"])}" download="嚴格作文評審.zip">⬇ 下載技能檔（嚴格作文評審.zip）</a>'
    if d.get("src"):
        out += f'<p class="src">資料來源｜{e(d["src"])}</p>'
    return out


def render(d):
    t = d["t"]
    if t == "cover":
        return f'''<div class="cover">{ill("cover_bg")}
<div class="cover-text">
<div class="org">臺北市科技領域輔導團 國小分團｜資訊人員分區共備</div>
<h1>AI 工具衝擊下的<br><mark>作業與評量</mark></h1>
<div class="meta">2026.11.13（場次二）　南港／內湖區</div>
<div class="who"><span>臺北市數位學習中心 <b>周凡淇</b></span><span>日新科技中心 <b>何詩慧</b> 主任</span></div>
</div></div>'''
    if t == "closing":
        return f'''<div class="cover">{ill("cover_bg")}<div class="cover-text">
<h1><mark>跨校共備好樂趣</mark></h1><div class="hand">See You Next Time</div>
<div class="who"><span>周凡淇</span><span>何詩慧 主任</span></div></div></div>'''
    if t == "divider":
        return f'''<div class="divider"><div class="dv-text"><div class="kicker big">{e(d["kicker"])}</div>
<h2 class="dv-title">{e(d["title"])}</h2><div class="dv-sub">{e(d["sub"])}</div></div>
<div class="dv-ill">{ill(d["ill"])}</div></div>'''
    if t == "bullets":
        tag = "ol" if d.get("numbered") else "ul"
        lis = "".join(f'<li class="{"hl" if i in d.get("hl", []) else ""}">{e(x)}</li>' for i, x in enumerate(d["items"]))
        if d.get("roster"):
            # 研習員名冊（依報名序；輪流發言時對照學校）
            ros = "".join(f'<li><span>{e(sc)}</span>{e(n)}</li>' for sc, n in d["roster"])
            return f'{head(d)}<div class="icebreak"><{tag} class="bul">{lis}</{tag}><ol class="roster">{ros}</ol></div>{foot(d)}'
        return f'{head(d)}<{tag} class="bul">{lis}</{tag}>{foot(d)}'
    if t == "shot":
        cls = "shot wide" if d.get("wide") else "shot"
        return f'{head(d)}<div class="{cls}"><img src="{SHOT}{d["img"]}" alt=""></div>{foot(d)}'
    if t == "shot2":
        imgs = "".join(f'<img src="{SHOT}{i}" alt="">' for i in d["imgs"])
        return f'{head(d)}<div class="shot two">{imgs}</div>{foot(d)}'
    if t == "qrpage":
        lis = "".join(f"<li>{e(x)}</li>" for x in d["lines"])
        return f'{head(d)}<div class="qrpage"><img src="{SHOT}{d["img"]}" alt="{e(d.get("alt", "LINE 群組 QR Code"))}"><ul class="bul">{lis}</ul></div>{foot(d)}'
    if t == "article":
        # AI 回答樣式的短文；[[n|句子]] 是埋的問題句，reveal=True 時標號highlight
        def mk(x):
            x = e(x)
            return re.sub(r"\[\[(\d+)\|(.+?)\]\]", (r'<mark class="err"><sup>\1</sup>\2</mark>' if d.get("reveal") else r"\2"), x)
        ps = "".join(f"<p>{mk(x)}</p>" for x in d["paras"])
        return f'''{head(d)}<div class="art"><div class="ask"><span class="tag">提問</span>{e(d["prompt"])}</div>
<div class="ans"><div class="who">✦ AI 回答</div>{ps}</div></div>{foot(d)}'''
    if t == "compare":
        figs = "".join(f'<figure><img src="{SHOT}{i}" alt=""><figcaption>{e(c)}</figcaption></figure>' for i, c in d["imgs"])
        return f'{head(d)}<div class="shot two">{figs}</div>{foot(d)}'
    if t == "shotText":
        ps = "".join(f"<p>{e(x)}</p>" for x in d["text"])
        return f'{head(d)}<div class="st"><div class="st-img"><img src="{SHOT}{d["img"]}" alt=""></div><div class="st-text">{ps}</div></div>{foot(d)}'
    if t == "illus":
        return f'{head(d)}<div class="illus">{ill(d["ill"])}</div>{foot(d)}'
    if t == "cards":
        cs = "".join(f'<div class="card"><h3>{e(h)}</h3><p>{e(b)}</p>{f"<div class=note>{e(n)}</div>" if n else ""}</div>' for h, b, n in d["cards"])
        return f'{head(d)}<div class="cards c{d["cols"]}">{cs}</div>{foot(d)}'
    if t == "redesign":
        cs = "".join(f'<div class="card rd{i}"><h3>{e(h)}</h3><p>{e(b)}</p>{f"<div class=note>{e(n)}</div>" if n else ""}</div>'
                     for i, (h, b, n) in enumerate(d["cols"]))
        return f'{head(d)}<div class="cards c3 arrows">{cs}</div>{foot(d)}'
    if t == "flow":
        cs = "".join(f'<div class="card"><div class="num">{i + 1}</div><h3>{e(h)}</h3><p>{e(b)}</p></div>' for i, (h, b) in enumerate(d["steps"]))
        return f'{head(d)}<div class="cards c4 arrows">{cs}</div>{foot(d)}'
    if t == "steps":
        cs = "".join(f'<li><span class="num">{i + 1}</span><span>{e(x)}</span></li>' for i, x in enumerate(d["steps"]))
        if d.get("colormark"):
            # 顏色標記法面板（教育部《國小生聰明用 AI》手冊 p.38 的寫詩例）
            C = {"k": "#222", "r": "#c0392b", "b": "#1f5fbf"}
            poem = "".join("<div>" + "".join(f'<span style="color:{C[c]}">{html.escape(w)}</span>' for c, w in line) + "</div>" for line in d["colormark"]["poem"])
            leg = "".join(f'<li><i style="background:{C[c]}"></i>{e(x)}</li>' for c, x in d["colormark"]["legend"])
            panel = f'<div class="cmark"><h3>{e(d["colormark"]["title"])}</h3><ul class="cleg">{leg}</ul><div class="cpoem">{poem}</div><p class="cnote">{e(d["colormark"]["note"])}</p></div>'
            return f'{head(d)}<div class="cmwrap"><ol class="steps">{cs}</ol>{panel}</div>{foot(d)}'
        return f'{head(d)}<ol class="steps">{cs}</ol>{foot(d)}'
    if t == "case":
        mark = "ABC" if d.get("letters") else "123"
        qs = "".join(f'<li><span class="num">{"" if d.get("letters") else mark[i]}</span><span>{e(q)}</span></li>' for i, q in enumerate(d["qs"]))
        ask = f'<p class="foot">{e(d["ask"])}</p>' if d.get("ask") else ""
        return f'''<div class="kicker">{e(d["kicker"])}</div><div class="situation"><span class="tag">情境</span>{e(d["situation"])}</div>
<ol class="steps qs">{qs}</ol>{ask}{foot(d)}'''
    if t == "table":
        th = "".join(f"<th>{e(x)}</th>" for x in d["head"])
        trs = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in d["rows"])
        cls = "tbl compact" if d.get("compact") else "tbl"
        return f'{head(d)}<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>{foot(d)}'
    if t == "stats":
        cs = "".join(f'<div class="card stat"><div class="big">{e(n)}</div><h3>{e(l)}</h3>{f"<p>{e(s)}</p>" if s else ""}</div>' for n, l, s in d["stats"])
        return f'{head(d)}<div class="cards c{len(d["stats"])}">{cs}</div>{foot(d)}'
    if t == "quote":
        return f'{head(d)}<blockquote class="quote">{e(d["text"])}</blockquote>{foot(d)}'
    if t == "check":
        cs = "".join(f'<div class="card"><h3>{e(h)}</h3><p>{e(b)}</p></div>' for h, b in d["cols"])
        return f'<div class="kicker">{e(d["kicker"])}</div><blockquote class="quote q2">{e(d["q"])}</blockquote><div class="cards c2">{cs}</div>'
    if t == "aiday":
        lis = "".join(f"<li>{e(x)}</li>" for x in d["lines"])
        qr = f'<img class="qr" src="{SHOT}{d["qr"]}" alt="QR code">' if d.get("qr") else ""
        return f'''<div class="kicker">{e(d.get("kicker", "案例激盪｜從 AI Day 看到什麼？"))}</div><h2 class="title"><span>{e(d["title"])}</span></h2>
<div class="aiday"><ul class="bul">{lis}</ul>{qr}</div>{foot(d)}'''
    if t == "sources":
        cols = "".join("<ul>" + "".join(f"<li>{e(x)}</li>" for x in c) + "</ul>" for c in d["cols"])
        return f'<div class="kicker">來源</div><h2 class="title"><span>{e(d["title"])}</span></h2><div class="srcs">{cols}</div>'
    raise ValueError(t)


def sup_html(n):
    items = SUP.get(str(n), [])
    out = []
    for it in items:
        pts = "".join(f"<li>{e(p)}</li>" for p in it.get("points", []))
        cl = "".join(f"<li>{e(p)}</li>" for p in it.get("classroom", []))
        cl = f'<div class="cl"><b>課堂可以這樣做</b><ol>{cl}</ol></div>' if cl else ""
        rd = "".join(f"<p>{e(x)}</p>" for x in it.get("read", []))
        rd = f'<details class="rd" open><summary>深入閱讀</summary>{rd}</details>' if rd else ""
        lm = "".join(f"<li>{e(x)}</li>" for x in it.get("limits", []))
        lm = f'<div class="lm"><b>研究限制・引用提醒</b><ul>{lm}</ul></div>' if lm else ""
        tk = f'<div class="tk"><b>上台可以這樣說</b><p>{e(it["talk"])}</p></div>' if it.get("talk") else ""
        url = f' <a href="{html.escape(it["url"])}" target="_blank" rel="noopener">原文</a>' if it.get("url") else ""
        ev = it.get("evidence", "")
        code = ""
        if it.get("code"):
            code = f'<div class="code"><button class="copy">複製</button><pre>{html.escape(it["code"])}</pre></div>'
        if it.get("download"):
            code += f'<p><a class="dl" href="{html.escape(it["download"])}" download>⬇ {e(it.get("download_label","下載"))}</a></p>'
        out.append(f'''<article class="sup"><div class="sup-k"><span class="kind">{e(it.get("kind",""))}</span><span class="ev ev-{html.escape(ev)}">{e(ev)}</span></div>
<h4>{e(it["title"])}</h4><ul>{pts}</ul>{rd}{lm}{tk}{cl}{code}<p class="sup-src">{e(it.get("source",""))}{url}</p></article>''')
    return "".join(out), len(items)


slides, side, pops_html = [], [], []
POOL = getattr(content_mod, "_L", {})
canva, sub, cur = 0, 0, "0"
dmain, dsub = 0, 0
# pg= 的頁是 HTML 版搬過位置的頁，保留 Canva 原頁碼；依序編號時跳過這些頁碼
moved = {str(d["pg"]) for d in S if "pg" in d and not d.get("extra")}
for d in S:
    # extra=True 的頁是 HTML 版新增，編號接在前一頁後面（23-1、23-2…），其餘頁碼與 Canva 一致
    if "pg" in d:
        label = str(d["pg"])
        if not d.get("extra"):
            cur, sub = label, 0
        note = d.get("notes") or ("" if d.get("extra") else notes.get(int(label), ""))
    elif d.get("extra"):
        sub += 1; label = f"{cur}-{sub}"; note = d.get("notes", "")
    else:
        canva += 1
        while str(canva) in moved:
            canva += 1
        sub = 0; cur = label = str(canva); note = d.get("notes") or notes.get(canva, "")
    # 畫面頁碼依 HTML 實際順序重編（搬過位置也連續）；label 仍是 Canva 頁碼，講稿與補充資料用它對應
    if d.get("extra"):
        dsub += 1; disp = f"{dmain}-{dsub}"
    else:
        dmain += 1; dsub = 0; disp = str(dmain)
    body = render(d)
    # 提到四問框架／備課四階段的字，點了直接叫出彈窗（不用翻回 p11、p12）
    for w, i in (('四問框架', 0), ('備課四階段', 1)):
        body = body.replace(w, f'<a class="fwlink" data-fw="{i}">{w} 📐</a>')
    sh, cnt = sup_html(label)
    badge = f'<button class="supbtn" title="補充資料（S）">📎 補充（{cnt} 則）</button>' if cnt else ""
    # 討論頁標記：老師一眼知道這頁要討論、手機填哪個主題
    if d.get("talk"):
        badge += f'<div class="talkbadge">🗣 {e(d["talk"])}</div>'
    # 彈出頁：點按鈕跳出場次一的原頁（含補充資料），不佔主線頁數
    if d.get("pops"):
        bs = ""
        for btxt, labs in d["pops"]:
            gid = f"g{len(pops_html)}"
            bs += f'<button class="popbtn" data-pop="{gid}">🔍 {e(btxt)}</button>'
            for i, lb in enumerate(labs):
                pd = POOL[str(lb)]
                psh, pcnt = sup_html(str(lb))
                supb = f'<button class="popsupbtn">📎 補充（{pcnt} 則）</button><template class="psup">{psh}</template>' if pcnt else ""
                pops_html.append(f'<section class="slide popslide t-{pd["t"]}" data-pop="{gid}" data-i="{i}" data-n="{len(labs)}"><div class="inner">{render(pd)}</div>'
                                 f'<div class="popbar"><b>上週｜{e(btxt)}</b><span>{i + 1} / {len(labs)}　← → 換頁　Esc 關閉</span>{supb}<button class="popx">✕ 關閉</button></div></section>')
        badge += f'<div class="pops">{bs}</div>'
    battr = f' data-board="{d["board"]}"' if d.get("board") else ""
    slides.append(f'<section class="slide t-{d["t"]}" id="p{disp}" data-label="{disp}" data-canva="{label}"{battr}><div class="inner">{body}</div>{badge}<div class="pno" title="Canva 第 {label} 頁">{disp}</div></section>')
    side.append({"n": disp, "canva": label, "notes": note, "sup": sh})

tpl = open(os.path.join(BASE, "template.html")).read()
out = tpl.replace("<!--SLIDES-->", "\n".join(slides + pops_html)).replace("/*PRIOR*/[]", json.dumps(getattr(content_mod, "PRIOR", []), ensure_ascii=False)).replace("/*QTXT*/{}", json.dumps(getattr(content_mod, "QTXT", {}), ensure_ascii=False)).replace("/*SIDE*/[]", json.dumps(side, ensure_ascii=False))
open(os.path.join(BASE, "..", "docs", "index.html"), "w").write(out)
print("slides", len(slides), "with supplements", sum(1 for s in side if s["sup"]))
