# AGENTS.md — Apache Solr Orbit Workloads

This file provides guidance for AI coding agents (Claude Code, Codex, Cursor, etc.) working in
this repository. Read it before making any changes.

## Project overview

This repository contains the default workload specifications for
[Apache Solr Orbit](https://github.com/apache/solr-orbit), the macrobenchmarking framework for
[Apache Solr](https://solr.apache.org/). It is an **Apache Software Foundation (ASF) project**
governed by the Solr PMC.

Each workload is a self-contained directory that defines:
- the Solr collection schema (`configsets/`)
- the data corpus references (`workload.json`, `files.txt`)
- the named operations (`operations/default.json`)
- the test procedures (`test_procedures/default.json`)

## Apache Software Foundation rules

This is an ASF project. The following rules are **non-negotiable**:

- Every source file must carry the standard Apache License 2.0 header. Do not remove or alter
  existing license headers.
- Do not add dependencies, tools, or services that are not ASF-compatible (Category A or B
  licenses only; GPL, AGPL, SSPL, and similar are forbidden).
- All commits must represent the contributor's own work or work they have the right to submit
  under Apache License 2.0 (DCO / ICLA obligations).
- Do not commit secrets, credentials, or personally identifiable information (PII) of any kind.
- The canonical project mailing list is **dev@solr.apache.org**. Significant decisions belong
  there, not in code comments or commit messages.
- Bug reports and feature requests live in
  [GitHub Issues](https://github.com/apache/solr-orbit-workloads/issues).

## Dataset attribution and licensing

Each dataset bundled in a workload carries its own licence. Agents **must not** strip, alter,
or omit these attributions.

### Adding a new workload dataset

Before introducing a new dataset, verify:
1. It contains no PII and no proprietary data.
2. You hold, or have obtained in writing, the rights to redistribute it.
3. Its licence is documented verbatim in the workload's `README.md`.
4. The licence is ASF-compatible (CC-BY, public-domain, ODbL, and similar are fine; CC-NC or
   CC-ND variants are **not** acceptable).

## Repository structure

```
common_operations/          # Shared operation snippets (collection lifecycle)
  create_collection.json
  delete_collection.json
  check_cluster_health.json
  optimize.json

<workload>/                 # One directory per workload (e.g. geonames/, nyc_taxis/)
  workload.json             # Collections, corpora, operations refs, test procedure refs
  workload.py               # (optional) Dynamic workload logic
  files.txt                 # List of corpus data files
  README.md                 # Required — see "Contributing a workload" section
  configsets/<name>/        # Solr configset: schema.xml + solrconfig.xml
  operations/
    default.json            # Named operations referenced by test procedures
  test_procedures/
    default.json            # At least one procedure must be marked "default": true
  common_operations/        # (optional) Workload-local operation overrides
```

Reuse the root-level `common_operations/` snippets for collection lifecycle steps. Do not
duplicate `create_collection`, `delete_collection`, `optimize`, or `check_cluster_health`
inside individual workloads.

## Branching model

| Branch | Purpose |
|--------|---------|
| `main` | Default; target for changes that apply to all Solr versions |
| `10`, `9`, … | Solr major-version branches; cherry-pick from `main` as needed |

`solr-orbit` automatically selects the branch matching the Solr version under test, falling
back to `main`. Use `--workload-revision` to pin an explicit branch.

When backporting: `main → 10 → 9`. If a cherry-pick conflicts, open a separate PR targeting
the version branch directly.

## How to test changes

There is no local test runner in this repository. Validation is done through the `solr-orbit`
CLI (from [apache/solr-orbit](https://github.com/apache/solr-orbit)).

### Quick sanity check (local Solr required)

```bash
# Test a modified workload using a local path
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload-path=/path/to/your/fork/<workload> \
  --test-mode

# Or use Docker to provision Solr automatically
solr-orbit run \
  --pipeline=docker \
  --distribution-version=10.1.0 \
  --workload=nyc_taxis \
  --test-mode
```

`--test-mode` reduces corpus size and iteration counts for fast feedback. Always run it before
claiming a change works.

### Full benchmark (required before opening a PR for a new workload)

```bash
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload-path=/path/to/your/workload
```

Include the result summary in the PR description.

## Code and file conventions

- **workload.json**: uses Jinja2 templating. Prefer `zstd` compression for corpora; include a
  `bz2` fallback via the conditional already established in existing workloads.
- **schema.xml / solrconfig.xml**: must carry the full ASF license header (see existing files
  as the template).
- **JSON files**: 2-space indentation, no trailing commas (standard JSON).
- Do not add comments to JSON files — JSON does not support comments and `solr-orbit` will
  reject malformed input.
- **README.md for a workload** must include: workload purpose, example document, parameters
  table, test procedures table, sample output, and dataset licence. See
  `nyc_taxis/README.md` as the reference implementation.

## Pull request checklist

Before opening a PR, confirm:

- [ ] `--test-mode` run completes cleanly against at least one supported Solr version.
- [ ] For new workloads: a full (non-test-mode) benchmark was run; output is in the PR description.
- [ ] Dataset licence is documented in the workload README and is ASF-compatible.
- [ ] No PII, credentials, or non-ASF-licensed code is introduced.
- [ ] ASF license header is present on every new source file.
- [ ] The PR description states which branches need backporting.

## What agents should avoid

- Do not edit `files.txt` unless you have actually verified the corpus file list.
- Do not change `base-url` values in `workload.json` — corpus hosting is managed by the
  maintainers and is pending migration to ASF infrastructure (see `INCUBATION_TODO.md`).
- Do not introduce Python dependencies in `workload.py` beyond the standard library and what
  `solr-orbit` already provides.
- Do not modify the branch protection or merge strategy configured in `.asf.yml` without
  explicit maintainer approval.
- Do not open issues, PRs, or send emails on behalf of the user without explicit instruction.
