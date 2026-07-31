# ヤマネ整体院 トップLP オファーバナー（症状別）

元のオファーバナー（初回限定 特別価格）の「腰痛」表記を各症状に差し替えたバナー画像です。
背景・レイアウト・価格（2,980円 / 66%OFF）などは元画像のまま、**文字だけ**を変更しています。

## ファイル一覧

| ファイル | 症状 |
| --- | --- |
| `offer-banner_腰痛.png` | 腰痛 |
| `offer-banner_坐骨.png` | 坐骨 |
| `offer-banner_脊柱管.png` | 脊柱管 |
| `offer-banner_ヘルニア.png` | ヘルニア |

サイズ: 1104 × 1425 px（元画像と同一）

差し替えた箇所は以下の3か所です。
1. ヘッダー緑帯「◯◯の方限定の特別価格！」
2. メインコピー（大きい赤文字）「◯◯の 軽減や効果を すぐに実感!!」
3. 「◯◯の方へ」ボックス

## 再生成方法

`make_banner.py` で任意の症状名のバナーを生成できます。
元画像 `orig.png` と、見出し用フォント `ZenKakuGothicNew-Black.ttf`
（Google Fonts / Zen Kaku Gothic New, OFL）が必要です。

```bash
python3 make_banner.py "坐骨" ZenKakuGothicNew-Black.ttf out.png
```
