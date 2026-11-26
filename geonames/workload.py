# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.
# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.
# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Modifications copyright (C) 2026 The Apache Software Foundation
# (Apache Solr contributors). Licensed under the Apache License, Version 2.0.

import random
import os


# Some geonames place names contain a comma ("Schenkon, Tannberg"). {!terms} splits strictly on
# its separator, which defaults to ",", so join on a character that never occurs in terms.txt.
TERMS_SEPARATOR = "|"
TERMS_QUERY_PREFIX = '{!terms f=name_raw separator="' + TERMS_SEPARATOR + '"}'


class QueryParamSource:
    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def __init__(self, workload, params, **kwargs):
        self._params = params
        self.infinite = True
        cwd = os.path.dirname(__file__)
        # The terms.txt file has been generated with:
        # sed -n '13~250p' /path/to/geonames/documents.json | shuf | sed -e "s/.*name\": \"//;s/\",.*$//" > terms.txt
        with open(os.path.join(cwd, "terms.txt"), "r") as ins:
            self.terms = [line.strip() for line in ins.readlines()]

    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def partition(self, partition_index, total_partitions):
        return self


class PureTermsQueryParamSource(QueryParamSource):
    def params(self):
        query_terms = list(self.terms)  # copy
        query_terms.append(str(random.randint(1, 100)))  # avoid caching
        result = {
            "collection": "geonames",
            "body": {
                "query": TERMS_QUERY_PREFIX + TERMS_SEPARATOR.join(query_terms)
            }
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result


class FilteredTermsQueryParamSource(QueryParamSource):
    def params(self):
        query_terms = list(self.terms)  # copy
        query_terms.append(str(random.randint(1, 1000)))  # avoid caching
        result = {
            "collection": "geonames",
            "body": {
                "query": "feature_class_raw:T",
                "filter": TERMS_QUERY_PREFIX + TERMS_SEPARATOR.join(query_terms)
            }
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result


class ProhibitedTermsQueryParamSource(QueryParamSource):
    def params(self):
        query_terms = list(self.terms)  # copy
        query_terms.append(str(random.randint(1, 1000)))  # avoid caching
        result = {
            "collection": "geonames",
            "body": {
                "query": {
                    "bool": {
                        "must": "feature_class_raw:A",
                        "must_not": TERMS_QUERY_PREFIX + TERMS_SEPARATOR.join(query_terms)
                    }
                }
            }
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result


def register(registry):
    registry.register_param_source("pure-terms-query-source", PureTermsQueryParamSource)
    registry.register_param_source("filtered-terms-query-source", FilteredTermsQueryParamSource)
    registry.register_param_source("prohibited-terms-query-source", ProhibitedTermsQueryParamSource)
