#!/usr/bin/env python3
"""
ヤマネ整体院 WordPress へオファーバナーを設置するインストーラー。

GitHub Actions 上（外部サイトへ接続可能な環境）で実行する前提。
認証は WordPress の「アプリケーションパスワード」を使った Basic 認証。

必要な環境変数（GitHub Secrets 推奨）:
  WP_SITE          例: https://yamane-seitai.com   (未設定なら下記 DEFAULT_SITE)
  WP_USER          WordPress のユーザー名
  WP_APP_PASSWORD  アプリケーションパスワード（管理画面→ユーザー→プロフィールで発行）

任意の実行オプション（環境変数）:
  MODE       "install"(既定) = メディアへアップロード + 各症状ページへバナー挿入
             "media_only"    = メディアへアップロードのみ（URLを出力）
  POSITION   "top"(既定) / "bottom"  … 本文への挿入位置
  DRY_RUN    "1" にすると、対象ページの検出結果を表示するだけで書き込まない
  PAGE_MAP   JSON。症状→ページID を明示指定する場合。例: {"腰痛":12,"坐骨":34}
"""
import base64
import json
import os
import sys
import mimetypes

import requests

DEFAULT_SITE = "https://yamane-seitai.com"
HERE = os.path.dirname(os.path.abspath(__file__))

# 症状 → バナー画像ファイル
BANNERS = {
    "腰痛":     "offer-banner_腰痛.png",
    "坐骨":     "offer-banner_坐骨.png",
    "脊柱管":   "offer-banner_脊柱管.png",
    "ヘルニア": "offer-banner_ヘルニア.png",
}

TIMEOUT = 60


def env(name, default=None):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def auth_header():
    user = env("WP_USER")
    pw = env("WP_APP_PASSWORD")
    if not user or not pw:
        sys.exit("ERROR: WP_USER / WP_APP_PASSWORD が未設定です。GitHub Secrets に登録してください。")
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def banner_html(symptom, img_url):
    return (
        f'<!-- claude-offer-banner:START:{symptom} -->\n'
        f'<div class="claude-offer-banner" '
        f'style="max-width:600px;margin:24px auto;text-align:center;">\n'
        f'  <img src="{img_url}" '
        f'alt="{symptom}でお悩みの方へ 初回限定特別価格2,980円 66%OFF" '
        f'style="width:100%;height:auto;display:block;border:0;border-radius:8px;" />\n'
        f'</div>\n'
        f'<!-- claude-offer-banner:END:{symptom} -->'
    )


def find_existing_media(site, headers, filename):
    slug = os.path.splitext(filename)[0]
    r = requests.get(f"{site}/wp-json/wp/v2/media",
                     params={"search": slug, "per_page": 20},
                     headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    for m in r.json():
        src = m.get("source_url", "")
        if os.path.basename(src).startswith(slug) or m.get("slug", "").startswith(slug):
            return m["id"], src
    return None, None


def upload_media(site, headers, path):
    filename = os.path.basename(path)
    mid, src = find_existing_media(site, headers, filename)
    if mid:
        print(f"  既存メディアを再利用: id={mid} {src}")
        return mid, src
    ctype = mimetypes.guess_type(filename)[0] or "image/png"
    with open(path, "rb") as f:
        data = f.read()
    # Content-Disposition のファイル名は ASCII が無難なので filename* を併用
    h = dict(headers)
    h["Content-Type"] = ctype
    h["Content-Disposition"] = f"attachment; filename*=UTF-8''{requests.utils.quote(filename)}"
    r = requests.post(f"{site}/wp-json/wp/v2/media", headers=h, data=data, timeout=TIMEOUT)
    if r.status_code not in (200, 201):
        print(f"  アップロード失敗 {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    j = r.json()
    print(f"  アップロード完了: id={j['id']} {j['source_url']}")
    return j["id"], j["source_url"]


def discover_target(site, headers, symptom):
    """症状名でページ/投稿を検索し、最も確からしいものを返す。"""
    for kind in ("pages", "posts"):
        r = requests.get(f"{site}/wp-json/wp/v2/{kind}",
                         params={"search": symptom, "per_page": 20,
                                 "status": "publish", "context": "edit"},
                         headers=headers, timeout=TIMEOUT)
        if r.status_code != 200:
            continue
        items = r.json()
        # タイトル/スラッグに症状名を含むものを優先
        def score(it):
            t = (it.get("title", {}) or {}).get("raw") or (it.get("title", {}) or {}).get("rendered", "")
            s = it.get("slug", "")
            return (symptom in t) * 2 + (symptom in s)
        items = [it for it in items if score(it) > 0]
        items.sort(key=score, reverse=True)
        if items:
            it = items[0]
            t = (it.get("title", {}) or {}).get("raw") or (it.get("title", {}) or {}).get("rendered", "")
            return kind, it["id"], t
    return None, None, None


def get_content(site, headers, kind, pid):
    r = requests.get(f"{site}/wp-json/wp/v2/{kind}/{pid}",
                     params={"context": "edit"}, headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["content"]["raw"]


def upsert_banner(content, symptom, html, position):
    start = f"<!-- claude-offer-banner:START:{symptom} -->"
    end = f"<!-- claude-offer-banner:END:{symptom} -->"
    if start in content and end in content:
        pre = content[:content.index(start)]
        post = content[content.index(end) + len(end):]
        return pre + html + post, "更新"
    if position == "bottom":
        return content + "\n\n" + html, "末尾に追加"
    return html + "\n\n" + content, "先頭に追加"


def main():
    site = env("WP_SITE", DEFAULT_SITE).rstrip("/")
    mode = env("MODE", "install")
    position = env("POSITION", "top")
    dry = env("DRY_RUN", "0") == "1"
    page_map = json.loads(env("PAGE_MAP", "{}"))
    headers = auth_header()

    print(f"サイト: {site}  モード: {mode}  位置: {position}  DRY_RUN: {dry}")

    # 接続 & 認証チェック
    r = requests.get(f"{site}/wp-json/wp/v2/users/me",
                     headers=headers, timeout=TIMEOUT)
    if r.status_code != 200:
        sys.exit(f"ERROR: 認証/接続に失敗 ({r.status_code}): {r.text[:300]}")
    print(f"認証OK: {r.json().get('name')}")

    # 1) メディアアップロード
    urls = {}
    for symptom, fname in BANNERS.items():
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            print(f"[{symptom}] 画像が見つかりません: {path}"); continue
        print(f"[{symptom}] メディア処理: {fname}")
        _, src = upload_media(site, headers, path)
        urls[symptom] = src

    if mode == "media_only":
        print("\n=== 完了(メディアのみ) ===")
        for s, u in urls.items():
            print(f"{s}: {u}")
        return

    # 2) 各症状ページへ挿入
    print("\n=== ページ設置 ===")
    for symptom, img_url in urls.items():
        if symptom in page_map:
            kind, pid, title = "pages", page_map[symptom], "(指定)"
            # 指定IDがページか投稿か不明なので両方試す
        else:
            kind, pid, title = discover_target(site, headers, symptom)
        if not pid:
            print(f"[{symptom}] 対象ページが見つかりませんでした。手動設置用URL: {img_url}")
            continue
        print(f"[{symptom}] 対象: {kind} id={pid} 「{title}」")
        html = banner_html(symptom, img_url)
        if dry:
            print(f"  DRY_RUN のため書き込みスキップ")
            continue
        # 指定IDの場合は pages→posts の順で取得を試す
        kinds = [kind] if symptom not in page_map else ["pages", "posts"]
        done = False
        for k in kinds:
            try:
                content = get_content(site, headers, k, pid)
            except Exception:
                continue
            new_content, action = upsert_banner(content, symptom, html, position)
            rr = requests.post(f"{site}/wp-json/wp/v2/{k}/{pid}",
                               headers={**headers, "Content-Type": "application/json"},
                               data=json.dumps({"content": new_content}), timeout=TIMEOUT)
            if rr.status_code in (200, 201):
                print(f"  {action}で設置完了 ({k} id={pid})")
                done = True
                break
        if not done:
            print(f"  設置に失敗しました。手動設置用URL: {img_url}")

    print("\n=== 完了 ===")


if __name__ == "__main__":
    main()
