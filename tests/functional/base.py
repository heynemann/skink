#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import skink.lib

from storm.locals import *

def create_store():
    database = create_database("sqlite:")
    store = Store(database)

    return store

def create_models(store):
    create_project_model(store)

def create_project_model(store):
    sql = """DROP TABLE IF EXISTS `projects`; 
CREATE TABLE  `projects` (
  `id` INTEGER PRIMARY KEY,
  `name` varchar(255) default NULL,
  `build_script` varchar(2000) default NULL,
  `scm_repository` varchar(1500) default NULL,
  `monitor_changes` tinyint(1) default NULL,
  `build_status` varchar(15) default NULL
);"""
    execute_sql(store, sql)

def execute_sql(store, sql):
    for statement in sql.split(';'):
        store.execute(statement)
