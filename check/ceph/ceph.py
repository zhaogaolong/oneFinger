#!/usr/bin/env python
# coding:utf8
from storage.ceph.api import ceph
from event.ceph import osd as event_osd, monitor as event_mon, \
    ceph as event_ceph

from storage import  models as storage_models


class Check():
    def __init__(self):
        self.models = storage_models
        self.cm = ceph.Ceph()
        # import pdb
        # pdb.set_trace()

    def start(self):
        self._check_mon()
        self._check_osd()
        self._check_ceph_status()

    def _check_mon(self):
        # 检查每一个mon
        online = self.cm.quorum_online()
        # print online
        for node, val in self.cm.mon_list().items():
            if not val['id'] in online:
                # 检查现在的状态和数据库状态是否一致
                self._update_mon_node_status(val['id'], 'down')
            else:
                self._update_mon_node_status(val['id'], 'up')

    def _update_mon_node_status(self, id, status):
        mon = self.models.CephMonitorStatus.objects.get(mon_id=id)
        if mon.status != status:
            mon.status = status
            mon.save()
            if status == 'up':
                event_mon.up(mon.host.hostname)
            elif status == 'down':
                event_mon.down(mon.host.hostname)

    def _check_osd(self):
        # 检查每一个osd
        for item, v in self.cm.osd_list().items():
            # 检查现在的状态和数据库状态是否一致
            # print item, v['status']
            self._update_osd_node_status(item, v['status'])

    def _update_osd_node_status(self, osd_name, status):
        osd = self.models.CephOsdStatus.objects.get(osd_name=osd_name)
        if osd.status != status:
            osd.status = status
            osd.save()
            if status == 'up':
                event_osd.up(osd.host.hostname)
            elif status == 'down':
                event_osd.down(osd.host.hostname)

    def _check_ceph_mon_status(self):
        # 检查整个ceph节点的mon
        mon_db_list = self.models.CephMonitorStatus.objects.all()
        status_list = []
        for mon in mon_db_list:
            # 取出每一个mon状态
            status_list.append(mon.status)

        if not self.models.CephStatus.objects.filter():
            dic = {
                'static': 'null',
                'monitor_status': 'null',
                'osd_status': 'null',
            }
            self.models.CephStatus(**dic)
        ceph_db_obj = self.models.CephStatus.objects.first()

        # 开始对比状态是否正常
        if len(status_list) == status_list.count('up'):
            # ceph_db_obj.monitor_status = 'up'
            self._update_ceph_cluster_status('monitor_status', ceph_db_obj,
                                             'up')
        elif len(status_list) > status_list.count('up') > 0:
            # ceph_db_obj.monitor_status = 'warning'
            self._update_ceph_cluster_status('monitor_status', ceph_db_obj,
                                             'warning')
        else:
            # ceph_db_obj.monitor_status = 'down'
            self._update_ceph_cluster_status('monitor_status', ceph_db_obj,
                                             'down')
        # ceph_db_obj.save()

    def _check_ceph_osd_status(self):
        # 检查整个ceph节点的osd
        osd_db_list = self.models.CephOsdStatus.objects.all()
        status_list = []

        for osd in osd_db_list:
            status_list.append(osd.status)
        ceph_db_obj = self.models.CephStatus.objects.first()
        if len(status_list) == status_list.count('up'):
            # ceph_db_obj.osd_status = 'up'
            self._update_ceph_cluster_status('osd_status', ceph_db_obj, 'up')

        elif len(status_list) > status_list.count('up') > 0:
            # ceph_db_obj.osd_status = 'warning'
            self._update_ceph_cluster_status('osd_status', ceph_db_obj,
                                             'warning')
        else:
            # ceph_db_obj.monitor_status = 'down'
            self._update_ceph_cluster_status('osd_status', ceph_db_obj,
                                             'down')
        # ceph_db_obj.save()

    def _check_ceph_status(self):
        # 检查整个ceph status
        if not self.models.CephStatus.objects.filter():
            dic = {
                'status': 'null',
                'monitor_status': 'null',
                'osd_status': 'null',
            }
            co = self.models.CephStatus(**dic)
            co.save()
        self._check_ceph_mon_status()
        self._check_ceph_osd_status()
        ceph_db_obj = self.models.CephStatus.objects.first()
        status = [
            ceph_db_obj.monitor_status,
            ceph_db_obj.osd_status,
        ]
        if 'down' in status:
            # ceph_db_obj.status = 'down'
            self._update_ceph_cluster_status('status', ceph_db_obj, 'down')

        elif 'warning' in status:
            #　ceph_db_obj.status = 'warning'
            self._update_ceph_cluster_status('status', ceph_db_obj,
                                             'warning')
        else:
            # ceph_db_obj.status = 'up'
            self._update_ceph_cluster_status('status', ceph_db_obj, 'up')
        # ceph_db_obj.save()

    def _update_ceph_cluster_status(self, item_name, item_obj, status):
        # 该条记录是更新整个ceph status table 的方法
        # print 'update item %s %s %s' % (item_name, item_obj, status)
        # 所以触发事件记录的时候不属于任何主机
        if getattr(item_obj, item_name) != status:
            setattr(item_obj, item_name, status)
            item_obj.save()
            if item_name == 'monitor_status':
                print 'start monitor log'
                getattr(event_mon, status)()
            elif item_name == 'osd_status':
                print 'start osd log'
                getattr(event_osd, status)()
            elif item_name == 'status':
                # 检查是否是ceph的状态主表
                print 'start ceph log'
                getattr(event_ceph, status)()



