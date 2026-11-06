"""ハンドブックの Markdown を Gemini に「内容はそのまま、自然な文章に」書き直させる。

内容が変わらないように、次の 2 段構えにしている。

1. 送る前に保護する: 見出し行・コードブロック・インラインコード・リンク先 URL・
   Status 行を ⟦P0⟧ のような記号に置き換えてから送る。Gemini が触れるのは地の文だけ。
2. 戻ってきたら検査する: 記号がすべて 1 回ずつ残っているか、数字・<mark>・注意書き
   （[!CAUTION] など）・表の行数と列数・箇条書きの数が元と同じかを確かめる。
   1 つでも違えば、理由を添えてやり直させ（最大 2 回）、それでもだめなら元のまま残す。

使い方（ほかのツールで書き直したファイルを検査する。API キー不要）:
    python tools/rewrite_with_gemini.py --check                 # 未コミットの変更を HEAD と比べる
    python tools/rewrite_with_gemini.py --check --base main     # コミット済みの変更を main と比べる
    python tools/rewrite_with_gemini.py --check --revert        # 不合格のファイルを元に戻す

使い方（このスクリプトから Gemini API を呼ぶ）:
    export GEMINI_API_KEY=...            # キーは環境変数で渡す（ファイルに書かない）
    python tools/rewrite_with_gemini.py --list-models
    python tools/rewrite_with_gemini.py --model <モデル名> --dry-run   # 検査だけ、書き込まない
    python tools/rewrite_with_gemini.py --model <モデル名>             # 合格したファイルだけ上書き
    python tools/rewrite_with_gemini.py --model <モデル名> fe/03-basic-theory/README.md  # 1 ファイルだけ

標準ライブラリだけで動く。書き換え後は git diff で必ず中身を確かめること。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DIRS = ["chapters", "fe", "ap", "sc"]
API = "https://generativelanguage.googleapis.com/v1beta"

PROMPT = """あなたは日本語の技術文書の編集者です。次の Markdown は、非エンジニアの大学生向けの IT 学習ハンドブックの 1 章です。
内容はそのままに、日本語として自然で読みやすい文章に書き直してください。

守ること:
- 事実・数値・用語・例・主張を変えない。情報を足さない、削らない、順番を入れ替えない
- ⟦P数字⟧ の形の記号は、1 文字も変えず、すべてそのまま残す（見出し・コード・リンク先などを保護している）
- Markdown の構造を保つ: 段落・箇条書きの項目数・番号付きリストの項目数・表の行数と列数・`|` の位置
- <mark>…</mark> は数を変えずに残す（中の言い回しは自然にしてよい）
- **太字** は残す。> [!CAUTION] などの注意書きの行はそのまま残す
- 「です・ます」と「だ・である」の混在は、その段落の多い方にそろえる
- 説明を前置きせず、書き直した Markdown だけを出力する（```markdown で囲まない）
"""


# ---------------------------------------------------------------- 保護と復元

def protect(text: str) -> tuple[str, list[str]]:
    """壊されたくない部分を ⟦P0⟧ 形式の記号に置き換える。"""
    saved: list[str] = []

    def keep(s: str) -> str:
        saved.append(s)
        return f"⟦P{len(saved) - 1}⟧"

    # コードブロック（``` で囲まれた範囲）を丸ごと
    text = re.sub(r"^```.*?^```[^\n]*$", lambda m: keep(m.group(0)), text, flags=re.M | re.S)
    # 見出し行と Status 行は行ごと（章どうしのリンクやアンカーを壊さない）
    text = re.sub(r"^(#{1,6} .*|> Status: .*)$", lambda m: keep(m.group(0)), text, flags=re.M)
    # インラインコード
    text = re.sub(r"`[^`\n]+`", lambda m: keep(m.group(0)), text)
    # リンクの URL 部分（リンクの文字は書き直してよい）
    text = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + keep(m.group(1)) + ")", text)
    return text, saved


def restore(text: str, saved: list[str]) -> str:
    return re.sub(r"⟦P(\d+)⟧", lambda m: saved[int(m.group(1))], text)


# ---------------------------------------------------------------- 検査

def fingerprint(protected: str) -> dict[str, object]:
    """書き直しで変わってはいけない特徴を取り出す（保護済みの文字列から）。"""
    lines = protected.splitlines()
    table_shapes = [
        line.count("|") for line in lines if line.lstrip().startswith("|")
    ]
    no_placeholders = re.sub(r"⟦P\d+⟧", "", protected)
    return {
        "記号": Counter(re.findall(r"⟦P\d+⟧", protected)),
        "数字": Counter(re.findall(r"\d+(?:[.,]\d+)*", no_placeholders)),
        "<mark>": protected.count("<mark>"),
        "</mark>": protected.count("</mark>"),
        "注意書き": Counter(re.findall(r"\[!(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", protected)),
        "表の各行の | の数": table_shapes,
        "箇条書きの項目数": sum(1 for line in lines if re.match(r"^\s*[-*] ", line)),
        "番号付きの項目数": sum(1 for line in lines if re.match(r"^\s*\d+\. ", line)),
        "太字の数": protected.count("**") // 2,
    }


def differences(before: dict[str, object], after: dict[str, object]) -> list[str]:
    problems = []
    for key in before:
        if before[key] != after[key]:
            if isinstance(before[key], Counter):
                lost = before[key] - after[key]  # type: ignore[operator]
                added = after[key] - before[key]  # type: ignore[operator]
                problems.append(f"{key}が変わった（消えた: {dict(lost)}、増えた: {dict(added)}）")
            else:
                problems.append(f"{key}が変わった（元: {before[key]}、後: {after[key]}）")
    return problems


# ---------------------------------------------------------------- Gemini API

def call(path: str, body: dict | None, key: str) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}/{path}",
        data=data,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST" if body is not None else "GET",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as res:
                return json.load(res)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 2))  # 混雑時は待ってやり直す
                continue
            raise SystemExit(f"Gemini API エラー {exc.code}: {exc.read().decode(errors='replace')[:500]}")
    raise SystemExit("Gemini API に繰り返し失敗した")


def rewrite(protected: str, model: str, key: str, feedback: str = "") -> str:
    text = PROMPT
    if feedback:
        text += f"\n前回の出力は次の点で条件を満たしていませんでした。直してください:\n{feedback}\n"
    text += "\n----- ここから章の本文 -----\n" + protected
    result = call(
        f"models/{model}:generateContent",
        {"contents": [{"role": "user", "parts": [{"text": text}]}], "generationConfig": {"temperature": 0.3}},
        key,
    )
    try:
        out = "".join(p.get("text", "") for p in result["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise SystemExit(f"Gemini の応答を読めなかった: {json.dumps(result, ensure_ascii=False)[:500]}")
    out = re.sub(r"^```(?:markdown)?\n|\n```\s*$", "", out.strip())  # 念のため囲みを外す
    return out + ("\n" if protected.endswith("\n") else "")


# ---------------------------------------------------------------- 検査だけのモード

def check_against(original: str, rewritten: str) -> list[str]:
    """ほかのツールで書き直した文章が、元の内容を保っているかを確かめる。"""
    prot_orig, saved_orig = protect(original)
    prot_new, saved_new = protect(rewritten)
    problems = []
    if saved_orig != saved_new:
        # 見出し・コード・インラインコード・リンク先・Status 行は、順番も含めて 1 文字も変えてはいけない
        for i, (a, b) in enumerate(zip(saved_orig, saved_new)):
            if a != b:
                problems.append(f"保護すべき部分が変わった（{i + 1} 個目）: 元 {a[:60]!r} → 後 {b[:60]!r}")
                break
        if len(saved_orig) != len(saved_new):
            problems.append(f"保護すべき部分の数が変わった（元 {len(saved_orig)}、後 {len(saved_new)}）")
        return problems
    return differences(fingerprint(prot_orig), fingerprint(prot_new))


def git_show(base: str, rel: Path) -> str | None:
    result = subprocess.run(["git", "show", f"{base}:{rel.as_posix()}"], cwd=REPO, capture_output=True)
    return result.stdout.decode("utf-8") if result.returncode == 0 else None


def run_check(files: list[Path], base: str, revert: bool) -> None:
    passed, failed, unchanged = [], [], 0
    for path in files:
        rel = path.relative_to(REPO)
        original = git_show(base, rel)
        if original is None:
            continue  # 比較元にないファイル（新しく作ったもの）は対象外
        rewritten = path.read_text(encoding="utf-8")
        if rewritten == original:
            unchanged += 1
            continue
        problems = check_against(original, rewritten)
        if problems:
            failed.append(rel)
            print(f"[不合格] {rel}")
            for p in problems:
                print(f"    - {p}")
            if revert:
                path.write_text(original, encoding="utf-8")
                print("    → 元に戻しました")
        else:
            passed.append(rel)
            print(f"[合格] {rel}")
    print(f"\n合格 {len(passed)} 件、不合格 {len(failed)} 件、変更なし {unchanged} 件（比較元: {base}）")
    if failed and not revert:
        sys.exit(1)


# ---------------------------------------------------------------- メイン

def target_files(args: list[str]) -> list[Path]:
    if args:
        return [REPO / a for a in args]
    files: list[Path] = []
    for d in DEFAULT_DIRS:
        files.extend(sorted((REPO / d).rglob("README.md")))
    return [f for f in files if "/code/" not in f.as_posix()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="対象のファイル（省略時は chapters・fe・ap・sc の README.md すべて）")
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL"), help="使う Gemini のモデル名")
    parser.add_argument("--list-models", action="store_true", help="使えるモデルの一覧を表示して終わる")
    parser.add_argument("--dry-run", action="store_true", help="書き直しと検査だけ行い、ファイルは書き換えない")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--check", action="store_true", help="API を呼ばず、書き直し済みのファイルを比較元と比べて検査する")
    parser.add_argument("--base", default="HEAD", help="--check の比較元（git のブランチ名やコミット）")
    parser.add_argument("--revert", action="store_true", help="--check で不合格のファイルを比較元の内容に戻す")
    args = parser.parse_args()

    if args.check:
        run_check(target_files(args.files), args.base, args.revert)
        return

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("環境変数 GEMINI_API_KEY が設定されていません")

    if args.list_models:
        for m in call("models?pageSize=1000", None, key).get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(m["name"].removeprefix("models/"))
        return
    if not args.model:
        raise SystemExit("--model でモデル名を指定してください（--list-models で一覧）")

    ok, kept = [], []
    for path in target_files(args.files):
        original = path.read_text(encoding="utf-8")
        protected, saved = protect(original)
        assert restore(protected, saved) == original, f"保護と復元が一致しない: {path}"
        before = fingerprint(protected)

        feedback, result = "", None
        for attempt in range(args.retries + 1):
            candidate = rewrite(protected, args.model, key, feedback)
            problems = differences(before, fingerprint(candidate))
            if not problems:
                result = restore(candidate, saved)
                break
            feedback = "\n".join(f"- {p}" for p in problems)
        rel = path.relative_to(REPO)
        if result is None:
            kept.append(rel)
            print(f"[元のまま] {rel}\n{feedback}", file=sys.stderr)
            continue
        ok.append(rel)
        if result == original:
            print(f"[変更なし] {rel}")
        elif args.dry_run:
            print(f"[合格・未書き込み] {rel}")
        else:
            path.write_text(result, encoding="utf-8")
            print(f"[書き換え] {rel}")

    print(f"\n合格 {len(ok)} 件、元のまま {len(kept)} 件")
    if kept:
        print("元のままにしたファイル:", *kept, sep="\n  ")


if __name__ == "__main__":
    main()
