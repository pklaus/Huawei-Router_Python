#!/usr/bin/env python

import requests
import xml.dom.minidom, urllib.parse, sys

class HuaweiE5332(object):

    BASE_URL = 'http://{host}/api/'

    XML_APIS = {
      'device_information'             : {'type': 'flat', 'url': 'device/information'}, # IMEI, MAC, etc
      'monitoring_status'              : {'type': 'flat', 'url': 'monitoring/status'},
      'monitoring_basic_settings'      : {'type': 'flat', 'url': 'monitoring/traffic-statistics'},
      'monitoring_check_notifications' : {'type': 'flat', 'url': 'monitoring/check-notifications'},
      'wlan_basic_settings'            : {'type': 'flat', 'url': 'wlan/basic-settings'},
      'wlan_host_list'                 : {'type': 'tree', 'url': 'wlan/host-list'}, # connected wireless clients
      'wlan_wps'                       : {'type': 'flat', 'url': 'wlan/wps'}, # WPS pin
      'security_dmz'                   : {'type': 'flat', 'url': 'security/dmz'}, # DMZ host settings
      'pin_simlock'                    : {'type': 'flat', 'url': 'pin/simlock'}, # enable SIM lock
    }
    API_ORDER = [
      'device_information',
      'monitoring_status',
      'monitoring_basic_settings',
      'monitoring_check_notifications',
      'wlan_basic_settings',
      'wlan_host_list',
      'wlan_wps',
      'security_dmz',
      'pin_simlock',
    ]

    def __init__(self, host='192.168.1.1'):
        self.host = host
        self.base_url = self.BASE_URL.format(host=host)

    def wlan_host_list(self):
        host_list = []
        api = self.XML_APIS['wlan_host_list']
        url = urllib.parse.urljoin(self.base_url, api['url'])
        r = requests.get(url)
        dom = xml.dom.minidom.parseString(r.text)
        dom.getElementsByTagName("response")[0]
        hosts = dom.getElementsByTagName("Hosts")[0]
        for host in hosts.childNodes:
            if type(host) is not xml.dom.minidom.Element: continue
            host_dict = {}
            for prop in host.childNodes:
                if type(prop) is not xml.dom.minidom.Element: continue
                prop, val = prop.tagName, prop.firstChild.data if prop.firstChild is not None else None
                host_dict[prop] = val
            host_list.append(host_dict)
        return host_list

    def flat_properties(self):
        properties = []
        flat_apis = [api for api in self.API_ORDER if self.XML_APIS[api]['type'] == 'flat']
        for api in flat_apis:
            url = urllib.parse.urljoin(self.base_url, self.XML_APIS[api]['url'])
            r = requests.get(url)
            dom = xml.dom.minidom.parseString(r.text)
            response = dom.getElementsByTagName("response")[0]
            for cn in response.childNodes:
                if type(cn) is not xml.dom.minidom.Element: continue
                prop, val = cn.tagName, cn.firstChild.data if cn.firstChild is not None else None
                properties.append((api + '_' + prop, val))
        for host in self.wlan_host_list():
            hid = host['ID']
            for key in host:
                properties.append(('wlan_host_list' + '_' + hid + '_' + key, host[key]))
        return properties
        

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch all kinds of status information from the Huawei E5332 UMTS Hotspot.')
    parser.add_argument('host', nargs='?', default='192.168.1.1', help='The hostname / IP address your E5332 is reachable at')
    
    args = parser.parse_args()
    e5332 = HuaweiE5332(host=args.host)
    fp = e5332.flat_properties()
    for pv in fp:
        print("{}: {}".format(*pv))

if __name__ == "__main__":
    main()
