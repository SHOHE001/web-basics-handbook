"""このハンドブックを「もの文読書室」に置ける静的 HTML に変換する。

- chapters/（Web 編）・fe/（基本情報）・ap/（応用情報）・sc/（支援士）・extras/ の Markdown を HTML にする
- README.md は index.html に、ほかの .md は同じ場所の .html にする
- Markdown 間のリンク（xxx.md）も .html に書き換える
- GitHub の注意書き（> [!CAUTION] など）を色付きの枠にする
- GitHub と解釈が違って崩れるリスト（段落直後で空行なしのリスト、浅いインデントの入れ子リスト）をレンダリング前に正規化する
- 見出しの id は日本語でも空にならないよう slugify_unicode を指定する
- 章ページにはステータス行・章内目次（h2/h3）・パンくず・前後の章のカードを出す
- トップページには各編へ飛ぶチップ・枠付きの編セクション・「続きから読む」を出す
- code/ などの Markdown 以外のファイルはそのままコピーする
- 外部の CDN を使わず、CSS と JS も各ページに埋め込む（オフラインでも読める）

依存は markdown のみ。出力先のフォルダは丸ごと作り直す。読書室の他のファイルを消さないよう、
出力先には読書室の中の「このハンドブック専用のサブフォルダ」を指定すること。

使い方:
    pip install markdown
    python tools/build_reading_room.py --out dist/web-basics-handbook
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

REPO = Path(__file__).resolve().parent.parent
SOURCE_DIRS = ["chapters", "fe", "ap", "sc", "extras"]
BOOK_DIRS = ["chapters", "fe", "ap", "sc"]
SITE_TITLE = "Web と情報処理試験のハンドブック"

ALERT_LABELS = {
    "NOTE": "補足",
    "TIP": "ヒント",
    "IMPORTANT": "重要",
    "WARNING": "警告",
    "CAUTION": "注意",
}

# 各編の定義。見出し（title）とチップの短縮名（chip）をここ1箇所で管理し、
# トップページの見出し・チップ・パンくずの「編の名前」で共有する。
# folder はソースのディレクトリ、top は編の概要ページ（README.md）。extras は番外編。
BOOKS = [
    {"folder": "chapters", "title": "Web 技術の基本", "chip": "Web 技術の基本", "top": None,
     "intro": "ブラウザの裏側で何が起きているかを、Python で再現しながら学ぶ本編です。"},
    {"folder": "fe", "title": "基本情報技術者試験", "chip": "基本情報", "top": "fe/README.md",
     "intro": "本編の知識を試験の分野ごとに整理し直し、科目 A・科目 B に備えるパートです。"},
    {"folder": "ap", "title": "応用情報技術者試験", "chip": "応用情報", "top": "ap/README.md",
     "intro": "基本情報から上乗せされる知識と、記述式の科目 B の解き方を分野ごとにまとめたパートです。"},
    {"folder": "sc", "title": "情報処理安全確保支援士試験", "chip": "支援士", "top": "sc/README.md",
     "intro": "セキュリティの専門家として説明・判断できる深さまで掘り下げるパートです。登録制の資格の仕組みも扱います。"},
    {"folder": "extras", "title": "番外編", "chip": "番外編", "top": None,
     "intro": ""},
]

CSS = """
:root {
  --bg: #fbfaf7; --surface: #ffffff; --text: #1f1d1a; --muted: #6b665e;
  --line: #e4e0d8; --accent: #2f5d8a; --code-bg: #f2efe9; --mark: #fff1a8;
  --caution-bg: #fdecec; --caution-line: #c93c3c;
  --note-bg: #eaf2fb; --note-line: #2f6fb3;
  --tip-bg: #eaf6ee; --tip-line: #2f8a4c;
  --important-bg: #f2ecfb; --important-line: #7a4cc2;
  --toc-active-bg: #e9f0f7;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #171614; --surface: #201f1c; --text: #ece8e1; --muted: #a39d93;
    --line: #36332e; --accent: #8fb8e3; --code-bg: #2a2824; --mark: #5c4f12;
    --caution-bg: #3a1f1f; --caution-line: #e07070;
    --note-bg: #1d2a38; --note-line: #78a9de;
    --tip-bg: #1d3024; --tip-line: #6cc28a;
    --important-bg: #2a2238; --important-line: #ad8be6;
    --toc-active-bg: #24303c;
  }
}
:root[data-theme="dark"] {
  --bg: #171614; --surface: #201f1c; --text: #ece8e1; --muted: #a39d93;
  --line: #36332e; --accent: #8fb8e3; --code-bg: #2a2824; --mark: #5c4f12;
  --caution-bg: #3a1f1f; --caution-line: #e07070;
  --note-bg: #1d2a38; --note-line: #78a9de;
  --tip-bg: #1d3024; --tip-line: #6cc28a;
  --important-bg: #2a2238; --important-line: #ad8be6;
  --toc-active-bg: #24303c;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic UI", "Meiryo", system-ui, sans-serif;
  font-size: 17px; line-height: 1.85; overflow-wrap: break-word;
}
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
header.site, footer.site {
  max-width: 46rem; margin: 0 auto; padding: 12px 16px;
  font-size: 14px; color: var(--muted);
}
header.site { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 8px; border-bottom: 1px solid var(--line); }
header.site a, footer.site a { color: var(--muted); }
header.site .crumb-sep { opacity: .6; }
main { max-width: 46rem; margin: 0 auto; padding: 8px 16px 48px; }
h1, h2, h3, h4 { scroll-margin-top: 1rem; }
h1 { font-size: clamp(1.4rem, 1.1rem + 2vw, 1.9rem); line-height: 1.4; margin: 1.2em 0 .6em; }
h2 { font-size: 1.3rem; line-height: 1.4; margin: 2.2em 0 .6em; padding-bottom: .3em; border-bottom: 2px solid var(--line); }
h3 { font-size: 1.12rem; margin: 1.8em 0 .5em; }
h4 { font-size: 1rem; margin: 1.5em 0 .4em; }
a { color: var(--accent); }
p, li { margin: .5em 0; }
mark { background: var(--mark); color: inherit; padding: 0 .15em; border-radius: 2px; }
code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", "BIZ UDGothic", "Noto Sans Mono CJK JP", "Osaka-Mono", "MS Gothic", monospace; font-size: .88em;
  background: var(--code-bg); padding: .1em .35em; border-radius: 4px; overflow-wrap: anywhere; }
pre { background: var(--code-bg); padding: 12px 14px; border-radius: 8px; overflow-x: auto; line-height: 1.55; }
pre code { background: none; padding: 0; font-size: 14px; overflow-wrap: normal; }
.table-wrap { overflow-x: auto; margin: 1em 0; }
table { border-collapse: collapse; min-width: 100%; font-size: 15px; line-height: 1.6; background: var(--surface); }
th, td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; vertical-align: top; min-width: 5.5em; }
th { background: var(--code-bg); }
blockquote { margin: 1em 0; padding: 4px 16px; border-left: 4px solid var(--line); color: var(--muted); }
blockquote.alert { color: var(--text); border-radius: 6px; padding: 8px 16px; }
blockquote.alert .alert-title { font-weight: 700; margin-bottom: .2em; }
blockquote.alert-caution, blockquote.alert-warning { background: var(--caution-bg); border-left-color: var(--caution-line); }
blockquote.alert-caution .alert-title, blockquote.alert-warning .alert-title { color: var(--caution-line); }
blockquote.alert-note { background: var(--note-bg); border-left-color: var(--note-line); }
blockquote.alert-note .alert-title { color: var(--note-line); }
blockquote.alert-tip { background: var(--tip-bg); border-left-color: var(--tip-line); }
blockquote.alert-tip .alert-title { color: var(--tip-line); }
blockquote.alert-important { background: var(--important-bg); border-left-color: var(--important-line); }
blockquote.alert-important .alert-title { color: var(--important-line); }
.status { color: var(--muted); font-size: 13px; margin: 0 0 .4em; }
/* 章内目次 */
nav.toc { font-size: 14px; line-height: 1.5; }
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc li { margin: 0; }
nav.toc a { display: block; color: var(--muted); text-decoration: none; padding: 4px 8px; border-radius: 4px; }
nav.toc a:hover { color: var(--text); background: var(--code-bg); }
nav.toc a.active { color: var(--text); background: var(--toc-active-bg); }
nav.toc li.toc-h3 a { padding-left: 24px; }
/* スマホ・狭い画面の目次（details） */
details.toc { margin: .8em 0 1.2em; border: 1px solid var(--line); border-radius: 8px; padding: 2px 8px; background: var(--surface); }
details.toc summary { cursor: pointer; padding: 8px 4px; color: var(--accent); }
details.toc nav.toc { padding: 0 4px 8px; }
/* 右下の「目次」固定リンク（狭い画面のみ） */
a.toc-fab {
  position: fixed; right: 14px; bottom: 14px; z-index: 10;
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 44px; min-height: 44px; padding: 0 14px;
  background: var(--surface); color: var(--accent); text-decoration: none;
  border: 1px solid var(--line); border-radius: 22px; font-size: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,.15);
}
@media (min-width: 1180px) { a.toc-fab { display: none; } }
nav.pager { display: flex; gap: 12px; margin-top: 3em; padding-top: 1em; border-top: 1px solid var(--line); }
nav.pager a {
  flex: 1 1 0; display: flex; flex-direction: column; justify-content: space-between; gap: 4px;
  min-height: 76px; padding: 10px 14px; text-decoration: none;
  background: var(--surface); border: 1px solid var(--line); border-radius: 8px; color: var(--text);
}
nav.pager a:hover { border-color: var(--accent); }
nav.pager a.next { text-align: right; }
nav.pager .pager-gap { flex: 1 1 0; }
nav.pager .pager-label { font-size: 12px; color: var(--muted); }
nav.pager .pager-title { font-size: 15px; line-height: 1.4; }
.book { margin: 1.5em 0 2.5em; padding: 16px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }
.book h2 { margin-top: .2em; border-bottom: none; }
.book ol, .book ul { list-style: none; padding: 0; margin: .4em 0 0; }
.book li { margin: 0; }
.book li a { display: flex; align-items: center; min-height: 44px; padding: 4px 2px; color: var(--text); text-decoration: none; }
.book li a:hover { color: var(--accent); }
.book .book-top { margin: .4em 0 .6em; }
.book .book-top a { font-weight: 700; }
.book .intro { margin: .2em 0 0; color: var(--muted); font-size: 15px; }
/* トップの編へ飛ぶチップ */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 1em 0 1.4em; }
.chips a { display: inline-flex; align-items: center; min-height: 44px; padding: 4px 14px;
  background: var(--surface); border: 1px solid var(--line); border-radius: 999px;
  color: var(--accent); text-decoration: none; font-size: 14px; }
.chips a:hover { border-color: var(--accent); }
/* 続きから読む */
.continue { margin: .8em 0 1.2em; padding: 10px 14px; background: var(--surface);
  border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 8px; }
.continue a { font-weight: 700; }
/* 広い画面では本文左の余白に固定表示（本文の横幅・中央寄せは変えない） */
@media (min-width: 1180px) {
  details.toc { position: fixed; top: 4rem; left: max(16px, calc(50vw - 23rem - 220px));
    width: 200px; max-height: calc(100vh - 6rem); overflow-y: auto; border: none; background: none; }
  details.toc[open] summary { display: none; }
  details.toc nav.toc { display: block; padding: 0; font-size: 13px; }
}
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
}
@media (max-width: 479px) {
  nav.pager { flex-direction: column; }
  nav.pager .pager-gap { display: none; }
}
"""


def rel_href(from_page: Path, to_page: Path) -> str:
    """出力先での相対リンクを作る。"""
    return Path(os.path.relpath(to_page, from_page.parent)).as_posix()


def md_to_html_path(md_path: Path) -> Path:
    """README.md → index.html、それ以外の xxx.md → xxx.html。"""
    if md_path.name == "README.md":
        return md_path.with_name("index.html")
    return md_path.with_suffix(".html")


def rewrite_links(body: str) -> str:
    """Markdown どうしのリンクを .html に書き換える（外部 URL は触らない）。"""

    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if re.match(r"^[a-z]+:", href) or href.startswith("#"):
            return match.group(0)
        path, sep, frag = href.partition("#")
        if path.endswith("README.md"):
            path = path[: -len("README.md")] + "index.html"
        elif path.endswith(".md"):
            path = path[:-3] + ".html"
        return f'href="{path}{sep}{frag}"'

    return re.sub(r'href="([^"]+)"', repl, body)


def convert_alerts(body: str) -> str:
    """<blockquote><p>[!CAUTION] ... を色付きの注意書きに変える。"""

    def repl(match: re.Match[str]) -> str:
        kind = match.group(1)
        label = ALERT_LABELS[kind]
        return (
            f'<blockquote class="alert alert-{kind.lower()}">'
            f'<p class="alert-title">{label}</p><p>'
        )

    return re.sub(r"<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*", repl, body)


def wrap_tables(body: str) -> str:
    """スマホ幅で表が画面からはみ出さないよう、横スクロールの箱で包む。"""
    body = body.replace("<table>", '<div class="table-wrap"><table>')
    return body.replace("</table>", "</table></div>")


def normalize_lists(text: str) -> str:
    """Python-Markdown が GitHub と違って崩すリスト書き方を直す（コードフェンス内は触らない）。

    1. 段落や見出しの直後に空行なしで始まるリストの前に空行を補う
    2. 入れ子リストのインデントを「深さ × 4 スペース」にそろえる
    """
    text = _blank_before_lists(text)
    return _normalize_indent(text)


def _blank_before_lists(text: str) -> str:
    """段落の直後に空行なしで始まるリストの前に空行を補う（フェンス内は触らない）。

    直前が空行・リスト項目・見出しの場合はそのまま（崩れないので補わない）。
    """
    lines = text.split("\n")
    out: list[str] = []
    fence_depth = 0
    fence_char = ""
    for i, line in enumerate(lines):
        stripped = line.strip()
        # フェンス内では触らない
        if stripped[:3] in ("```", "~~~"):
            out.append(line)
            if fence_depth == 0:
                fence_depth = 1
                fence_char = stripped[:3]
            elif stripped[:3] == fence_char:
                fence_depth = 0
            continue
        if fence_depth:
            out.append(line)
            continue
        if _is_list_item(line):
            # 直前の行が「空でもリスト項目でも見出しでもない段落」のときだけ空行を補う
            if len(out) > 0:
                prev = out[-1]
                if prev.strip() != "" and not _is_list_item(prev) and not prev.lstrip().startswith("#"):
                    out.append("")
        out.append(line)
    return "\n".join(out)


def _is_list_item(line: str) -> bool:
    """リスト項目の行か（箇条書き・番号付き）。"""
    stripped = line.strip()
    return bool(re.match(r"^[-*+][ \t]+", stripped)) or bool(re.match(r"^\d+[.)][ \t]+", stripped))


def _normalize_indent(text: str) -> str:
    """リスト項目のインデントを、親子の深さに応じて深さ×4スペースにそろえる。

    1階層目の項目やリスト外の行は動かさない。コードフェンス内は触らない。
    深さの状態は空行や字下げされた継続行では保持し、字下げのない非リスト行に
    ぶつかったときだけリセットする（リストが増えても崩れない）。
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    fence_depth = 0
    fence_char = ""
    levels: list[int] = []  # 深さの状態（各階層のインデント幅）。字下げのない非リスト行でリセット
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped[:3] in ("```", "~~~"):
            out.append(line)
            if fence_depth == 0:
                fence_depth = 1
                fence_char = stripped[:3]
            elif stripped[:3] == fence_char:
                fence_depth = 0
            i += 1
            continue
        if fence_depth:
            out.append(line)
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not _is_list_item(line):
            out.append(line)
            # 字下げのない非リスト行だけがリストの終わり。継続行（字下げあり）は深さを保つ
            if indent == 0 and stripped != "":
                levels = []
            i += 1
            continue
        # 連続するリストブロックを集める（字下げされた継続行はブロック内として扱う）
        block: list[str] = []
        while i < n:
            cur = lines[i]
            cs = cur.strip()
            if cs[:3] in ("```", "~~~"):
                break
            cur_indent = len(cur) - len(cur.lstrip(" "))
            if _is_list_item(cur):
                block.append(cur)
                i += 1
            elif cs == "":
                # 空行でブロックは切れるが、深さの状態（levels）は保持する
                break
            elif cur_indent > 0:
                # リスト内の継続行・コードフェンス内容は動かさず、そのまま続きとして扱う
                block.append(cur)
                i += 1
            else:
                break
        out.extend(_renumber_indent(block, levels))
    return "\n".join(out)


def _renumber_indent(block: list[str], levels: list[int]) -> list[str]:
    """ひとつながりのリスト項目群に対し、深さを数えて深さ×4スペースに整える。

    levels は前のブロックから引き継いだ深さの状態で、その場で更新される。
    """
    depths: list[int] = []
    for line in block:
        if not _is_list_item(line):
            # 空行・継続行は深さを変えない
            depths.append(None)
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not levels or indent > levels[-1]:
            levels.append(indent)
        elif indent < levels[-1]:
            while len(levels) > 1 and indent < levels[-1]:
                levels.pop()
        depths.append(len(levels) - 1)
    result: list[str] = []
    for line, depth in zip(block, depths):
        if depth is None:
            result.append(line)
        else:
            content = line.lstrip(" ")
            result.append(" " * (depth * 4) + content)
    return result


def render_markdown(text: str) -> tuple[str, list[dict]]:
    """Markdown を 1 回だけ変換し、HTML 本文と h2・h3 の見出しトークンを返す。"""
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": slugify_unicode}},
    )
    body = md.convert(normalize_lists(text))
    body = wrap_tables(convert_alerts(rewrite_links(body)))
    tokens: list[dict] = []

    def walk(nodes: list[dict]) -> None:
        for tok in nodes:
            if tok["level"] in (2, 3):
                tokens.append(tok)
            walk(tok.get("children", []))

    walk(md.toc_tokens)
    return body, tokens


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return SITE_TITLE


def status_of(text: str) -> str:
    match = re.search(r"^> Status: (.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def book_of(src: Path) -> dict | None:
    """ソースファイルが属する編の定義を返す（どれにも属さなければ None）。"""
    rel = src.relative_to(REPO)
    top = rel.parts[0] if rel.parts else ""
    for book in BOOKS:
        if book["folder"] == top:
            return book
    return None


def book_id(folder: str) -> str:
    """トップページの編セクションに付ける安定した id。"""
    return f"book-{folder}"


def strip_status_blockquote(body: str) -> str:
    """`> Status: ...` から生まれた引用ブロックを本文から取り除く。"""
    return re.sub(r'<blockquote>\s*<p>Status:.*?</p>\s*</blockquote>\s*', "", body, count=1)


def inject_after_h1(body: str, extra: str) -> str:
    """最初の h1 閉じタグの直後に差し込む。"""
    if not extra:
        return body
    idx = body.find("</h1>")
    if idx == -1:
        return extra + body
    return body[: idx + len("</h1>")] + "\n" + extra + body[idx + len("</h1>") :]


def build_toc(tokens: list[dict], summary: str = "この章の目次") -> str:
    """h2・h3 から章内目次（details + nav）を作る。"""
    items = []
    for t in tokens:
        cls = "toc-h2" if t["level"] == 2 else "toc-h3"
        items.append(f'<li class="{cls}"><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>')
    return (
        f'<details class="toc" id="toc"><summary>{html.escape(summary)}</summary>'
        f'<nav class="toc"><ol>{"".join(items)}</ol></nav></details>'
    )


# 章内目次の開閉（matchMedia）と現在の節のハイライト（スクロール位置）を担うインライン JS。
# JS が無効でも details は summary クリックで開閉でき、本文はそのまま読める。
TOC_JS = """
<script>
(function () {
  var details = document.querySelector('details.toc');
  if (!details) return;
  var wide = window.matchMedia('(min-width: 1180px)');
  function apply(mq) { details.open = mq.matches; }
  apply(wide);
  if (wide.addEventListener) { wide.addEventListener('change', apply); }
  // 右下の「目次」リンクを押したら details を開く
  var fab = document.querySelector('a.toc-fab');
  if (fab) { fab.addEventListener('click', function () { details.open = true; }); }
  var links = details.querySelectorAll('nav.toc a[href^="#"]');
  var byId = {};
  var heads = [];
  links.forEach(function (a) {
    var href = a.getAttribute('href');
    var el = document.getElementById(decodeURIComponent(href.slice(1)));
    if (!el) return;
    byId[el.id] = a;
    heads.push(el);
  });
  if (!heads.length) return;
  var current = null;
  function update() {
    // 画面の高さの 20% 以下にある見出しのうち、最後のものを現在の節とする
    var limit = window.innerHeight * 0.2;
    var found = null;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top <= limit) found = heads[i];
    }
    var a = byId[(found || heads[0]).id];
    if (!a || a === current) return;
    if (current) current.classList.remove('active');
    a.classList.add('active');
    current = a;
    // 広い画面で目次が縦にあふれるとき、ハイライト中の項目が枠内に収まるよう調整
    var d = a.closest('details');
    if (d) {
      var top = a.offsetTop - d.offsetTop;
      if (top < d.scrollTop) { d.scrollTop = top; }
      else if (top + a.offsetHeight > d.scrollTop + d.clientHeight) {
        d.scrollTop = top + a.offsetHeight - d.clientHeight;
      }
    }
  }
  var queued = false;
  function schedule() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(function () { queued = false; update(); });
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
})();
</script>
"""


def is_chapter_path(src: Path) -> bool:
    """章フォルダ（NN-xxx/README.md）かを判定する。"""
    return re.match(r"^[0-9][0-9]-", src.parent.name) is not None and src.name == "README.md"


def build_pager_html(src: Path, out_path: Path, out_root: Path) -> str:
    """同じ編の前後の章への「前の章／次の章」カードを作る。"""
    chapters: list[Path] = []
    for folder in BOOK_DIRS:
        chapters = chapter_readmes(folder)
        if src in chapters:
            break
    else:
        return ""

    i = chapters.index(src)
    parts = []
    if i > 0:
        prev = chapters[i - 1]
        href = rel_href(out_path, out_root / md_to_html_path(prev.relative_to(REPO)))
        parts.append(
            '<a class="prev" href="' + href + '"><span class="pager-label">前の章</span>'
            f'<span class="pager-title">{html.escape(first_heading(prev.read_text(encoding="utf-8")))}</span></a>'
        )
    else:
        # 前の章がないときも、次の章を右側に置くための空スペース
        parts.append('<span class="pager-gap"></span>')
    if i + 1 < len(chapters):
        nxt = chapters[i + 1]
        href = rel_href(out_path, out_root / md_to_html_path(nxt.relative_to(REPO)))
        parts.append(
            '<a class="next" href="' + href + '"><span class="pager-label">次の章</span>'
            f'<span class="pager-title">{html.escape(first_heading(nxt.read_text(encoding="utf-8")))}</span></a>'
        )
    return '<nav class="pager">' + "".join(parts) + "</nav>"


def _doc(title: str, body: str, header_html: str, footer_html: str = "", extra_body: str = "") -> str:
    """共通の HTML 外枠（head・header・main・footer）を組み立てる。"""
    footer = f'<footer class="site">\n{footer_html}\n</footer>' if footer_html else ""
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{html.escape(title)} | {SITE_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
<header class="site">{header_html}</header>
<main>
{body}
</main>
{footer}
{extra_body}
</body>
</html>
"""


def page(src: Path, out_path: Path, out_root: Path) -> str:
    """1 ページ分の HTML を作る（章・編概要・番外編すべてここを通る）。"""
    text = src.read_text(encoding="utf-8")
    title = first_heading(text)

    home = rel_href(out_path, out_root / "index.html")
    room = rel_href(out_path, out_root.parent / "index.html")

    # パンくず（編に属さないページでは編の名前を省略）
    book = book_of(src)
    crumb = ""
    if book is not None:
        crumb = (
            f'<span class="crumb-sep">›</span> '
            f'<a href="{home}#{book_id(book["folder"])}">{html.escape(book["title"])}</a>'
        )
    crumb_hdr = (
        f'<a href="{room}">もの文読書室</a>'
        f'<span class="crumb-sep">›</span> <a href="{home}">ハンドブック</a>{crumb}'
    )

    # ステータス行（「完了」だけなら非表示、それ以外は h1 直下に灰色 1 行）
    status = status_of(text)
    status_html = f'<p class="status">{html.escape(status)}</p>' if status and status != "完了" else ""

    # 章内目次（h2 が 3 個以上あるときだけ）
    body, tokens = render_markdown(text)
    h2_count = sum(1 for t in tokens if t["level"] == 2)
    summary = "この章の目次" if is_chapter_path(src) else "このページの目次"
    toc_html = build_toc(tokens, summary) if h2_count >= 3 else ""
    toc_fab = '<a class="toc-fab" href="#toc">目次</a>' if toc_html else ""

    pager = build_pager_html(src, out_path, out_root)
    body = strip_status_blockquote(body)
    body = inject_after_h1(body, status_html + toc_html)
    body = body + pager

    # 「続きから読む」用に、章ページを開いたら出力ルートからの相対パスとタイトルを保存する
    resume_js = ""
    if is_chapter_path(src):
        entry = {"path": rel_href(out_root / "index.html", out_path), "title": title}
        resume_js = (
            "<script>(function(){try{var k='wbh-resume';var e=" + json.dumps(entry, ensure_ascii=False)
            + ";localStorage.setItem(k,JSON.stringify(e));}catch(_){}})();</script>"
        )

    footer_html = f'<a href="{home}">目次へ戻る</a>'
    extra_body = toc_fab + resume_js + (TOC_JS if toc_html else "")
    return _doc(title, body, crumb_hdr, footer_html, extra_body)


def collect_pages() -> list[Path]:
    pages: list[Path] = []
    for name in SOURCE_DIRS:
        pages.extend(sorted((REPO / name).rglob("*.md")))
    return pages


def chapter_readmes(folder: str) -> list[Path]:
    """章のフォルダ（01-xxx/README.md の形）を番号順に返す。"""
    return sorted(p for p in (REPO / folder).glob("[0-9][0-9]-*/README.md"))


def build_index(out_root: Path) -> None:
    """読書室向けのトップページ（各編の目次）を作る。"""
    out_path = out_root / "index.html"

    def book_section(b: dict) -> str:
        folder = b["folder"]
        items = []
        if folder == "extras":
            for md in sorted((REPO / folder).rglob("*.md")):
                href = rel_href(out_path, out_root / md_to_html_path(md.relative_to(REPO)))
                text = md.read_text(encoding="utf-8")
                items.append(
                    f'<li><a href="{href}">{html.escape(first_heading(text))}</a></li>'
                )
        else:
            for readme in chapter_readmes(folder):
                href = rel_href(out_path, out_root / md_to_html_path(readme.relative_to(REPO)))
                text = readme.read_text(encoding="utf-8")
                # 「完了」ちょうどのステータス表示は消す（執筆中・執筆予定などは付ける）
                status = status_of(text)
                s = f' <span class="status">（{html.escape(status)}）</span>' if status and status != "完了" else ""
                items.append(f'<li><a href="{href}">{html.escape(first_heading(text))}</a>{s}</li>')

        top_link = ""
        if b["top"] is not None:
            href = rel_href(out_path, out_root / md_to_html_path((REPO / b["top"]).relative_to(REPO)))
            top_link = f'<p class="book-top"><a href="{href}">この編の概要・試験情報を読む</a></p>'
        intro = f'<p class="intro">{b["intro"]}</p>' if b["intro"] else ""
        list_tag = "ol" if folder != "extras" else "ul"
        return (
            f'<section class="book" id="{book_id(folder)}"><h2>{html.escape(b["title"])}</h2>'
            f'{intro}{top_link}<{list_tag}>{"".join(items)}</{list_tag}></section>'
        )

    chips = "".join(
        f'<a href="#{book_id(b["folder"])}">{html.escape(b["chip"])}</a>' for b in BOOKS
    )

    # 「続きから読む」は localStorage に保存があるときだけ出す（挿入は textContent で行う）
    resume = (
        '<div class="continue" id="resume" hidden>'
        '<a href="" id="resume-link"></a></div>'
    )

    body = (
        f"<h1>{SITE_TITLE}</h1>"
        "<p>非エンジニアの大学生が、手を動かしながら Web 技術の基礎を学び、"
        "その知識を基本情報・応用情報・情報処理安全確保支援士の試験の言葉で整理し直すための自分用ハンドブックです。</p>"
        f"{resume}"
        f'<nav class="chips">{chips}</nav>'
        + "".join(book_section(b) for b in BOOKS)
    )

    resume_js = """<script>
(function () {
  var box = document.getElementById('resume');
  var link = document.getElementById('resume-link');
  if (!box || !link) return;
  try {
    var e = JSON.parse(localStorage.getItem('wbh-resume') || 'null');
    // 古い配列形式（[0] に path/title が入る）にも耐える
    if (Array.isArray(e)) { e = e[0]; }
    if (!e || typeof e.path !== 'string' || typeof e.title !== 'string') return;
    link.href = e.path;
    link.textContent = '続きから読む：' + e.title;
    box.hidden = false;
  } catch (_) {}
})();
</script>"""

    out_path.write_text(_index_doc(SITE_TITLE, body, resume_js, out_path, out_root), encoding="utf-8")


def _index_doc(title: str, body: str, resume_js: str, out_path: Path, out_root: Path) -> str:
    """トップページ専用の HTML を組み立てる（章ページとはヘッダー構成が違う）。"""
    home = rel_href(out_path, out_root / "index.html")
    room = rel_href(out_path, out_root.parent / "index.html")
    header_html = (
        f'<a href="{room}">もの文読書室</a>'
        f'<span class="crumb-sep">›</span> <a href="{home}">ハンドブック</a>'
    )
    # トップページはフッターの「目次へ戻る」が自分自身へのリンクになるため出さない
    return _doc(title, body, header_html, "", resume_js)


MARKER = ".web-basics-handbook"


def build(out_root: Path) -> None:
    # 出力先は丸ごと作り直すので、このスクリプトが前に作ったフォルダ（目印ファイルあり）か、
    # 空のフォルダでなければ止める。読書室のほかのファイルを誤って消さないための安全策。
    if out_root.exists():
        if any(out_root.iterdir()) and not (out_root / MARKER).exists():
            raise SystemExit(
                f"{out_root} には別のファイルがあります。このハンドブック専用の空のサブフォルダを指定してください。"
            )
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)
    (out_root / MARKER).write_text("built by tools/build_reading_room.py\n", encoding="utf-8")

    # Markdown 以外（code/ のスクリプト、CSV など）をそのままコピー
    for name in SOURCE_DIRS:
        for src in (REPO / name).rglob("*"):
            if src.is_file() and src.suffix != ".md" and src.name != ".gitkeep" and "__pycache__" not in src.parts:
                dest = out_root / src.relative_to(REPO)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

    count = 0
    for src in collect_pages():
        out_path = out_root / md_to_html_path(src.relative_to(REPO))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page(src, out_path, out_root), encoding="utf-8")
        count += 1

    build_index(out_root)
    print(f"{count} ページ ＋ 目次を {out_root} に書き出しました")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="dist/web-basics-handbook", help="出力先フォルダ（中身は作り直される）")
    args = parser.parse_args()
    build(Path(args.out).resolve())


if __name__ == "__main__":
    main()
