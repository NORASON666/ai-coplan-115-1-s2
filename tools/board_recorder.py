# 討論板常駐錄製：訂閱 ntfy 頻道，每一筆回報立刻寫進 GDrive（jsonl 原始檔＋可讀 md）
# 為什麼要有它：ntfy 只保留 12 小時，簡報端只存在投影那台電腦的瀏覽器；這支讓紀錄不依賴任何一台瀏覽器
# 用法：python board_recorder.py <頻道> <輸出資料夾> <結束時間 YYYY-MM-DDTHH:MM> [開始時間：早於此的訊息不收]
import json, os, sys, time, urllib.request, datetime
TOPIC, OUT, END = sys.argv[1], sys.argv[2], datetime.datetime.fromisoformat(sys.argv[3])
START = datetime.datetime.fromisoformat(sys.argv[4]).timestamp() if len(sys.argv) > 4 else 0
os.makedirs(OUT, exist_ok=True)
RAW = os.path.join(OUT, f"{TOPIC}_原始.jsonl"); MD = os.path.join(OUT, "小組討論紀錄_1113_自動備份.md")
seen = set()
if os.path.exists(RAW):
    for l in open(RAW, encoding="utf-8"):
        try: seen.add(json.loads(l)["id"])
        except Exception: pass

def write_md():
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8")] if os.path.exists(RAW) else []
    latest, edits = {}, {}
    for ev in sorted(rows, key=lambda x: x["time"]):
        try: d = json.loads(ev["message"])
        except Exception: continue
        k = (int(d.get("q", 0)), int(d.get("g", 0)))
        latest[k] = (ev["time"], str(d.get("t", ""))); edits[k] = edits.get(k, 0) + 1
    out = [f"# 115-1 港湖區分區共備 場次二 小組討論紀錄（自動備份，更新於 {time.strftime('%F %T')}）\n",
           "> 每組每主題只列最新一版；完整修改歷程在同資料夾的 jsonl 原始檔。\n"]
    latest = {k: v for k, v in latest.items() if v[1].strip()}   # 最新一版是「清除」就不列
    for q in sorted({k[0] for k in latest}):
        out.append(f"\n## 主題 {q}\n")
        for g in sorted(k[1] for k in latest if k[0] == q):
            t, txt = latest[(q, g)]
            out.append(f"\n### 第 {g} 組（{time.strftime('%H:%M', time.localtime(t))} 最後修改，共 {edits[(q, g)]} 版）\n\n{txt}\n")
    tmp = MD + ".tmp"; open(tmp, "w", encoding="utf-8").write("".join(out)); os.replace(tmp, MD)

def log(*a): print(time.strftime("%F %T"), *a, flush=True)
write_md()
while datetime.datetime.now() < END:
    try:
        # since=all：重連時把 12 小時內的都再拉一次，用 id 去重，斷線期間不會漏
        with urllib.request.urlopen(f"https://ntfy.sh/{TOPIC}/json?since=all", timeout=90) as r:
            log("已連線")
            for line in r:
                if datetime.datetime.now() >= END: break
                ev = json.loads(line)
                if ev.get("event") != "message" or ev["id"] in seen or ev["time"] < START: continue
                seen.add(ev["id"])
                with open(RAW, "a", encoding="utf-8") as f: f.write(json.dumps(ev, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())
                write_md(); log("收到", ev["id"])
    except Exception as e:
        log("重連", type(e).__name__, str(e)[:80]); time.sleep(5)
log("到結束時間，停止")
