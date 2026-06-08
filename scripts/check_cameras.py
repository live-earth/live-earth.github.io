#!/usr/bin/env python3
"""
LIVE EARTH — カメラ死活監視スクリプト

data/cameras.json の各カメラについて、YouTube動画が「公開・埋め込み可能」かを
YouTube oEmbed エンドポイント（APIキー不要）で判定します。

- youtube が動画ID（文字列）       … oEmbedで判定
- youtube が {channel:...}          … チャンネルの現在ライブ。oEmbedでは判定不可のためSKIP
- link / image タイプ               … 対象外（SKIP）

GitHub Actions から毎日実行する想定。死んでいるカメラがあれば終了コード1を返すので、
Actionsの実行が「赤（失敗）」になり、メンテが必要だと気づけます。

判定結果は data/health.json にも書き出します（サイト表示やAPI読み取り用）。

ローカル実行:  python scripts/check_cameras.py
"""
import json, sys, urllib.parse, urllib.request, urllib.error, os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cameras.json")
HEALTH = os.path.join(ROOT, "data", "health.json")
OEMBED = "https://www.youtube.com/oembed"


def check_video(video_id):
    """埋め込み可能なら(True, タイトル)、不可なら(False, 理由)を返す。"""
    watch = f"https://www.youtube.com/watch?v={video_id}"
    url = OEMBED + "?" + urllib.parse.urlencode({"url": watch, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "live-earth-checker"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            return True, data.get("title", "")
    except urllib.error.HTTPError as e:
        # 401/403/404 = 非公開・埋め込み禁止・削除済みなど
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"error {e}"


def main():
    with open(DATA, encoding="utf-8") as f:
        doc = json.load(f)

    ok, dead, skipped = [], [], []
    for cam in doc["cameras"]:
        name = cam.get("name", "?")
        yt = cam.get("youtube")
        if cam.get("link") or cam.get("image") or not yt or isinstance(yt, dict):
            skipped.append(name)
            continue
        alive, info = check_video(yt)
        if alive:
            ok.append((name, info))
        else:
            dead.append((name, yt, info))

    print(f"✅ 再生可能: {len(ok)}")
    for n, t in ok:
        print(f"   - {n}  «{t}»")
    print(f"⏭  対象外(リンク/静止画/チャンネル): {len(skipped)}")
    print(f"❌ 再生不可: {len(dead)}")
    for n, vid, reason in dead:
        print(f"   - {n}  (id={vid}, {reason})  → cameras.json のIDを更新してください")

    # 結果を data/health.json に書き出す（サイト表示 / API読み取り用）
    health = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {"ok": len(ok), "skipped": len(skipped), "dead": len(dead)},
        "ok": [{"name": n, "title": t} for n, t in ok],
        "skipped": skipped,
        "dead": [{"name": n, "id": vid, "reason": reason} for n, vid, reason in dead],
    }
    with open(HEALTH, "w", encoding="utf-8") as f:
        json.dump(health, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 死んでいるカメラがあれば失敗扱いにして気づけるようにする
    if dead:
        sys.exit(1)


if __name__ == "__main__":
    main()
