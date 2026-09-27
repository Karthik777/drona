# Approval stall fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** A missed approval prompt in the ramabana terminal must never silently turn into a reasonless refusal the model retries; refusals carry their reason, are logged, and dhrona teaches and detects the right model response.

**Architecture:** Three repos, released in dependency order: urai (tool loop passes a denial's reason to the model) → ramabana (interactive CLI waits instead of timing out, re-rings, re-asks; refused asks recorded in activity + run log) → dhrona (finding for retry-after-denial, denial counts in `dhrona-tools`, an approval seed round).

**Tech Stack:** nbdev 3 (all three repos; notebooks are source), hatchling, uv, fastcore.

**Spec:** `docs/superpowers/specs/2026-09-26-tool-simplification-design.md` (this is an addendum; root-cause below is binding context).

## Root cause (session agent_20260926-125757-426029, terminal CLI, claude-fable-5-1)

1. `ramabana/agent.py:204` `DFLT_TIMEOUT = 300`; `Approvals.request` (`agent.py:423-473`) resolves an unanswered ask as `resolve(False, 'no answer after 300s')`.
2. `urai/loop.py:67-75` `_approve1` reduces the approver's result to a bool and always returns `'Denied by human operator'` — ramabana's `Ask.reply()` (`agent.py:288-291`, "Denied by human operator. Reason given: …") is never used.
3. Denied calls never enter `call_tool`, so ramabana's `_record` wrapper (`agent.py:1033-1057`) never logs them; the CLI builds `Approvals` without an `on_ask/on_answer` recorder (`cli.py:1907`). History shows nothing.
4. Each "continue" produced a new write, a new unanswered prompt, another 300 s timeout.

## Global Constraints

- Notebooks are the source of truth in all three repos; run `uv --directory <repo> run nbdev-prepare` (hyphen) after changes; clear notebook outputs before committing.
- fastai style; one-line docstrings; reuse existing helpers (`Ask.reply`, `ask_md`/`answer_md`, `Act`, `Activity`).
- Shell hook blocks `cd`, `bash`, `rm`, `jq`, `twine`: absolute paths, `git -C`, `&&`, `uv --directory`.
- Work on a branch `approval-stall` in each repo; commit trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`. Do not push, merge, or publish — the controller releases with `nbdev-release-gh` + `nbdev-pypi`.
- Versions: uraiyadal 0.0.7 → 0.0.8; ramabana 0.1.38 → 0.1.39 (pin `uraiyadal>=0.0.8`); dhrona 0.1.1 → 0.1.2.
- Backwards compatible: approvers returning plain bools keep working unchanged.

## Review Focus

1. An approver returning `False`/`None` (plain) still yields exactly `'Denied by human operator'`. Test in Task 1.
2. Budget-exceeded denials keep `budget_msg_` even if the approver object has a reason. Test in Task 1.
3. Non-interactive frontends (ACP/MCP, tests) keep a finite timeout; only the interactive CLI waits forever. Test in Task 2.
4. A refused ask is recorded once (not twice when both the recorder and a hook path fire). Test in Task 2.
5. History rows for refused asks must not break dhrona's readers (they carry `tool`, `args`, `ok: False`, `detail` with the reason). Test in Task 3.

---

### Task 1: urai — denial reasons reach the model

**Repo:** `/Users/71293/code/personal/orgs/urai` (dist `uraiyadal`, import `urai`). **Files:** `nbs/06_loop.ipynb` (exports `urai/loop.py`), `urai/__init__.py` version, `CHANGELOG.md` untouched (release tool writes it).

**Interface:** `ToolLoopMixin._approve1(tc) -> (ok: bool, result_text: str)`. New rule: when the approver returns a falsy value that has a callable `reply` attribute, the denial text is `str(r.reply())`; otherwise `'Denied by human operator'`. Budget denials unchanged. Extract `_denial(r)` helper.

- [ ] Write failing test cells in `06_loop.ipynb`: a fake approver returning an object with `__bool__ -> False` and `reply() -> 'Denied by human operator. Reason given: no answer after 300s'` → recorded tool result equals that string and the tool function was not called; approver returning `False` → `'Denied by human operator'`; `max_steps=0` with the reason object → `budget_msg_`.
- [ ] Run `uv --directory /Users/71293/code/personal/orgs/urai run nbdev-test nbs/06_loop.ipynb` → FAIL.
- [ ] Implement:

```python
def _denial(r): return str(r.reply()) if callable(getattr(r, 'reply', None)) else 'Denied by human operator'
# in _approve1
        r = False if over else (self.approve is None or self.approve(tc))
        ok = bool(r)
        ...
        return ok, (budget_msg_ if over else _denial(r))
```

- [ ] `nbdev-prepare` → Success; bump `urai/__init__.py` to `0.0.8`; commit "Pass approval denial reasons to the model".

### Task 2: ramabana — wait, re-ring, re-ask, and log refusals

**Repo:** `/Users/71293/code/personal/orgs/ramabana`. **Files:** the notebooks exporting `ramabana/agent.py` (Approvals, `request`, `DFLT_TIMEOUT`, recorder) and `ramabana/cli.py` (`mk_agent` at ~1907, `_ask` ~1100-1108, pending-ask input handling ~1363, bell). `pyproject.toml` pin `uraiyadal>=0.0.8` (use the local urai branch via `uv --directory ... add --editable /Users/71293/code/personal/orgs/urai` only for testing; the committed pin must be `uraiyadal>=0.0.8` — run `uv lock` after the controller publishes, or leave lock regeneration to the controller and say so).

Requirements:
1. `Approvals(timeout=None)` means wait indefinitely; `request()` handles `None`. The terminal CLI constructs `Approvals(..., timeout=None)`; ACP/MCP/other constructors keep `DFLT_TIMEOUT`.
2. While an ask is pending in the CLI, re-ring the bell and re-show the ask summary every `REASK_EVERY = 120` seconds.
3. While an ask is pending, typed text that is not an answer (y/yes/n/no/`n: <reason>`/the existing approve/deny keywords — read the current handler and keep its answer vocabulary) re-shows the pending ask with a one-line hint instead of refusing. Explicit refusals with a reason still refuse and pass that reason.
4. Register an `on_ask`/`on_answer` recorder on the agent's `Approvals` (all frontends) that records a refused ask as an `Act` in `Activity` (so it lands in the turn's `activity` history rows) and writes it to the run log: `tool` = the tool name, `args` = the call args, `ok: False`, `kind: 'ask'`, `detail` = the `Ask.reply()` text. Approved asks are not duplicated (the tool call itself is recorded as today). Guard against double-recording with the `before_tool` hook denial path at `agent.py:1055-1057`.
5. Tests (in the relevant notebooks): timeout=None waits until resolved (resolve from another thread after a short delay); ACP/default constructor still has 300; a refused ask produces exactly one activity row with the fields above and the reason text; the CLI input handler re-asks on non-answer text and refuses on `n: reason` (test the handler function directly, not a live terminal).

- [ ] TDD each requirement; `nbdev-prepare` → Success; bump `ramabana/__init__.py` to `0.1.39`; commit "Wait for, re-ask and log approval prompts".

### Task 3: dhrona — detect and teach the right response to a refusal

**Repo:** `/Users/71293/code/personal/orgs/drona` (package `dhrona`). **Files:** `nbs/00_core.ipynb`, `nbs/03_tools.ipynb`, new seed `dhrona/seeds/approval-refused.json`, `nbs/index.ipynb`.

1. `assess_history`: new finding kind `denial_retry` when a refused call (activity row `ok is False` and `kind == 'ask'`, or detail starting `Denied by human operator`) is followed — later in the same turn or in the next turn of the same session — by a call with the same tool and args, with no user-facing question in the intervening reply (reply text lacks `?`). Message: `Ask the user about the refused call instead of retrying it.`
2. `tool_report`: add `denials: {tool: count}` and `denial_reasons: [[reason, count], ...]` (normalised like failures) from rows with `kind == 'ask'` or detail starting `Denied by human operator`; `fmt_report` prints a denials line.
3. Seed round `approval-refused.json` (accepted, reviewer Karthik, `tools: ['view_file', 'replace_text']`): user asks for a small edit; assistant views the file; assistant calls `replace_text` with args that bind to the *current* shalya `replace_text` signature (inspect `/Users/71293/code/personal/orgs/shalya/shalya/tools.py` for the real parameter names); tool result `Denied by human operator. Reason given: no answer after 300s`; final assistant text leads with the refused action and one question, e.g. "I need your approval to edit `x.py` — the approval prompt timed out, so nothing changed. Approve the edit (or run `/approve edits`) and I'll apply it." Test: `round_valid` against stand-in functions with the real signatures; `warm_start` with those stand-ins returns both seeds.
4. README: one paragraph on refusals.
5. Bump `dhrona/__init__.py` to `0.1.2`; `nbdev-prepare`; commit "Detect retries after refusals and seed the approval round".
