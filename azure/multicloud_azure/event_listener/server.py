#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

from oslo_config import cfg
from oslo_log import log as logging
from i18n import _LI
import oslo_messaging
import ConfigParser
import json
import os
import requests
from multicloud_azure.pub.config.config import MR_ADDR
from multicloud_azure.pub.config.config import MR_PORT


LOG = logging.getLogger(__name__)


def prepare():

    product_name = "oslo_server"
    logging.register_options(cfg.CONF)
    logging.setup(cfg.CONF, product_name)


'''
below items must be added into vio nova.conf then restart nova services:
notification_driver=messaging
notification_topics= notifications_test
notify_on_state_change=vm_and_task_state
notify_on_any_change=True
instance_usage_audit=True
instance_usage_audit_period=hour
'''


def getConfig(section, key):

    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/listener.conf'
    config.read(path)
    return config.get(section, key)


class NotificationEndPoint():

    filter_rule = oslo_messaging.NotificationFilter(
            publisher_id='^compute.*')

    def info(self, ctxt, publisher_id, event_type, payload, metadata):

        VM_EVENTS = {
            'compute.instance.unpause.start',
            'compute.instance.pause.start',
            'compute.instance.power_off.start',
            'compute.instance.reboot.start',
            'compute.instance.create.start'
        }

        status = payload.get('state_description')
        if status != '' and event_type in VM_EVENTS:
            url = 'http://%s:%s/events/test' % (MR_ADDR, MR_PORT)
            headers = {'Content-type': 'application/json'}
            requests.post(url, json.dumps(payload), headers=headers)

        LOG.info(event_type)
        self.action(payload)

    def action(self, data):
        LOG.info(_LI(json.dumps(data)))


class Server(object):

    def __init__(self):
        self.topic = 'notifications_test'
        self.server = None
        prepare()


class NotificationServer(Server):

    def __init__(self):
        super(NotificationServer, self).__init__()
        # rabbit IP and password come from listener.conf
        url = 'rabbit://test:%s@%s:5672/' % (
            getConfig('Listener', 'rabbit_passwd'),
            getConfig('Listener', 'rabbit_ip')
            )
        self.transport = oslo_messaging.get_notification_transport(
            cfg.CONF,
            url=url)
        # The exchange must be the same as
        # control_exchange in transport setting in client.
        self.targets = [oslo_messaging.Target(
            topic=self.topic,
            exchange='nova')]
        self.endpoints = [NotificationEndPoint()]

    def start(self):
        LOG.info(_LI("Start Notification server..."))
        self.server = oslo_messaging.get_notification_listener(
            self.transport,
            self.targets,
            self.endpoints,
            executor='threading')
        self.server.start()
        self.server.wait()


if __name__ == '__main__':

    notification_server = NotificationServer()
    notification_server.start()
