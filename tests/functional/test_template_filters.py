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

import template_filters

def test_convert_author_name_to_gravatar():
    gravatar_link = 'http://gravatar.com/avatar/34f8d85f596bd2e1edaf20a777cabc66'
    author_name = 'Evandro Flores <eof@eof.com.br>'

    assert template_filters.gravatar(author_name) == gravatar_link

def test_convert_empty_to_gravatar():
    gravatar_link = 'http://gravatar.com/avatar/'
    author_name = ''

    assert template_filters.gravatar(author_name) == gravatar_link

def test_convert_unformated_author_name_to_gravatar():
    gravatar_link = 'http://gravatar.com/avatar/'
    author_name = 'Evandro Flores - without email'

def test_convert_author_name_whit_two_mails_to_gravatar():
    gravatar_link = 'http://gravatar.com/avatar/1de5f26601d08d1cabe742f8efd55d4e'
    author_name = 'Evandro Flores <eof@eof.com.br> Pairing with Ni Knight <knights@whosay.ni>'
    

    assert template_filters.gravatar(author_name) == gravatar_link

def test_convert_unformated_author_name_to_gravatar():
    gravatar_link = 'http://gravatar.com/avatar/'
    author_name = None

    assert template_filters.gravatar(author_name) == gravatar_link
        
        