#!/usr/bin/env python3
"""NEoWave 보조 수집(K6): Bitstamp 코인 6개 시장 15m 완성 봉을 시장별 CSV 끝에 추가(없으면 2022-11-21부터 생성). GitHub Actions 매일 실행."""
import csv, json, os, time, urllib.request, datetime as dt
STEP, START = 900, 1668988800
PAIRS = ["ethusd", "xrpusd", "ltcusd", "bchusd", "xlmusd", "linkusd"]
for pair in PAIRS:
    F = f"Bitstamp_{pair.upper()}_15m.csv"
    if not os.path.exists(F):
        with open(F, "w", newline="", encoding="utf-8") as f:
            f.write("https://www.bitstamp.net/api/v2/ohlc/,,,,,,,\r\nunix,date,symbol,open,high,low,close,volume\r\n")
    rows = list(csv.reader(open(F, encoding="utf-8-sig")))
    last = int(rows[-1][0]) if len(rows) > 2 else START - STEP
    new, now = [], time.time()
    while last + 2 * STEP <= now:
        url = f"https://www.bitstamp.net/api/v2/ohlc/{pair}/?step={STEP}&limit=1000&start={last + STEP}"
        req = urllib.request.Request(url, headers={"User-Agent": "neowave-data"})
        ohlc = json.load(urllib.request.urlopen(req, timeout=30))["data"]["ohlc"]
        got = sorted((o for o in ohlc if int(o["timestamp"]) > last and int(o["timestamp"]) + STEP <= now), key=lambda o: int(o["timestamp"]))
        if not got:
            break
        for o in got:
            t = int(o["timestamp"])
            new.append([t, dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), pair[:-3].upper() + "/USD",
                        o["open"], o["high"], o["low"], o["close"], o["volume"]])
            last = t
        time.sleep(0.5)
    with open(F, "a", newline="", encoding="utf-8") as f:
        csv.writer(f, lineterminator="\r\n").writerows(new)
    print(pair, "added", len(new), "last", dt.datetime.fromtimestamp(last, dt.timezone.utc))
