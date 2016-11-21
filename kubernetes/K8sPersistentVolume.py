#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.md', which is part of this source code package.
#

import time

from kubernetes import K8sObject
from kubernetes.K8sExceptions import TimedOutException
from kubernetes.models.v1.PersistentVolume import PersistentVolume
from kubernetes.models.v1.Volume import Volume

READY_WAIT_TIMEOUT_SECONDS = 60


class K8sPersistentVolume(K8sObject):
    VALID_VOLUME_TYPES = filter(lambda x: x not in ['emptyDir', 'gitRepo', 'secret'], Volume.VOLUME_TYPES_TO_SOURCE_MAP.keys())

    def __init__(self, config=None, name=None, type=None):
        super(K8sPersistentVolume, self).__init__(config=config, name=name, obj_type='PersistentVolume')
        self._type = None
        self.model = PersistentVolume()
        self.name = name
        self.type = type

    # ------------------------------------------------------------------------------------- api calls

    def create(self):
        super(K8sPersistentVolume, self).create()
        self._wait_for_available()
        return self

    def get(self):
        self.model = PersistentVolume(model=self.get_model())
        return self

    def _wait_for_available(self):
        start_time = time.time()
        while not self.model.status.phase == 'Available':
            self.get()
            elapsed_time = time.time() - start_time
            if elapsed_time >= READY_WAIT_TIMEOUT_SECONDS:  # timeout
                raise TimedOutException(
                    "Timed out waiting on readiness of PersistentVolume: [ {} ]".format(self.name)
                )

    # ------------------------------------------------------------------------------------- name

    @property
    def name(self):
        return self.model.metadata.name

    @name.setter
    def name(self, name=None):
        self.model.metadata.name = name
        self.model.metadata.labels['name'] = name

    # ------------------------------------------------------------------------------------- type

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t=None):
        if t not in self.VALID_VOLUME_TYPES:
            raise SyntaxError('K8sPersistentVolume: type: [ {} ] is invalid.'.format(t))
        self._type = t
        setattr(self.model.spec, t, Volume.vol_type_to_source(t))

    # ------------------------------------------------------------------------------------- source

    @property
    def source(self):
        return getattr(self.model.spec, self._type, None)

    @source.setter
    def source(self, s=None):
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------- accessModes

    @property
    def access_modes(self):
        return self.model.spec.access_modes

    @access_modes.setter
    def access_modes(self, modes=None):
        self.model.spec.access_modes = modes

    # ------------------------------------------------------------------------------------- capacity

    @property
    def capacity(self):
        return self.model.spec.capacity

    @capacity.setter
    def capacity(self, cap=None):
        self.model.spec.capacity = cap

    # ------------------------------------------------------------------------------------- path (hostPath)

    @property
    def host_path(self):
        if not hasattr(self.source, 'path'):
            raise NotImplementedError()
        return self.source.path

    @host_path.setter
    def host_path(self, p=None):
        if not hasattr(self.source, 'path'):
            raise NotImplementedError()
        self.source.path = p

    # ------------------------------------------------------------------------------------- volume_id (AWS)

    # http://kubernetes.io/docs/user-guide/volumes/#awselasticblockstore
    # - the nodes on which pods are running must be AWS EC2 instances
    # - those instances need to be in the same region and availability-zone as the EBS volume
    # - EBS only supports a single EC2 instance mounting a volume

    # Pod creation will timeout waiting for readiness if not on AWS; unschedulable.

    @property
    def volume_id(self):
        if not hasattr(self.source, 'volume_id'):
            raise NotImplementedError()
        return self.source.volume_id

    @volume_id.setter
    def volume_id(self, vid=None):
        if not hasattr(self.source, 'volume_id'):
            raise NotImplementedError()
        self.source.volume_id = vid

    # ------------------------------------------------------------------------------------- pd_name (GCE)

    # http://kubernetes.io/docs/user-guide/volumes/#gcepersistentdisk
    # - the nodes on which pods are running must be GCE VMs
    # - those VMs need to be in the same GCE project and zone as the PD

    # Pod creation will timeout waiting for readiness if not on GCE; unschedulable.

    @property
    def pd_name(self):
        if not hasattr(self.source, 'pd_name'):
            raise NotImplementedError()
        return self.source.pd_name

    @pd_name.setter
    def pd_name(self, pd=None):
        if not hasattr(self.source, 'pd_name'):
            raise NotImplementedError()
        self.source.pd_name = pd

    # ------------------------------------------------------------------------------------- fs_type (AWS, GCE)

    @property
    def fs_type(self):
        if not hasattr(self.source, 'fs_type'):
            raise NotImplementedError()
        return self.source.fs_type

    @fs_type.setter
    def fs_type(self, t=None):
        if not hasattr(self.source, 'fs_type'):
            raise NotImplementedError()
        self.source.fs_type = t

    # ------------------------------------------------------------------------------------- nfs_server

    @property
    def nfs_server(self):
        if not hasattr(self.source, 'server'):
            raise NotImplementedError()
        return self.source.server

    @nfs_server.setter
    def nfs_server(self, s=None):
        if not hasattr(self.source, 'server'):
            raise NotImplementedError()
        self.source.server = s

    # ------------------------------------------------------------------------------------- nfs_path

    @property
    def nfs_path(self):
        if not hasattr(self.source, 'path'):
            raise NotImplementedError()
        return self.source.path

    @nfs_path.setter
    def nfs_path(self, p=None):
        if not hasattr(self.source, 'path'):
            raise NotImplementedError()
        self.source.path = p