# Copyright 2014 Intel Corporation
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

from datetime import datetime
from functools import partial

from django.template import defaultfilters as django_filters
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
from horizon.utils import filters
import pytz

from blazar_dashboard import api


class UpdateLease(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Lease")
    url = "horizon:project:leases:update"
    classes = ("btn-create", "ajax-modal")

    def allowed(self, request, lease):
        if datetime.strptime(lease.end_date, '%Y-%m-%dT%H:%M:%S.%f').\
                replace(tzinfo=pytz.utc) > datetime.now(pytz.utc):
            return True
        return False


class DeleteLease(tables.DeleteAction):
    name = "delete"
    data_type_singular = _("Lease")
    data_type_plural = _("Leases")
    classes = ('btn-danger', 'btn-terminate')

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Lease",
            u"Delete Leases",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Lease",
            u"Deleted Leases",
            count
        )

    def delete(self, request, lease_id):
        api.client.lease_delete(request, lease_id)


class LeasesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Lease name"),
                         link="horizon:project:leases:detail",)
    start_date = tables.Column("start_date", verbose_name=_("Start date"),
                               filters=(filters.parse_isotime,
                                        partial(django_filters.date,
                                                arg='Y-m-d H:i T')),)
    end_date = tables.Column("end_date", verbose_name=_("End date"),
                             filters=(filters.parse_isotime,
                                      partial(django_filters.date,
                                              arg='Y-m-d H:i T')),)
    action = tables.Column("action", verbose_name=_("Action"),)
    status = tables.Column("status", verbose_name=_("Status"),)
    status_reason = tables.Column("status_reason", verbose_name=_("Reason"),)

    class Meta(object):
        name = "leases"
        verbose_name = _("Leases")
        table_actions = (DeleteLease, )
        row_actions = (UpdateLease, DeleteLease, )
