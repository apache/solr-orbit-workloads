## Geonames workload

This workload is based on a [geonames](http://www.geonames.org/) dump of the file
[allCountries.zip](http://download.geonames.org/export/dump/allCountries.zip) retrieved as of
**April 27, 2017**. This is a **fixed historical snapshot** — it is not updated as the live
Geonames database changes — which ensures reproducible benchmark results across runs and time.

For further details about the semantics of individual fields, please see the
[geonames dump README](http://download.geonames.org/export/dump/readme.txt).

Modifications from the original data:

* The original CSV data have been converted to JSON.
* The original `longitude` and `latitude` fields are combined into a single `location` field
  (`[longitude, latitude]` array in GeoJSON order).

### Example Document

```json
{
  "geonameid": 2986043,
  "name": "Pic de Font Blanca",
  "asciiname": "Pic de Font Blanca",
  "alternatenames": "Pic de Font Blanca,Pic du Port",
  "feature_class": "T",
  "feature_code": "PK",
  "country_code": "AD",
  "admin1_code": "00",
  "population": 0,
  "dem": "2860",
  "timezone": "Europe/Andorra",
  "location": [
    1.53335,
    42.64991
  ]
}
```

### Test Procedures

* `append-no-conflicts` (default): Indexes the whole corpus with unique document IDs, then runs a suite of search and faceting queries.
* `append-no-conflicts-index-only`: Indexes the whole corpus with unique document IDs, no queries.

### Scoring operations

* `field_value_function_score`: ranks every document by `log10(population * 1.2 + 2)`, written as the function query `log(sum(product(population,1.2),2))`; Solr's `log` is the base-10 logarithm.
* `decay_geo_gauss_function_score`: ranks every document by a gaussian decay of its distance from `52.37,4.8951`, with a scale of 500 km, no offset and a decay of 0.1 at the scale. The score is `exp(-d^2 / (2*sigma^2))`, where `d` is `geodist(location, ...)` in kilometres and `2*sigma^2 = -scale^2 / ln(decay) = 108573.62` km^2, which is the constant in the query. Solr has no built-in decay function, so the curve is composed from `exp`, `pow` and `div`.

### Significant terms operations

`significant_text_selective` (documents whose `alternatenames` contain `street`) and `significant_text_unselective` (documents whose `timezone` contains `America`) list the ten terms of `alternatenames` that are most characteristic of the matching documents. They use a terms facet sorted by `relatedness()`, with the matching documents as the foreground and the whole collection as the background, and only terms that occur in at least three documents.

The score is the `relatedness()` value; the text of the documents is not analysed again at query time, the facet reads the indexed terms.

### Parameters

This workload allows the following parameters via `--workload-params`:

#### Indexing

* `bulk_size` (default: `5000`): Number of documents per bulk indexing request.
* `bulk_indexing_clients` (default: `8`): Number of clients that issue bulk indexing requests.
* `warmup_time_period` (default: `120`): Seconds of indexing warm-up before measurements begin.
* `ingest_percentage` (default: `100`): A number between 0 and 100 that defines how much of the document corpus should be ingested.
* `conflicts` (default: `"random"`): Type of id conflicts to simulate. Valid values are `sequential` (a document id is replaced with a sequentially increasing id) and `random` (replaced with a random other id).
* `conflict_probability` (default: `25`): A number between 0 and 100 that defines the probability of id conflicts. Only applies when running `index-update` operations.
* `on_conflict` (default: `"index"`): Whether to use an `"index"` or `"update"` action when simulating an id conflict.
* `recency` (default: `0`): A number between 0 and 1 that biases towards more recent ids when simulating conflicts. `0` means uniform distribution; `1` means always pick the most recent id.
* `error_level` (default: `"non-fatal"`): Error handling for bulk operations. Use `"fatal"` to abort on any indexing error.

#### Collection

* `num_shards` (default: `1`): Number of shards for the Solr collection.
* `replication_factor` (default: `1`): Number of NRT replica copies per shard.

#### Optimize

* `max_segments` (default: `1`): Target number of segments after force-merge (optimize).
* `optimize_timeout` (default: `600`): Timeout in seconds for the optimize operation.

#### Search

* `target_throughput`: Global default for maximum requests per second across all search operations. Use `none` for no limit. Individual operations can be overridden with `<operation_name>_target_throughput`.
* `search_clients` (default: `1`): Number of clients issuing search requests.
* `warmup_iterations`: Global default warmup iterations before measurement begins.
* `iterations`: Global default number of measured iterations per operation.

### License

The data originates from [GeoNames](https://www.geonames.org/) and is licensed under the
[Creative Commons Attribution 3.0 License](https://creativecommons.org/licenses/by/3.0/).
Use of this data requires crediting GeoNames as the source.

```
This work is licensed under a Creative Commons Attribution 3.0 License,
see http://creativecommons.org/licenses/by/3.0/
The Data is provided "as is" without warranty or any representation of accuracy, timeliness or completeness.
```
