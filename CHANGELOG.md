# Release notes

<!-- do not remove -->

## 0.1.20

- Each replay, editor and judge run gets `--max-cost`: the dollars left in its round's limit (`ROUND_LIMIT`, $8) or in the night's `budget`, whichever is smaller. Ramabana stops the turn after the model step that passes it. Before, both limits were checked only between runs, so one replay cost $20.94 against an $8 limit and a $20 night.
- A run that records no turn says why: `no turn was recorded (exit 1): The turn model, gpt, cannot run here: needs OPENAI_API_KEY ...`. Before, the error named only the run log. `night_error` still turns that into its hint to set the schedule's `model`.
- Needs ramabana 0.2.80, the first release with `--max-cost`.

## 0.1.19

- Uncommitted files in the learned folder never stop a batch, a round's keep or a compaction. Before, `improve_batch`, `learned_repo` and `_compact` raised `has uncommitted changes; commit or discard them`, which refused a whole night. Dhrona never stages, commits or discards a person's edit.
- A round keeps a lesson as an entry in `dhrona-<date>.md`, one file a day (`keep_lesson`, `lesson_entry`). The entry holds the request and the round's notes, with no diff. `keep_lesson` commits the file as Dhrona on a new `pending/` branch, as `keep` did for a candidate, so a person accepts it with `ramabana-learned accept`. It does not check the branch out and does not touch the learned folder's branch, index or files. A second lesson on the same day goes on its own branch, whose file holds both entries. The round's report names the branch as `pending`.
- Replays start from the learned folder's committed HEAD (`committed_copy`), so a replay never sees uncommitted text.
- `LEARNED_MAX` (2,000) counts `AGENTS.md` alone, as before. Dated learning files have their own limit, `DATED_MAX` (4,000 characters across all of them). A lesson that would pass it is not kept, and the round's `problems` says so.
- `expire_dated` removes each dated learning file over `DATED_DAYS` (30) days old, with `git rm` and a commit of that path alone as Dhrona. `expire_learned` calls it, and it works on a folder with uncommitted changes. The `AGENTS.md` and skill expiry still skips a folder with uncommitted changes, and now stages and commits only the paths it changed, not everything (`git add -A`).
- A fixed-defects record, `~/.config/dhrona/fixed.json`, keyed by the issue draft's slug, holds when a fix was made, a note and an optional quick check, a shell command or a `module:callable` path. `record_fix` and the `dhrona-fixed` command write it. `history_health(fixed=...)` counts only occurrences after the fix, `health_findings` reports a recurrence as `recurred after fix`, and `nightly` runs each check once before the batch and lists failures in the note. Issue drafts name their slug and the command.
- `committed_copy` no longer fails on a learned folder whose HEAD has no files.

## 0.1.18

- A `history_health` group's examples name up to three distinct sessions. Before, one session failing three times filled every slot, so an issue draft showed the same call three times.

## 0.1.17

- An untracked hidden path in the learned folder, such as a `.kosha/` code index, no longer stops a batch, and `learned_repo` excludes `.kosha/` in new repos. A modified tracked file still does.
- A refused night is visible: `improve_batch` makes the night's folder before its checks, writes `night-failed` and a `summary.json` holding the error, and `nightly` returns `night refused: ...` instead of raising.
- `history_health(cfg, days=14)` reads the history in one streaming pass: log size, rows and bytes per day, the largest row, tool-error groups with counts against the previous window (each a defect, habit or noise), guard refusals, back-to-back repeats and sub-agent results without a `state:` line.
- `health_findings` adds beat lines when the log passes `LOG_MAX_MB` (200) or grows over `LOG_GROWTH_MB` (20) a day, a row passes `ROW_MAX_MB` (5), or a defect group passes `DEFECT_MAX` (20) in 14 days or doubles. `issue_drafts` writes `issues/<slug>.md` for each defect over threshold, and `lesson_candidates` writes habit groups to `lessons-candidates.md` in the night's folder.
- `improve_round` stops a round whose recorded cost passes `limit` (`ROUND_LIMIT`, $8).

## 0.1.16

- The nightly note and `dhrona-improve` end with `REVIEW`: "review with: /learned in Ramabana, or ramabana-learned in a shell". They said `ramabana-learned list`, which fails: the command takes its subcommand as `--cmd`, and lists when given none.

## 0.1.15

- `read_history` gives back tool results whole. Since Ramabana 0.2.59 a result over 600 characters is stored in `<cfg>/<log>-details/<session>.jsonl` and the history row keeps only its first 600 characters, so assessments, tool reports, rounds and the nightly batch saw clipped results. It now reads them through Ramabana's `hydrate_turns`, and requires ramabana 0.2.60. Older rows, with their results inline, read as before. Whole results also reach a round's warm-start messages and `tool_report`'s failure keys.
- The git commands behind replays and the learned folder get `/dev/null` as stdin, so they never read the caller's terminal.

## 0.1.14

- A night where every round failed and nothing was spent raises `NightFailed` with its note, so the beat retries it, and leaves a `night-failed` marker; `tried_sessions` passes over a session only after `FAILED_TRIES` (2) such nights, so the retry replays the same sessions. The documented schedule is `retries=2, retry_after='1h'` (pobblebonk 0.0.5).
- The nightly note lists each failed round's first error line (`night_error`). Ramabana's `/model NAME` advice becomes the schedule key to set, `model` or `editor`, and a Claude Code login failure says to run `claude /login` or use Ramabana's `beat.env`.
- `run_turn` starts the replay in its own process session and kills the whole group on a timeout or any interruption, so a `claude` or `git` the replay started does not outlive it.
- The `dhrona` schedule's payload takes `timeout`, the seconds before a replay, base or candidate, is abandoned, 1,800 by default. `improve_round`, `improve_batch` and `dhrona-improve --timeout` take it too. A replay on a local model that hangs then costs at most that long, and the round's batch row carries `the run in ... was still going after Ns`. `nightly` accepts the number as text, and raises `ValueError` before any round for a `timeout` that is not a positive number.

## 0.1.13

- A compaction's commit message is no longer scrubbed. It holds only ids, counts and times, and `scrub` read about one pending id in ten as a card number, which broke the `Includes:` trailer and so the candidate a compaction folded in. `keep(scrubbed=False)` commits a message as given.

## 0.1.12

- A compaction's editor turn counts against the nightly `budget`. `compact_learned` returns its `cost`, `compaction.json` records it, the night's total includes it, and the note's compaction line shows it. A compaction that spends the budget leaves no round to run.
- Accepting a compaction no longer renews the lessons it rewrote. Each rewritten paragraph takes the newest time of the lessons it draws on, matched by shared words, or of all of them when none matches. The commit's `Lesson-times:` trailer (`TIMES`) records it per line, and `expire_learned` reads it through `_blame`, so a paragraph merged from stale lessons expires on their schedule.
- `compact_learned(onto=ID)` folds in a pending candidate refused for size: it compacts the file that candidate would make, carries the candidate's other files, and names it in an `Includes:` trailer (`INCLUDES`), so accepting the compaction accepts the candidate. Ramabana 0.2.41 uses it for `/learned compact ID`.

## 0.1.11

- `compact_learned(learned, target, chat, editor, exe)` proposes a shorter learned `AGENTS.md`. git blame splits HEAD's file into the paragraphs Dhrona proposed and the rest. The editor model rewrites only Dhrona's paragraphs: it merges lessons that overlap, drops duplicates and lessons a later one replaced, and keeps fenced blocks whole, aiming at `COMPACT_TARGET`, 1,200 characters, for the whole file. A person's paragraphs reach the editor only as `[kept N]` markers and come back byte for byte. The prompt and the rewrite are scrubbed. A rewrite that drops, moves or edits a marker, drops a fenced block, is no shorter, or passes `LEARNED_MAX` is refused and nothing is committed.
- A compaction waits on a `pending/` branch with the message `Compact learned AGENTS.md (N → M characters)`, so `ramabana-learned` reviews it. What it wrote counts as Dhrona's own and expires as a lesson does. `compact_learned` takes `learned_lock` and returns `{ok, pending, before, after}` or `{ok: False, error}`. It refuses while a batch runs, with uncommitted changes, with no paragraph Dhrona proposed, and while a compaction is already pending.
- A night proposes a compaction after expiry and before the rounds when `AGENTS.md` is over the schedule's `compact_at` of `LEARNED_MAX`, 0.8 by default, and its note says `compaction pending <branch>`. It tries one compaction per HEAD, so a rejected one is not proposed again until HEAD moves. `improve_batch(compact_at=)` does the same and writes `compaction.json`.

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
