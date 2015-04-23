#!/usr/bin/env python

BASE_URL = 'http://{host}/api/'

XML_APIS = {
  'monitoring_status' : 'monitoring/status',
  'monitoring_basic_settings': 'monitoring/traffic-statistics',
  'monitoring_check_notifications' :  'monitoring/check-notifications',
  'wlan_basic_settings' :  'wlan/basic-settings',
  'wlan_host_list' :  'wlan/host-list'
}

import requests
import urllib.parse

base_url = BASE_URL.format(host='192.168.1.1')
for api in XML_APIS:
    url = urllib.parse.urljoin(base_url, XML_APIS[api])
    r = requests.get(url)
    print('-----------------')
    print(api)
    print(r.text)
    print('-----------------')

