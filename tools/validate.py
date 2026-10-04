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
