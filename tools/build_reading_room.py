"""このハンドブックを「もの文読書室」に置ける静的 HTML に変換する。

- chapters/（Web 編）・fe/（基本情報）・ap/（応用情報）・sc/（支援士）・extras/ の Markdown を HTML にする
- README.md は index.html に、ほかの .md は同じ場所の .html にする
- Markdown 間のリンク（xxx.md）も .html に書き換える
- GitHub の注意書き（> [!CAUTION] など）を色付きの枠にする
- code/ などの Markdown 以外のファイルはそのままコピーする
- 外部の CDN を使わず、CSS も各ページに埋め込む（オフラインでも読める）

出力先のフォルダは丸ごと作り直す。読書室の他のファイルを消さないよう、
出力先には読書室の中の「このハンドブック専用のサブフォルダ」を指定すること。

使い方:
    pip install markdown
    python tools/build_reading_room.py --out dist/web-basics-handbook
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from pathlib import Path

import markdown

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

CSS = """
:root {
  --bg: #fbfaf7; --surface: #ffffff; --text: #1f1d1a; --muted: #6b665e;
  --line: #e4e0d8; --accent: #2f5d8a; --code-bg: #f2efe9; --mark: #fff1a8;
  --caution-bg: #fdecec; --caution-line: #c93c3c;
  --note-bg: #eaf2fb; --note-line: #2f6fb3;
  --tip-bg: #eaf6ee; --tip-line: #2f8a4c;
  --important-bg: #f2ecfb; --important-line: #7a4cc2;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #171614; --surface: #201f1c; --text: #ece8e1; --muted: #a39d93;
    --line: #36332e; --accent: #8fb8e3; --code-bg: #2a2824; --mark: #5c4f12;
    --caution-bg: #3a1f1f; --caution-line: #e07070;
    --note-bg: #1d2a38; --note-line: #78a9de;
    --tip-bg: #1d3024; --tip-line: #6cc28a;
    --important-bg: #2a2238; --important-line: #ad8be6;
  }
}
:root[data-theme="dark"] {
  --bg: #171614; --surface: #201f1c; --text: #ece8e1; --muted: #a39d93;
  --line: #36332e; --accent: #8fb8e3; --code-bg: #2a2824; --mark: #5c4f12;
  --caution-bg: #3a1f1f; --caution-line: #e07070;
  --note-bg: #1d2a38; --note-line: #78a9de;
  --tip-bg: #1d3024; --tip-line: #6cc28a;
  --important-bg: #2a2238; --important-line: #ad8be6;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic UI", "Meiryo", system-ui, sans-serif;
  font-size: 17px; line-height: 1.85; overflow-wrap: anywhere;
}
header.site, footer.site {
  max-width: 46rem; margin: 0 auto; padding: 12px 16px;
  font-size: 14px; color: var(--muted);
}
header.site { display: flex; flex-wrap: wrap; gap: 4px 16px; border-bottom: 1px solid var(--line); }
header.site a, footer.site a { color: var(--muted); }
main { max-width: 46rem; margin: 0 auto; padding: 8px 16px 48px; }
h1 { font-size: 1.6rem; line-height: 1.4; margin: 1.2em 0 .6em; }
h2 { font-size: 1.3rem; line-height: 1.4; margin: 2.2em 0 .6em; padding-bottom: .3em; border-bottom: 2px solid var(--line); }
h3 { font-size: 1.12rem; margin: 1.8em 0 .5em; }
h4 { font-size: 1rem; margin: 1.5em 0 .4em; }
a { color: var(--accent); }
p, li { margin: .5em 0; }
mark { background: var(--mark); color: inherit; padding: 0 .15em; border-radius: 2px; }
code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; font-size: .88em;
  background: var(--code-bg); padding: .1em .35em; border-radius: 4px; }
pre { background: var(--code-bg); padding: 12px 14px; border-radius: 8px; overflow-x: auto; line-height: 1.55; }
pre code { background: none; padding: 0; font-size: 14px; }
.table-wrap { overflow-x: auto; margin: 1em 0; }
table { border-collapse: collapse; min-width: 100%; font-size: 15px; line-height: 1.6; background: var(--surface); }
th, td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: var(--code-bg); white-space: nowrap; }
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
nav.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 3em;
  padding-top: 1em; border-top: 1px solid var(--line); font-size: 15px; }
nav.pager a { max-width: 48%; }
.book { margin: 1.5em 0 2.5em; }
.book ol { padding-left: 1.4em; }
.status { color: var(--muted); font-size: 14px; }
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


def render_markdown(text: str) -> str:
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "toc"])
    return wrap_tables(convert_alerts(rewrite_links(body)))


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return SITE_TITLE


def status_of(text: str) -> str:
    match = re.search(r"^> Status: (.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def page(title: str, body: str, out_path: Path, out_root: Path, pager: str = "") -> str:
    home = rel_href(out_path, out_root / "index.html")
    room = rel_href(out_path, out_root.parent / "index.html")
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {SITE_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
<header class="site">
  <a href="{room}">もの文読書室</a>
  <a href="{home}">{SITE_TITLE}</a>
</header>
<main>
{body}
{pager}
</main>
<footer class="site">
  <a href="{home}">目次へ戻る</a>
</footer>
</body>
</html>
"""


def collect_pages() -> list[Path]:
    pages: list[Path] = []
    for name in SOURCE_DIRS:
        pages.extend(sorted((REPO / name).rglob("*.md")))
    return pages


def chapter_readmes(folder: str) -> list[Path]:
    """章のフォルダ（01-xxx/README.md の形）を番号順に返す。"""
    return sorted(p for p in (REPO / folder).glob("[0-9][0-9]-*/README.md"))


def build_pager(src: Path, out_path: Path, out_root: Path) -> str:
    """同じ編の前後の章へのリンクを作る。"""
    for folder in BOOK_DIRS:
        chapters = chapter_readmes(folder)
        if src in chapters:
            i = chapters.index(src)
            parts = []
            if i > 0:
                prev = chapters[i - 1]
                href = rel_href(out_path, out_root / md_to_html_path(prev.relative_to(REPO)))
                parts.append(f'<a href="{href}">← {html.escape(first_heading(prev.read_text(encoding="utf-8")))}</a>')
            else:
                parts.append("<span></span>")
            if i + 1 < len(chapters):
                nxt = chapters[i + 1]
                href = rel_href(out_path, out_root / md_to_html_path(nxt.relative_to(REPO)))
                parts.append(f'<a href="{href}">{html.escape(first_heading(nxt.read_text(encoding="utf-8")))} →</a>')
            return '<nav class="pager">' + "".join(parts) + "</nav>"
    return ""


def build_index(out_root: Path) -> None:
    """読書室向けのトップページ（2 冊の目次）を作る。"""
    out_path = out_root / "index.html"

    def book(title: str, intro: str, top: Path | None, folder: str) -> str:
        items = []
        for readme in chapter_readmes(folder):
            text = readme.read_text(encoding="utf-8")
            href = rel_href(out_path, out_root / md_to_html_path(readme.relative_to(REPO)))
            status = status_of(text)
            items.append(
                f'<li><a href="{href}">{html.escape(first_heading(text))}</a>'
                + (f' <span class="status">（{html.escape(status)}）</span>' if status else "")
                + "</li>"
            )
        top_link = ""
        if top is not None:
            href = rel_href(out_path, out_root / md_to_html_path(top.relative_to(REPO)))
            top_link = f'<p><a href="{href}">この編の概要・試験情報を読む</a></p>'
        return (
            f'<section class="book"><h2>{html.escape(title)}</h2><p>{intro}</p>{top_link}'
            f'<ol>{"".join(items)}</ol></section>'
        )

    extras = []
    for md in sorted((REPO / "extras").rglob("*.md")):
        href = rel_href(out_path, out_root / md_to_html_path(md.relative_to(REPO)))
        extras.append(f'<li><a href="{href}">{html.escape(first_heading(md.read_text(encoding="utf-8")))}</a></li>')

    body = (
        f"<h1>{SITE_TITLE}</h1>"
        "<p>非エンジニアの大学生が、手を動かしながら Web 技術の基礎を学び、"
        "その知識を基本情報・応用情報・情報処理安全確保支援士の試験の言葉で整理し直すための自分用ハンドブックです。</p>"
        + book("Web 技術の基本", "ブラウザの裏側で何が起きているかを、Python で再現しながら学ぶ本編です。", None, "chapters")
        + book(
            "基本情報技術者試験",
            "本編の知識を試験の分野ごとに整理し直し、科目 A・科目 B に備えるパートです。",
            REPO / "fe" / "README.md",
            "fe",
        )
        + book(
            "応用情報技術者試験",
            "基本情報から上乗せされる知識と、記述式の科目 B の解き方を分野ごとにまとめたパートです。",
            REPO / "ap" / "README.md",
            "ap",
        )
        + book(
            "情報処理安全確保支援士試験",
            "セキュリティの専門家として説明・判断できる深さまで掘り下げるパートです。登録制の資格の仕組みも扱います。",
            REPO / "sc" / "README.md",
            "sc",
        )
        + f'<section class="book"><h2>番外編</h2><ul>{"".join(extras)}</ul></section>'
    )
    out_path.write_text(page(SITE_TITLE, body, out_path, out_root), encoding="utf-8")


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
        text = src.read_text(encoding="utf-8")
        out_path = out_root / md_to_html_path(src.relative_to(REPO))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pager = build_pager(src, out_path, out_root)
        out_path.write_text(page(first_heading(text), render_markdown(text), out_path, out_root, pager), encoding="utf-8")
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
