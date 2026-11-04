import json, subprocess, time
from pathlib import Path

import pytest

from dhrona.improve import CHECKLIST_MAX, PENDING, check_learned, checklist_calls, checklist_md, keep_checklist, learned_repo, new_checklist_lines, recent_checklist


def git(d, *a): return subprocess.run(['git', '-C', str(d), *a], check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()


def test_check_learned_checklist(tmp_path):
    (tmp_path/'checklist.md').write_text('- run the tests\n\n- update the changelog\n')
    assert check_learned(tmp_path) == []
    (tmp_path/'checklist.md').write_text('- ' + 'x' * CHECKLIST_MAX + '\n')
    assert [p for p in check_learned(tmp_path) if 'checklist.md' in p and str(CHECKLIST_MAX) in p]
    (tmp_path/'checklist.md').write_text('- run the tests\nupdate the changelog\n')
    assert [p for p in check_learned(tmp_path) if 'checklist.md' in p and '- ' in p]


def test_keep_checklist(tmp_path):
    learned = tmp_path/'learned'
    learned.mkdir()
    (learned/'AGENTS.md').write_text('Read sizes from `ls`.\n')
    (learned/'checklist.md').write_text('- run the tests\n')
    learned_repo(learned)
    head = git(learned, 'rev-parse', 'HEAD')
    b = keep_checklist(learned, ['Run  the tests', '- update the changelog', 'update the changelog', 'mail ann@example.com'], 'Checklist from a replay')
    assert b.startswith(PENDING)
    assert git(learned, 'rev-parse', f'{b}^') == head and git(learned, 'rev-parse', 'HEAD') == head
    lines = git(learned, 'show', f'{b}:checklist.md').splitlines()
    assert lines == ['- run the tests', '- update the changelog', '- mail [EMAIL_1]']
    assert git(learned, 'show', f'{b}:AGENTS.md') == 'Read sizes from `ls`.'
    with pytest.raises(ValueError, match=f'{CHECKLIST_MAX:,}'):
        keep_checklist(learned, ['z' * CHECKLIST_MAX], 'Checklist from a replay')
    assert len(git(learned, 'branch', '--list', 'pending/*').splitlines()) == 1


REFUSED = 'refused: item 2 gates a commit or push and belongs to the person. Ask them to run `/check done 2` (or `/check skip 2`); do not retry it here.'
NO_MATCH = "no open item matches 'ship'; open items:\n1. run the tests"


def call(action, item, detail, ok=True): return dict(tool='checklist', ok=ok, args=dict(action=action, item=item, reason=''), detail=detail)


def test_recent_checklist(tmp_path):
    blocked = lambda item: dict(tool='run_shell', ok=False, detail=f'checklist: {item}\nfinish it first')
    rows = [dict(session='s0', at=time.time() - 40*86400, activity=[call('check', 'run the tests', 'checked 1: run the tests')]),
            dict(session='s1', at=time.time() - 60, activity=[call('check', '1', 'checked 1: run the tests'), call('skip', 'update the changelog', 'skipped 2: update the changelog'),
                 call('add', 'mail ann@example.com', 'added 3: mail ann@example.com'), call('check', 'lost', 'checked 1: lost', ok=False),
                 call('purge', 'run the tests', "unknown action 'purge'; use check, skip or add"), call('check', 'update the changelog', REFUSED),
                 call('check', 'ship', NO_MATCH), call('add', 'run the tests', 'already pinned: run the tests'), call('add', ' ', 'nothing to add: item is empty'),
                 blocked('update the changelog'), dict(tool='run_shell', ok=False, detail='refused: no approver')]),
            dict(session='s2', at=time.time() - 30, activity=[call('check', 'tests', 'checked 1: Run  the tests'), blocked('update the changelog')])]
    (tmp_path/'agent-history.jsonl').write_text('\n'.join(map(json.dumps, rows)) + '\n')
    got = {r['item']: r for r in recent_checklist(tmp_path)}
    counts = lambda r: (r['checked'], r['skipped'], r['added'], r['blocked'])
    assert counts(got['Run the tests']) == (2, 0, 0, 0)
    assert counts(got['update the changelog']) == (0, 1, 0, 2)
    assert counts(got['mail [EMAIL_1]']) == (0, 0, 1, 0)
    assert len(got) == 3 and 'ann@' not in checklist_md(list(got.values()))
    assert recent_checklist(tmp_path, days=0) == []


def test_checklist_calls():
    turn = dict(activity=[call('check', '1', 'checked 1: run the tests'), call('skip', 'change', 'skipped 2: update  the changelog'),
                          call('check', 'update the changelog', REFUSED), call('check', 'ship', NO_MATCH), call('check', 'x', 'checked 1: x', ok=False),
                          call('add', 'run the tests', 'already pinned: run the tests')])
    turn['activity'][1]['args']['reason'] = 'no user-facing change'
    assert checklist_calls(turn) == [('check', 'run the tests', ''), ('skip', 'update the changelog', 'no user-facing change')]


def test_checklist_symlink(tmp_path):
    learned = tmp_path/'learned'
    learned.mkdir()
    (learned/'AGENTS.md').write_text('Read sizes from `ls`.\n')
    (learned/'checklist.md').symlink_to('AGENTS.md')
    assert [p for p in check_learned(learned) if 'checklist.md' in p and 'symlink' in p]
    learned_repo(learned)
    with pytest.raises(ValueError, match='symlink'): keep_checklist(learned, ['ship it'], 'Checklist from a replay')
    assert git(learned, 'branch', '--list', 'pending/*') == '' and (learned/'AGENTS.md').read_text() == 'Read sizes from `ls`.\n'


def test_keep_checklist_nothing_new(tmp_path):
    (tmp_path/'checklist.md').write_text('- run the tests\n')
    learned_repo(tmp_path)
    assert keep_checklist(tmp_path, ['Run  the tests', '- run the tests', ' '], 'Checklist from a replay') is None
    assert git(tmp_path, 'branch', '--list', 'pending/*') == ''


def test_new_checklist_lines():
    assert new_checklist_lines('- run the tests\n- old step\n', '- Run  the tests\n- ship it\n\n- SHIP  it\n') == ['- ship it']
    assert new_checklist_lines('- a\n', '') == []
