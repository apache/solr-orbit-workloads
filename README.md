Apache Solr Orbit Workloads
---------------------------

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

This repository contains the default workload specifications for
[Apache Solr Orbit](https://github.com/apache/solr-orbit),
the macrobenchmarking framework for [Apache Solr](https://solr.apache.org/).

You do not need to interact with this repository directly unless you want to inspect existing
workloads, run benchmarks with a custom workload, or contribute a new workload.

## Documentation

Full documentation — including how to run workloads, workload structure, operation types,
parameters, and how to write custom workloads — is available on the
**[Apache Solr Orbit documentation site](https://apache.github.io/solr-orbit/)**.

## Quick start

```bash
# Run the default nyc_taxis workload against a local Solr cluster
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload=nyc_taxis \
  --test-mode

# Or provision Solr via Docker and benchmark
solr-orbit run \
  --pipeline=docker \
  --distribution-version=10.1.0 \
  --workload=nyc_taxis \
  --test-mode
```

## Workloads in this repository

| Workload | Description |
|----------|-------------|
| [`geonames`](geonames/README.md) | 11M geographic points-of-interest; text search, faceting, sorting |
| [`nyc_taxis`](nyc_taxis/README.md) | 165M NYC taxi trips from 2015; range filters, date facets, sorting |

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to test your changes locally, open a pull request,
and contribute a new workload.

## Getting help

- Questions and discussion: [dev@solr.apache.org](https://lists.apache.org/list.html?dev@solr.apache.org)
- Bug reports and feature requests: [GitHub Issues](https://github.com/apache/solr-orbit-workloads/issues)
- Benchmark tool documentation: [Apache Solr Orbit docs](https://apache.github.io/solr-orbit/)

## Data hosting

> **FIXME (pre-ASF):** The corpus data files referenced by the workloads in this repository are
> currently hosted on a CloudFront distribution that is not operated by the Apache Software
> Foundation. Before or shortly after the ASF donation, the data must be migrated to
> ASF-managed infrastructure or another stable, community-controlled host.

## License

This repository is licensed under the [Apache License 2.0](LICENSE).
Individual workloads may incorporate datasets with additional licensing terms;
see each workload's `README.md` for details.
