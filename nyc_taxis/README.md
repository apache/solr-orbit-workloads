# nyc_taxis workload

This workload indexes yellow-taxi trip records from New York City in 2015 and runs a mix of
search, range-filter, facet/aggregation, and sort queries against the resulting Solr collection.

The dataset originates from the
[NYC Taxi and Limousine Commission Trip Record Data](https://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml).
It has been tested with the 2015 yellow-taxi dump but should work with any annual yellow-taxi
dump and is straightforward to adapt for green-taxi data.

The full corpus contains **165,346,692 documents** (~74 GB uncompressed JSON).

## Generating the corpus from raw CSV data

If you are starting from the raw TLC CSV files rather than the pre-built corpus hosted on
CloudFront, generate the JSON documents with the bundled helper script:

```bash
python3 _tools/parse.py json file_name.csv > documents.json
```

Then compress for storage/transfer:

```bash
bzip2 -k documents.json
# or, for faster decompression at benchmark time:
zstd --long documents.json -o documents.json.zst
```

The Solr schema is already defined in `configsets/nyc_taxis/schema.xml` — no generation step
is needed.

## Example document

```json
{
  "total_amount": 6.3,
  "improvement_surcharge": 0.3,
  "pickup_location": [-73.92259216308594, 40.7545280456543],
  "pickup_datetime": "2015-01-01T00:34:42Z",
  "trip_type": "1",
  "dropoff_datetime": "2015-01-01T00:38:34Z",
  "rate_code_id": "1",
  "tolls_amount": 0.0,
  "dropoff_location": [-73.91363525390625, 40.76552200317383],
  "passenger_count": 1,
  "fare_amount": 5.0,
  "extra": 0.5,
  "trip_distance": 0.88,
  "tip_amount": 0.0,
  "store_and_fwd_flag": "N",
  "payment_type": "2",
  "mta_tax": 0.5,
  "vendor_id": "2"
}
```

## Quick start

```bash
# Quick sanity-check against a local Solr cluster (reduced corpus, fewer iterations)
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload=nyc_taxis \
  --test-mode

# Full default benchmark (append-no-conflicts test procedure)
solr-orbit run \
  --pipeline=benchmark-only \
  --target-host=localhost:8983 \
  --workload=nyc_taxis

# Provision Solr 9 via Docker and benchmark
solr-orbit run \
  --pipeline=docker \
  --distribution-version=9.10.1 \
  --workload=nyc_taxis
```

## Test procedures

| Name | Default | Description |
|------|---------|-------------|
| `append-no-conflicts` | ✓ | Indexes the full corpus (append-only, unique IDs) then runs all search/aggregation/sort queries. |
| `append-no-conflicts-index-only` | | Indexes the full corpus without running any queries. Useful for measuring peak indexing throughput. |
| `append-sorted-no-conflicts-index-only` | | Same as above, intended for use with a schema that sorts documents at index time (e.g. by `pickup_datetime`). Configure sorting in `configsets/nyc_taxis/schema.xml`. |
| `update` | | Indexes the corpus while deliberately re-using document IDs to simulate updates and conflicts. |
| `search-longevity-test` | | Indexes 50 % of the corpus, optimizes, then concurrently indexes the remaining 50 % while running all search operations in parallel. |
| `indexing-search-longevity-test` | | Indexes and queries entirely concurrently for a configurable time period. |

See [TEST_PROCEDURES.md](TEST_PROCEDURES.md) for details on each procedure and its specific
parameters.

## Search operations

The following named operations are defined in `operations/default.json` and used by the test
procedures above:

| Operation | Query | Notes |
|-----------|-------|-------|
| `match-all` | `*:*` | Full-collection match |
| `range` | `total_amount:[5 TO 15}` | Range filter on a float field. The upper bound is exclusive, matching the upstream `lt: 15` |
| `distance_amount_facet` | `trip_distance:[0 TO 50}` + range facet | Range facet on `trip_distance`. Exclusive upper bound, matching the upstream `lt: 50` |
| `date_histogram_facet` | Date range, `+1DAY` gap | Daily dropoff histogram, all 21 days of Jan 2015. Upstream bounds this with `lte: 21/01/2015` in `dd/MM/yyyy`, which covers the whole of the 21st, so the filter runs to `2015-01-22T00:00:00Z` exclusive |
| `date_histogram_calendar_interval` | Date range, `+1MONTH` gap | Monthly histogram, calendar-aligned buckets. Exclusive upper bound, matching the upstream `lt: 2016-01-01` |
| `date_histogram_fixed_interval` | Date range, `+30DAY` gap | Monthly histogram, fixed-width buckets. Exclusive upper bound, matching the upstream `lt: 2016-01-01` |
| `desc_sort_tip_amount` | `*:*` sort `tip_amount desc` | Descending sort |
| `asc_sort_tip_amount` | `*:*` sort `tip_amount asc` | Ascending sort |
| `desc_sort_passenger_count` | `*:*` sort `passenger_count desc` | Descending sort |
| `asc_sort_passenger_count` | `*:*` sort `passenger_count asc` | Ascending sort |

## Parameters

Pass parameters with `--workload-params`, either inline or via a JSON file:

```bash
# Inline
solr-orbit run --workload=nyc_taxis \
  --workload-params="bulk_indexing_clients:4,num_shards:2"

# JSON file
solr-orbit run --workload=nyc_taxis \
  --workload-params=/path/to/params.json
```

### Indexing parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bulk_size` | `10000` | Documents per indexing batch |
| `bulk_indexing_clients` | `8` | Parallel indexing clients |
| `ingest_percentage` | `100` | Percentage of corpus to ingest (0–100) |
| `error_level` | `non-fatal` | Error handling for bulk operations (`non-fatal` or `fatal`) |

### Collection parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_shards` | `1` | Number of shards for the `nyc_taxis` collection |
| `replication_factor` | `1` | Replication factor for the `nyc_taxis` collection |

### Optimize parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_segments` | `1` | Target segment count for the post-index optimize step |
| `optimize_timeout` | `600` | Timeout in seconds for the optimize operation |

### Search parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_throughput` | *(per operation)* | Max requests per second for search operations; `none` for no limit |
| `search_clients` | `1` | Parallel search clients (applies to all search operations unless overridden per operation) |
| `warmup_iterations` | *(per operation)* | Warmup iterations before measurement |
| `iterations` | *(per operation)* | Measured iterations |

Per-operation overrides follow the pattern `<operation_name>_target_throughput`,
`<operation_name>_iterations`, `<operation_name>_warmup_iterations`, and
`<operation_name>_search_clients`. For example:

```bash
--workload-params="match_all_iterations:200,range_target_throughput:1.0"
```

### Update / conflict parameters (used by the `update` test procedure)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `conflicts` | `random` | ID conflict strategy: `sequential` or `random` |
| `conflict_probability` | `25` | Probability (0–100) that a document re-uses an existing ID |
| `on_conflict` | `update` | Action on conflict: `index` (overwrite) or `update` (partial update) |
| `recency` | `0` | Bias towards recent IDs when choosing conflict targets (0 = uniform, 1 = most-recent) |

## License

The dataset originates from the
[NYC Taxi and Limousine Commission (TLC) Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
and is published by the City of New York under the
[NYC Open Data Law](https://opendata.cityofnewyork.us/open-data-law/) as public domain.
