"""公開前に授業テストの必須項目と正解番号を確認する。"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'data/catalog.json').read_text())
ids = set()
for entry in catalog['tests']:
    assert entry['id'] not in ids, 'テストIDが重複しています'
    ids.add(entry['id'])
    path = (root / 'data' / entry['file']).resolve()
    assert path.parent == root / 'data' and path.suffix == '.json', '問題ファイルの場所が不正です'
    test = json.loads(path.read_text())
    assert test['id'] == entry['id']
    for field in ('title', 'subject', 'version', 'questions'):
        assert test.get(field), f'{path.name}: {field}が必要です'
    qids = set()
    for q in test['questions']:
        assert q['id'] not in qids, '問題IDが重複しています'
        qids.add(q['id'])
        for field in ('prompt', 'hint', 'explanation', 'review', 'level'):
            assert isinstance(q.get(field), str) and q[field].strip(), f'{q["id"]}: {field}が必要です'
        assert len(q['choices']) >= 2 and all(isinstance(c, str) and c.strip() for c in q['choices'])
        assert len(set(q['choices'])) == len(q['choices']), '選択肢が重複しています'
        assert type(q['answer']) is int and 0 <= q['answer'] < len(q['choices']), '正解番号が不正です'
print(f'検証成功: {len(ids)}件の授業テスト')

# 新規HTMLも含め、検索除外とロック設定の欠落を公開前に検出する。
import re
from html.parser import HTMLParser
class RobotsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.protected = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            values = {x.strip().lower() for x in attrs.get('content', '').split(',')}
            self.protected |= {'noindex', 'nofollow'} <= values
for html in root.glob('*.html'):
    parser = RobotsParser()
    parser.feed(html.read_text())
    assert parser.protected, f'{html.name}: noindex, nofollowが必要です'
config = json.loads((root / 'access-config.json').read_text())
assert re.fullmatch(r'[a-f0-9]{64}', config['passwordSha256']), 'パスワード照合値が不正です'
assert 'src="auth.js"' in (root / 'index.html').read_text(), '共通パスワード画面が必要です'
assert 'Disallow: /' in (root / 'robots.txt').read_text(), 'クロール拒否が必要です'
print('検証成功: 検索除外・共通パスワード設定')
