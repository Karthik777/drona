# Release notes

<!-- do not remove -->

## 0.1.10

- A kept candidate waits for review. `keep` commits it on a new `pending/<id>` branch of the learned folder's repository, in a temporary worktree, and leaves the folder's files, which Ramabana reads, alone. Every round of a batch starts from HEAD. A round's report and a batch row name the branch as `pending`; `nightly` and `dhrona-improve` list the pending branches and point at `ramabana-learned list`. `learned_repo` makes the folder a repository the first time, with what it already held as the first commit.
- Personal details never reach the editor, the judge or the learned folder. `scrub` masks emails, phone numbers, keys and other identifying values with rahasya as numbered labels such as `[EMAIL_1]` (`SCRUB_KINDS`). It runs over every evidence file, the judge's prompt, the editor's notes and commit message, and every file of a candidate before the candidate is run, so what is tested is what is kept. The editor and the judge stay on Ramabana's normal routing. Requires rahasya 0.0.5.
- The editor reads recent lessons. `recent_lessons(cfg, days)` reads every structured `remember` call in Ramabana's history, vault or memory file alike, through shalya's `parse_lesson`, newest first and scrubbed. `improve_batch(cfg=)` gives them to each round as `lessons.md`, tool defects first, and the mission asks for a skill that works around a tool defect the runs also show. Requires shalya 0.1.14.
- What Dhrona proposed expires when unused. At the start of a batch with `cfg`, `expire_learned` removes skills nobody read and `AGENTS.md` paragraphs no accepted round renewed in `days` days (default 30, the schedule's `expire_days`), and commits the removal. Only commits Dhrona proposed expire, a fenced block is never split, and nothing expires when nobody worked in that time. A night with no session left still expires.

## 0.1.9

- `delivered` needs a `state` of `complete`, and `trainable` skips a first turn that did not end complete. A run that was stopped, abandoned or interrupted has no error, so a cut-off replay could count as a cheaper delivered candidate.
- `trainable_sessions` matches a `start.json` entry on the resolved repository path. Ramabana writes resolved paths, so a root reached through a link used to ignore the entry and its uncommitted changes.
- An unreadable `start.json` or `agent-sessions.json`, or one that holds the wrong shape, counts as missing. It used to raise and end the whole night.
- `learned_lock` raises `BatchBusy`, a `RuntimeError`. `nightly` returns a note for it instead of raising, so a beat that takes back a night still running past pobblebonk's 300-second lease leaves no retries and no "gave up" note. Uncommitted changes in the learned folder still raise.
- `improve_batch` takes `models` as a comma-separated string as well as a list. A string used to match by substring.
- The docs are in plain sentences, and imports sit in their own cells so the docs build runs.

## 0.1.8

- `improve_batch` and `dhrona-improve` take a `budget` in dollars. No round starts once the rounds so far have cost that much. A batch can pass its budget by the cost of its last round.
- Each batch row's `cost` is the dollars every run in the round's folder recorded, whether or not the round finished (`round_cost`). `dhrona-improve` prints the batch's total.
- A batch with a learned folder holds `learned_lock` for its whole run. A second batch on the same folder raises `RuntimeError` before it creates anything.
- `nightly` runs one scheduled batch over the sessions no earlier night started a round on (`tried_sessions`), within the schedule's `budget`. A fire without a positive budget raises `ValueError`. Dhrona registers `nightly` with `ramabana-tick` through the `ramabana.ticks` entry point `dhrona`.

## 0.1.7

- The judge sees each run's refused shell commands under its answer, as what the run would have done with approval. A command the request needed, stated so the person can run it, counts as done. `refused_commands` lists them, and `judge_prompt` builds the prompt.
- When a round has the person's own session of the request, the judge sees the commands that session ran, failed or declined, with the person's reason, as what the work needed. `ran_commands` lists them. The editor reads the whole session as `original.md`.
- `trainable` keeps each session's first turn as `turn`, and `improve_batch` passes it to `improve_round(original=)`.
- Replay clones have no remote, so nothing in a replay can push to the person's repository.

## 0.1.6

- `dhrona-improve` and `improve_batch` run improvement rounds over past Ramabana sessions in turn. Each round starts from the learned folder the previous one left. `summary.json` holds one row per round, and a failed round is a row with its error. `--models`, `--skip` and `--max-calls` choose the sessions.
- `trainable_sessions` finds sessions to replay: self-contained first turns whose route cost something, placed in the repository their tool paths touched and replayed from its last commit before the turn.
- A candidate with a cheaper route is kept only when `judge_reply`, a blind judge over every reply, says its answer is at least as complete as the best base answer.
- Replays may edit files in their clone with `approve='edits'`, and read outside it by default. Route cost ignores approvals refused because nobody could answer.
- `bypass_tool` flags a shell command only when every part of it has a dedicated tool. `git show`, `git log` with patches, stats or searches, and `git diff` against refs are not bypasses. Separators inside quotes and heredoc bodies no longer split a command.

## 0.1.5

- `dhrona.improve.improve_round` runs one improvement round for Ramabana's learned folder. It replays a session's request from the commit the session started at, edits a copy of the folder with an editor model, and keeps the copy only when its run replied and cost less than every base run. A route costs its findings, then its failed or refused calls, then its calls.
- `keep` commits a kept copy in the learned folder's own git repository, authored by Dhrona. It first commits what the folder already held, and refuses a folder with uncommitted changes.
- `check_learned` allows only `AGENTS.md`, up to 2000 characters, and `skills/<name>/SKILL.md` with a matching `name` and a `description`.

## 0.1.4


## 0.1.3


## 0.1.2


## 0.1.1


## 0.1.0
