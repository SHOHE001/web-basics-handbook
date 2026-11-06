"""SC Chapter 2: 暗号の基本を Python 標準ライブラリだけで試す。

- HMAC: 共通鍵による改ざん検知
- パスワードの保存: ソルト ＋ ストレッチング（scrypt）
- 照合は hmac.compare_digest で（比較にかかる時間から中身を推測されないように）

学習用の例。実際のサービスでは、実績のあるライブラリの推奨設定を使うこと。

使い方:
    python crypto_basics.py
"""

import hashlib
import hmac
import secrets


def sign(key: bytes, message: bytes) -> str:
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def hash_password(password: str) -> tuple[bytes, bytes]:
    """(ソルト, ハッシュ値) を返す。ソルトは利用者ごとにランダムに作る。"""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt, digest


def verify_password(password: str, salt: bytes, stored: bytes) -> bool:
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(digest, stored)


def main() -> None:
    print("== HMAC による改ざん検知 ==")
    key = secrets.token_bytes(32)  # 送信者と受信者だけが知る共通鍵
    message = b"amount=1000&to=alice"
    tag = sign(key, message)
    tampered = b"amount=9000&to=alice"
    print("  元のメッセージ    :", hmac.compare_digest(tag, sign(key, message)))
    print("  書き換えたメッセージ:", hmac.compare_digest(tag, sign(key, tampered)))

    print("\n== パスワードの保存（ソルト ＋ scrypt）==")
    salt_a, hash_a = hash_password("correct horse")
    salt_b, hash_b = hash_password("correct horse")
    print("  同じパスワードでも、ソルトが違うので保存される値は違う:", hash_a != hash_b)
    print("  正しいパスワードで照合:", verify_password("correct horse", salt_a, hash_a))
    print("  間違ったパスワードで照合:", verify_password("correct horse!", salt_a, hash_a))

    print("\n== 汎用ハッシュだけだと ==")
    print("  SHA-256 は同じ入力に同じ値を返す:",
          hashlib.sha256(b"password").hexdigest() == hashlib.sha256(b"password").hexdigest())


if __name__ == "__main__":
    main()
