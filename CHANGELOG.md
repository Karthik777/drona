# Release notes

<!-- do not remove -->

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
