"""パスワードを非表示で入力し、公開用の照合値だけを書き出す。"""
import getpass
import hashlib
import json
from pathlib import Path

password = getpass.getpass('新しいパスワード: ')
if not password or password.isspace():
    raise SystemExit('空のパスワードは設定できません。')
if password != getpass.getpass('確認のためもう一度: '):
    raise SystemExit('一致しません。設定は変更していません。')
path = Path(__file__).resolve().parents[1] / 'access-config.json'
path.write_text(json.dumps({'passwordSha256': hashlib.sha256(password.encode('utf-8')).hexdigest()}, indent=2) + '\n')
print('設定を更新しました。access-config.jsonをコミットして公開してください。')
