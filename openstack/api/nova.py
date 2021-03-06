#!/usr/bin/env python
# coding:utf8

from novaclient import client as nova_client
import urllib2
import json

#####
from django.conf import settings
from openstack.api.base import NovaBase
from openstack.api import keystone
from openstack import models as openstack_models
from one_finger import models as one_finger_models
from asset import models as asset_models


def host_list():
    data = host_data()
    hosts = []
    for item in data['services']:
        if item['host'] in hosts:
            continue
        else:
            hosts.append(item['host'])
    return hosts


def host_data():
    kc = keystone.KeyStone()
    # 获取keystone的服务的数据库对象
    service_obj = one_finger_models.OpenStackKeystoneService.objects.filter(
        name='nova')

    # pdb.set_trace()
    # 获取 service id
    service_id = service_obj.values()[0]['service_id']

    # 获取endpoint的对象
    endpoint_obj = one_finger_models.OpenStackKeyStoneEndpoint.objects.filter(
        service_id=service_id)

    # 获取URL
    url = endpoint_obj.values()[0][settings.ACCEPT_URL]
    # print url, self.tenant_id

    # 拼接url ：http://192.168.254.242:8774/v2/239667eee2124453b69309e9cefae142/os-services
    url = url % {'tenant_id': kc.tenant_id} + '/os-services'

    # print url
    request = urllib2.Request(url, headers={
            'X-Auth-Project-Id': kc.username,
            'Accept': 'application/json',
            'User-Agent': 'python-novaclient',
            'X-Auth-Token': kc.token,

            })
    data = json.loads(urllib2.urlopen(request, timeout=5).read())

    # 创建主机

    return data

def mgmt_api_status(host):
    kc = keystone.KeyStone()
    # 获取keystone的服务的数据库对象
    service_obj = one_finger_models.OpenStackKeystoneService.objects.filter(
        name='nova')

    # pdb.set_trace()
    # 获取 service id
    service_id = service_obj.values()[0]['service_id']

    # 获取endpoint的对象
    endpoint_obj = one_finger_models.OpenStackKeyStoneEndpoint.objects.filter(
        service_id=service_id)

    # 获取URL
    url = endpoint_obj.values()[0][settings.ACCEPT_URL]
    # print url, self.tenant_id

    # 拼接url ：http://192.168.254.242:8774/v2/xxxxxxxxxxxxxxxx/os-services
    url = 'http://%(host)s:8774/v2/%(tenant_id)s' % {
        'host': host,
        'tenant_id': kc.tenant_id}+'/os-services'

    # print url
    request = urllib2.Request(url, headers={
            'X-Auth-Project-Id': kc.username,
            'Accept': 'application/json',
            'User-Agent': 'python-novaclient',
            'X-Auth-Token': kc.token,
            })
    try:
        data = json.loads(urllib2.urlopen(request, timeout=5).read())
    except :
        return None

    return data



def host_db_list():
    return asset_models.Host.objects.all()


def link_hosts(data, ):
    pass



def nova_client(NovaBase):
    pass
    # c = nova_client.Client(2, request.user.username,
    #                        request.user.token.id,
    #                        project_id=request.user.tenant_id,
    #                        auth_url=base.url_for(request, 'compute'),
    #                        insecure=False,
    #                        cacert=None,
    #                        http_log_debug=settings.DEBUG)
    # c.client.auth_token = request.user.token.id
    # c.client.management_url = base.url_for(request, 'compute')
    # return c