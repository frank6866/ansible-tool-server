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

"""Nova base exception handling.

Includes decorator for re-raising Nova-type exceptions.

SHOULD include dedicated exception logging.

"""

import sys

from oslo_log import log as logging
import six
import webob.exc
from webob import util as woutil

# import nova.conf
# from nova.i18n import _, _LE

import anstool.conf

LOG = logging.getLogger(__name__)


CONF = anstool.conf.CONF


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init_(self, code, title="", explanation=""):
        self.code = code
        # There is a strict rule about constructing status line for HTTP:
        # '...Status-Line, consisting of the protocol version followed by a
        # numeric status code and its associated textual phrase, with each
        # element separated by SP characters'
        # (http://www.faqs.org/rfcs/rfc2616.html)
        # 'code' and 'title' can not be empty because they correspond
        # to numeric status code and its associated text
        if title:
            self.title = title
        else:
            try:
                self.title = woutil.status_reasons[self.code]
            except KeyError:
                msg = "Improper or unknown HTTP status code used: %d"
                LOG.error(msg, code)
                self.title = woutil.status_generic_reasons[self.code // 100]
        self.explanation = explanation
        super(ConvertedException, self).__init_()


class NovaException(Exception):
    """Base Nova Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    msg_fmt = ("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init_(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs

            except Exception:
                exc_info = sys.exc_info()
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(('Exception in string format operation'))
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))    # noqa

                if CONF.fatal_exception_format_errors:
                    six.reraise(*exc_info)
                else:
                    # at least get the core message out if something happened
                    message = self.msg_fmt

        self.message = message
        super(NovaException, self).__init_(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full NovaException message, (see __init__)
        return self.args[0]


class EncryptionFailure(NovaException):
    msg_fmt = ("Failed to encrypt text: %(reason)s")


class DecryptionFailure(NovaException):
    msg_fmt = ("Failed to decrypt text: %(reason)s")


class RevokeCertFailure(NovaException):
    msg_fmt = ("Failed to revoke certificate for %(project_id)s")


class VirtualInterfaceCreateException(NovaException):
    msg_fmt = ("Virtual Interface creation failed")


class VirtualInterfaceMacAddressException(NovaException):
    msg_fmt = ("Creation of virtual interface with "
                "unique mac address failed")


class VirtualInterfacePlugException(NovaException):
    msg_fmt = ("Virtual interface plugin failed")


class VirtualInterfaceUnplugException(NovaException):
    msg_fmt = ("Failed to unplug virtual interface: %(reason)s")


class GlanceConnectionFailed(NovaException):
    msg_fmt = ("Connection to glance host %(server)s failed: "
        "%(reason)s")


class CinderConnectionFailed(NovaException):
    msg_fmt = ("Connection to cinder host failed: %(reason)s")


class Forbidden(NovaException):
    msg_fmt = ("Forbidden")
    code = 403


class AdminRequired(Forbidden):
    msg_fmt = ("User does not have admin privileges")


class PolicyNotAuthorized(Forbidden):
    msg_fmt = ("Policy doesn't allow %(action)s to be performed.")


class VolumeLimitExceeded(Forbidden):
    msg_fmt = ("Volume resource quota exceeded")


class ImageNotActive(NovaException):
    # NOTE(jruzicka): IncorrectState is used for volumes only in EC2,
    # but it still seems like the most appropriate option.
    msg_fmt = ("Image %(image_id)s is not active.")


class ImageNotAuthorized(NovaException):
    msg_fmt = ("Not authorized for image %(image_id)s.")


class Invalid(NovaException):
    msg_fmt = ("Bad Request - Invalid Parameters")
    code = 400


class InvalidBDM(Invalid):
    msg_fmt = ("Block Device Mapping is Invalid.")


class InvalidBDMSnapshot(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "failed to get snapshot %(id)s.")


class InvalidBDMVolume(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "failed to get volume %(id)s.")


class UnsupportedBDMVolumeAuthMethod(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "%(auth_method)s is unsupported.")


class InvalidBDMImage(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "failed to get image %(id)s.")


class InvalidBDMBootSequence(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "Boot sequence for the instance "
                "and image/block device mapping "
                "combination is not valid.")


class InvalidBDMLocalsLimit(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "You specified more local devices than the "
                "limit allows")


class InvalidBDMEphemeralSize(InvalidBDM):
    msg_fmt = ("Ephemeral disks requested are larger than "
                "the instance type allows.")


class InvalidBDMSwapSize(InvalidBDM):
    msg_fmt = ("Swap drive requested is larger than instance type allows.")


class InvalidBDMFormat(InvalidBDM):
    msg_fmt = ("Block Device Mapping is Invalid: "
                "%(details)s")


class InvalidBDMForLegacy(InvalidBDM):
    msg_fmt = ("Block Device Mapping cannot "
                "be converted to legacy format. ")


class InvalidBDMVolumeNotBootable(InvalidBDM):
    msg_fmt = ("Block Device %(id)s is not bootable.")


class InvalidAttribute(Invalid):
    msg_fmt = ("Attribute not supported: %(attr)s")


class ValidationError(Invalid):
    msg_fmt = "%(detail)s"


class VolumeAttachFailed(Invalid):
    msg_fmt = ("Volume %(volume_id)s could not be attached. "
                "Reason: %(reason)s")


class VolumeUnattached(Invalid):
    msg_fmt = ("Volume %(volume_id)s is not attached to anything")


class VolumeNotCreated(NovaException):
    msg_fmt = ("Volume %(volume_id)s did not finish being created"
                " even after we waited %(seconds)s seconds or %(attempts)s"
                " attempts. And its status is %(volume_status)s.")


class VolumeEncryptionNotSupported(Invalid):
    msg_fmt = ("Volume encryption is not supported for %(volume_type)s "
                "volume %(volume_id)s")


class InvalidKeypair(Invalid):
    msg_fmt = ("Keypair data is invalid: %(reason)s")


class InvalidRequest(Invalid):
    msg_fmt = ("The request is invalid.")


class InvalidInput(Invalid):
    msg_fmt = ("Invalid input received: %(reason)s")


class InvalidVolume(Invalid):
    msg_fmt = ("Invalid volume: %(reason)s")


class InvalidVolumeAccessMode(Invalid):
    msg_fmt = ("Invalid volume access mode: %(access_mode)s")


class InvalidMetadata(Invalid):
    msg_fmt = ("Invalid metadata: %(reason)s")


class InvalidMetadataSize(Invalid):
    msg_fmt = ("Invalid metadata size: %(reason)s")


class InvalidPortRange(Invalid):
    msg_fmt = ("Invalid port range %(from_port)s:%(to_port)s. %(msg)s")


class InvalidIpProtocol(Invalid):
    msg_fmt = ("Invalid IP protocol %(protocol)s.")


class InvalidContentType(Invalid):
    msg_fmt = ("Invalid content type %(content_type)s.")


class InvalidAPIVersionString(Invalid):
    msg_fmt = ("API Version String %(version)s is of invalid format. Must "
                "be of format MajorNum.MinorNum.")


class VersionNotFoundForAPIMethod(Invalid):
    msg_fmt = ("API version %(version)s is not supported on this method.")


class InvalidGlobalAPIVersion(Invalid):
    msg_fmt = ("Version %(req_ver)s is not supported by the API. Minimum "
                "is %(min_ver)s and maximum is %(max_ver)s.")


class ApiVersionsIntersect(Invalid):
    msg_fmt = ("Version of %(name) %(min_ver) %(max_ver) intersects "
                "with another versions.")


# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    msg_fmt = ("%(err)s")


class InvalidAggregateAction(Invalid):
    msg_fmt = ("Unacceptable parameters.")
    code = 400


class InvalidAggregateActionAdd(InvalidAggregateAction):
    msg_fmt = ("Cannot add host to aggregate "
                "%(aggregate_id)s. Reason: %(reason)s.")


class InvalidAggregateActionDelete(InvalidAggregateAction):
    msg_fmt = ("Cannot remove host from aggregate "
                "%(aggregate_id)s. Reason: %(reason)s.")


class InvalidAggregateActionUpdate(InvalidAggregateAction):
    msg_fmt = ("Cannot update aggregate "
                "%(aggregate_id)s. Reason: %(reason)s.")


class InvalidAggregateActionUpdateMeta(InvalidAggregateAction):
    msg_fmt = ("Cannot update metadata of aggregate "
                "%(aggregate_id)s. Reason: %(reason)s.")


class InvalidGroup(Invalid):
    msg_fmt = ("Group not valid. Reason: %(reason)s")


class InvalidSortKey(Invalid):
    msg_fmt = ("Sort key supplied was not valid.")


class InvalidStrTime(Invalid):
    msg_fmt = ("Invalid datetime string: %(reason)s")


class InvalidName(Invalid):
    msg_fmt = ("An invalid 'name' value was provided. "
                "The name must be: %(reason)s")


class InstanceInvalidState(Invalid):
    msg_fmt = ("Instance %(instance_uuid)s in %(attr)s %(state)s. Cannot "
                "%(method)s while the instance is in this state.")


class InstanceNotRunning(Invalid):
    msg_fmt = ("Instance %(instance_id)s is not running.")


class InstanceNotInRescueMode(Invalid):
    msg_fmt = ("Instance %(instance_id)s is not in rescue mode")


class InstanceNotRescuable(Invalid):
    msg_fmt = ("Instance %(instance_id)s cannot be rescued: %(reason)s")


class InstanceNotReady(Invalid):
    msg_fmt = ("Instance %(instance_id)s is not ready")


class InstanceSuspendFailure(Invalid):
    msg_fmt = ("Failed to suspend instance: %(reason)s")


class InstanceResumeFailure(Invalid):
    msg_fmt = ("Failed to resume instance: %(reason)s")


class InstancePowerOnFailure(Invalid):
    msg_fmt = ("Failed to power on instance: %(reason)s")


class InstancePowerOffFailure(Invalid):
    msg_fmt = ("Failed to power off instance: %(reason)s")


class InstanceRebootFailure(Invalid):
    msg_fmt = ("Failed to reboot instance: %(reason)s")


class InstanceTerminationFailure(Invalid):
    msg_fmt = ("Failed to terminate instance: %(reason)s")


class InstanceDeployFailure(Invalid):
    msg_fmt = ("Failed to deploy instance: %(reason)s")


class MultiplePortsNotApplicable(Invalid):
    msg_fmt = ("Failed to launch instances: %(reason)s")


class InvalidFixedIpAndMaxCountRequest(Invalid):
    msg_fmt = ("Failed to launch instances: %(reason)s")


class ServiceUnavailable(Invalid):
    msg_fmt = ("Service is unavailable at this time.")


class ComputeResourcesUnavailable(ServiceUnavailable):
    msg_fmt = ("Insufficient compute resources: %(reason)s.")


class HypervisorUnavailable(NovaException):
    msg_fmt = ("Connection to the hypervisor is broken on host: %(host)s")


class ComputeServiceUnavailable(ServiceUnavailable):
    msg_fmt = ("Compute service of %(host)s is unavailable at this time.")


class ComputeServiceInUse(NovaException):
    msg_fmt = ("Compute service of %(host)s is still in use.")


class UnableToMigrateToSelf(Invalid):
    msg_fmt = ("Unable to migrate instance (%(instance_id)s) "
                "to current host (%(host)s).")


class InvalidHypervisorType(Invalid):
    msg_fmt = ("The supplied hypervisor type of is invalid.")


class HypervisorTooOld(Invalid):
    msg_fmt = ("This compute node's hypervisor is older than the minimum "
                "supported version: %(version)s.")


class DestinationHypervisorTooOld(Invalid):
    msg_fmt = ("The instance requires a newer hypervisor version than "
                "has been provided.")


class ServiceTooOld(Invalid):
    msg_fmt = ("This service is older (v%(thisver)i) than the minimum "
                "(v%(minver)i) version of the rest of the deployment. "
                "Unable to continue.")


class DestinationDiskExists(Invalid):
    msg_fmt = ("The supplied disk path (%(path)s) already exists, "
                "it is expected not to exist.")


class InvalidDevicePath(Invalid):
    msg_fmt = ("The supplied device path (%(path)s) is invalid.")


class DevicePathInUse(Invalid):
    msg_fmt = ("The supplied device path (%(path)s) is in use.")
    code = 409


class DeviceIsBusy(Invalid):
    msg_fmt = ("The supplied device (%(device)s) is busy.")


class InvalidCPUInfo(Invalid):
    msg_fmt = ("Unacceptable CPU info: %(reason)s")


class InvalidIpAddressError(Invalid):
    msg_fmt = ("%(address)s is not a valid IP v4/6 address.")


class InvalidVLANTag(Invalid):
    msg_fmt = ("VLAN tag is not appropriate for the port group "
                "%(bridge)s. Expected VLAN tag is %(tag)s, "
                "but the one associated with the port group is %(pgroup)s.")


class InvalidVLANPortGroup(Invalid):
    msg_fmt = ("vSwitch which contains the port group %(bridge)s is "
                "not associated with the desired physical adapter. "
                "Expected vSwitch is %(expected)s, but the one associated "
                "is %(actual)s.")


class InvalidDiskFormat(Invalid):
    msg_fmt = ("Disk format %(disk_format)s is not acceptable")


class InvalidDiskInfo(Invalid):
    msg_fmt = ("Disk info file is invalid: %(reason)s")


class DiskInfoReadWriteFail(Invalid):
    msg_fmt = ("Failed to read or write disk info file: %(reason)s")


class ImageUnacceptable(Invalid):
    msg_fmt = ("Image %(image_id)s is unacceptable: %(reason)s")


class ImageBadRequest(Invalid):
    msg_fmt = ("Request of image %(image_id)s got BadRequest response: "
                "%(response)s")


class InstanceUnacceptable(Invalid):
    msg_fmt = ("Instance %(instance_id)s is unacceptable: %(reason)s")


class InvalidEc2Id(Invalid):
    msg_fmt = ("Ec2 id %(ec2_id)s is unacceptable.")


class InvalidUUID(Invalid):
    msg_fmt = ("Expected a uuid but received %(uuid)s.")


class InvalidID(Invalid):
    msg_fmt = ("Invalid ID received %(id)s.")


class ConstraintNotMet(NovaException):
    msg_fmt = ("Constraint not met.")
    code = 412


class NotFound(NovaException):
    msg_fmt = ("Resource could not be found.")
    code = 404


class AgentBuildNotFound(NotFound):
    msg_fmt = ("No agent-build associated with id %(id)s.")


class AgentBuildExists(NovaException):
    msg_fmt = ("Agent-build with hypervisor %(hypervisor)s os %(os)s "
                "architecture %(architecture)s exists.")


class VolumeNotFound(NotFound):
    msg_fmt = ("Volume %(volume_id)s could not be found.")


class UndefinedRootBDM(NovaException):
    msg_fmt = ("Undefined Block Device Mapping root: BlockDeviceMappingList "
                "contains Block Device Mappings from multiple instances.")


class BDMNotFound(NotFound):
    msg_fmt = ("No Block Device Mapping with id %(id)s.")


class VolumeBDMNotFound(NotFound):
    msg_fmt = ("No volume Block Device Mapping with id %(volume_id)s.")


class VolumeBDMIsMultiAttach(Invalid):
    msg_fmt = ("Block Device Mapping %(volume_id)s is a multi-attach volume"
                " and is not valid for this operation.")


class VolumeBDMPathNotFound(VolumeBDMNotFound):
    msg_fmt = ("No volume Block Device Mapping at path: %(path)s")


class DeviceDetachFailed(NovaException):
    msg_fmt = ("Device detach failed for %(device)s: %(reason)s)")


class DeviceNotFound(NotFound):
    msg_fmt = ("Device '%(device)s' not found.")


class SnapshotNotFound(NotFound):
    msg_fmt = ("Snapshot %(snapshot_id)s could not be found.")


class DiskNotFound(NotFound):
    msg_fmt = ("No disk at %(location)s")


class VolumeDriverNotFound(NotFound):
    msg_fmt = ("Could not find a handler for %(driver_type)s volume.")


class InvalidImageRef(Invalid):
    msg_fmt = ("Invalid image href %(image_href)s.")


class AutoDiskConfigDisabledByImage(Invalid):
    msg_fmt = ("Requested image %(image)s "
                "has automatic disk resize disabled.")


class ImageNotFound(NotFound):
    msg_fmt = ("Image %(image_id)s could not be found.")


class PreserveEphemeralNotSupported(Invalid):
    msg_fmt = ("The current driver does not support "
                "preserving ephemeral partitions.")


# NOTE(jruzicka): ImageNotFound is not a valid EC2 error code.
class ImageNotFoundEC2(ImageNotFound):
    msg_fmt = ("Image %(image_id)s could not be found. The nova EC2 API "
                "assigns image ids dynamically when they are listed for the "
                "first time. Have you listed image ids since adding this "
                "image?")


class ProjectNotFound(NotFound):
    msg_fmt = ("Project %(project_id)s could not be found.")


class StorageRepositoryNotFound(NotFound):
    msg_fmt = ("Cannot find SR to read/write VDI.")


class InstanceMappingNotFound(NotFound):
    msg_fmt = ("Instance %(uuid)s has no mapping to a cell.")


class NetworkDuplicated(Invalid):
    msg_fmt = ("Network %(network_id)s is duplicated.")


class NetworkDhcpReleaseFailed(NovaException):
    msg_fmt = ("Failed to release IP %(address)s with MAC %(mac_address)s")


class NetworkInUse(NovaException):
    msg_fmt = ("Network %(network_id)s is still in use.")


class NetworkSetHostFailed(NovaException):
    msg_fmt = ("Network set host failed for network %(network_id)s.")


class NetworkNotCreated(Invalid):
    msg_fmt = ("%(req)s is required to create a network.")


class LabelTooLong(Invalid):
    msg_fmt = ("Maximum allowed length for 'label' is 255.")


class InvalidIntValue(Invalid):
    msg_fmt = ("%(key)s must be an integer.")


class InvalidCidr(Invalid):
    msg_fmt = ("%(cidr)s is not a valid IP network.")


class InvalidAddress(Invalid):
    msg_fmt = ("%(address)s is not a valid IP address.")


class AddressOutOfRange(Invalid):
    msg_fmt = ("%(address)s is not within %(cidr)s.")


class DuplicateVlan(NovaException):
    msg_fmt = ("Detected existing vlan with id %(vlan)d")
    code = 409


class CidrConflict(NovaException):
    msg_fmt = ('Requested cidr (%(cidr)s) conflicts '
                'with existing cidr (%(other)s)')
    code = 409


class NetworkHasProject(NetworkInUse):
    msg_fmt = ('Network must be disassociated from project '
                '%(project_id)s before it can be deleted.')


class NetworkNotFound(NotFound):
    msg_fmt = ("Network %(network_id)s could not be found.")


class PortNotFound(NotFound):
    msg_fmt = ("Port id %(port_id)s could not be found.")


class NetworkNotFoundForBridge(NetworkNotFound):
    msg_fmt = ("Network could not be found for bridge %(bridge)s")


class NetworkNotFoundForUUID(NetworkNotFound):
    msg_fmt = ("Network could not be found for uuid %(uuid)s")


class NetworkNotFoundForCidr(NetworkNotFound):
    msg_fmt = ("Network could not be found with cidr %(cidr)s.")


class NetworkNotFoundForInstance(NetworkNotFound):
    msg_fmt = ("Network could not be found for instance %(instance_id)s.")


class NoNetworksFound(NotFound):
    msg_fmt = ("No networks defined.")


class NoMoreNetworks(NovaException):
    msg_fmt = ("No more available networks.")


class NetworkNotFoundForProject(NetworkNotFound):
    msg_fmt = ("Either network uuid %(network_uuid)s is not present or "
                "is not assigned to the project %(project_id)s.")


class NetworkAmbiguous(Invalid):
    msg_fmt = ("More than one possible network found. Specify "
                "network ID(s) to select which one(s) to connect to.")


class UnableToAutoAllocateNetwork(Invalid):
    msg_fmt = ('Unable to automatically allocate a network for project '
                '%(project_id)s')


class NetworkRequiresSubnet(Invalid):
    msg_fmt = ("Network %(network_uuid)s requires a subnet in order to boot"
                " instances on.")


class ExternalNetworkAttachForbidden(Forbidden):
    msg_fmt = ("It is not allowed to create an interface on "
                "external network %(network_uuid)s")


class NetworkMissingPhysicalNetwork(NovaException):
    msg_fmt = ("Physical network is missing for network %(network_uuid)s")


class VifDetailsMissingVhostuserSockPath(Invalid):
    msg_fmt = ("vhostuser_sock_path not present in vif_details"
                " for vif %(vif_id)s")


class VifDetailsMissingMacvtapParameters(Invalid):
    msg_fmt = ("Parameters %(missing_params)s not present in"
                " vif_details for vif %(vif_id)s. Check your Neutron"
                " configuration to validate that the macvtap parameters are"
                " correct.")


class OvsConfigurationFailure(NovaException):
    msg_fmt = ("OVS configuration failed with: %(inner_exception)s.")


class DatastoreNotFound(NotFound):
    msg_fmt = ("Could not find the datastore reference(s) which the VM uses.")


class PortInUse(Invalid):
    msg_fmt = ("Port %(port_id)s is still in use.")


class PortRequiresFixedIP(Invalid):
    msg_fmt = ("Port %(port_id)s requires a FixedIP in order to be used.")


class PortNotUsable(Invalid):
    msg_fmt = ("Port %(port_id)s not usable for instance %(instance)s.")


class PortNotUsableDNS(Invalid):
    msg_fmt = ("Port %(port_id)s not usable for instance %(instance)s. "
                "Value %(value)s assigned to dns_name attribute does not "
                "match instance's hostname %(hostname)s")


class PortNotFree(Invalid):
    msg_fmt = ("No free port available for instance %(instance)s.")


class PortBindingFailed(Invalid):
    msg_fmt = ("Binding failed for port %(port_id)s, please check neutron "
                "logs for more information.")


class FixedIpExists(NovaException):
    msg_fmt = ("Fixed IP %(address)s already exists.")


class FixedIpNotFound(NotFound):
    msg_fmt = ("No fixed IP associated with id %(id)s.")


class FixedIpNotFoundForAddress(FixedIpNotFound):
    msg_fmt = ("Fixed IP not found for address %(address)s.")


class FixedIpNotFoundForInstance(FixedIpNotFound):
    msg_fmt = ("Instance %(instance_uuid)s has zero fixed IPs.")


class FixedIpNotFoundForNetworkHost(FixedIpNotFound):
    msg_fmt = ("Network host %(host)s has zero fixed IPs "
                "in network %(network_id)s.")


class FixedIpNotFoundForSpecificInstance(FixedIpNotFound):
    msg_fmt = ("Instance %(instance_uuid)s doesn't have fixed IP '%(ip)s'.")


class FixedIpNotFoundForNetwork(FixedIpNotFound):
    msg_fmt = ("Fixed IP address (%(address)s) does not exist in "
                "network (%(network_uuid)s).")


class FixedIpAssociateFailed(NovaException):
    msg_fmt = ("Fixed IP associate failed for network: %(net)s.")


class FixedIpAlreadyInUse(NovaException):
    msg_fmt = ("Fixed IP address %(address)s is already in use on instance "
                "%(instance_uuid)s.")


class FixedIpAssociatedWithMultipleInstances(NovaException):
    msg_fmt = ("More than one instance is associated with fixed IP address "
                "'%(address)s'.")


class FixedIpInvalid(Invalid):
    msg_fmt = ("Fixed IP address %(address)s is invalid.")


class NoMoreFixedIps(NovaException):
    msg_fmt = ("No fixed IP addresses available for network: %(net)s")


class NoFixedIpsDefined(NotFound):
    msg_fmt = ("Zero fixed IPs could be found.")


class FloatingIpExists(NovaException):
    msg_fmt = ("Floating IP %(address)s already exists.")


class FloatingIpNotFound(NotFound):
    msg_fmt = ("Floating IP not found for ID %(id)s.")


class FloatingIpDNSExists(Invalid):
    msg_fmt = ("The DNS entry %(name)s already exists in domain %(domain)s.")


class FloatingIpNotFoundForAddress(FloatingIpNotFound):
    msg_fmt = ("Floating IP not found for address %(address)s.")


class FloatingIpNotFoundForHost(FloatingIpNotFound):
    msg_fmt = ("Floating IP not found for host %(host)s.")


class FloatingIpMultipleFoundForAddress(NovaException):
    msg_fmt = ("Multiple floating IPs are found for address %(address)s.")


class FloatingIpPoolNotFound(NotFound):
    msg_fmt = ("Floating IP pool not found.")
    safe = True


class NoMoreFloatingIps(FloatingIpNotFound):
    msg_fmt = ("Zero floating IPs available.")
    safe = True


class FloatingIpAssociated(NovaException):
    msg_fmt = ("Floating IP %(address)s is associated.")


class FloatingIpNotAssociated(NovaException):
    msg_fmt = ("Floating IP %(address)s is not associated.")


class NoFloatingIpsDefined(NotFound):
    msg_fmt = ("Zero floating IPs exist.")


class NoFloatingIpInterface(NotFound):
    msg_fmt = ("Interface %(interface)s not found.")


class FloatingIpAllocateFailed(NovaException):
    msg_fmt = ("Floating IP allocate failed.")


class FloatingIpAssociateFailed(NovaException):
    msg_fmt = ("Floating IP %(address)s association has failed.")


class FloatingIpBadRequest(Invalid):
    msg_fmt = ("The floating IP request failed with a BadRequest")


class CannotDisassociateAutoAssignedFloatingIP(NovaException):
    msg_fmt = ("Cannot disassociate auto assigned floating IP")


class KeypairNotFound(NotFound):
    msg_fmt = ("Keypair %(name)s not found for user %(user_id)s")


class ServiceNotFound(NotFound):
    msg_fmt = ("Service %(service_id)s could not be found.")


class ServiceBinaryExists(NovaException):
    msg_fmt = ("Service with host %(host)s binary %(binary)s exists.")


class ServiceTopicExists(NovaException):
    msg_fmt = ("Service with host %(host)s topic %(topic)s exists.")


class HostNotFound(NotFound):
    msg_fmt = ("Host %(host)s could not be found.")


class ComputeHostNotFound(HostNotFound):
    msg_fmt = ("Compute host %(host)s could not be found.")


class ComputeHostNotCreated(HostNotFound):
    msg_fmt = ("Compute host %(name)s needs to be created first"
                " before updating.")


class HostBinaryNotFound(NotFound):
    msg_fmt = ("Could not find binary %(binary)s on host %(host)s.")


class InvalidReservationExpiration(Invalid):
    msg_fmt = ("Invalid reservation expiration %(expire)s.")


class InvalidQuotaValue(Invalid):
    msg_fmt = ("Change would make usage less than 0 for the following "
                "resources: %(unders)s")


class InvalidQuotaMethodUsage(Invalid):
    msg_fmt = ("Wrong quota method %(method)s used on resource %(res)s")


class QuotaNotFound(NotFound):
    msg_fmt = ("Quota could not be found")


class QuotaExists(NovaException):
    msg_fmt = ("Quota exists for project %(project_id)s, "
                "resource %(resource)s")


class QuotaResourceUnknown(QuotaNotFound):
    msg_fmt = ("Unknown quota resources %(unknown)s.")


class ProjectUserQuotaNotFound(QuotaNotFound):
    msg_fmt = ("Quota for user %(user_id)s in project %(project_id)s "
                "could not be found.")


class ProjectQuotaNotFound(QuotaNotFound):
    msg_fmt = ("Quota for project %(project_id)s could not be found.")


class QuotaClassNotFound(QuotaNotFound):
    msg_fmt = ("Quota class %(class_name)s could not be found.")


class QuotaUsageNotFound(QuotaNotFound):
    msg_fmt = ("Quota usage for project %(project_id)s could not be found.")


class ReservationNotFound(QuotaNotFound):
    msg_fmt = ("Quota reservation %(uuid)s could not be found.")


class OverQuota(NovaException):
    msg_fmt = ("Quota exceeded for resources: %(overs)s")


class SecurityGroupNotFound(NotFound):
    msg_fmt = ("Security group %(security_group_id)s not found.")


class SecurityGroupNotFoundForProject(SecurityGroupNotFound):
    msg_fmt = ("Security group %(security_group_id)s not found "
                "for project %(project_id)s.")


class SecurityGroupNotFoundForRule(SecurityGroupNotFound):
    msg_fmt = ("Security group with rule %(rule_id)s not found.")


class SecurityGroupExists(Invalid):
    msg_fmt = ("Security group %(security_group_name)s already exists "
                "for project %(project_id)s.")


class SecurityGroupExistsForInstance(Invalid):
    msg_fmt = ("Security group %(security_group_id)s is already associated"
                " with the instance %(instance_id)s")


class SecurityGroupNotExistsForInstance(Invalid):
    msg_fmt = ("Security group %(security_group_id)s is not associated with"
                " the instance %(instance_id)s")


class SecurityGroupDefaultRuleNotFound(Invalid):
    msg_fmt = ("Security group default rule (%rule_id)s not found.")


class SecurityGroupCannotBeApplied(Invalid):
    msg_fmt = ("Network requires port_security_enabled and subnet associated"
                " in order to apply security groups.")


class SecurityGroupRuleExists(Invalid):
    msg_fmt = ("Rule already exists in group: %(rule)s")


class NoUniqueMatch(NovaException):
    msg_fmt = ("No Unique Match Found.")
    code = 409


class NoActiveMigrationForInstance(NotFound):
    msg_fmt = ("Active live migration for instance %(instance_id)s not found")


class MigrationNotFound(NotFound):
    msg_fmt = ("Migration %(migration_id)s could not be found.")


class MigrationNotFoundByStatus(MigrationNotFound):
    msg_fmt = ("Migration not found for instance %(instance_id)s "
                "with status %(status)s.")


class MigrationNotFoundForInstance(MigrationNotFound):
    msg_fmt = ("Migration %(migration_id)s not found for instance "
                "%(instance_id)s")


class InvalidMigrationState(Invalid):
    msg_fmt = ("Migration %(migration_id)s state of instance "
                "%(instance_uuid)s is %(state)s. Cannot %(method)s while the "
                "migration is in this state.")


class ConsoleLogOutputException(NovaException):
    msg_fmt = ("Console log output could not be retrieved for instance "
                "%(instance_id)s. Reason: %(reason)s")


class ConsolePoolNotFound(NotFound):
    msg_fmt = ("Console pool %(pool_id)s could not be found.")


class ConsolePoolExists(NovaException):
    msg_fmt = ("Console pool with host %(host)s, console_type "
                "%(console_type)s and compute_host %(compute_host)s "
                "already exists.")


class ConsolePoolNotFoundForHostType(NotFound):
    msg_fmt = ("Console pool of type %(console_type)s "
                "for compute host %(compute_host)s "
                "on proxy host %(host)s not found.")


class ConsoleNotFound(NotFound):
    msg_fmt = ("Console %(console_id)s could not be found.")


class ConsoleNotFoundForInstance(ConsoleNotFound):
    msg_fmt = ("Console for instance %(instance_uuid)s could not be found.")


class ConsoleNotAvailable(NotFound):
    msg_fmt = ("Guest does not have a console available.")


class ConsoleNotFoundInPoolForInstance(ConsoleNotFound):
    msg_fmt = ("Console for instance %(instance_uuid)s "
                "in pool %(pool_id)s could not be found.")


class ConsoleTypeInvalid(Invalid):
    msg_fmt = ("Invalid console type %(console_type)s")


class ConsoleTypeUnavailable(Invalid):
    msg_fmt = ("Unavailable console type %(console_type)s.")


class ConsolePortRangeExhausted(NovaException):
    msg_fmt = ("The console port range %(min_port)d-%(max_port)d is "
                "exhausted.")


class FlavorNotFound(NotFound):
    msg_fmt = ("Flavor %(flavor_id)s could not be found.")


class FlavorNotFoundByName(FlavorNotFound):
    msg_fmt = ("Flavor with name %(flavor_name)s could not be found.")


class FlavorAccessNotFound(NotFound):
    msg_fmt = ("Flavor access not found for %(flavor_id)s / "
                "%(project_id)s combination.")


class FlavorExtraSpecUpdateCreateFailed(NovaException):
    msg_fmt = ("Flavor %(id)s extra spec cannot be updated or created "
                "after %(retries)d retries.")


class CellNotFound(NotFound):
    msg_fmt = ("Cell %(cell_name)s doesn't exist.")


class CellExists(NovaException):
    msg_fmt = ("Cell with name %(name)s already exists.")


class CellRoutingInconsistency(NovaException):
    msg_fmt = ("Inconsistency in cell routing: %(reason)s")


class CellServiceAPIMethodNotFound(NotFound):
    msg_fmt = ("Service API method not found: %(detail)s")


class CellTimeout(NotFound):
    msg_fmt = ("Timeout waiting for response from cell")


class CellMaxHopCountReached(NovaException):
    msg_fmt = ("Cell message has reached maximum hop count: %(hop_count)s")


class NoCellsAvailable(NovaException):
    msg_fmt = ("No cells available matching scheduling criteria.")


class CellsUpdateUnsupported(NovaException):
    msg_fmt = ("Cannot update cells configuration file.")


class InstanceUnknownCell(NotFound):
    msg_fmt = ("Cell is not known for instance %(instance_uuid)s")


class SchedulerHostFilterNotFound(NotFound):
    msg_fmt = ("Scheduler Host Filter %(filter_name)s could not be found.")


class FlavorExtraSpecsNotFound(NotFound):
    msg_fmt = ("Flavor %(flavor_id)s has no extra specs with "
                "key %(extra_specs_key)s.")


class ComputeHostMetricNotFound(NotFound):
    msg_fmt = ("Metric %(name)s could not be found on the compute "
                "host node %(host)s.%(node)s.")


class FileNotFound(NotFound):
    msg_fmt = ("File %(file_path)s could not be found.")


class SwitchNotFoundForNetworkAdapter(NotFound):
    msg_fmt = ("Virtual switch associated with the "
                "network adapter %(adapter)s not found.")


class NetworkAdapterNotFound(NotFound):
    msg_fmt = ("Network adapter %(adapter)s could not be found.")


class ClassNotFound(NotFound):
    msg_fmt = ("Class %(class_name)s could not be found: %(exception)s")


class InstanceTagNotFound(NotFound):
    msg_fmt = ("Instance %(instance_id)s has no tag '%(tag)s'")


class RotationRequiredForBackup(NovaException):
    msg_fmt = ("Rotation param is required for backup image_type")


class KeyPairExists(NovaException):
    msg_fmt = ("Key pair '%(key_name)s' already exists.")


class InstanceExists(NovaException):
    msg_fmt = ("Instance %(name)s already exists.")


class FlavorExists(NovaException):
    msg_fmt = ("Flavor with name %(name)s already exists.")


class FlavorIdExists(NovaException):
    msg_fmt = ("Flavor with ID %(flavor_id)s already exists.")


class FlavorAccessExists(NovaException):
    msg_fmt = ("Flavor access already exists for flavor %(flavor_id)s "
                "and project %(project_id)s combination.")


class InvalidSharedStorage(NovaException):
    msg_fmt = ("%(path)s is not on shared storage: %(reason)s")


class InvalidLocalStorage(NovaException):
    msg_fmt = ("%(path)s is not on local storage: %(reason)s")


class StorageError(NovaException):
    msg_fmt = ("Storage error: %(reason)s")


class MigrationError(NovaException):
    msg_fmt = ("Migration error: %(reason)s")


class MigrationPreCheckError(MigrationError):
    msg_fmt = ("Migration pre-check error: %(reason)s")


class MigrationPreCheckClientException(MigrationError):
    msg_fmt = ("Client exception during Migration Pre check: %(reason)s")


class MigrationSchedulerRPCError(MigrationError):
    msg_fmt = ("Migration select destinations error: %(reason)s")


class MalformedRequestBody(NovaException):
    msg_fmt = ("Malformed message body: %(reason)s")


# NOTE(johannes): NotFound should only be used when a 404 error is
# appropriate to be returned
class ConfigNotFound(NovaException):
    msg_fmt = ("Could not find config at %(path)s")


class PasteAppNotFound(NovaException):
    msg_fmt = ("Could not load paste app '%(name)s' from %(path)s")


class CannotResizeToSameFlavor(NovaException):
    msg_fmt = ("When resizing, instances must change flavor!")


class ResizeError(NovaException):
    msg_fmt = ("Resize error: %(reason)s")


class CannotResizeDisk(NovaException):
    msg_fmt = ("Server disk was unable to be resized because: %(reason)s")


class FlavorMemoryTooSmall(NovaException):
    msg_fmt = ("Flavor's memory is too small for requested image.")


class FlavorDiskTooSmall(NovaException):
    msg_fmt = ("The created instance's disk would be too small.")


class FlavorDiskSmallerThanImage(FlavorDiskTooSmall):
    msg_fmt = ("Flavor's disk is too small for requested image. Flavor disk "
                "is %(flavor_size)i bytes, image is %(image_size)i bytes.")


class FlavorDiskSmallerThanMinDisk(FlavorDiskTooSmall):
    msg_fmt = ("Flavor's disk is smaller than the minimum size specified in "
                "image metadata. Flavor disk is %(flavor_size)i bytes, "
                "minimum size is %(image_min_disk)i bytes.")


class VolumeSmallerThanMinDisk(FlavorDiskTooSmall):
    msg_fmt = ("Volume is smaller than the minimum size specified in image "
                "metadata. Volume size is %(volume_size)i bytes, minimum "
                "size is %(image_min_disk)i bytes.")


class InsufficientFreeMemory(NovaException):
    msg_fmt = ("Insufficient free memory on compute node to start %(uuid)s.")


class NoValidHost(NovaException):
    msg_fmt = ("No valid host was found. %(reason)s")


class MaxRetriesExceeded(NoValidHost):
    msg_fmt = ("Exceeded maximum number of retries. %(reason)s")


class QuotaError(NovaException):
    msg_fmt = ("Quota exceeded: code=%(code)s")
    # NOTE(cyeoh): 413 should only be used for the ec2 API
    # The error status code for out of quota for the nova api should be
    # 403 Forbidden.
    code = 413
    safe = True


class TooManyInstances(QuotaError):
    msg_fmt = ("Quota exceeded for %(overs)s: Requested %(req)s,"
                " but already used %(used)s of %(allowed)s %(overs)s")


class FloatingIpLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of floating IPs exceeded")


class FixedIpLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of fixed IPs exceeded")


class MetadataLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of metadata items exceeds %(allowed)d")


class OnsetFileLimitExceeded(QuotaError):
    msg_fmt = ("Personality file limit exceeded")


class OnsetFilePathLimitExceeded(OnsetFileLimitExceeded):
    msg_fmt = ("Personality file path too long")


class OnsetFileContentLimitExceeded(OnsetFileLimitExceeded):
    msg_fmt = ("Personality file content too long")


class KeypairLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of key pairs exceeded")


class SecurityGroupLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of security groups or rules exceeded")


class PortLimitExceeded(QuotaError):
    msg_fmt = ("Maximum number of ports exceeded")


class AggregateError(NovaException):
    msg_fmt = ("Aggregate %(aggregate_id)s: action '%(action)s' "
                "caused an error: %(reason)s.")


class AggregateNotFound(NotFound):
    msg_fmt = ("Aggregate %(aggregate_id)s could not be found.")


class AggregateNameExists(NovaException):
    msg_fmt = ("Aggregate %(aggregate_name)s already exists.")


class AggregateHostNotFound(NotFound):
    msg_fmt = ("Aggregate %(aggregate_id)s has no host %(host)s.")


class AggregateMetadataNotFound(NotFound):
    msg_fmt = ("Aggregate %(aggregate_id)s has no metadata with "
                "key %(metadata_key)s.")


class AggregateHostExists(NovaException):
    msg_fmt = ("Aggregate %(aggregate_id)s already has host %(host)s.")


class InstancePasswordSetFailed(NovaException):
    msg_fmt = ("Failed to set admin password on %(instance)s "
                "because %(reason)s")
    safe = True


class InstanceNotFound(NotFound):
    msg_fmt = ("Instance %(instance_id)s could not be found.")


class InstanceInfoCacheNotFound(NotFound):
    msg_fmt = ("Info cache for instance %(instance_uuid)s could not be "
                "found.")


class InvalidAssociation(NotFound):
    msg_fmt = ("Invalid association.")


class MarkerNotFound(NotFound):
    msg_fmt = ("Marker %(marker)s could not be found.")


class InvalidInstanceIDMalformed(Invalid):
    msg_fmt = ("Invalid id: %(instance_id)s (expecting \"i-...\")")


class InvalidVolumeIDMalformed(Invalid):
    msg_fmt = ("Invalid id: %(volume_id)s (expecting \"i-...\")")


class CouldNotFetchImage(NovaException):
    msg_fmt = ("Could not fetch image %(image_id)s")


class CouldNotUploadImage(NovaException):
    msg_fmt = ("Could not upload image %(image_id)s")


class TaskAlreadyRunning(NovaException):
    msg_fmt = ("Task %(task_name)s is already running on host %(host)s")


class TaskNotRunning(NovaException):
    msg_fmt = ("Task %(task_name)s is not running on host %(host)s")


class InstanceIsLocked(InstanceInvalidState):
    msg_fmt = ("Instance %(instance_uuid)s is locked")


class ConfigDriveInvalidValue(Invalid):
    msg_fmt = ("Invalid value for Config Drive option: %(option)s")


class ConfigDriveUnsupportedFormat(Invalid):
    msg_fmt = ("Config drive format '%(format)s' is not supported.")


class ConfigDriveMountFailed(NovaException):
    msg_fmt = ("Could not mount vfat config drive. %(operation)s failed. "
                "Error: %(error)s")


class ConfigDriveUnknownFormat(NovaException):
    msg_fmt = ("Unknown config drive format %(format)s. Select one of "
                "iso9660 or vfat.")


class ConfigDriveNotFound(NotFound):
    msg_fmt = ("Instance %(instance_uuid)s requires config drive, but it "
                "does not exist.")


class InterfaceAttachFailed(Invalid):
    msg_fmt = ("Failed to attach network adapter device to "
                "%(instance_uuid)s")


class InterfaceAttachFailedNoNetwork(InterfaceAttachFailed):
    msg_fmt = ("No specific network was requested and none are available "
                "for project '%(project_id)s'.")


class InterfaceDetachFailed(Invalid):
    msg_fmt = ("Failed to detach network adapter device from "
                "%(instance_uuid)s")


class InstanceUserDataTooLarge(NovaException):
    msg_fmt = ("User data too large. User data must be no larger than "
                "%(maxsize)s bytes once base64 encoded. Your data is "
                "%(length)d bytes")


class InstanceUserDataMalformed(NovaException):
    msg_fmt = ("User data needs to be valid base 64.")


class InstanceUpdateConflict(NovaException):
    msg_fmt = ("Conflict updating instance %(instance_uuid)s. "
                "Expected: %(expected)s. Actual: %(actual)s")


class UnknownInstanceUpdateConflict(InstanceUpdateConflict):
    msg_fmt = ("Conflict updating instance %(instance_uuid)s, but we were "
                "unable to determine the cause")


class UnexpectedTaskStateError(InstanceUpdateConflict):
    pass


class UnexpectedDeletingTaskStateError(UnexpectedTaskStateError):
    pass


class InstanceActionNotFound(NovaException):
    msg_fmt = ("Action for request_id %(request_id)s on instance"
                " %(instance_uuid)s not found")


class InstanceActionEventNotFound(NovaException):
    msg_fmt = ("Event %(event)s not found for action id %(action_id)s")


class CryptoCAFileNotFound(FileNotFound):
    msg_fmt = ("The CA file for %(project)s could not be found")


class CryptoCRLFileNotFound(FileNotFound):
    msg_fmt = ("The CRL file for %(project)s could not be found")


class InstanceRecreateNotSupported(Invalid):
    msg_fmt = ('Instance recreate is not supported.')


class DBNotAllowed(NovaException):
    msg_fmt = ('%(binary)s attempted direct database access which is '
                'not allowed by policy')


class UnsupportedVirtType(Invalid):
    msg_fmt = ("Virtualization type '%(virt)s' is not supported by "
                "this compute driver")


class UnsupportedHardware(Invalid):
    msg_fmt = ("Requested hardware '%(model)s' is not supported by "
                "the '%(virt)s' virt driver")


class Base64Exception(NovaException):
    msg_fmt = ("Invalid Base 64 data for file %(path)s")


class BuildAbortException(NovaException):
    msg_fmt = ("Build of instance %(instance_uuid)s aborted: %(reason)s")


class RescheduledException(NovaException):
    msg_fmt = ("Build of instance %(instance_uuid)s was re-scheduled: "
                "%(reason)s")


class ShadowTableExists(NovaException):
    msg_fmt = ("Shadow table with name %(name)s already exists.")


class InstanceFaultRollback(NovaException):
    def __init_(self, inner_exception=None):
        message = ("Instance rollback performed due to: %s")
        self.inner_exception = inner_exception
        super(InstanceFaultRollback, self).__init_(message % inner_exception)


class OrphanedObjectError(NovaException):
    msg_fmt = ('Cannot call %(method)s on orphaned %(objtype)s object')


class ObjectActionError(NovaException):
    msg_fmt = ('Object action %(action)s failed because: %(reason)s')


class CoreAPIMissing(NovaException):
    msg_fmt = ("Core API extensions are missing: %(missing_apis)s")


class AgentError(NovaException):
    msg_fmt = ('Error during following call to agent: %(method)s')


class AgentTimeout(AgentError):
    msg_fmt = ('Unable to contact guest agent. '
                'The following call timed out: %(method)s')


class AgentNotImplemented(AgentError):
    msg_fmt = ('Agent does not support the call: %(method)s')


class InstanceGroupNotFound(NotFound):
    msg_fmt = ("Instance group %(group_uuid)s could not be found.")


class InstanceGroupIdExists(NovaException):
    msg_fmt = ("Instance group %(group_uuid)s already exists.")


class InstanceGroupMemberNotFound(NotFound):
    msg_fmt = ("Instance group %(group_uuid)s has no member with "
                "id %(instance_id)s.")


class InstanceGroupPolicyNotFound(NotFound):
    msg_fmt = ("Instance group %(group_uuid)s has no policy %(policy)s.")


class InstanceGroupSaveException(NovaException):
    msg_fmt = ("%(field)s should not be part of the updates.")


class PluginRetriesExceeded(NovaException):
    msg_fmt = ("Number of retries to plugin (%(num_retries)d) exceeded.")


class ImageDownloadModuleError(NovaException):
    msg_fmt = ("There was an error with the download module %(module)s. "
                "%(reason)s")


class ImageDownloadModuleMetaDataError(ImageDownloadModuleError):
    msg_fmt = ("The metadata for this location will not work with this "
                "module %(module)s.  %(reason)s.")


class ImageDownloadModuleNotImplementedError(ImageDownloadModuleError):
    msg_fmt = ("The method %(method_name)s is not implemented.")


class ImageDownloadModuleConfigurationError(ImageDownloadModuleError):
    msg_fmt = ("The module %(module)s is misconfigured: %(reason)s.")


class SignatureVerificationError(NovaException):
    msg_fmt = ("Signature verification for the image "
                "failed: %(reason)s.")


class ResourceMonitorError(NovaException):
    msg_fmt = ("Error when creating resource monitor: %(monitor)s")


class PciDeviceWrongAddressFormat(NovaException):
    msg_fmt = ("The PCI address %(address)s has an incorrect format.")


class PciDeviceInvalidAddressField(NovaException):
    msg_fmt = ("Invalid PCI Whitelist: "
                "The PCI address %(address)s has an invalid %(field)s.")


class PciDeviceInvalidDeviceName(NovaException):
    msg_fmt = ("Invalid PCI Whitelist: "
                "The PCI whitelist can specify devname or address,"
                " but not both")


class PciDeviceNotFoundById(NotFound):
    msg_fmt = ("PCI device %(id)s not found")


class PciDeviceNotFound(NotFound):
    msg_fmt = ("PCI Device %(node_id)s:%(address)s not found.")


class PciDeviceInvalidStatus(Invalid):
    msg_fmt = (
        "PCI device %(compute_node_id)s:%(address)s is %(status)s "
        "instead of %(hopestatus)s")


class PciDeviceVFInvalidStatus(Invalid):
    msg_fmt = (
        "Not all Virtual Functions of PF %(compute_node_id)s:%(address)s "
        "are free.")


class PciDevicePFInvalidStatus(Invalid):
    msg_fmt = (
        "Physical Function %(compute_node_id)s:%(address)s, related to VF"
        " %(compute_node_id)s:%(vf_address)s is %(status)s "
        "instead of %(hopestatus)s")


class PciDeviceInvalidOwner(Invalid):
    msg_fmt = (
        "PCI device %(compute_node_id)s:%(address)s is owned by %(owner)s "
        "instead of %(hopeowner)s")


class PciDeviceRequestFailed(NovaException):
    msg_fmt = (
        "PCI device request %(requests)s failed")


class PciDevicePoolEmpty(NovaException):
    msg_fmt = (
        "Attempt to consume PCI device %(compute_node_id)s:%(address)s "
        "from empty pool")


class PciInvalidAlias(Invalid):
    msg_fmt = ("Invalid PCI alias definition: %(reason)s")


class PciRequestAliasNotDefined(NovaException):
    msg_fmt = ("PCI alias %(alias)s is not defined")


class MissingParameter(NovaException):
    msg_fmt = ("Not enough parameters: %(reason)s")
    code = 400


class PciConfigInvalidWhitelist(Invalid):
    msg_fmt = ("Invalid PCI devices Whitelist config %(reason)s")


# Cannot be templated, msg needs to be constructed when raised.
class InternalError(NovaException):
    msg_fmt = "%(err)s"


class PciDevicePrepareFailed(NovaException):
    msg_fmt = ("Failed to prepare PCI device %(id)s for instance "
                "%(instance_uuid)s: %(reason)s")


class PciDeviceDetachFailed(NovaException):
    msg_fmt = ("Failed to detach PCI device %(dev)s: %(reason)s")


class PciDeviceUnsupportedHypervisor(NovaException):
    msg_fmt = ("%(type)s hypervisor does not support PCI devices")


class KeyManagerError(NovaException):
    msg_fmt = ("Key manager error: %(reason)s")


class VolumesNotRemoved(Invalid):
    msg_fmt = ("Failed to remove volume(s): (%(reason)s)")


class InvalidVideoMode(Invalid):
    msg_fmt = ("Provided video model (%(model)s) is not supported.")


class RngDeviceNotExist(Invalid):
    msg_fmt = ("The provided RNG device path: (%(path)s) is not "
                "present on the host.")


class RequestedVRamTooHigh(NovaException):
    msg_fmt = ("The requested amount of video memory %(req_vram)d is higher "
                "than the maximum allowed by flavor %(max_vram)d.")


class InvalidWatchdogAction(Invalid):
    msg_fmt = ("Provided watchdog action (%(action)s) is not supported.")


class NoLiveMigrationForConfigDriveInLibVirt(NovaException):
    msg_fmt = ("Live migration of instances with config drives is not "
                "supported in libvirt unless libvirt instance path and "
                "drive data is shared across compute nodes.")


class LiveMigrationWithOldNovaNotSupported(NovaException):
    msg_fmt = ("Live migration with API v2.25 requires all the Mitaka "
                "upgrade to be complete before it is available.")


class LiveMigrationURINotAvailable(NovaException):
    msg_fmt = ('No live migration URI configured and no default available '
                'for "%(virt_type)s" hypervisor virtualization type.')


class UnshelveException(NovaException):
    msg_fmt = ("Error during unshelve instance %(instance_id)s: %(reason)s")


class ImageVCPULimitsRangeExceeded(Invalid):
    msg_fmt = ("Image vCPU limits %(sockets)d:%(cores)d:%(threads)d "
                "exceeds permitted %(maxsockets)d:%(maxcores)d:%(maxthreads)d")


class ImageVCPUTopologyRangeExceeded(Invalid):
    msg_fmt = ("Image vCPU topology %(sockets)d:%(cores)d:%(threads)d "
                "exceeds permitted %(maxsockets)d:%(maxcores)d:%(maxthreads)d")


class ImageVCPULimitsRangeImpossible(Invalid):
    msg_fmt = ("Requested vCPU limits %(sockets)d:%(cores)d:%(threads)d "
                "are impossible to satisfy for vcpus count %(vcpus)d")


class InvalidArchitectureName(Invalid):
    msg_fmt = ("Architecture name '%(arch)s' is not recognised")


class ImageNUMATopologyIncomplete(Invalid):
    msg_fmt = ("CPU and memory allocation must be provided for all "
                "NUMA nodes")


class ImageNUMATopologyForbidden(Forbidden):
    msg_fmt = ("Image property '%(name)s' is not permitted to override "
                "NUMA configuration set against the flavor")


class ImageNUMATopologyAsymmetric(Invalid):
    msg_fmt = ("Asymmetric NUMA topologies require explicit assignment "
                "of CPUs and memory to nodes in image or flavor")


class ImageNUMATopologyCPUOutOfRange(Invalid):
    msg_fmt = ("CPU number %(cpunum)d is larger than max %(cpumax)d")


class ImageNUMATopologyCPUDuplicates(Invalid):
    msg_fmt = ("CPU number %(cpunum)d is assigned to two nodes")


class ImageNUMATopologyCPUsUnassigned(Invalid):
    msg_fmt = ("CPU number %(cpuset)s is not assigned to any node")


class ImageNUMATopologyMemoryOutOfRange(Invalid):
    msg_fmt = ("%(memsize)d MB of memory assigned, but expected "
                "%(memtotal)d MB")


class InvalidHostname(Invalid):
    msg_fmt = ("Invalid characters in hostname '%(hostname)s'")


class NumaTopologyNotFound(NotFound):
    msg_fmt = ("Instance %(instance_uuid)s does not specify a NUMA topology")


class MigrationContextNotFound(NotFound):
    msg_fmt = ("Instance %(instance_uuid)s does not specify a migration "
                "context.")


class SocketPortRangeExhaustedException(NovaException):
    msg_fmt = ("Not able to acquire a free port for %(host)s")


class SocketPortInUseException(NovaException):
    msg_fmt = ("Not able to bind %(host)s:%(port)d, %(error)s")


class ImageSerialPortNumberInvalid(Invalid):
    msg_fmt = ("Number of serial ports '%(num_ports)s' specified in "
                "'%(property)s' isn't valid.")


class ImageSerialPortNumberExceedFlavorValue(Invalid):
    msg_fmt = ("Forbidden to exceed flavor value of number of serial "
                "ports passed in image meta.")


class SerialPortNumberLimitExceeded(Invalid):
    msg_fmt = ("Maximum number of serial port exceeds %(allowed)d "
                "for %(virt_type)s")


class InvalidImageConfigDrive(Invalid):
    msg_fmt = ("Image's config drive option '%(config_drive)s' is invalid")


class InvalidHypervisorVirtType(Invalid):
    msg_fmt = ("Hypervisor virtualization type '%(hv_type)s' is not "
                "recognised")


class InvalidVirtualMachineMode(Invalid):
    msg_fmt = ("Virtual machine mode '%(vmmode)s' is not recognised")


class InvalidToken(Invalid):
    msg_fmt = ("The token '%(token)s' is invalid or has expired")


class InvalidConnectionInfo(Invalid):
    msg_fmt = ("Invalid Connection Info")


class InstanceQuiesceNotSupported(Invalid):
    msg_fmt = ('Quiescing is not supported in instance %(instance_id)s')


class InstanceAgentNotEnabled(Invalid):
    msg_fmt = ('Guest agent is not enabled for the instance')
    safe = True


class QemuGuestAgentNotEnabled(InstanceAgentNotEnabled):
    msg_fmt = ('QEMU guest agent is not enabled')


class SetAdminPasswdNotSupported(Invalid):
    msg_fmt = ('Set admin password is not supported')
    safe = True


class MemoryPageSizeInvalid(Invalid):
    msg_fmt = ("Invalid memory page size '%(pagesize)s'")


class MemoryPageSizeForbidden(Invalid):
    msg_fmt = ("Page size %(pagesize)s forbidden against '%(against)s'")


class MemoryPageSizeNotSupported(Invalid):
    msg_fmt = ("Page size %(pagesize)s is not supported by the host.")


class CPUPinningNotSupported(Invalid):
    msg_fmt = ("CPU pinning is not supported by the host: "
                "%(reason)s")


class CPUPinningInvalid(Invalid):
    msg_fmt = ("Cannot pin/unpin cpus %(requested)s from the following "
                "pinned set %(pinned)s")


class CPUPinningUnknown(Invalid):
    msg_fmt = ("CPU set to pin/unpin %(requested)s must be a subset of "
                "known CPU set %(cpuset)s")


class ImageCPUPinningForbidden(Forbidden):
    msg_fmt = ("Image property 'hw_cpu_policy' is not permitted to override "
                "CPU pinning policy set against the flavor")


class ImageCPUThreadPolicyForbidden(Forbidden):
    msg_fmt = ("Image property 'hw_cpu_thread_policy' is not permitted to "
                "override CPU thread pinning policy set against the flavor")


class UnsupportedPolicyException(Invalid):
    msg_fmt = ("ServerGroup policy is not supported: %(reason)s")


class CellMappingNotFound(NotFound):
    msg_fmt = ("Cell %(uuid)s has no mapping.")


class NUMATopologyUnsupported(Invalid):
    msg_fmt = ("Host does not support guests with NUMA topology set")


class MemoryPagesUnsupported(Invalid):
    msg_fmt = ("Host does not support guests with custom memory page sizes")


class EnumFieldInvalid(Invalid):
    msg_fmt = ('%(typename)s in %(fieldname)s is not an instance of Enum')


class EnumFieldUnset(Invalid):
    msg_fmt = ('%(fieldname)s missing field type')


class InvalidImageFormat(Invalid):
    msg_fmt = ("Invalid image format '%(format)s'")


class UnsupportedImageModel(Invalid):
    msg_fmt = ("Image model '%(image)s' is not supported")


class HostMappingNotFound(Invalid):
    msg_fmt = ("Host '%(name)s' is not mapped to any cell")


class RealtimeConfigurationInvalid(Invalid):
    msg_fmt = ("Cannot set realtime policy in a non dedicated "
                "cpu pinning policy")


class CPUThreadPolicyConfigurationInvalid(Invalid):
    msg_fmt = ("Cannot set cpu thread pinning policy in a non dedicated "
                "cpu pinning policy")


class RequestSpecNotFound(NotFound):
    msg_fmt = ("RequestSpec not found for instance %(instance_uuid)s")


class UEFINotSupported(Invalid):
    msg_fmt = ("UEFI is not supported")


class TriggerCrashDumpNotSupported(Invalid):
    msg_fmt = ("Triggering crash dump is not supported")


class UnsupportedHostCPUControlPolicy(Invalid):
    msg_fmt = ("Requested CPU control policy not supported by host")


class LibguestfsCannotReadKernel(Invalid):
    msg_fmt = ("Libguestfs does not have permission to read host kernel.")


class RealtimePolicyNotSupported(Invalid):
    msg_fmt = ("Realtime policy not supported by hypervisor")


class RealtimeMaskNotFoundOrInvalid(Invalid):
    msg_fmt = ("Realtime policy needs vCPU(s) mask configured with at least "
                "1 RT vCPU and 1 ordinary vCPU. See hw:cpu_realtime_mask "
                "or hw_cpu_realtime_mask")


class OsInfoNotFound(NotFound):
    msg_fmt = ("No configuration information found for operating system "
                "%(os_name)s")


class BuildRequestNotFound(NotFound):
    msg_fmt = ("BuildRequest not found for instance %(uuid)s")


class AttachInterfaceNotSupported(Invalid):
    msg_fmt = ("Attaching interfaces is not supported for "
                "instance %(instance)s.")


class InvalidReservedMemoryPagesOption(Invalid):
    msg_fmt = ("The format of the option 'reserved_huge_pages' is invalid. "
                "(found '%(conf)s') Please refer to the nova "
                "config-reference.")


class ConcurrentUpdateDetected(NovaException):
    msg_fmt = ("Another thread concurrently updated the data. "
                "Please retry your update")


class UnsupportedPointerModelRequested(Invalid):
    msg_fmt = ("Pointer model '%(model)s' requested is not supported by "
                "host.")
