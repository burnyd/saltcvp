# -*- coding: utf-8 -*-
'''
CVPSALT
=======

This is a module for working with Arista networks Cloud vision portal using salt stack.

The module has multiple salt functions which will talk to the cloud vision api via the cvprac wrapper.

'''
#
# Copyright (c) 2019, Arista Networks AS-EMEA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, print_function, unicode_literals
from cvprac.cvp_client import CvpClient
import salt
import urllib3
import salt.utils
import salt.utils.itertools
import salt.utils.url
import salt.fileserver
from salt.utils.odict import OrderedDict

#disables url lib
urllib3.disable_warnings()

#Pull back a config that will exists inside of a pillar.  Please call this cvp.sls
#cvp.sls
#cvp:
#  server: x.x.x.x #Cvp server IP
#  username: cvpadmin
#  password: cvppassword

def config():
    config = __salt__['config.get']('cvp')
    if not config:
        #raise CommandExecutionError(
        #    'cvp execution module configuration could not be found'
        #)
	return (False, "Cannot find the execution module")
    return config

#create a dictionary out of the config
def config_dict():
    cvp_dict = {}
    cvp_dict['server'] = config().get('server')
    cvp_dict['username'] = config().get('username')
    cvp_dict['password'] = config().get('password')
    return cvp_dict

#Connect to CVP with cvprac
def connect_cvp():
    urllib3.disable_warnings()
    client = CvpClient()
    client.connect([config_dict()['server']], config_dict()['username'], config_dict()['password'])
    return client

#Config module

#The config function to add, delete or getconfig

'''
mode:
 add: adds a configlet to cvp
 delete: deletes a configlet from cvp
 getconfig: returns a dictionary of configlet information by name

Examples:
  How to add a configlet from a one line

  salt 'minion' cvpsalt.load_config mode='add'  configlet_name='vlans' configlet='vlan 2,3,4'

  Delete a configlet

  salt 'minion' cvpsalt.load_config mode='delte' configlet_name='vlans'

  Show the contents of a configlet

  salt 'minion' cvpsalt.load_config mode='getconfig' configlet_name='leaf-vlans'

'''

def load_config(mode=None, configlet_name=None, configlet=None, **kwargs):
    client = connect_cvp()
    if mode == 'add':
        add_configlet = client.api.add_configlet(configlet_name, configlet)
        return add_configlet + ' ' + ' created'
    if mode == 'delete':
        find_key = client.api.get_configlet_by_name(configlet_name)
        client.api.delete_configlet(configlet_name, find_key['key'])
        return 'configlet' + ' ' + configlet_name + 'have been deleted'
    if mode == 'getconfig':
        getconfig = client.api.get_configlet_by_name(configlet_name)
        return getconfig
    else:
        return "Please specify add, delete or show + configlet name"

#work in progress
def load_template(config_name, configlet):
    client = connect_cvp()
    files = __salt__['cp.get_file_str'](configlet)
    add = client.api.add_configlet(config_name, files)

#Work in progress
def add_config_to(mode=None, configlet_name=None, configlet=None, **kwargs):
