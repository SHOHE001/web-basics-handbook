# Chapter 4: データ形式

> Status: 完了

## この章で学ぶこと

- HTTP のボディに乗ってくるのは **ただの文字列（または バイト列）** であること
- HTML / JSON / CSV、それぞれの形と使い分け
- **MIME タイプ** と `Content-Type` の関係
- 文字コード（UTF-8 中心）— なぜ「文字化け」が起きるのか
- Python で JSON ↔ dict、CSV ↔ dict のリストの変換

## 前提知識

- [Chapter 3](../03-http/README.md) を読み終えていること。とくに「ヘッダーとボディ」「`Content-Type`」が頭に入っていれば OK。

## 本文

### 1. なぜ「データ形式」が独立した章になるか

Chapter 3 で見たように、HTTP のレスポンスのボディには **HTML でも JSON でも CSV でも画像でも何でも** 入ります。Web を成り立たせているのは「ただのテキスト（または バイト列）の往復」だけど、その中身がどの形式かによって読み方が変わる。

<mark>「サーバーが何を返してきたか」「ブラウザや JS がそれをどう解釈するか」を担当するのが `Content-Type` ヘッダーと、そこに書かれた **MIME タイプ**</mark> です。この章は「ボディの中身は何で、どう読むのか」を扱います。

### 2. HTML — Web ページの構造を書く言語

**HTML（HyperText Markup Language）** は、Web ページの構造を表現するための **マークアップ言語** です。プログラミング言語ではない、というのは Chapter 1 でも触れたとおり。

#### 最小の HTML

```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <title>はじめてのページ</title>
  </head>
  <body>
    <h1>こんにちは</h1>
    <p>これは <a href="https://example.com">リンク</a> です。</p>
  </body>
</html>
```

- `<タグ>...</タグ>` で要素を作る
- `<タグ 属性="値">` で要素に情報を添える
- `<!DOCTYPE html>` は「これは HTML5 です」の宣言（おまじない）
- `<meta charset="utf-8" />` は <mark>**文字コード宣言**。なくてもブラウザが推測してくれることが多いが、推測を外すと文字化けする</mark>

**実例**: 適当なサイトで `Ctrl + U`（表示 → ソースを表示）すると HTML 全文が見えます。X や YouTube みたいな大きなサイトはタグの嵐になっていますが、根本の構造は上の例と同じです。

#### よく出るタグ

| タグ | 役割 |
|---|---|
| `<h1>`〜`<h6>` | 見出し |
| `<p>` | 段落 |
| `<a href="...">` | リンク |
| `<img src="..." alt="...">` | 画像 |
| `<ul>` `<ol>` `<li>` | リスト |
| `<table>` `<tr>` `<td>` | 表 |
| `<div>` `<span>` | 意味を持たない箱（レイアウト用） |
| `<form>` `<input>` `<button>` | フォーム |
| `<script>` | JavaScript の埋め込み |
| `<link>` `<style>` | CSS の読み込み・埋め込み |

#### HTML はだいたい寛容

HTML はブラウザがかなり頑張って解釈してくれる、という設計です。閉じタグを忘れても、属性のクオートを外しても、それなりに表示されてしまうことが多い。これは初心者には親切ですが、ちゃんと書かれていないと **ブラウザの解釈が想定とズレてレイアウトが崩れる** ので、書くときは省略しないのが無難です。

**実例**: 開発者ツールの `Elements` タブで見える HTML は、あなたが書いた HTML を **ブラウザが解釈して直したもの** です。ソース表示（`Ctrl + U`）の HTML とは微妙に違うことがあります。

### 3. JSON — API のデファクト

**JSON（JavaScript Object Notation）** は、データ構造をテキストで表現するための形式。元は JavaScript の文法から派生しましたが、今では言語を問わず使われています。

```json
{
  "name": "Alice",
  "age": 22,
  "is_student": true,
  "favorites": ["python", "music", null],
  "address": {
    "city": "Tokyo",
    "zip": "100-0001"
  }
}
```

#### JSON のデータ型

- 文字列（`"hello"`）— <mark>**ダブルクオート必須**。シングルクオートは不可</mark>
- 数値（`42`, `3.14`）— クオートしない
- 真偽値（`true`, `false`）— 小文字
- `null` — 小文字
- 配列（`[1, 2, 3]`）
- オブジェクト（`{"key": "value"}`）

たったこれだけ。シンプルが売り。

#### なぜ JSON が主流になったか

昔は **XML** が主流でした。

```xml
<user>
  <name>Alice</name>
  <age>22</age>
</user>
```

JSON だと、

```json
{"name": "Alice", "age": 22}
```

- **短い**: 文字数が少ない（通信量が少ない）
- **JavaScript と相性が良い**: ブラウザの JS が `JSON.parse` 一発で扱える
- **データ型がある**: XML は何でも文字列だけど、JSON は数値・真偽値・null が区別できる
- **書きやすい・読みやすい**

この実用面の良さで、<mark>**API のレスポンス形式は 2010 年代以降ほぼ JSON が標準**</mark>になりました。

**実例**:
- Twitter / X、YouTube、Google Maps、Instagram、ほぼ全ての Web API のレスポンスは JSON
- ブラウザ開発者ツールの `Network → Response` で「綺麗に整形された JSON」が表示されるのは、ブラウザが `Content-Type: application/json` を見て「これは JSON だな」と解釈してくれているから

#### JSON にはコメントが書けない

<mark>`#` でも `//` でも `/* */` でもダメ。仕様で禁止されています</mark>。設定ファイルとして使うときに困りがちで、これを嫌って **JSONC**（コメントを書ける JSON 風の形式。VS Code の設定ファイルで採用）や、より読み書きしやすい設定ファイル形式である **YAML**（インデントで階層を表す。`docker-compose.yml` などで使われる）、**TOML**（`key = value` 形式。Python の `pyproject.toml` などで使われる）といった派生・代替が生まれました。

### 4. CSV — 表計算と相性のいい古参

**CSV（Comma Separated Values）** は、行ごとに 1 レコード、列をカンマで区切る、超単純な形式。

```csv
name,age,is_student
Alice,22,true
Bob,30,false
"Carol, the great",25,true
```

- 1 行目を **ヘッダー行**（列名）にすることが多い
- 値にカンマや改行を含めたいときは `"..."` で囲む
- 文字コード問題が起きやすい（後述）

Excel や Google スプレッドシートとそのままやり取りできるので、業務データ・分析データの世界では今でも CSV が大量に流通しています。

**実例**: 銀行の取引明細をダウンロードすると CSV が多い。Google フォームの回答集計、Wikipedia の表データ、政府の統計データなど、「人が表計算で開くこと前提のデータ」は CSV が定番。

#### TSV

`Tab Separated Values`。カンマの代わりにタブで区切る。値にカンマを含むことが多いデータ（住所など）で使われがち。中身は CSV とほぼ同じ。

### 5. MIME タイプと `Content-Type`

サーバーが「このボディは何の形式か」を伝えるのが `Content-Type` ヘッダーで、その値が **MIME タイプ**。「`タイプ/サブタイプ`」という形式です。

| MIME タイプ | 中身 |
|---|---|
| `text/html` | HTML |
| `text/plain` | プレーンテキスト |
| `text/css` | CSS |
| `text/csv` | CSV |
| `application/json` | JSON |
| `application/xml` | XML |
| `text/javascript` | JavaScript（RFC 9239 で推奨。`application/javascript` も歴史的に広く使われている） |
| `application/pdf` | PDF |
| `application/octet-stream` | 種類不明のバイナリ |
| `image/png` | PNG 画像 |
| `image/jpeg` | JPEG 画像 |
| `image/svg+xml` | SVG（ベクター画像、中身は XML） |
| `audio/mpeg` | MP3 |
| `video/mp4` | MP4 |
| `multipart/form-data` | フォーム（ファイルアップロード） |
| `application/x-www-form-urlencoded` | フォーム（普通の送信） |

#### `text/*` と `application/*` の違い

ざっくり言うと、

- **`text/*`**: テキストで、人間がそのまま読んでもなんとなく意味が分かる
- **`application/*`**: プログラムが解釈する前提のもの（JSON や PDF や ZIP）

<mark>JSON は **`application/json`** で、`text/json` ではない</mark>ので注意。

#### `charset`

`Content-Type: text/html; charset=utf-8` のように、後ろに **文字コード** を添えられます。<mark>これがないとブラウザが文字コードを推測することになり、推測を外すと文字化けします</mark>。

**実例**: 開発者ツールの `Network` から通信を 1 つ選んで `Headers → Response Headers` を見ると、`Content-Type: application/json` とか `Content-Type: text/html; charset=utf-8` が必ず付いているのが分かります。

#### MIME はファイル拡張子の代わり

OS（とくに Windows）はファイル拡張子で種類を判断しますが、<mark>**Web の通信ではファイル拡張子に頼らず `Content-Type` で判断するのが原則**</mark>。URL の末尾が `.json` でも、サーバーが `Content-Type: text/html` で返してきたらブラウザは HTML として解釈します（そして表示が壊れる）。

### 6. 文字コード — UTF-8 の話

#### なぜ文字コードが必要か

コンピュータは 0 と 1 しか扱えない。だから「あ」「a」「漢」のような文字を **数値に対応付けるルール（文字コード）** が必要です。

#### 主な文字コード

| 文字コード | 守備範囲 | 1 文字のバイト数 |
|---|---|---|
| **ASCII** | 英数字・記号（128 種類） | 1 バイト |
| **Shift_JIS** | 日本語向け（昔の Windows・古いガラケー） | 1〜2 バイト |
| **EUC-JP** | 日本語向け（昔の UNIX） | 1〜3 バイト |
| **UTF-8** | 世界中の文字（Unicode） | 1〜4 バイト（英数字は 1 バイト） |
| **UTF-16** | 世界中の文字（Unicode） | 2 or 4 バイト |

#### UTF-8 が標準になった

理由は単純で、

- **世界中の文字を 1 つの規格で扱える**（多言語サイトでも 1 つのファイルで OK）
- **ASCII と互換**（英数字部分は ASCII と同じバイト列）
- **どの言語からも扱いやすい**

今では <mark>**「文字コード＝とりあえず UTF-8」が世界の合意事項**</mark>。HTML5 の標準も UTF-8 です。

#### 文字化けが起きる理由

文字化けは <mark>**「保存したときの文字コードと、読むときの文字コードがズレている」**</mark> ときに起きます。

| 例 | 保存 | 読む側の解釈 | 結果 |
|---|---|---|---|
| 1 | UTF-8 | UTF-8 | 正しく表示 |
| 2 | Shift_JIS | UTF-8 | 「縺ゅ＞縺・▲縺」みたいな化け方 |
| 3 | UTF-8 | Shift_JIS | 「・蜈・蜉幢ｼ・」みたいな化け方 |

ブラウザの推測がだいたい当たるので最近は派手な化けに出くわす機会が減りましたが、**API が UTF-8 で返してきた JSON を、`charset=shift_jis` で誤って解釈する** とアプリ側で派手に化けます。

**実例**:
- 古い日本企業のサイトを開くと、たまにブラウザ上部に「文字エンコーディングを指定」みたいなメニューが出ることがありますよね。あれは「サイトが文字コードを宣言してないので、ブラウザが推測している」サイン
- CSV を Excel で開くと文字化けする件: Excel は CSV を Shift_JIS だと思い込みがちで、UTF-8 で保存された CSV を化けさせる。回避策として **BOM 付き UTF-8** で保存することがある

#### BOM

**BOM（Byte Order Mark）** はもともと UTF-16 や UTF-32 で **バイト並び順（エンディアン）** を示すための目印で、Unicode 文字 `U+FEFF` をファイル先頭に置きます。**UTF-8 にはバイト順の概念がない** ので本来 BOM は不要なのですが、`U+FEFF` を UTF-8 で符号化した **3 バイト（`EF BB BF`）** を「これは UTF-8 です」のマーカーとして流用することがあり、これを **UTF-8 BOM** と呼びます。Excel 対策で付けることがあるが、Unicode 標準では UTF-8 への BOM 付与は推奨されておらず、付けるとプログラム側が「最初の文字が変な空白に見える」とハマることもある諸刃の剣です。

### 7. データ形式と HTTP の組み合わせ

ここまでの話を Chapter 3 の HTTP につなげると、

```
[サーバー]                      [クライアント]
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 42

{"name": "Alice", "age": 22}    ← 「ただのテキスト」
                                  ↓
                                  クライアントは Content-Type を見て
                                  「これは JSON だな」と判断し、
                                  JSON としてパースして dict / object にする
```

サーバーは **テキストを送るだけ**。「これは JSON だよ」と教えているのは `Content-Type` ヘッダー。クライアントはそれを信じてパースする。<mark>**だから `Content-Type` を間違えると全てが壊れる**</mark>。

逆に言えば、`Content-Type` さえ正しければ、ボディの中身はテキストでもバイナリでも JSON でも CSV でも自由。HTTP は形式に依存しない、汎用の運び屋です。

## 手を動かすパート

`code/` 配下に 3 本のスクリプトがあります。Python の **標準ライブラリだけ** で書かれていて、追加インストールは不要です。

```powershell
cd chapters\04-data-format\code

# 1. JSON と Python dict の相互変換
python 01_json_basics.py

# 2. CSV をパースして dict のリストに変換、結果を JSON で書き出し
python 02_csv_parse.py

# 3. ファイル拡張子から MIME タイプを判定する
python 03_mime_types.py
```

データのサンプルとして `code/sample.csv` も同梱しています。

`02_csv_parse.py` は CSV を読んで JSON に変換するだけのスクリプトですが、`Content-Type` の発想と直結します。「同じデータでも形式を変えれば違うアプリで使える」という体験。

## つまずきポイント

- <mark>**JSON のクオートはダブル必須**</mark>: `{'name': 'Alice'}` は **Python の dict としてはアリ** だが JSON としては不正。`json.dumps()` を通すと自動で正しい JSON になる
- **JSON にコメントは書けない**: 設定ファイルに使いたくなると詰まる。YAML / TOML / JSONC を検討する
- <mark>**CSV のエンコーディング事故**</mark>: 日本語 CSV は Shift_JIS と UTF-8 の両方が世の中に流れていて事故りやすい。`open()` の `encoding=` を意識する
- **`Content-Type` を信じすぎない**: サーバーが間違ったヘッダーを返してくることもある。とくに古い API はあてにならない
- **`text/html` でも文字化けは起きる**: `charset=utf-8` を付け忘れたサイトはブラウザの推測次第で化ける
- <mark>**拡張子と MIME は別**</mark>: 拡張子 `.json` のファイルでも、サーバーが `text/html` で返したらブラウザは HTML として扱う

## 次の章へ

次は **[Chapter 5: Web アプリ](../05-web-app/README.md) ★ 実装重め**。ここまでに学んだ「URL・HTTP・JSON」を全部使って、自分で簡単な API を立てて、自分のブラウザの JS から叩きます。CORS エラーをわざと出して直す関門もあります。

## 重要な単語まとめ

| 用語 | 一言で言うと | 身近な実例 |
|---|---|---|
| **HTML** | Web ページの構造を書くマークアップ言語 | `Ctrl + U` でソース表示 |
| **タグ / 属性** | HTML の要素と、それに添える情報 | `<a href="..."></a>` |
| **JSON** | データ構造を表現するテキスト形式 | API のレスポンスはほぼ全部これ |
| **XML** | JSON の前世代の表現形式 | RSS フィード、Office ファイルの中身 |
| **CSV / TSV** | 行 1 件・カンマ（タブ）区切りの素朴な形式 | Excel、Google フォーム、銀行明細 |
| **MIME タイプ** | データ形式の標準名（`タイプ/サブタイプ`） | `application/json`, `image/png` |
| **`Content-Type`** | ボディの形式を伝える HTTP ヘッダー | `application/json; charset=utf-8` |
| **`charset`** | 文字コードの指定 | `charset=utf-8` |
| **文字コード** | 文字 ↔ バイト列の対応ルール | UTF-8, Shift_JIS, EUC-JP |
| **UTF-8** | Unicode を 1〜4 バイトで表す。世界標準 | HTML5 の標準、Web の事実上の標準 |
| **文字化け** | 保存時と読込時の文字コードがズレた結果 | 「縺ゅ＞縺・▲縺」みたいな表示 |
| **BOM** | UTF-8 を示すファイル先頭 3 バイトの目印 | Excel が CSV を化けさせない対策で付ける |
| **`application/x-www-form-urlencoded`** | 普通のフォーム送信の MIME | ログインフォームの POST ボディ |
| **`multipart/form-data`** | ファイルアップロード用 MIME | 画像投稿フォーム |
