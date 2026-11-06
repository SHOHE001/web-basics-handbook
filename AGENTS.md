# AGENTS.md

執筆と進捗のルールは `CLAUDE.md` にあります。GitHub の運用は `docs/development-workflow.md` に従います。

- default branch（`main`）へ直接 push せず、作業 branch → PR → CI 確認 → merge で進める
- 検証コマンド: `python -m py_compile tools/*.py` と `python tools/build_reading_room.py --out dist/web-basics-handbook`
- テストスイート、lint、型チェックはこのリポジトリにはない
- このリポジトリは public。秘密情報、個人情報、第三者の文章をコミットしない
