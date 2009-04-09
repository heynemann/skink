'''
This module provides the ``Entity`` base class, as well as its metaclass
``EntityMeta``.
'''

from py23compat import set, rsplit, sorted

import sys
import inspect
import warnings
from copy import copy

import sqlalchemy
from sqlalchemy     import Table, Column, Integer, desc, ForeignKey, and_, \
                           ForeignKeyConstraint
from sqlalchemy.orm import Query, MapperExtension, mapper, object_session, \
                           EXT_CONTINUE, polymorphic_union, ScopedSession, \
                           ColumnProperty

import elixir
from elixir.statements import process_mutators
from elixir import options
from elixir.properties import Property

DEBUG = False

__doc_all__ = ['Entity', 'EntityMeta']


class EntityDescriptor(object):
    '''
    EntityDescriptor describes fields and options needed for table creation.
    '''

    def __init__(self, entity):
        entity.table = None
        entity.mapper = None

        self.entity = entity
        self.module = sys.modules[entity.__module__]

        self.has_pk = False
        self._pk_col_done = False

        self.builders = []

        self.parent = None
        #XXX: use entity.__subclasses__ ?
        self.children = []

        for base in entity.__bases__:
            if isinstance(base, EntityMeta) and is_entity(base):
                if self.parent:
                    raise Exception('%s entity inherits from several entities,'
                                    ' and this is not supported.'
                                    % self.entity.__name__)
                else:
                    self.parent = base
                    self.parent._descriptor.children.append(entity)

        # columns and constraints waiting for a table to exist
        self._columns = list()
        self.constraints = list()

        # properties (it is only useful for checking dupe properties at the
        # moment, and when adding properties before the mapper is created,
        # which shouldn't happen).
        self.properties = dict()

        #
        self.relationships = list()

        # set default value for options
        self.order_by = None
        self.table_args = list()

        # set default value for options with an optional module-level default
        self.metadata = getattr(self.module, '__metadata__', elixir.metadata)
        self.session = getattr(self.module, '__session__', elixir.session)
        self.collection = getattr(self.module, '__entity_collection__',
                                  elixir.entities)

        for option in ('autosetup', 'inheritance', 'polymorphic', 'identity',
                       'autoload', 'tablename', 'shortnames',
                       'auto_primarykey', 'version_id_col',
                       'allowcoloverride'):
            setattr(self, option, options.options_defaults[option])

        for option_dict in ('mapper_options', 'table_options'):
            setattr(self, option_dict,
                    options.options_defaults[option_dict].copy())

    def setup_options(self):
        '''
        Setup any values that might depend on using_options. For example, the
        tablename or the metadata.
        '''
        elixir.metadatas.add(self.metadata)
        if self.collection is not None:
            self.collection.append(self.entity)

        entity = self.entity
        if self.parent:
            if self.inheritance == 'single':
                self.tablename = self.parent._descriptor.tablename

        if not self.tablename:
            if self.shortnames:
                self.tablename = entity.__name__.lower()
            else:
                modulename = entity.__module__.replace('.', '_')
                tablename = "%s_%s" % (modulename, entity.__name__)
                self.tablename = tablename.lower()
        elif callable(self.tablename):
            self.tablename = self.tablename(entity)

        if not self.identity:
            if 'polymorphic_identity' in self.mapper_options:
                self.identity = self.mapper_options['polymorphic_identity']
            else:
                #TODO: include module name
                self.identity = entity.__name__.lower()
        elif 'polymorphic_identity' in kwargs:
            raise Exception('You cannot use the "identity" option and the '
                            'polymorphic_identity mapper option at the same '
                            'time.')
        elif callable(self.identity):
            self.identity = self.identity(entity)

        if self.polymorphic:
            if not isinstance(self.polymorphic, basestring):
                self.polymorphic = options.DEFAULT_POLYMORPHIC_COL_NAME

    #---------------------
    # setup phase methods

    def setup_autoload_table(self):
        self.setup_table(True)

    def create_pk_cols(self):
        """
        Create primary_key columns. That is, call the 'create_pk_cols'
        builders then add a primary key to the table if it hasn't already got
        one and needs one.

        This method is "semi-recursive" in some cases: it calls the
        create_keys method on ManyToOne relationships and those in turn call
        create_pk_cols on their target. It shouldn't be possible to have an
        infinite loop since a loop of primary_keys is not a valid situation.
        """
        if self._pk_col_done:
            return

        self.call_builders('create_pk_cols')

        if not self.autoload:
            if self.parent:
                if self.inheritance == 'multi':
                    # Add columns with foreign keys to the parent's primary
                    # key columns
                    parent_desc = self.parent._descriptor
                    tablename = parent_desc.table_fullname
                    for pk_col in parent_desc.primary_keys:
                        colname = options.MULTIINHERITANCECOL_NAMEFORMAT % \
                                  {'entity': self.parent.__name__.lower(),
                                   'key': pk_col.key}

                        # It seems like SA ForeignKey is not happy being given
                        # a real column object when said column is not yet
                        # attached to a table
                        pk_col_name = "%s.%s" % (tablename, pk_col.key)
                        fk = ForeignKey(pk_col_name, ondelete='cascade')
                        col = Column(colname, pk_col.type, fk,
                                     primary_key=True)
                        self.add_column(col)
                elif self.inheritance == 'concrete':
                    # Copy primary key columns from the parent.
                    for col in self.parent._descriptor.columns:
                        if col.primary_key:
                            self.add_column(col.copy())
            elif not self.has_pk and self.auto_primarykey:
                if isinstance(self.auto_primarykey, basestring):
                    colname = self.auto_primarykey
                else:
                    colname = options.DEFAULT_AUTO_PRIMARYKEY_NAME

                self.add_column(
                    Column(colname, options.DEFAULT_AUTO_PRIMARYKEY_TYPE,
                           primary_key=True))
        self._pk_col_done = True

    def setup_relkeys(self):
        self.call_builders('create_non_pk_cols')

    def before_table(self):
        self.call_builders('before_table')

    def setup_table(self, only_autoloaded=False):
        '''
        Create a SQLAlchemy table-object with all columns that have been
        defined up to this point.
        '''
        if self.entity.table:
            return

        if self.autoload != only_autoloaded:
            return

        kwargs = self.table_options
        if self.autoload:
            args = self.table_args
            kwargs['autoload'] = True
        else:
            if self.parent:
                if self.inheritance == 'single':
                    # we know the parent is setup before the child
                    self.entity.table = self.parent.table

                    # re-add the entity columns to the parent entity so that
                    # they are added to the parent's table (whether the
                    # parent's table is already setup or not).
                    for col in self.columns:
                        self.parent._descriptor.add_column(col)
                    for constraint in self.constraints:
                        self.parent._descriptor.add_constraint(constraint)
                    return
                elif self.inheritance == 'concrete':
                    #TODO: we should also copy columns from the parent table
                    # if the parent is a base (abstract?) entity (whatever the
                    # inheritance type -> elif will need to be changed)

                    # Copy all non-primary key columns from parent table
                    # (primary key columns have already been copied earlier).
                    for col in self.parent._descriptor.columns:
                        if not col.primary_key:
                            self.add_column(col.copy())

                    #FIXME: use the public equivalent of _get_colspec when
                    #available
                    for con in self.parent._descriptor.constraints:
                        self.add_constraint(
                            ForeignKeyConstraint(
                                [c.key for c in con.columns],
                                [e._get_colspec() for e in con.elements],
                                name=con.name, #TODO: modify it
                                onupdate=con.onupdate, ondelete=con.ondelete,
                                use_alter=con.use_alter))

            if self.polymorphic and \
               self.inheritance in ('single', 'multi') and \
               self.children and not self.parent:
                self.add_column(Column(self.polymorphic,
                                       options.POLYMORPHIC_COL_TYPE))

            if self.version_id_col:
                if not isinstance(self.version_id_col, basestring):
                    self.version_id_col = options.DEFAULT_VERSION_ID_COL_NAME
                self.add_column(Column(self.version_id_col, Integer))

            args = self.columns + self.constraints + self.table_args

        self.entity.table = Table(self.tablename, self.metadata,
                                  *args, **kwargs)

    def setup_reltables(self):
        self.call_builders('create_tables')

    def after_table(self):
        self.call_builders('after_table')

    def setup_events(self):
        def make_proxy_method(methods):
            def proxy_method(self, mapper, connection, instance):
                for func in methods:
                    ret = func(instance)
                    # I couldn't commit myself to force people to
                    # systematicaly return EXT_CONTINUE in all their event
                    # methods.
                    # But not doing that diverge to how SQLAlchemy works.
                    # I should try to convince Mike to do EXT_CONTINUE by
                    # default, and stop processing as the special case.
#                    if ret != EXT_CONTINUE:
                    if ret is not None and ret != EXT_CONTINUE:
                        return ret
                return EXT_CONTINUE
            return proxy_method

        # create a list of callbacks for each event
        methods = {}
        for name, method in self.entity.__dict__.items():
            if hasattr(method, '_elixir_events'):
                for event in method._elixir_events:
                    event_methods = methods.setdefault(event, [])
                    event_methods.append(method)
        if not methods:
            return

        # transform that list into methods themselves
        for event in methods:
            methods[event] = make_proxy_method(methods[event])

        # create a custom mapper extension class, tailored to our entity
        ext = type('EventMapperExtension', (MapperExtension,), methods)()

        # then, make sure that the entity's mapper has our mapper extension
        self.add_mapper_extension(ext)

    def before_mapper(self):
        self.call_builders('before_mapper')

    def _get_children(self):
        children = self.children[:]
        for child in self.children:
            children.extend(child._descriptor._get_children())
        return children

    def translate_order_by(self, order_by):
        if isinstance(order_by, basestring):
            order_by = [order_by]

        order = list()
        for colname in order_by:
            col = self.get_column(colname.strip('-'))
            if colname.startswith('-'):
                col = desc(col)
            order.append(col)
        return order

    def setup_mapper(self):
        '''
        Initializes and assign a mapper to the entity.
        At this point the mapper will usually have no property as they are
        added later.
        '''
        if self.entity.mapper:
            return

        # for now we don't support the "abstract" parent class in a concrete
        # inheritance scenario as demonstrated in
        # sqlalchemy/test/orm/inheritance/concrete.py
        # this should be added along other
        kwargs = self.mapper_options
        if self.order_by:
            kwargs['order_by'] = self.translate_order_by(self.order_by)

        if self.version_id_col:
            kwargs['version_id_col'] = self.get_column(self.version_id_col)

        if self.inheritance in ('single', 'concrete', 'multi'):
            if self.parent and \
               not (self.inheritance == 'concrete' and not self.polymorphic):
                kwargs['inherits'] = self.parent.mapper

            if self.inheritance == 'multi' and self.parent:
                col_pairs = zip(self.primary_keys,
                                self.parent._descriptor.primary_keys)
                kwargs['inherit_condition'] = \
                    and_(*[pc == c for c, pc in col_pairs])

            if self.polymorphic:
                if self.children:
                    if self.inheritance == 'concrete':
                        keys = [(self.identity, self.entity.table)]
                        keys.extend([(child._descriptor.identity, child.table)
                                     for child in self._get_children()])
                        #XXX: we might need to change the alias name so that
                        # children (which are parent themselves) don't end up
                        # with the same alias than their parent?
                        pjoin = polymorphic_union(
                                    dict(keys), self.polymorphic, 'pjoin')

                        kwargs['with_polymorphic'] = ('*', pjoin)
                        kwargs['polymorphic_on'] = \
                            getattr(pjoin.c, self.polymorphic)
                    elif not self.parent:
                        kwargs['polymorphic_on'] = \
                            self.get_column(self.polymorphic)

                    #TODO: this is an optimization, and it breaks the multi
                    # table polymorphic inheritance test with a relation.
                    # So I turn it off for now. We might want to provide an
                    # option to turn it on.
#                    if self.inheritance == 'multi':
#                        children = self._get_children()
#                        join = self.entity.table
#                        for child in children:
#                            join = join.outerjoin(child.table)
#                        kwargs['select_table'] = join

                if self.children or self.parent:
                    kwargs['polymorphic_identity'] = self.identity

                if self.parent and self.inheritance == 'concrete':
                    kwargs['concrete'] = True

        #TODO: document this!
        if 'primary_key' in kwargs:
            cols = self.entity.table.c
            kwargs['primary_key'] = [getattr(cols, colname) for
                colname in kwargs['primary_key']]

        if self.parent and self.inheritance == 'single':
            args = []
        else:
            args = [self.entity.table]

        # do the mapping
        if self.session is None:
            self.entity.mapper = mapper(self.entity, *args, **kwargs)
        elif isinstance(self.session, ScopedSession):
            self.entity.mapper = self.session.mapper(self.entity,
                                                     *args, **kwargs)
        else:
            raise Exception("Failed to map entity '%s' with its table or "
                            "selectable" % self.entity.__name__)

    def after_mapper(self):
        self.call_builders('after_mapper')

    def setup_properties(self):
        self.call_builders('create_properties')

    def finalize(self):
        self.call_builders('finalize')
        self.entity._setup_done = True

    #----------------
    # helper methods

    def call_builders(self, what):
        for builder in self.builders:
            if hasattr(builder, what):
                getattr(builder, what)()

    def add_column(self, col, check_duplicate=None):
        '''when check_duplicate is None, the value of the allowcoloverride
        option of the entity is used.
        '''
        if check_duplicate is None:
            check_duplicate = not self.allowcoloverride

        if check_duplicate and self.get_column(col.key, False) is not None:
            raise Exception("Column '%s' already exist in '%s' ! " %
                            (col.key, self.entity.__name__))
        self._columns.append(col)

        if col.primary_key:
            self.has_pk = True

        # Autosetup triggers shouldn't be active anymore at this point, so we
        # can theoretically access the entity's table safely. But the problem
        # is that if, for some reason, the trigger removal phase didn't
        # happen, we'll get an infinite loop. So we just make sure we don't
        # get one in any case.
        table = type.__getattribute__(self.entity, 'table')
        if table:
            if check_duplicate and col.key in table.columns.keys():
                raise Exception("Column '%s' already exist in table '%s' ! " %
                                (col.key, table.name))
            table.append_column(col)
            if DEBUG:
                print "table.append_column(%s)" % col

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

        table = self.entity.table
        if table:
            table.append_constraint(constraint)

    def add_property(self, name, property, check_duplicate=True):
        if check_duplicate and name in self.properties:
            raise Exception("property '%s' already exist in '%s' ! " %
                            (name, self.entity.__name__))
        self.properties[name] = property

#FIXME: something like this is needed to propagate the relationships from
# parent entities to their children in a concrete inheritance scenario. But
# this doesn't work because of the backref matching code.
#        if self.children and self.inheritance == 'concrete':
#            for child in self.children:
#                child._descriptor.add_property(name, property)

        mapper = self.entity.mapper
        if mapper:
            mapper.add_property(name, property)
            if DEBUG:
                print "mapper.add_property('%s', %s)" % (name, repr(property))

    def add_mapper_extension(self, extension):
        extensions = self.mapper_options.get('extension', [])
        if not isinstance(extensions, list):
            extensions = [extensions]
        extensions.append(extension)
        self.mapper_options['extension'] = extensions

    def get_column(self, key, check_missing=True):
        #TODO: this needs to work whether the table is already setup or not
        #TODO: support SA table/autoloaded entity
        for col in self.columns:
            if col.key == key:
                return col
        if check_missing:
            raise Exception("No column named '%s' found in the table of the "
                            "'%s' entity!" % (key, self.entity.__name__))
        return None

    def get_inverse_relation(self, rel, check_reverse=True):
        '''
        Return the inverse relation of rel, if any, None otherwise.
        '''

        matching_rel = None
        for other_rel in self.relationships:
            if rel.is_inverse(other_rel):
                if matching_rel is None:
                    matching_rel = other_rel
                else:
                    raise Exception(
                            "Several relations match as inverse of the '%s' "
                            "relation in entity '%s'. You should specify "
                            "inverse relations manually by using the inverse "
                            "keyword."
                            % (rel.name, rel.entity.__name__))
        # When a matching inverse is found, we check that it has only
        # one relation matching as its own inverse. We don't need the result
        # of the method though. But we do need to be careful not to start an
        # infinite recursive loop.
        if matching_rel and check_reverse:
            rel.entity._descriptor.get_inverse_relation(matching_rel, False)

        return matching_rel

    def find_relationship(self, name):
        for rel in self.relationships:
            if rel.name == name:
                return rel
        if self.parent:
            return self.parent._descriptor.find_relationship(name)
        else:
            return None

    #------------------------
    # some useful properties

    def table_fullname(self):
        '''
        Complete name of the table for the related entity.
        Includes the schema name if there is one specified.
        '''
        schema = self.table_options.get('schema', None)
        if schema is not None:
            return "%s.%s" % (schema, self.tablename)
        else:
            return self.tablename
    table_fullname = property(table_fullname)

    def columns(self):
        #FIXME: this would be more correct but it breaks inheritance, so I'll
        # use the old test for now.
#        if self.entity.table:
        if self.autoload:
            return self.entity.table.columns
        else:
            #FIXME: depending on the type of inheritance, we should also
            # return the parent entity's columns (for example for order_by
            # using a column defined in the parent.
            return self._columns
    columns = property(columns)

    def primary_keys(self):
        """
        Returns the list of primary key columns of the entity.

        This property isn't valid before the "create_pk_cols" phase.
        """
        if self.autoload:
            return [col for col in self.entity.table.primary_key.columns]
        else:
            if self.parent and self.inheritance == 'single':
                return self.parent._descriptor.primary_keys
            else:
                return [col for col in self.columns if col.primary_key]
    primary_keys = property(primary_keys)

    def primary_key_properties(self):
        """
        Returns the list of (mapper) properties corresponding to the primary
        key columns of the table of the entity.

        This property caches its value, so it shouldn't be called before the
        entity is fully set up.
        """
        if not hasattr(self, '_pk_props'):
            col_to_prop = {}
            mapper = self.entity.mapper
            for prop in mapper.iterate_properties:
                if isinstance(prop, ColumnProperty):
                    for col in prop.columns:
                        for col in col.proxy_set:
                            col_to_prop[col] = prop
            pk_cols = [c for c in mapper.mapped_table.c if c.primary_key]
            self._pk_props = [col_to_prop[c] for c in pk_cols]
        return self._pk_props
    primary_key_properties = property(primary_key_properties)

class TriggerProxy(object):
    """
    A class that serves as a "trigger" ; accessing its attributes runs
    the setup_all function.

    Note that the `setup_all` is called on each access of the attribute.
    """

    def __init__(self, class_, attrname):
        self.class_ = class_
        self.attrname = attrname

    def __getattr__(self, name):
        elixir.setup_all()
        #FIXME: it's possible to get an infinite loop here if setup_all doesn't
        #remove the triggers for this entity. This can happen if the entity is
        #not in the `entities` list for some reason.
        proxied_attr = getattr(self.class_, self.attrname)
        return getattr(proxied_attr, name)

    def __repr__(self):
        proxied_attr = getattr(self.class_, self.attrname)
        return "<TriggerProxy (%s)>" % (self.class_.__name__)


class TriggerAttribute(object):

    def __init__(self, attrname):
        self.attrname = attrname

    def __get__(self, instance, owner):
        #FIXME: it's possible to get an infinite loop here if setup_all doesn't
        #remove the triggers for this entity. This can happen if the entity is
        #not in the `entities` list for some reason.
        elixir.setup_all()
        return getattr(owner, self.attrname)

def is_entity(cls):
    """
    Scan the bases classes of `cls` to see if any is an instance of
    EntityMeta. If we don't find any, it means it is either an unrelated class
    or an entity base class (like the 'Entity' class).
    """
    for base in cls.__bases__:
        if isinstance(base, EntityMeta):
            return True
    return False


class EntityMeta(type):
    """
    Entity meta class.
    You should only use it directly if you want to define your own base class
    for your entities (ie you don't want to use the provided 'Entity' class).
    """

    def __init__(cls, name, bases, dict_):
        # Only process further subclasses of the base classes (Entity et al.),
        # not the base classes themselves. We don't want the base entities to
        # be registered in an entity collection, nor to have a table name and
        # so on.
        if not is_entity(cls):
            return

        # create the entity descriptor
        desc = cls._descriptor = EntityDescriptor(cls)

        # Determine whether this entity is a *direct* subclass of its base
        # entity
        entity_base = None
        for base in cls.__bases__:
            if isinstance(base, EntityMeta):
                if not is_entity(base):
                    entity_base = base

        if entity_base:
            # If so, copy the base entity properties ('Property' instances).
            # We use inspect.getmembers (instead of __dict__) so that we also
            # get the properties from the parents of the base_class if any.
            base_props = inspect.getmembers(entity_base,
                                            lambda a: isinstance(a, Property))
            base_props = [(name, copy(attr)) for name, attr in base_props]
        else:
            base_props = []

        # Process attributes (using the assignment syntax), looking for
        # 'Property' instances and attaching them to this entity.
        properties = [(name, attr) for name, attr in cls.__dict__.iteritems()
                                   if isinstance(attr, Property)]
        sorted_props = sorted(base_props + properties,
                              key=lambda i: i[1]._counter)
        for name, prop in sorted_props:
            prop.attach(cls, name)

        # Process mutators. Needed before _install_autosetup_triggers so that
        # we know of the metadata
        process_mutators(cls)

        # setup misc options here (like tablename etc.)
        desc.setup_options()

        # create trigger proxies
        # TODO: support entity_name... It makes sense only for autoloaded
        # tables for now, and would make more sense if we support "external"
        # tables
        if desc.autosetup:
            _install_autosetup_triggers(cls)

    def __call__(cls, *args, **kwargs):
        if cls._descriptor.autosetup and not hasattr(cls, '_setup_done'):
            elixir.setup_all()
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, key, value):
        if isinstance(value, Property):
            if hasattr(cls, '_setup_done'):
                raise Exception('Cannot set attribute on a class after '
                                'setup_all')
            else:
                value.attach(cls, key)
        else:
            type.__setattr__(cls, key, value)


def _install_autosetup_triggers(cls, entity_name=None):
    #TODO: move as much as possible of those "_private" values to the
    # descriptor, so that we don't mess the initial class.
    tablename = cls._descriptor.tablename
    schema = cls._descriptor.table_options.get('schema', None)
    cls._table_key = sqlalchemy.schema._get_table_key(tablename, schema)

    table_proxy = TriggerProxy(cls, 'table')

    md = cls._descriptor.metadata
    md.tables[cls._table_key] = table_proxy

    # We need to monkeypatch the metadata's table iterator method because
    # otherwise it doesn't work if the setup is triggered by the
    # metadata.create_all().
    # This is because ManyToMany relationships add tables AFTER the list
    # of tables that are going to be created is "computed"
    # (metadata.tables.values()).
    # see:
    # - table_iterator method in MetaData class in sqlalchemy/schema.py
    # - visit_metadata method in sqlalchemy/ansisql.py
    original_table_iterator = md.table_iterator
    if not hasattr(original_table_iterator,
                   '_non_elixir_patched_iterator'):
        def table_iterator(*args, **kwargs):
            elixir.setup_all()
            return original_table_iterator(*args, **kwargs)
        table_iterator.__doc__ = original_table_iterator.__doc__
        table_iterator._non_elixir_patched_iterator = \
            original_table_iterator
        md.table_iterator = table_iterator

    #TODO: we might want to add all columns that will be available as
    #attributes on the class itself (in SA 0.4+). This is a pretty
    #rare usecase, as people will normally hit the query attribute before the
    #column attributes, but I've seen people hitting this problem...
    for name in ('c', 'table', 'mapper', 'query'):
        setattr(cls, name, TriggerAttribute(name))

    cls._has_triggers = True


def _cleanup_autosetup_triggers(cls):
    if not hasattr(cls, '_has_triggers'):
        return

    for name in ('table', 'mapper'):
        setattr(cls, name, None)

    for name in ('c', 'query'):
        delattr(cls, name)

    desc = cls._descriptor
    md = desc.metadata

    # the fake table could have already been removed (namely in a
    # single table inheritance scenario)
    md.tables.pop(cls._table_key, None)

    # restore original table iterator if not done already
    if hasattr(md.table_iterator, '_non_elixir_patched_iterator'):
        md.table_iterator = \
            md.table_iterator._non_elixir_patched_iterator

    del cls._has_triggers


def setup_entities(entities):
    '''Setup all entities in the list passed as argument'''

    for entity in entities:
        if entity._descriptor.autosetup:
            _cleanup_autosetup_triggers(entity)

    for method_name in (
            'setup_autoload_table', 'create_pk_cols', 'setup_relkeys',
            'before_table', 'setup_table', 'setup_reltables', 'after_table',
            'setup_events',
            'before_mapper', 'setup_mapper', 'after_mapper',
            'setup_properties',
            'finalize'):
        for entity in entities:
            if hasattr(entity, '_setup_done'):
                continue
            method = getattr(entity._descriptor, method_name)
            method()


def cleanup_entities(entities):
    """
    Try to revert back the list of entities passed as argument to the state
    they had just before their setup phase. It will not work entirely for
    autosetup entities as we need to remove the autosetup triggers.

    As of now, this function is *not* functional in that it doesn't revert to
    the exact same state the entities were before setup. For example, the
    properties do not work yet as those would need to be regenerated (since the
    columns they are based on are regenerated too -- and as such the
    corresponding joins are not correct) but this doesn't happen because of
    the way relationship setup is designed to be called only once (especially
    the backref stuff in create_properties).
    """
    for entity in entities:
        desc = entity._descriptor
        if desc.autosetup:
            _cleanup_autosetup_triggers(entity)

        if hasattr(entity, '_setup_done'):
            del entity._setup_done

        entity.table = None
        entity.mapper = None

        desc._pk_col_done = False
        desc.has_pk = False
        desc._columns = []
        desc.constraints = []
        desc.properties = {}


class Entity(object):
    '''
    The base class for all entities

    All Elixir model objects should inherit from this class. Statements can
    appear within the body of the definition of an entity to define its
    fields, relationships, and other options.

    Here is an example:

    .. sourcecode:: python

        class Person(Entity):
            name = Field(Unicode(128))
            birthdate = Field(DateTime, default=datetime.now)

    Please note, that if you don't specify any primary keys, Elixir will
    automatically create one called ``id``.

    For further information, please refer to the provided examples or
    tutorial.
    '''
    __metaclass__ = EntityMeta

    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def update_or_create(cls, data, surrogate=True):
        pk_props = cls._descriptor.primary_key_properties

        # if all pk are present and not None
        if not [1 for p in pk_props if data.get(p.key) is None]:
            pk_tuple = tuple([data[prop.key] for prop in pk_props])
            record = cls.query.get(pk_tuple)
            if record is None:
                if surrogate:
                    raise Exception("cannot create surrogate with pk")
                else:
                    record = cls()
        else:
            if surrogate:
                record = cls()
            else:
                raise Exception("cannot create non surrogate without pk")
        record.from_dict(data)
        return record
    update_or_create = classmethod(update_or_create)

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        # surrogate can be guessed from autoincrement/sequence but I guess
        # that's not 100% reliable, so we'll need an override

        mapper = sqlalchemy.orm.object_mapper(self)

        for key, value in data.iteritems():
            if isinstance(value, dict):
                dbvalue = getattr(self, key)
                rel_class = mapper.get_property(key).mapper.class_
                pk_props = rel_class._descriptor.primary_key_properties

                # If the data doesn't contain any pk, and the relationship
                # already has a value, update that record.
                if not [1 for p in pk_props if p.key in data] and \
                   dbvalue is not None:
                    dbvalue.from_dict(value)
                else:
                    record = rel_class.update_or_create(value)
                    setattr(self, key, record)
            elif isinstance(value, list) and \
                 value and isinstance(value[0], dict):

                rel_class = mapper.get_property(key).mapper.class_
                new_attr_value = []
                for row in value:
                    if not isinstance(row, dict):
                        raise Exception(
                                'Cannot send mixed (dict/non dict) data '
                                'to list relationships in from_dict data.')
                    record = rel_class.update_or_create(row)
                    new_attr_value.append(record)
                setattr(self, key, new_attr_value)
            else:
                setattr(self, key, value)

    def to_dict(self, deep={}, exclude=[]):
        """Generate a JSON-style nested dict/list structure from an object."""
        col_prop_names = [p.key for p in self.mapper.iterate_properties \
                                      if isinstance(p, ColumnProperty)]
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        for rname, rdeep in deep.iteritems():
            dbdata = getattr(self, rname)
            #FIXME: use attribute names (ie coltoprop) instead of column names
            fks = self.mapper.get_property(rname).remote_side
            exclude = [c.name for c in fks]
            if isinstance(dbdata, list):
                data[rname] = [o.to_dict(rdeep, exclude) for o in dbdata]
            else:
                data[rname] = dbdata.to_dict(rdeep, exclude)
        return data

    # session methods
    def flush(self, *args, **kwargs):
        return object_session(self).flush([self], *args, **kwargs)

    def delete(self, *args, **kwargs):
        return object_session(self).delete(self, *args, **kwargs)

    def expire(self, *args, **kwargs):
        return object_session(self).expire(self, *args, **kwargs)

    def refresh(self, *args, **kwargs):
        return object_session(self).refresh(self, *args, **kwargs)

    def expunge(self, *args, **kwargs):
        return object_session(self).expunge(self, *args, **kwargs)

    # This bunch of session methods, along with all the query methods below
    # only make sense when using a global/scoped/contextual session.
    def _global_session(self):
        return self._descriptor.session.registry()
    _global_session = property(_global_session)

    def merge(self, *args, **kwargs):
        return self._global_session.merge(self, *args, **kwargs)

    def save(self, *args, **kwargs):
        return self._global_session.save(self, *args, **kwargs)

    def update(self, *args, **kwargs):
        return self._global_session.update(self, *args, **kwargs)

    # only exist in SA < 0.5
    # IMO, the replacement (session.add) doesn't sound good enough to be added
    # here. For example: "o = Order(); o.add()" is not very telling. It's
    # better to leave it as "session.add(o)"
    def save_or_update(self, *args, **kwargs):
        return self._global_session.save_or_update(self, *args, **kwargs)

    # query methods
    def get_by(cls, *args, **kwargs):
        return cls.query.filter_by(*args, **kwargs).first()
    get_by = classmethod(get_by)

    def get(cls, *args, **kwargs):
        return cls.query.get(*args, **kwargs)
    get = classmethod(get)

