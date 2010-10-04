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
from sqlalchemy import MetaData, create_engine, __version__ as sa_version
from sqlalchemy.orm import scoped_session, sessionmaker

def new_session():
    return scoped_session(sessionmaker(autoflush=True, autocommit=False))

def create_store():
    metadata = MetaData()
    session = new_session()
    mapper = session.mapper

    engine = create_engine("sqlite://", echo=False, convert_unicode=True)
    session.bind = engine

    return session

def create_models(store):
    create_project_model(store)
    create_build_model(store)

def create_project_model(store):
    sql = """DROP TABLE IF EXISTS `projects`;
CREATE TABLE  `projects` (
  `id` INTEGER PRIMARY KEY,
  `name` varchar(255) default NULL,
  `build_script` varchar(2000) default NULL,
  `scm_repository` varchar(1500) default NULL,
  `monitor_changes` tinyint(1) default NULL,
  `build_status` varchar(15) default NULL,
  `branch` varchar(255) default NULL
);"""
    execute_sql(store, sql)

def create_build_model(store):
    sql = """DROP TABLE IF EXISTS `builds`;
CREATE TABLE  `builds` (
  `id` INTEGER PRIMARY KEY,
  `number` INTEGER,
  `build_date` TEXT,
  `status` TEXT,
  `scm_status` TEXT,
  `log` TEXT,
  `commit_number` TEXT,
  `commit_author` TEXT,
  `commit_committer` TEXT,
  `commit_text` TEXT,
  `commit_author_date` TEXT,
  `commit_committer_date` TEXT,
  `project_id` INTEGER
);"""
    execute_sql(store, sql)

def execute_sql(store, sql):
    for statement in sql.split(';'):
        store.execute(statement)
