#!/usr/bin/env bash
# もの文読書室（gen8 の ~/monobun-reading-room）にこのハンドブックを配置する。
#
# gen8 の上で実行する想定:
#   cd ~/web-basics-handbook && git pull && bash tools/deploy_reading_room.sh
#
# 読書室フォルダの中の web-basics-handbook/ サブフォルダだけを作り直す。
# 読書室のほかのファイル（index.html や service worker など）には触らない。
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROOM_DIR="${READING_ROOM_DIR:-$HOME/monobun-reading-room}"
SUBDIR="${READING_ROOM_SUBDIR:-web-basics-handbook}"
VENV="$REPO_DIR/.venv-build"
TARGET="$ROOM_DIR/$SUBDIR"
NEW="$ROOM_DIR/.$SUBDIR.new"
OLD="$ROOM_DIR/.$SUBDIR.old"

if [ ! -d "$ROOM_DIR" ]; then
  echo "読書室のフォルダ $ROOM_DIR が見つかりません（READING_ROOM_DIR で指定できます）" >&2
  exit 1
fi

# 前回このスクリプトが作ったフォルダ以外は上書きしない
if [ -e "$TARGET" ] && [ ! -f "$TARGET/.web-basics-handbook" ]; then
  echo "$TARGET はこのスクリプトが作ったものではないので上書きしません（READING_ROOM_SUBDIR で別名を指定できます）" >&2
  exit 1
fi

# 何かを変える前に、読書室フォルダ全体をバックアップする（古いバックアップは自動では消さない）
BACKUP_DIR="${READING_ROOM_BACKUP_DIR:-$HOME/monobun-reading-room-backups}"
mkdir -p "$BACKUP_DIR"
BACKUP="$BACKUP_DIR/monobun-reading-room-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP" -C "$(dirname "$ROOM_DIR")" "$(basename "$ROOM_DIR")"
echo "バックアップしました: $BACKUP"
echo "  元に戻すとき: rm -rf \"$ROOM_DIR\" && tar -xzf \"$BACKUP\" -C \"$(dirname "$ROOM_DIR")\""

# ビルド用の仮想環境（初回だけ作る）
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet -r "$REPO_DIR/tools/requirements.txt"
fi

# 一時フォルダに作ってから入れ替える（作っている途中の状態を配信しないため）
rm -rf "$NEW" "$OLD"
"$VENV/bin/python" "$REPO_DIR/tools/build_reading_room.py" --out "$NEW"
if [ -e "$TARGET" ]; then
  mv "$TARGET" "$OLD"
fi
mv "$NEW" "$TARGET"
rm -rf "$OLD"

echo "配置しました: $TARGET/index.html"
echo "読書室のトップ URL の後ろに /$SUBDIR/ を付けて開いてください"
echo "  gen8 の中から確認する場合: curl -sI http://127.0.0.1:8910/$SUBDIR/ | head -1"
