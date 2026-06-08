# LIVE EARTH — 世界のライブカメラ

世界中のライブカメラを地図上から手軽に閲覧できるサイトです。マーカーをクリックするとポップアップで映像を再生でき、「ミニ窓固定」モードでは複数のカメラを同時に並べて視聴できます。

公開URL: `https://<organization>.github.io/`
（`<organization>` の部分は、実際のOrganization名に置き換えてください）

## 構成

```
.
├─ index.html          サイト本体（HTML/CSS/JS 一体）
├─ data/
│   └─ cameras.json     カメラ台帳（ここを編集してカメラを追加・修正）
├─ assets/              画像・アイコン・OGP画像
├─ articles/            各カメラの解説記事（収益化用に拡張予定）
├─ scripts/             死活監視・データ更新スクリプト（将来）
├─ 404.html
├─ LICENSE
└─ README.md
```

## カメラの追加・編集

`data/cameras.json` の `cameras` 配列に項目を追加します。映像の種類に応じて3つの書き方があります。

YouTube動画（動画IDで指定）:
```json
{ "name": "表示名", "loc": "場所名", "lat": 35.0, "lng": 135.0, "cat": "city", "youtube": "動画ID" }
```

YouTubeチャンネルの「現在のライブ」を常に表示（IDが入れ替わるカメラ向け・推奨）:
```json
{ "name": "表示名", "loc": "場所名", "lat": 35.0, "lng": 135.0, "cat": "city", "youtube": { "channel": "UCxxxxxxxx" } }
```

静止画カメラ（一定間隔で自動更新する河川カメラなど）:
```json
{ "name": "表示名", "loc": "場所名", "lat": 35.0, "lng": 135.0, "cat": "river", "image": { "url": "画像URL", "refresh": 30 } }
```

外部サイトを開くだけ（埋め込み不可のカメラ向け）:
```json
{ "name": "表示名", "loc": "場所名", "lat": 35.0, "lng": 135.0, "cat": "city", "link": "配信ページURL", "note": "補足説明" }
```

`cat` は `data/cameras.json` の `categories` に定義されたキー（city / nature / beach / wildlife / mountain / space / river）を使います。新しいカテゴリを足したいときは `categories` に追記してください。

## ローカルで確認する方法

`index.html` をブラウザで直接開くと、データ読み込みとYouTube埋め込みの両方が動きません（ローカルファイルの制約）。確認するときは、このフォルダで簡易サーバを立ててください。

```
python -m http.server 8000
```

その後ブラウザで `http://localhost:8000/` を開きます。

## 使用している無料サービス

- 地図エンジン: Leaflet（OpenStreetMap / CARTO のタイル）
- マーカー集約: Leaflet.markercluster
- ライブ映像: YouTube 埋め込みプレーヤー
- ISS位置: wheretheiss.at API（キー不要）

## 注意

- ライブ配信の動画IDは配信者の都合で変わることがあります。映像が出ない場合は `cameras.json` のIDを更新するか、`{ "channel": "..." }` 方式に切り替えてください。
- 配信元によっては埋め込みが許可されておらず、その場合は「YouTubeで開く」リンクからの視聴になります。
- 各カメラ映像の著作権は各配信者に帰属します。商用利用（広告・アフィリエイト等）の際は、各配信元の利用規約を確認してください。
