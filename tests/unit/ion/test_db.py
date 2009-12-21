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

from fudge import Fake, with_fakes, with_patched_object, clear_expectations
from fudge.inspector import arg

import skink.lib
import ion.db as db
from ion.db import Db

def test_can_create_db():
    db = Db(None)

    assert db

def test_db_is_not_connected_by_default():
    db = Db(None)

    assert not db.is_connected

connection_context = Fake('context').has_attr(settings=Fake('Settings'))
connection_context.settings.has_attr(Db=Fake('Db'))
connection_context.settings.Db.has_attr(host="host", user="user", password="pass", name="name", protocol="mysql", port=20)

database_fake = Fake('database')
create_database = Fake(callable=True).with_args("mysql://user:pass@host:20/name").returns(database_fake)

fake_store = Fake(callable=True).with_args(database_fake)

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", fake_store)
def test_can_connect_to_db():
    db = Db(connection_context)

    db.connect()
    assert db.is_connected

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", fake_store)
def test_connecting_twice_raises():
    db = Db(connection_context)

    db.connect()

    try:
        db.connect()
    except RuntimeError, err:
        assert str(err) == "You have to disconnect before connecting again"
        return

    assert False, "Should not have gotten this far"

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", fake_store)
def test_disconnecting_from_not_connected_raises():
    db = Db(connection_context)

    try:
        db.disconnect()
    except RuntimeError, err:
        assert str(err) == "You have to connect before disconnecting"
        return

    assert False, "Should not have gotten this far"


closable_store = Fake('closable_store')
closable_store.expects('close')
store2 = Fake(callable=True).with_args(database_fake).returns(closable_store)

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", store2)
def test_disconnection_calls_close():
    db = Db(connection_context)

    db.connect()
    db.disconnect()
    assert not db.is_connected

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", store2)
def test_disconnection_sets_store_to_null():
    db = Db(connection_context)

    db.connect()
    db.disconnect()
    assert not db.store

@with_fakes
@with_patched_object(db, "create_database", create_database)
@with_patched_object(db, "Store", store2)
def test_disconnecting_twice_raises():
    db = Db(connection_context)

    db.connect()
    db.disconnect()
    try:
        db.disconnect()
    except RuntimeError, err:
        assert str(err) == "You have to connect before disconnecting"
        return

    assert False, "Should not have gotten this far"
