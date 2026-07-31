# WordPress へのオファーバナー設置手順

作成した4枚のバナー画像を、各症状ページのWordPressに設置する手順です。

## STEP 1. 画像をアップロード
1. WordPress管理画面 →「メディア」→「新規追加」
2. 以下の4枚をアップロード
   - `offer-banner_腰痛.png`
   - `offer-banner_坐骨.png`
   - `offer-banner_脊柱管.png`
   - `offer-banner_ヘルニア.png`
3. アップロード後、各画像の「ファイルのURL」をコピーしておく
   （例: `https://あなたのサイト/wp-content/uploads/2026/07/offer-banner_脊柱管.png`）

## STEP 2. バナーを設置
各症状ページの、設置したい位置に「カスタムHTML」ブロックを追加し、
下のコードを貼り付けます。`【画像URL】`と`【予約リンク】`を差し替えてください。

### 腰痛ページ用
```html
<div style="max-width:600px;margin:24px auto;text-align:center;">
  <a href="【予約リンク】">
    <img src="【腰痛バナーの画像URL】" alt="腰痛でお悩みの方へ 初回限定特別価格2,980円 66%OFF"
         style="width:100%;height:auto;display:block;border:0;border-radius:8px;" />
  </a>
</div>
```

### 坐骨ページ用
```html
<div style="max-width:600px;margin:24px auto;text-align:center;">
  <a href="【予約リンク】">
    <img src="【坐骨バナーの画像URL】" alt="坐骨でお悩みの方へ 初回限定特別価格2,980円 66%OFF"
         style="width:100%;height:auto;display:block;border:0;border-radius:8px;" />
  </a>
</div>
```

### 脊柱管ページ用
```html
<div style="max-width:600px;margin:24px auto;text-align:center;">
  <a href="【予約リンク】">
    <img src="【脊柱管バナーの画像URL】" alt="脊柱管でお悩みの方へ 初回限定特別価格2,980円 66%OFF"
         style="width:100%;height:auto;display:block;border:0;border-radius:8px;" />
  </a>
</div>
```

### ヘルニアページ用
```html
<div style="max-width:600px;margin:24px auto;text-align:center;">
  <a href="【予約リンク】">
    <img src="【ヘルニアバナーの画像URL】" alt="ヘルニアでお悩みの方へ 初回限定特別価格2,980円 66%OFF"
         style="width:100%;height:auto;display:block;border:0;border-radius:8px;" />
  </a>
</div>
```

- ボタン（リンク）が不要な場合は `<a>...</a>` を外して `<img ...>` だけでOKです。
- `max-width:600px` は表示幅の目安です。大きくしたい場合は数値を変更してください。

## （任意）私が直接WordPressに設置する場合
以下をご用意いただければ、REST API 経由でこちらから画像アップロード〜ページ反映まで行えます。
1. サイトのURL（例: `https://example.com`）
2. WordPressのユーザー名
3. 「アプリケーションパスワード」（管理画面 → ユーザー → プロフィール → アプリケーションパスワードで発行）
4. どのページ（URLまたはページ名）に設置するか

※アプリケーションパスワードは通常のログインパスワードとは別物で、後からいつでも失効できます。
