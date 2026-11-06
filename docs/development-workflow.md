# 開発の進め方

Issueに目的・受入条件を記録し、作業branchで実装します。意味のある単位でcommitし、作業branchへpushしてPRを作成します。CIとレビュー、受入条件を確認してからdefault branchへmergeします。

`push` はmainへ直接送る操作ではありません。基本は **作業branchへpush → PR → CI確認 → merge** です。

Issueにはタスクと経緯、PRには変更と検証、docsには確定した設計を残します。Projectは進捗一覧です。作業開始はIn Progress、PR準備完了はReview、3回の意味ある試行が失敗して未解決ならBlocked、mergeと受入条件の確認後にDoneにします。

同じ問題を再試行する際は仮説・検証・結果を記録します。3回目で解決した場合はBlockedにしません。過去Issueを検索して情報を引き継ぎます。

秘密情報・認証情報・個人情報はcommitやIssue/PRへ載せません。環境変数の例にはダミー値を使います。

Projectやネットワークの権限不足時は、可能な範囲の開発を進めて未同期の状態を報告します。CI・branch保護・Projectの設定状況は実際の設定と検証結果に基づいて記載します。

## 導入状況（最終確認 2026-11-06）

| 項目 | 状態 | 根拠 |
|---|---|---|
| 指示 | 設定済み | `AGENTS.md`、`CLAUDE.md` |
| Issue / PR テンプレート | 設定済み | `.github/ISSUE_TEMPLATE/`、`.github/PULL_REQUEST_TEMPLATE.md` |
| CI | 設定済み（main へ merge 後に有効） | `.github/workflows/ci.yml`、チェック名 `build-reading-room` |
| branch 保護 | 未設定 | CI が main で成功し、チェック名を確認してから設定する |
| Project | 設定済み | [Development HQ](https://github.com/users/SHOHE001/projects/1) |
