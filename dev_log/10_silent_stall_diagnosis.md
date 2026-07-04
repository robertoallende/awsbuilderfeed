# Unit 10: Silent Runner Stall Diagnosis

## Objective

Diagnose why `fetch-articles-deployment` (and `post-tweets-deployment`) stopped
producing scheduled flow runs for an extended period, with no crash and no
error logged.

## Problem

No new articles were being fetched and no new tweets were going out, despite
both `builderfeed.service` and `prefect-server.service` reporting as
`active (running)` the entire time.

## Evidence

**Article fetch activity by month** (from `articles.fetched_at`):

| Month | Articles fetched |
|---|---|
| 2026-01 | 332 |
| 2026-02 | 1061 |
| 2026-03 | 1460 |
| 2026-04 | 1220 |
| 2026-05 | 1287 |
| 2026-06 | 245 |
| 2026-07 (partial) | 10 (before fix) |

**Gap analysis:** a 27-day gap in fetch activity, from **2026-06-07 to
2026-07-04**, with zero articles fetched in between.

**systemd journal (`builderfeed.service`):** the last log line before the gap
is a normal, successful `fetch_articles_task` completion at `18:30:08` on
June 7:
```
Jun 07 18:30:07 ... Task run 'fetch_articles_task-b8c' - Fetched: 10, Added: 0, Skipped: 10
Jun 07 18:30:07 ... Task run 'fetch_articles_task-b8c' - Finished in state Completed()
Jun 07 18:30:08 ... prefect.flow_runs.runner - Process for flow run 'certain-sawfly' exited cleanly.
```
No further log lines appear until the service was manually restarted on
2026-07-04. No exception, no traceback, no warning — just silence.

**No reboot occurred in this window.** `journalctl --list-boots` and `uptime -s`
confirm the Pi has been running the same boot continuously since
2026-03-19, well before and after the gap. The `builderfeed.service` process
(PID `2543755`) was the same PID for the entire 27 days per `systemctl status`.

**`prefect-server.service`** also produced no log output during the gap
window — consistent with a server that's technically up but idle, not with a
crash/restart cycle.

## Diagnosis

The Prefect `serve()` runner's internal scheduling loop stopped submitting new
scheduled flow runs at some point after `18:30:08` on June 7, without raising
an exception or exiting the process. The OS-level process stayed alive and
"healthy" from systemd's point of view (no crash → no automatic restart),
but it was no longer doing its job internally.

This is consistent with a known class of issue in long-running async
schedulers: a stuck/hung background task (e.g., a network call without a
hard timeout, or an internal deadlock) can silently wedge the event loop
without killing the process. Because nothing crashed, there was no signal
for systemd, logs, or monitoring to catch — the outage was only discovered by
manually comparing `fetched_at` timestamps in the database against wall-clock
time.

Restarting `builderfeed.service` (done today for an unrelated code deploy)
immediately and fully resolved the issue — flows resumed running on their
normal schedule right away, with no further code changes required.

## Potential Solutions

### Option 1: External DB-based watchdog (recommended, low effort)
A small script checks `MAX(fetched_at)` in the `articles` table. If it's
older than ~3x the fetch interval (e.g., 3 hours), it runs
`systemctl restart builderfeed`. Wire it to a systemd timer (every 15–30 min).

- ✅ No changes to `deploy.py` / `flows.py`
- ✅ Uses ground-truth data (an article was actually fetched), not just
  "is the process alive"
- ⚠️ Treats the symptom (auto-heals) rather than the root cause — if the
  runner hang recurs, we just restart it silently every time instead of
  understanding why.

### Option 2: systemd watchdog (`WatchdogSec` + `sd_notify`)
The app periodically calls `sd_notify(WATCHDOG=1)`; if it stops "pinging"
within `WatchdogSec`, systemd kills and restarts it automatically.

- ✅ More "proper" process-supervision pattern
- ⚠️ Requires adding heartbeat calls inside the flow/task loop (Prefect
  doesn't emit this natively) — more invasive code change
- ⚠️ Only proves the process is alive, not that it's actually submitting
  flow runs — could still miss a scheduler-loop-only hang unless the
  heartbeat is placed carefully.

### Option 3: Prefect Automations (built-in)
Self-hosted Prefect Server supports **Automations** that can trigger on
"flow run didn't start / complete within expected time" and send a
notification (or even trigger a webhook/action). Since a Prefect server is
already running here, this could flag lateness without any custom scripts.

- ✅ Uses existing Prefect infrastructure, no new script/timer to maintain
- ⚠️ Notifies but doesn't automatically restart the OS-level service —
  would still need a human (or a follow-up automation/webhook) to act on
  the alert.

### Option 4: Investigate root cause upstream
Check for a Prefect version known-issue/bug tracker entry matching this
symptom (runner silently stops submitting scheduled runs), and consider
upgrading Prefect or reporting the issue.

- ✅ Fixes the actual bug rather than working around it
- ⚠️ Unclear timeline / no guarantee of finding a fix, and doesn't protect
  against a recurrence in the meantime.

## Status: Diagnosed — Awaiting Decision

Root cause identified as a silent scheduler-loop stall in the Prefect
`serve()` runner process (no crash, no reboot, no error logged). Fixed for
now via manual restart. No monitoring/auto-recovery has been implemented yet
— a solution (or combination, e.g. Option 1 + Option 3) needs to be chosen
before this is considered resolved long-term.
