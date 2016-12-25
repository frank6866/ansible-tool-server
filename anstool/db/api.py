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

"""Defines interface for DB access.

Functions in this module are imported into the nova.db namespace. Call these
functions from nova.db namespace, not the nova.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.

"""

from oslo_db import concurrency
from oslo_log import log as logging

import anstool.conf


CONF = anstool.conf.CONF

_BACKEND_MAPPING = {'sqlalchemy': 'nova.db.sqlalchemy.api'}


IMPL = concurrency.TpoolDbapiWrapper(CONF, backend_mapping=_BACKEND_MAPPING)

LOG = logging.getLogger(__name__)

# The maximum value a signed INT type may have
MAX_INT = 0x7FFFFFFF

# NOTE(dosaboy): This is supposed to represent the maximum value that we can
# place into a SQL single precision float so that we can check whether values
# are oversize. Postgres and MySQL both define this as their max whereas Sqlite
# uses dynamic typing so this would not apply. Different dbs react in different
# ways to oversize values e.g. postgres will raise an exception while mysql
# will round off the value. Nevertheless we may still want to know prior to
# insert whether the value is oversize or not.
SQL_SP_FLOAT_MAX = 3.40282e+38

###################


def constraint(**conditions):
    """Return a constraint object suitable for use with some updates."""
    return IMPL.constraint(**conditions)


def equal_any(*values):
    """Return an equality condition object suitable for use in a constraint.

    Equal_any conditions require that a model object's attribute equal any
    one of the given values.
    """
    return IMPL.equal_any(*values)


def not_equal(*values):
    """Return an inequality condition object suitable for use in a constraint.

    Not_equal conditions require that a model object's attribute differs from
    all of the given values.
    """
    return IMPL.not_equal(*values)


def create_context_manager(connection):
    """Return a context manager for a cell database connection."""
    return IMPL.create_context_manager(connection=connection)


###################


def select_db_reader_mode(f):
    """Decorator to select synchronous or asynchronous reader mode.

    The kwarg argument 'use_slave' defines reader mode. Asynchronous reader
    will be used if 'use_slave' is True and synchronous reader otherwise.
    """
    return IMPL.select_db_reader_mode(f)


###################


def service_destroy(context, service_id):
    """Destroy the service or raise if it does not exist."""
    return IMPL.service_destroy(context, service_id)


def service_get(context, service_id):
    """Get a service or raise if it does not exist."""
    return IMPL.service_get(context, service_id)


def service_get_minimum_version(context, binary):
    """Get the minimum service version in the database."""
    return IMPL.service_get_minimum_version(context, binary)


def service_get_by_host_and_topic(context, host, topic):
    """Get a service by hostname and topic it listens to."""
    return IMPL.service_get_by_host_and_topic(context, host, topic)


def service_get_by_host_and_binary(context, host, binary):
    """Get a service by hostname and binary."""
    return IMPL.service_get_by_host_and_binary(context, host, binary)


def service_get_all(context, disabled=None):
    """Get all services."""
    return IMPL.service_get_all(context, disabled)


def service_get_all_by_topic(context, topic):
    """Get all services for a given topic."""
    return IMPL.service_get_all_by_topic(context, topic)


def service_get_all_by_binary(context, binary, include_disabled=False):
    """Get services for a given binary.

    Includes disabled services if 'include_disabled' parameter is True
    """
    return IMPL.service_get_all_by_binary(context, binary,
                                          include_disabled=include_disabled)


def service_get_all_by_host(context, host):
    """Get all services for a given host."""
    return IMPL.service_get_all_by_host(context, host)


def service_get_by_compute_host(context, host):
    """Get the service entry for a given compute host.

    Returns the service entry joined with the compute_node entry.
    """
    return IMPL.service_get_by_compute_host(context, host)


def service_create(context, values):
    """Create a service from the values dictionary."""
    return IMPL.service_create(context, values)


def service_update(context, service_id, values):
    """Set the given properties on a service and update it.

    Raises NotFound if service does not exist.

    """
    return IMPL.service_update(context, service_id, values)
