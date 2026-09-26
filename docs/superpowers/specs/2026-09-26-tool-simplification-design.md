# Tool simplification and warm starts — design

Date: 2026-09-26 · Repos: drona, vishalakshi, shalya, ramabana, leela

## Goal

Agents built on shalya/ramabana/leela are offered 70–90 tools per turn (shalya 56, ramabana +14, leela +~20). Only ~11 are used heavily and ~25 at all. Make the model pick the right tool by (a) fixing tools whose plumbing or schema makes them fail or unattractive, (b) removing true duplicates and model-facing housekeeping, (c) gating contextual tools to their mode, and (d) teaching the remaining set with drona warm-start rounds. Simplify code toward fastai style along the way. Release each package to PyPI and consume the releases downstream.

Non-goals: fine-tuning weights; redesigning the agent loop; refactoring leela/ramabana monoliths beyond the touched code.

## Evidence (history 2026-08-03 → 09-25, 17,481 calls)

- Usage: run_shell 3071, view_cell 2351, view_file 2128, grep 2083, edit_cell 1794, search_code 844 … ~30 tools never called.
- Low usage ≠ low merit. 774 run_shell calls were git (452 compound `git status && git diff && git log`), but git_diff/log/commit/stash/checkout only landed 2026-09-23 (shalya bd8d4dc). Genuine current bypasses are ~7% of run_shell (grep/find 107, cat/sed -n 47, ls 34, heredoc writes 33, `&` 7, curl 6).
- Schema is the biggest failure source: JSON-in-string args fail on JSONDecodeError — edit_cell 20% fail, edit_file 42% (plus stale lnhash), replace_text 7% (two competing arg names `spec`/`edits`), delegate_parallel 7%. ~130 failures.
- Bypass varies by model: Claude opus/sonnet-5 and small models 53–90% of shell calls had a dedicated tool; GPT-5.6/6 codex 22–36%.

## Principles

1. Judge tools on merit; fix plumbing and teach before culling.
2. Housekeeping (polling, staleness, environment) belongs to the harness, not model tools.
3. Contextual tools appear only in their context.
4. Tool params are native types (`list`, `dict`, `bool`), never JSON-encoded strings.
5. Drona measures before/after and teaches with rounds.

## Target tool set

Default (capability-gated as today):

| Group | Tools |
|---|---|
| code | `search_code`, `grep`, `ls(path='', pattern='', recursive=False)`, `outline`; `public_api`, `similar_code` only when `host.indexed` |
| file | `view_file`, `replace_text(path, edits: list[dict])`, `create_file`, `add_root` |
| notebook | `notebook_cells`, `view_cell`, `edit_cell(path, cell_id, edits: list[dict])` (replace_text dialect), `add_cell` |
| shell | `run_shell`, `run_shell_bg`, `shell_output`, `shell_stop` |
| session | `run_python`, `inspect_python(code='')` (empty lists vars), `read_terminal` |
| web | `web_search`, `read_url` |
| git | reads `git_status`, `git_diff(staged=False, path='')`, `git_log(n=10, path='')`, `git_divergence(against='', path='')`; writes `git_commit(message, paths='', amend=False)`, `git_checkout(branch, create=False, path='')`, `git_stash(action='push', message='', path='')`, `git_remote(op='fetch', publish=False, path='')` |
| memory (vault) | `memory_search` (rows carry `age`, `stale`), `memory_read(ref='')` (empty → roots, doc → tree, node → text), `remember(text, title='', tags='', key='')`, `memory_forget(doc_id)` (writes, user request only), `ask_memory(question, document='', instruction='')` |
| watch (vault) | `watch(target, kind='url', every='1d', note='', instructions='', pattern='')` with kind ∈ url/remind/search/folder, `list_watches(due_only=False)`, `cancel_watch(watch_id)` |
| skill | `read_skill` |
| plan | `set_plan(items: list[str])`, `update_todo(id='', status='', text='')` (empty id appends) |
| delegate (subagents) | `delegate_search(questions: list[str])`, `delegate_async`, `delegate_result(run_id='')`, `delegate_cancel` |

≈32 core; ≈43 with vault + subagents.

Opt-in / contextual: `api_load/api_ops/api_call` (ApiHost), `canvas_*` ×8 (canvas open), `news_*` ×6 (feeds exist), video ×3 (key), `generate_image` (key+writes), `create_skill` (author mode), `research` (no subagent backend), `edit_file` (exhash mode), `run_cell` (leela kernel).

Removed / absorbed: `list_files`→ls, `memory_tree`→memory_read, `list_vars`→inspect_python, `delegate_parallel`→delegate_search, `delegate_status`→delegate_result, `git_rebase_preview`→git_divergence, `add_todo`→update_todo, `list_plan` (plan is in prompt and every mutator returns it), `environment` (already in system prompt), `poll_watches`/`check_folders` (harness polls), `set_reminder`/`watch_url`/`watch_folder`/`list_folder_watches`/`cancel_folder_watch`→watch, `no_save_read` (internal alias only), `memory_topics`, `inspect_var`→inspect_python, `search_all`→search_code, `api_access`→api context, `user_steering` (internal, never advertised), `remember_note`→`remember` fallback of the same name.

Removed names keep a one-release deprecation shim only where external callers exist (slash commands, MCP); otherwise delete.

## Per-repo design

### drona (phase 1)

- Fix `core.py:70` precedence bug (`tool=='edit_cell' and any(s in detail for s in (...))`).
- Simplify: fastcore `Path` everywhere, `read_json`/`write_json`, `asdict`, one shared helper for "prompts not skipped → Dialog" and the review-note cell used by `rounds.py`/`sessions.py`, no needless lazy imports.
- `drona-tools [--since DATE] [--model M] [--history PATH...]` (CLI name `drona-tools`): per-tool calls, fail rate, top failure details, shell/python bypasses (classifier mapping command → dedicated tool), per-model bypass share. JSON and a compact table. This is the before/after instrument.
- Assessment findings extended with `bypass` (shell command with a dedicated tool) and `schema` (JSONDecodeError on any tool).
- Rounds carry `meta['drona']['tools']` (tools demonstrated) and `model`. A round library dir (`~/.config/drona/rounds/` + packaged seeds; `drona-accept --install` adds to it). `warm_start(tools, model=None)` selects accepted rounds that are valid while every recorded call binds to the live tool signature (`call_valid`, via `inspect.signature(...).bind`); stale rounds are skipped, same-model rounds sort first. Replace the hard-coded Urai demo with a seed round.
- Seed rounds: git flow (status → diff → commit → divergence → remote), notebook edit (notebook_cells → view_cell → edit_cell), search (search_code vs grep vs ls), memory (remember with key → memory_search), delegation.
- Release 0.1.0 to PyPI (confirm before upload).

### vishalakshi (phase 2)

- `Vault.note(..., key='')` upserts by `source=f'note:{key or slug(title)}'` with `force=True`; reminder fires upsert `reminder:{watch_id}`.
- Web re-read refreshes when content hash changes (port leela `Memory.remember` hashing).
- Search/tree rows expose `age` and `stale`; `stale` is a `doc_marks` flag; ranking demotes stale.
- `Vault.poll()` housekeeping: mark stale when file source mtime moved/vanished, web doc older than per-kind TTL and unwatched, or superseded by a watch; prune only stale ∧ superseded.
- Watches table gains `kind` folder + `instructions`/`pattern` so folder watches persist.
- `ask` policy: `local` when a local runtime exists else `redact`; never `off`. Retrieval PII setting stays separate.

### shalya (phase 3)

- Apply the target tool set to `tools.py`/`host.py`; native-typed params; one edit dialect (`edits: list[dict]`) for replace_text and edit_cell; edit_file moves to an opt-in exhash group.
- Git: expose gheasy `undo` token and `summary` in write results; `amend`, `create`, `publish`; `GIT_TERMINAL_PROMPT=0`; sharper one-line docstrings naming the operations.
- `memory_*`/`watch` per target set; `remember(key=)`.
- Style: docstrings ≤ one line, drop redundant local imports, absorb `except NotImplementedError: raise` boilerplate in a helper, remove the `core → tools` lazy import, stop importing gheasy private `_said`.
- Release 0.1.0.

### ramabana (phase 4)

- Bump shalya; drop removed extras (add_todo, list_plan, delegate_status, delegate_parallel, monitor tools → vault watch, remember_note → remember fallback); cart tools stay opt-in extension.
- Git: snapshot/settle tree around git writes so rewind sees them; `before_tool` hook on run_shell classifying `git commit|push|pull|fetch|stash|switch|checkout` → error pointing at the git tool; RULES entry keyed on `git_status`; rewrite the CLAUDE_NOTES git line to exempt read tools.
- Drop `exhash` from INLINE_SKILLS when edit_file is not offered (~3k tokens/turn).
- Harness fires watch polling at turn start (already ticks) and injects notes.
- Warm start: `session_start` calls `drona.warm_start(tool_names, model)` when drona is installed (optional dep `ramabana[drona]`); `--no-warm` flag.
- Trim `tools.py` re-export shim of removed names. Release 0.2.0.

### leela (phase 5; starts after the user commits current agent-pane WIP)

- Bump ramabana/shalya; remove shims for inspect_var, search_all, api_access; never advertise user_steering.
- Gate canvas_* on canvas open and news_* on feeds; if the backend fixes its tool list per session, rebuild the tool list at turn start (verify in `Assistant.tools` / `TurnRunner`).
- `vault_pii` no longer governs ask; ask uses local-else-redact.
- `Threads.new` applies `drona.warm_start`.
- Consolidate the seven `leela/agent/*.py` shims into `leela/agent/__init__.py`. Release via fastship.

## Testing

- Each phase: nbdev test cells (drona/shalya/ramabana, run `nbdev-prepare`) or pytest (leela, vishalakshi) covering new params, removed names, and failure paths (bad JSON no longer possible for list params; git write returns undo; stale marking; ask policy never off).
- `drona-tools` baseline captured before phase 3 and re-run after phase 5 on fresh sessions; success = JSON decode failures ≈ 0, git shell writes ≈ 0, default tool count ≤ 45 with vault+subagents.

## Release order

drona → vishalakshi → shalya → ramabana → leela. Each release bumps the downstream pin. PyPI uploads happen only after explicit user confirmation per package.

## Risks

- Leela backend may bind tools once per session; contextual gating may need a backend rebuild — verify before implementing.
- Renamed/removed tools break saved approval rules and old drona rounds; `call_valid` makes rounds stale explicitly (a call that no longer binds to the live signature drops the round), approval rules keyed on removed names are dropped with a log line.
- Git undo/rewind integration touches ramabana's `_record`; keep it behind the existing snapshot API.
