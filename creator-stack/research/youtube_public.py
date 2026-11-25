#!/usr/bin/env python3
"""Read-only, two-request public YouTube topic reconnaissance. Python standard library."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener

BASE = "https://www.googleapis.com/youtube/v3/"
ID = re.compile(r"[A-Za-z0-9_-]{11}")
DURATION = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def public_get(resource, params, key):
    if resource not in {"search", "videos"}:
        raise ValueError("Only search and videos are permitted.")
    req = Request(BASE + resource + "?" + urlencode(params),
                  headers={"X-Goog-Api-Key": key, "Accept": "application/json"}, method="GET")
    with build_opener(NoRedirect).open(req, timeout=20) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Unexpectedly large API response.")
        return json.loads(raw)

def parse_duration(value):
    m = DURATION.fullmatch(value or "")
    if not m:
        return None
    h, m_, s = (int(x or 0) for x in m.groups())
    return 3600*h + 60*m_ + s

def search(query, region, lang, days, max_results, seconds, key, fetch=public_get, now=None):
    now = now or datetime.now(timezone.utc)
    found = fetch("search", dict(part="snippet", type="video", order="relevance", q=query,
                  regionCode=region, relevanceLanguage=lang, maxResults=max_results,
                  publishedAfter=(now-timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")), key)
    ids = list(dict.fromkeys(row.get("id", {}).get("videoId", "") for row in found.get("items", [])))
    ids = [x for x in ids if ID.fullmatch(x)][:max_results]
    records = []
    if ids:
        page = fetch("videos", dict(part="snippet,statistics,contentDetails", id=",".join(ids)), key)
        for row in page.get("items", []):
            vid = row.get("id")
            if vid not in ids:
                continue
            sn, st = row.get("snippet", {}), row.get("statistics", {})
            total = parse_duration(row.get("contentDetails", {}).get("duration"))
            if seconds and (not total or total > seconds):
                continue
            published = sn.get("publishedAt")
            try:
                age = max(1.0, (now-datetime.fromisoformat(published.replace("Z","+00:00"))).total_seconds()/86400)
                count = int(st["viewCount"])
                rate = round(count/age)
            except (ValueError, TypeError, KeyError, AttributeError):
                count, rate = None, None
            records.append({"title": sn.get("title", ""), "channel": sn.get("channelTitle", ""),
                            "url": f"https://www.youtube.com/watch?v={vid}", "published_at": published,
                            "duration_seconds":total, "views": count, "views_per_day_estimate":rate})
    records.sort(key=lambda item: item["views_per_day_estimate"] if item["views_per_day_estimate"] is not None else -1, reverse=True)
    return {"query":query,"observed_at":now.isoformat(),"region":region,
            "language_hint":lang,"sample_note":"Relevance sample; age-adjusted views are directional. Duration alone does not confirm Shorts format.",
            "videos":records}

def demo_fetch(resource, params, unused):
    if resource == "search":
        return {"items": [{"id":{"videoId":v}} for v in ("test0000001", "test0000002","bad")]}
    assert params["id"]=="test0000001,test0000002"
    return {"items": [
        {"id":"test0000001","snippet":{"title":"Synthetic test: ocean story","channelTitle":"Fixture","publishedAt":"2026-11-20T08:00:00Z"},"statistics":{"viewCount":"2000"},"contentDetails":{"duration":"PT42S"}},
        {"id":"test0000002","snippet":{"title":"Synthetic test: long film","publishedAt":"2026-11-21T08:00:00Z"},"contentDetails":{"duration":"PT5M"}},
        {"id":"test0000003","snippet":{"title":"unexpected id"},"contentDetails":{"duration":"PT20S"}}
    ]}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("query",nargs="?")
    p.add_argument("--region",default="US")
    p.add_argument("--lang",default="en")
    p.add_argument("--days",type=int,default=90)
    p.add_argument("--limit",type=int,default=15)
    p.add_argument("--max-seconds",type=int,default=180,help="0 disables duration filtering")
    p.add_argument("--self-test", action="store_true")
    a=p.parse_args()
    if a.self_test:
        result=search("fiction","US","en",90,15,180,"",demo_fetch,datetime(2026,11,25,8,tzinfo=timezone.utc))
        assert len(result["videos"])==1 and result["videos"][0]["views_per_day_estimate"]==400
        assert parse_duration("PT1H2M3S")==3723 and parse_duration("garbage") is None
        print("Offline fixture OK: ID filtering, duration, statistics and ranking.")
        return
    key=os.environ.get("YOUTUBE_API_KEY","").strip()
    if not a.query or not key:
        p.error("Provide a topic and set YOUTUBE_API_KEY in the local environment (or use --self-test).")
    if not (1<=a.days<=365 and 1<=a.limit<=25 and 0<=a.max_seconds<=3600 and re.fullmatch(r"[A-Za-z]{2}",a.region) and re.fullmatch(r"[a-z]{2,3}",a.lang)):
        p.error("Invalid range or region/language code.")
    try:
        result=search(a.query,a.region.upper(),a.lang,a.days,a.limit,a.max_seconds,key)
    except HTTPError as exc:
        raise SystemExit(f"YouTube API HTTP {exc.code}. Check API activation, key restrictions and quota.") from None
    except (URLError, ValueError, TimeoutError):
        raise SystemExit("YouTube API response could not be read.") from None
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
