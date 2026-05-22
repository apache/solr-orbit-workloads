# Contributor Guidelines

This repository contains the default workload specifications for
[Apache Solr Orbit](https://github.com/apache/solr-orbit).
This document is a guide on best practices for contributing to this repository.

## Contents

- [Before you start](#before-you-start)
- [Branch naming convention](#branch-naming-convention)
- [Contributing a change to existing workload(s)](#contributing-a-change-to-existing-workloads)
- [Test changes](#test-changes)
  - [Testing changes locally](#testing-changes-locally)
  - [Testing changes with integration tests](#testing-changes-with-integration-tests)
- [Publish changes in a pull-request](#publish-changes-in-a-pull-request)
- [Reviewing pull-requests](#reviewing-pull-requests)
  - [Backporting](#backporting)
- [Contributing a workload](#contributing-a-workload)
  - [Data and licensing](#data-and-licensing)
  - [Required files](#required-files)
  - [README.md contents](#readmemd-contents)
  - [Testing a new workload](#testing-a-new-workload)
  - [Data corpus hosting](#data-corpus-hosting)


## Branch naming convention

This repository uses major version branches named after the Solr major version number (e.g.
`9`, `10`). The `main` branch is the default.

When running a benchmark, `solr-orbit` automatically selects the workload branch that
matches the Solr version being tested. For example, benchmarking a Solr 10.X.X cluster will
use the `10` branch if it exists, falling back to `main` otherwise. To cherry-pick your
workload changes to the right branch, base that on the major version of the cluster you intend
to test against.

Use `--workload-revision` to pin a specific branch explicitly, regardless of the Solr version.


## Before you start

By submitting a contribution to this repository you certify that you have the legal right
to submit it under the Apache License 2.0 — for example, that it is your own original work,
or that you have the necessary rights from your employer or from any third-party rights-holders
whose work is included. You agree that your contribution may be distributed under the terms of
the Apache License 2.0.

For significant new features or design changes, it is recommended to first raise a discussion
on the [dev@solr.apache.org](https://lists.apache.org/list.html?dev@solr.apache.org) mailing list
or open a GitHub issue so the community can provide early feedback.


## Contributing a change to existing workload(s)

Before making a change, fork this repository and make the change on a feature branch.

- If your change is only relevant to a specific Solr version branch, base the feature branch off
  that branch (e.g. `10` for Solr 10.x).
- If the change applies to all versions, base the feature branch off `main` and backport as
  needed once merged.


## Test changes

After making changes in your feature branch, test them locally and optionally via GitHub Actions
integration tests in your forked `solr-orbit` repository.

### Testing changes locally

1. Start a local Solr cluster to test against (standalone or SolrCloud).
2. Run `solr-orbit` pointing at your modified workload using `--workload-path` or
   `--workloads-repository`. Use `--test-mode` for a quick sanity-check run:

```bash
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload-path=/path/to/your/fork/nyc_taxis \
  --test-mode
```

3. Verify the benchmark completes successfully and produces the expected output.

Additional tips:
- `--test-mode` reduces the corpus size and iteration counts so the run finishes quickly.
- To enforce a specific workloads branch from a remote repository, pass
  `--workloads-repository=https://github.com/<YOUR USERNAME>/solr-orbit-workloads` and
  `--distribution-version=X.Y.Z` to pin `solr-orbit` to the matching branch.

### Testing changes with integration tests

To catch regressions across the full suite, run integration tests from your forked
`solr-orbit` repository.

**One-time setup:**

1. Fork [solr-orbit](https://github.com/apache/solr-orbit).
2. In your fork, create a branch called `test-forked-workloads` based off `main`.
3. In that branch, update the integration test configuration to point at your forked workloads
   repository:

```ini
[workloads]
default.url = https://github.com/<YOUR GITHUB USERNAME>/solr-orbit-workloads
```

4. Push that branch to your fork.

**Running the tests:**

1. Cherry-pick your workload change(s) onto the relevant branches of your forked workloads
   repository.
2. Push those branches.
3. In your forked `solr-orbit` repository, go to **GitHub Actions → Run Integration Tests**,
   select the `test-forked-workloads` branch, and click **Run workflow**.
4. Verify that all tests pass.


## Publish changes in a pull-request

Before opening a pull request, make sure you have addressed the following:

1. **Describe the changes**: Explain what the change does and what problem it solves. For bug
   fixes, include a before/after comparison. For new features, show what users can expect.
2. **Indicate where to backport**: Note whether the change should be merged into `main` only or
   also backported to one or more version branches (e.g. `9`, `10`).
3. **Provide evidence of testing**: Paste a short sample output from your local test run, or link
   to a successful GitHub Actions run in your fork.
4. **Request review**: For changes that touch workload correctness or Solr-version-specific
   behaviour, tag a subject-matter expert.

Create a pull request from your fork to the
[`main` branch of this repository](https://github.com/apache/solr-orbit-workloads).


## Reviewing pull-requests

Reviewers and maintainers should:

1. Review the diff for correctness and scope — changes should be well-defined and minimal.
2. Confirm the change has been tested (local run output or CI link).
3. Confirm the PR description specifies which branches to backport.
4. For workload correctness questions, ensure a subject-matter expert has reviewed.
5. Label the PR with the appropriate backport labels before approving.


### Backporting

If the workload repository has Solr-version branches, changes should be cherry-picked from
`main` to the most recent supported branch and backward from there. For example:

```
main → 10 → 9
```

In the event of a merge conflict during backporting, open a separate pull request that applies
the change directly to the target branch. Ensure **only** the changes from the original PR are
included in the backport PR.


## Contributing a workload

For a step-by-step guide to creating a new workload from scratch or migrating one from
OpenSearch Benchmark, see
[CREATE_WORKLOAD_GUIDE.md](https://github.com/apache/solr-orbit/blob/main/CREATE_WORKLOAD_GUIDE.md)
in the `solr-orbit` repository. If you are migrating an existing OSB workload, the
[converter tool](https://github.com/apache/solr-orbit/blob/main/docs/converter/) can
automate much of the mechanical translation.

See the [Apache Solr Orbit documentation site](https://apache.github.io/solr-orbit/)
for the full workload specification reference, including operation types, Jinja2 templating,
and test procedure format.

### Data and licensing

Before contributing a workload, confirm that:

- The dataset does not contain proprietary data or personally identifiable information (PII).
- You hold, or have obtained, the rights to redistribute the dataset.
- The open-source licence covering the dataset is documented in the workload's `README.md`.

### Required files

A new workload must provide:

- `workload.json` — defining `collections`, `corpora`, `operations`, and `test_procedures`
- `configsets/<name>/` — a valid Solr configset (`schema.xml` + `solrconfig.xml`). If no
  configset is provided, Apache Solr Orbit will attempt to auto-generate a basic schema
  from the document structure, but an explicit configset is strongly recommended for
  benchmarking accuracy.
- `operations/default.json` — the named operations referenced by test procedures
- `test_procedures/default.json` — at least one test procedure (mark one `"default": true`)
- `README.md` — see [README.md contents](#readmemd-contents) below
- `files.txt` — list of corpus data files

The workload may also include an optional `workload.py` to add dynamic functionality.

Reuse the shared `common_operations/` snippets for collection lifecycle and optimize steps
rather than duplicating those definitions inside each workload.

### README.md contents

Provide a detailed `README.md` that includes:

- The purpose of the workload and how it differs from other workloads in this repository.
- An example document from the dataset that illustrates the data's structure.
- The workload parameters that can be used to customize the workload.
- A list of default and available test procedures.
- A sample of the console output produced after a successful test run.
- The open-source licence that gives users and Apache Solr Orbit permission to use the
  dataset.

For an example, see the [`nyc_taxis` README](https://github.com/apache/solr-orbit-workloads/blob/main/nyc_taxis/README.md).

### Testing a new workload

All test runs used to produce example output must target a live Apache Solr cluster.

1. Run with `--test-mode` against at least one supported Solr version to confirm a clean
   end-to-end pass:

   ```bash
   solr-orbit run \
     --pipeline=benchmark-only \
     --target-host=localhost:8983 \
     --workload-path=/path/to/your/workload \
     --test-mode
   ```

2. Run a **full (non-test-mode)** benchmark without errors and include the result summary in
   your pull request description.

3. Optionally, run the integration suite using the steps in
   [Testing changes with integration tests](#testing-changes-with-integration-tests).

### Data corpus hosting

Once the PR is approved, coordinate with the maintainers about hosting the data corpora so
that other users can download them.

For questions, reach out on the
[dev@solr.apache.org](https://lists.apache.org/list.html?dev@solr.apache.org) mailing list or
open a [GitHub issue](https://github.com/apache/solr-orbit-workloads/issues).
