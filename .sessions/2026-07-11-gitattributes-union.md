# 2026-07-11 — repo hygiene: merge=union for the append-only ledgers

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · mechanical refactor (gitattributes-union builder, coordinator-assigned) · 2026-07-11T18:12Z–18:2xZ (`date -u`)

## What happened

Micro-hygiene slice, one build PR after a control fast-lane claim
(PR #62, `control/claims/gitattributes-union.md`, merged then removed
here): root `.gitattributes` marking the two append-only JSONL ledgers
`merge=union` —

- `.substrate/guard-fires.jsonl` — the kit appends a record on every
  `check`/hook guard fire, so ANY two concurrent sessions collide there;
  the ORDER-002 self-review recorded three hand-resolved recurrences
  (PRs #27, #38, #41) plus a fourth in the buy-max slice, each via
  stash → rebase → pop with zero content conflicts, and suggested
  exactly this gitattribute.
- `telemetry/model-usage.jsonl` — same append-only contract; both feeds
  are pinned append-mode-only in bootstrap.py ("Telemetry substrate":
  "full-file rewrites are never performed on either feed", one-line
  atomic appends, JSONL chosen over a JSON array precisely because
  appends beat rewrites — plan D-10). Union-merging an append-only feed
  is lossless by construction; line ORDER across sides is not
  guaranteed, which these unordered ledgers tolerate (readers key on
  `ts`/`session`, never on position).

WHY a one-line `.gitattributes` and not process discipline: union merge
makes git itself keep both sides' appended lines, so the recurring
conflict class disappears for every future concurrent slice instead of
each one re-paying the stash/rebase/pop tax.

Ownership check before touching the root: `.gitattributes` appears
NOWHERE in bootstrap.py (kit v1.7.1) or the kit backup — it is
host-owned surface, same class as the `.gitignore` PR #6 added.
State-shaped non-append files (`.substrate/state.json`,
`episodic_index.json`) are rewritten in place, NOT append-only —
deliberately excluded from the attribute.

Union behavior demonstrated in scratch repos before shipping: (1) two
branches each appending one line to a base guard-fires.jsonl —
`git merge` WITHOUT the attribute = `CONFLICT (content)`; WITH it =
clean auto-merge, resulting file carries base + both appended lines;
(2) the recorded pain shape — `git rebase` of an appending feature
branch over an appending main — rebases clean with the attribute, both
lines retained. Verify: `python3 -m pytest -q` green,
`python3 bootstrap.py check --strict` green with this flip.

## 💡 Session idea

The ORDER-002 self-review floated this as a KIT-level fix
(`.substrate/*.jsonl merge=union` planted by adopt/upgrade). This PR is
the host-side proof; worth relaying upstream via the manager so every
fleet repo stops re-paying the conflict tax — the kit would plant the
attribute next to the ledgers it owns, and the host-owned root file
here would simply become redundant-but-harmless.

## ⟲ Previous-session review

The buy-max card (2026-07-11-buy-max-math.md) closed by noting the
merge=union idea was "three-for-three justified" after its own
guard-fires stash/pop dance — this slice is that prediction cashed in,
and its scoping held: the fix really was one attribute line plus
verification, no engine surface. Its broader habit worth keeping: it
pinned the load-bearing NEGATIVE result (single-floor closed form
unsound) in tests; the analogous move here was pinning what the
attribute must NOT cover (the rewritten-in-place state files), recorded
above so a future "just glob `.substrate/*`" widening has to argue
against it.
