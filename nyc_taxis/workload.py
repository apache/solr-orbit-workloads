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
import datetime

# Common helper functions
def random_money_values(max_value):
    max_cents = round(max_value * 100)
    gte_cents = random.randrange(0, max_cents)
    lte_cents = random.randrange(gte_cents, max_cents)
    return {
        "gte":gte_cents/100,
        "lte":lte_cents/100
    }

def random_dates(min_value, max_value, format_string, whole_days=False):
    # arguments are datetime objects
    min_timestamp = datetime.datetime.timestamp(min_value)
    max_timestamp = datetime.datetime.timestamp(max_value)
    diff = max_timestamp - min_timestamp
    gte_fraction = random.uniform(0, 1)
    lte_fraction = random.uniform(gte_fraction, 1.0)

    gte_date = datetime.datetime.fromtimestamp(min_timestamp + int(gte_fraction * diff))
    lte_date = datetime.datetime.fromtimestamp(min_timestamp + int(lte_fraction * diff))
    if whole_days:
        gte_date = gte_date.replace(hour=0, minute=0, second=0, microsecond=0)
        lte_date = lte_date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    return {
        "gte":gte_date.strftime(format_string),
        "lte":lte_date.strftime(format_string)
    }

# Standard value sources for our operations
start_date = datetime.datetime(2015, 1, 1)
end_date = datetime.datetime(2015, 1, 15)

def total_amount_source():
    return random_money_values(111.98)

def date_source_with_hours():
    return random_dates(start_date, end_date, format_string="%Y-%m-%dT%H:%M:%SZ")

def date_source_without_hours():
    return random_dates(start_date, end_date, format_string="%Y-%m-%dT%H:%M:%SZ", whole_days=True)

def trip_distance_source():
    gte = random.randint(0, 10)
    lte = random.randint(gte, 20)
    return {"gte":gte, "lte":lte}

def register(registry):
    # Register standard value sources for range queries defined in operations/default.json. 
    # These are only used if --randomization-enabled is present. 
    registry.register_standard_value_source("range", "total_amount", total_amount_source)
    registry.register_standard_value_source("distance_amount_facet", "trip_distance", trip_distance_source)
    registry.register_standard_value_source("date_histogram_facet", "dropoff_datetime", date_source_without_hours)
    registry.register_standard_value_source("date_histogram_calendar_interval", "dropoff_datetime", date_source_with_hours)
    registry.register_standard_value_source("date_histogram_fixed_interval", "dropoff_datetime", date_source_with_hours)
