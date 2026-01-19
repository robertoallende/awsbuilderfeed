# Unit 07: Prefect Naming Convention

## Objective

Update flow and task names to use a project prefix for visual separation in the shared Prefect UI.

## Context

This machine now runs multiple Prefect projects on a shared server (`localhost:4200`):
- **builderfeed** (this project)
- **backup** (SD card mirror backup - `~/backup/`)

To maximize visual separation in the Prefect UI, all projects adopt a naming convention:
- Flow/task names prefixed with project identifier
- Consistent tags for filtering

## Implementation

### Current State

```python
# src/flows.py
@flow
def fetch_flow():
    ...

@flow
def tweet_flow():
    ...

# deploy.py
fetch_deployment = fetch_flow.to_deployment(
    name="fetch-articles-deployment",
    tags=["builderfeed", "fetch"]
)

tweet_deployment = tweet_flow.to_deployment(
    name="post-tweets-deployment",
    tags=["builderfeed", "tweet"]
)
```

### Target State

```python
# src/flows.py
@flow(name="builderfeed: fetch-articles")
def fetch_flow():
    ...

@flow(name="builderfeed: post-tweets")
def tweet_flow():
    ...

# deploy.py
fetch_deployment = fetch_flow.to_deployment(
    name="fetch-articles-deployment",
    tags=["builderfeed"]
)

tweet_deployment = tweet_flow.to_deployment(
    name="post-tweets-deployment",
    tags=["builderfeed"]
)
```

### Changes Required

| File | Change |
|------|--------|
| `src/flows.py` | Add `name="builderfeed: ..."` to `@flow` decorators |
| `deploy.py` | Simplify tags to `["builderfeed"]` |

### UI Result

After changes, Prefect UI shows:
```
Flow Runs
─────────────────────────────────
backup: sd-card-sync        [backup]
builderfeed: fetch-articles [builderfeed]
builderfeed: post-tweets    [builderfeed]
```

Flows group alphabetically by project prefix. Tag filter isolates each project.

## Files Modified

- `src/flows.py`
- `deploy.py`

## AI Interactions

Used Claude Code to:
- Update flow names in `src/flows.py`
- Simplify tags in `deploy.py`
- Restart systemd service

## Status: Complete

Changes applied and service restarted. Flows now appear as:
- `builderfeed: fetch-articles`
- `builderfeed: post-tweets`
