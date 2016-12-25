# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Implementation of SQLAlchemy backend."""

import functools
import inspect
import sys

import six
from oslo_db import api as oslo_db_api
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_log import log as logging
from oslo_utils import timeutils
from sqlalchemy import or_
from sqlalchemy.sql import false
from sqlalchemy.sql import func
from sqlalchemy.sql import null

# from nova import block_device
# from nova.compute import task_states
# from nova.compute import vm_states
# import nova.conf
# import nova.context
# from nova.db.sqlalchemy import models
# from nova import exception
# from nova.i18n import _, _LI, _LE, _LW
# from nova import quota
# from nova import safe_utils

import anstool.conf
import anstool.context
from anstool import exception
from anstool.db.sqlalchemy import models

CONF = anstool.conf.CONF

LOG = logging.getLogger(__name__)

main_context_manager = enginefacade.transaction_context()
api_context_manager = enginefacade.transaction_context()


def _get_db_conf(conf_group, connection=None):
    kw = dict(
        connection=connection or conf_group.connection,
        slave_connection=conf_group.slave_connection,
        sqlite_fk=False,
        __autocommit=True,
        expire_on_commit=False,
        mysql_sql_mode=conf_group.mysql_sql_mode,
        idle_timeout=conf_group.idle_timeout,
        connection_debug=conf_group.connection_debug,
        max_pool_size=conf_group.max_pool_size,
        max_overflow=conf_group.max_overflow,
        pool_timeout=conf_group.pool_timeout,
        sqlite_synchronous=conf_group.sqlite_synchronous,
        connection_trace=conf_group.connection_trace,
        max_retries=conf_group.max_retries,
        retry_interval=conf_group.retry_interval)
    return kw


def _context_manager_from_context(context):
    if context:
        try:
            return context.db_connection
        except AttributeError:
            pass


def configure(conf):
    main_context_manager.configure(**_get_db_conf(conf.database))
    api_context_manager.configure(**_get_db_conf(conf.api_database))


def create_context_manager(connection=None):
    """Create a database context manager object.

    : param connection: The database connection string
    """
    ctxt_mgr = enginefacade.transaction_context()
    ctxt_mgr.configure(**_get_db_conf(CONF.database, connection=connection))
    return ctxt_mgr


def get_context_manager(context):
    """Get a database context manager object.

    :param context: The request context that can contain a context manager
    """
    return _context_manager_from_context(context) or main_context_manager


def get_engine(use_slave=False, context=None):
    """Get a database engine object.

    :param use_slave: Whether to use the slave connection
    :param context: The request context that can contain a context manager
    """
    ctxt_mgr = _context_manager_from_context(context) or main_context_manager
    return ctxt_mgr.get_legacy_facade().get_engine(use_slave=use_slave)


def get_api_engine():
    return api_context_manager.get_legacy_facade().get_engine()


_SHADOW_TABLE_PREFIX = 'shadow_'
_DEFAULT_QUOTA_NAME = 'default'
PER_PROJECT_QUOTAS = ['fixed_ips', 'floating_ips', 'networks']


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def require_context(f):
    """Decorator to require *any* user or admin context.

    This does no authorization for user or project access matching, see
    :py:func:`nova.context.authorize_project_context` and
    :py:func:`nova.context.authorize_user_context`.

    The first argument to the wrapped function must be the context.

    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        anstool.context.require_context(args[0])
        return f(*args, **kwargs)

    return wrapper


def require_instance_exists_using_uuid(f):
    """Decorator to require the specified instance to exist.

    Requires the wrapped function to use context and instance_uuid as
    their first two arguments.
    """

    @functools.wraps(f)
    def wrapper(context, instance_uuid, *args, **kwargs):
        # instance_get_by_uuid(context, instance_uuid)
        return f(context, instance_uuid, *args, **kwargs)

    return wrapper


def select_db_reader_mode(f):
    """Decorator to select synchronous or asynchronous reader mode.

    The kwarg argument 'use_slave' defines reader mode. Asynchronous reader
    will be used if 'use_slave' is True and synchronous reader otherwise.
    If 'use_slave' is not specified default value 'False' will be used.

    Wrapped function must have a context in the arguments.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        wrapped_func = None  # safe_utils.get_wrapped_function(f)
        keyed_args = inspect.getcallargs(wrapped_func, *args, **kwargs)

        context = keyed_args['context']
        use_slave = keyed_args.get('use_slave', False)

        if use_slave:
            reader_mode = main_context_manager.async
        else:
            reader_mode = main_context_manager.reader

        with reader_mode.using(context):
            return f(*args, **kwargs)

    return wrapper


def pick_context_manager_writer(f):
    """Decorator to use a writer db context manager.

    The db context manager will be picked from the RequestContext.

    Wrapped function must have a RequestContext in the arguments.
    """

    @functools.wraps(f)
    def wrapped(context, *args, **kwargs):
        ctxt_mgr = get_context_manager(context)
        with ctxt_mgr.writer.using(context):
            return f(context, *args, **kwargs)

    return wrapped


def pick_context_manager_reader(f):
    """Decorator to use a reader db context manager.

    The db context manager will be picked from the RequestContext.

    Wrapped function must have a RequestContext in the arguments.
    """

    @functools.wraps(f)
    def wrapped(context, *args, **kwargs):
        ctxt_mgr = get_context_manager(context)
        with ctxt_mgr.reader.using(context):
            return f(context, *args, **kwargs)

    return wrapped


def pick_context_manager_reader_allow_async(f):
    """Decorator to use a reader.allow_async db context manager.

    The db context manager will be picked from the RequestContext.

    Wrapped function must have a RequestContext in the arguments.
    """

    @functools.wraps(f)
    def wrapped(context, *args, **kwargs):
        ctxt_mgr = get_context_manager(context)
        with ctxt_mgr.reader.allow_async.using(context):
            return f(context, *args, **kwargs)

    return wrapped


def model_query(context, model,
                args=None,
                read_deleted=None,
                project_only=False):
    """Query helper that accounts for context's `read_deleted` field.

    :param context:     NovaContext of the query.
    :param model:       Model to query. Must be a subclass of ModelBase.
    :param args:        Arguments to query. If None - model is used.
    :param read_deleted: If not None, overrides context's read_deleted field.
                        Permitted values are 'no', which does not return
                        deleted values; 'only', which only returns deleted
                        values; and 'yes', which does not filter deleted
                        values.
    :param project_only: If set and context is user-type, then restrict
                        query to match the context's project_id. If set to
                        'allow_none', restriction includes project_id = None.
    """

    if read_deleted is None:
        read_deleted = context.read_deleted

    query_kwargs = {}
    if 'no' == read_deleted:
        query_kwargs['deleted'] = False
    elif 'only' == read_deleted:
        query_kwargs['deleted'] = True
    elif 'yes' == read_deleted:
        pass
    else:
        pass

    query = sqlalchemyutils.model_query(
        model, context.session, args, **query_kwargs)

    # We can't use oslo.db model_query's project_id here, as it doesn't allow
    # us to return both our projects and unowned projects.
    if anstool.context.is_user_context(context) and project_only:
        if project_only == 'allow_none':
            query = query. \
                filter(or_(model.project_id == context.project_id,
                           model.project_id == null()))
        else:
            query = query.filter_by(project_id=context.project_id)

    return query


def convert_objects_related_datetimes(values, *datetime_keys):
    if not datetime_keys:
        datetime_keys = ('created_at', 'deleted_at', 'updated_at')

    for key in datetime_keys:
        if key in values and values[key]:
            if isinstance(values[key], six.string_types):
                try:
                    values[key] = timeutils.parse_strtime(values[key])
                except ValueError:
                    # Try alternate parsing since parse_strtime will fail
                    # with say converting '2015-05-28T19:59:38+00:00'
                    values[key] = timeutils.parse_isotime(values[key])
            # NOTE(danms): Strip UTC timezones from datetimes, since they're
            # stored that way in the database
            values[key] = values[key].replace(tzinfo=None)
    return values


###################


def constraint(**conditions):
    return Constraint(conditions)


def equal_any(*values):
    return EqualityCondition(values)


def not_equal(*values):
    return InequalityCondition(values)


class Constraint(object):
    def __init__(self, conditions):
        self.conditions = conditions

    def apply(self, model, query):
        for key, condition in self.conditions.items():
            for clause in condition.clauses(getattr(model, key)):
                query = query.filter(clause)
        return query


class EqualityCondition(object):
    def __init__(self, values):
        self.values = values

    def clauses(self, field):
        # method signature requires us to return an iterable even if for OR
        # operator this will actually be a single clause
        return [or_(*[field == value for value in self.values])]


class InequalityCondition(object):
    def __init__(self, values):
        self.values = values

    def clauses(self, field):
        return [field != value for value in self.values]


###################


@pick_context_manager_writer
def service_destroy(context, service_id):
    service = service_get(context, service_id)

    model_query(context, models.Service). \
        filter_by(id=service_id). \
        soft_delete(synchronize_session=False)

    # TODO(sbauza): Remove the service_id filter in a later release
    # once we are sure that all compute nodes report the host field
    model_query(context, models.ComputeNode). \
        filter(or_(models.ComputeNode.service_id == service_id,
                   models.ComputeNode.host == service['host'])). \
        soft_delete(synchronize_session=False)


@pick_context_manager_reader
def service_get(context, service_id):
    query = model_query(context, models.Service).filter_by(id=service_id)

    result = query.first()
    if not result:
        raise exception.ServiceNotFound(service_id=service_id)

    return result


@pick_context_manager_reader_allow_async
def service_get_minimum_version(context, binaries):
    min_versions = context.session.query(
        models.Service.binary,
        func.min(models.Service.version)). \
        filter(models.Service.binary.in_(binaries)). \
        filter(models.Service.forced_down == false()). \
        group_by(models.Service.binary)
    return dict(min_versions)


@pick_context_manager_reader
def service_get_all(context, disabled=None):
    query = model_query(context, models.Service)

    if disabled is not None:
        query = query.filter_by(disabled=disabled)

    return query.all()


@pick_context_manager_reader
def service_get_all_by_topic(context, topic):
    return model_query(context, models.Service, read_deleted="no"). \
        filter_by(disabled=False). \
        filter_by(topic=topic). \
        all()


@pick_context_manager_reader
def service_get_by_host_and_topic(context, host, topic):
    return model_query(context, models.Service, read_deleted="no"). \
        filter_by(disabled=False). \
        filter_by(host=host). \
        filter_by(topic=topic). \
        first()


@pick_context_manager_reader
def service_get_all_by_binary(context, binary, include_disabled=False):
    query = model_query(context, models.Service, read_deleted="no"). \
        filter_by(binary=binary)
    if not include_disabled:
        query = query.filter_by(disabled=False)
    return query.all()


@pick_context_manager_reader
def service_get_by_host_and_binary(context, host, binary):
    result = model_query(context, models.Service, read_deleted="no"). \
        filter_by(host=host). \
        filter_by(binary=binary). \
        first()

    if not result:
        raise exception.HostBinaryNotFound(host=host, binary=binary)

    return result


@pick_context_manager_reader
def service_get_all_by_host(context, host):
    return model_query(context, models.Service, read_deleted="no"). \
        filter_by(host=host). \
        all()


@pick_context_manager_reader_allow_async
def service_get_by_compute_host(context, host):
    result = model_query(context, models.Service, read_deleted="no"). \
        filter_by(host=host). \
        filter_by(binary='nova-compute'). \
        first()

    if not result:
        raise exception.ComputeHostNotFound(host=host)

    return result


@pick_context_manager_writer
def service_create(context, values):
    service_ref = models.Service()
    service_ref.update(values)
    if not CONF.enable_new_services:
        msg = "New service disabled due to config option."
        service_ref.disabled = True
        service_ref.disabled_reason = msg
    try:
        service_ref.save(context.session)
    except db_exc.DBDuplicateEntry as e:
        if 'binary' in e.columns:
            raise exception.ServiceBinaryExists(host=values.get('host'),
                                                binary=values.get('binary'))
        raise exception.ServiceTopicExists(host=values.get('host'),
                                           topic=values.get('topic'))
    return service_ref


@oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
@pick_context_manager_writer
def service_update(context, service_id, values):
    service_ref = service_get(context, service_id)
    # Only servicegroup.drivers.db.DbDriver._report_state() updates
    # 'report_count', so if that value changes then store the timestamp
    # as the last time we got a state report.
    if 'report_count' in values:
        if values['report_count'] > service_ref.report_count:
            service_ref.last_seen_up = timeutils.utcnow()
    service_ref.update(values)

    return service_ref
