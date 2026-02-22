# BMI計算機

標準ライブラリのみで動作する最小構成の Python Web アプリです。  
Flask 等の外部ライブラリは不要です。

---

## ファイル構成

```
bmi-app/
├── app.py           # アプリ本体（HTML/CSS/JS含む）
├── requirements.txt # 空（Render用ダミー）
├── .gitignore
└── README.md
```

---

## ローカルで実行する

```bash
# Python 3.10以上を推奨
python app.py
```

起動後、ブラウザで http://localhost:8000 を開いてください。

ポートを変えたい場合:

```bash
PORT=3000 python app.py   # Mac/Linux
set PORT=3000 && python app.py   # Windows
```

---

## Render にデプロイする手順

### 1. GitHub にリポジトリを作成してプッシュ

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
git push -u origin main
```

### 2. Render でサービスを作成

1. https://render.com にサインイン
2. **New → Web Service** をクリック
3. GitHub リポジトリを連携・選択
4. 各設定を以下のように入力:

| 項目 | 値 |
|------|-----|
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |

5. **Create Web Service** をクリック → デプロイ完了まで数分待つ

---

## よくある失敗と対処法

| エラー / 症状 | 原因 | 対処 |
|---|---|---|
| デプロイ後にアクセスできない | `host="127.0.0.1"` で起動している | `host="0.0.0.0"` に修正 |
| `Port scan timeout` エラー | PORT 環境変数を参照していない | `int(os.environ.get("PORT", 8000))` を確認 |
| ページが文字化けする | Content-Type の charset 指定漏れ | `text/html; charset=utf-8` を確認 |
| ビルドが失敗する | requirements.txt が存在しない | 空でも OK なのでファイルを作成 |

---

## 動作確認済み環境

- Python 3.10 / 3.11 / 3.12
- ローカル（Mac / Windows / Linux）
- Render（Python 3 ランタイム）