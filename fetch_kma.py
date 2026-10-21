#!/usr/bin/env python3
"""bungeo(붕어빵 장사) 날씨 파일 생성기 — 기상청 초단기실황(getUltraSrtNcst) 8개 도시 → weather.json.
GitHub Actions(공개 레포 · 무료)가 1시간마다 돌려 자기 레포에 커밋한다. 앱은 raw URL 한 파일만 읽는다.
키는 레포 secret KMA_KEY(환경변수). 실패한 도시는 이전 값을 유지하고 stale 플래그를 올린다."""
import json, os, sys, urllib.parse, urllib.request, datetime as dt
KEY = os.environ.get("KMA_KEY", "")
CITIES = {  # 기상청 격자(nx, ny) — weather14 Region 표와 같은 좌표계
    "seoul": (60, 127), "incheon": (55, 124), "daejeon": (67, 100), "daegu": (89, 90),
    "gwangju": (58, 74), "busan": (98, 76), "ulsan": (102, 84), "jeju": (52, 38),
}
OUT = "weather.json"
KST = dt.timezone(dt.timedelta(hours=9))

def fetch(nx, ny, base: dt.datetime):
    q = dict(serviceKey=KEY, pageNo=1, numOfRows=20, dataType="JSON",
             base_date=base.strftime("%Y%m%d"), base_time=base.strftime("%H00"), nx=nx, ny=ny)
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=20) as r:
        body = json.loads(r.read().decode("utf-8"))
    items = body["response"]["body"]["items"]["item"]
    v = {i["category"]: i["obsrValue"] for i in items}
    return dict(tempC=float(v["T1H"]), pty=int(float(v.get("PTY", 0))), rain1h=float(v.get("RN1", 0) or 0),
                wind=float(v.get("WSD", 0) or 0), humidity=float(v.get("REH", 0) or 0))

def main():
    now = dt.datetime.now(KST)
    base = (now - dt.timedelta(minutes=45)).replace(minute=0, second=0, microsecond=0)  # 실황은 매시 40분경 확정
    prev = {}
    if os.path.exists(OUT):
        try: prev = json.load(open(OUT, encoding="utf-8")).get("cities", {})
        except Exception: prev = {}
    cities, fails = {}, []
    for name, (nx, ny) in CITIES.items():
        try:
            d = fetch(nx, ny, base); d["observedAt"] = base.isoformat(); d["stale"] = False
            cities[name] = d
        except Exception as e:  # 이전 값 유지 + stale
            fails.append(f"{name}: {type(e).__name__} {e}")
            if name in prev:
                cities[name] = dict(prev[name], stale=True)
    doc = dict(version=1, generatedAt=now.isoformat(), source="KMA getUltraSrtNcst (기상청 초단기실황)",
               attribution="기상청", cities=cities, failures=fails)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ok cities={len(cities)} fails={len(fails)}", *fails, sep="\n")
    if not cities: sys.exit(1)

if __name__ == "__main__":
    main()
