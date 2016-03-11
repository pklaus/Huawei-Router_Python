#!/usr/bin/env python

import xml.dom.minidom, urllib.request, urllib.parse, http.cookiejar, sys, pprint

class HuaweiE5332(object):

    HOME_URL = 'http://{host}'
    BASE_URL = 'http://{host}/api/'

    XML_APIS = [
      {'name': 'device_information',            'kind': 'flat',  'url': '/api/device/information'}, # IMEI, MAC, etc
      {'name': 'global_module_switch',          'kind': 'flat',  'url': '/api/global/module-switch'},
      {'name': 'monitoring_status',             'kind': 'flat',  'url': '/api/monitoring/status'},
      {'name': 'monitoring_converged_status',   'kind': 'flat',  'url': '/api/monitoring/converged-status'},
      {'name': 'monitoring_traffic_statistics', 'kind': 'flat',  'url': '/api/monitoring/traffic-statistics'},
      {'name': 'monitoring_check_notifications','kind': 'flat',  'url': '/api/monitoring/check-notifications'},
      {'name': 'dialup_connection',             'kind': 'flat',  'url': '/api/dialup/connection'},
      {'name': 'dialup_profiles',               'kind': 'tree',  'url': '/api/dialup/profiles'},
      {'name': 'net_register',                  'kind': 'flat',  'url': '/api/net/register'},
      {'name': 'net_network',                   'kind': 'flat',  'url': '/api/net/network'},
      {'name': 'sms_config',                    'kind': 'flat',  'url': '/api/sms/config'},
      {'name': 'wlan_basic_settings',           'kind': 'flat',  'url': '/api/wlan/basic-settings'},
      {'name': 'wlan_security_settings',        'kind': 'flat',  'url': '/api/wlan/security-settings'},
      {'name': 'wlan_host_list',                'kind': 'tree',  'url': '/api/wlan/host-list'}, # connected wireless clients
      {'name': 'wlan_wps',                      'kind': 'flat',  'url': '/api/wlan/wps'}, # WPS pin
      {'name': 'wlan_mac_filter',               'kind': 'flat',  'url': '/api/wlan/mac-filter'},
      {'name': 'dhcp_settings',                 'kind': 'flat',  'url': '/api/dhcp/settings'},
      {'name': 'security_dmz',                  'kind': 'flat',  'url': '/api/security/dmz'}, # DMZ host settings
      {'name': 'security_firewall_switch',      'kind': 'flat',  'url': '/api/security/firewall-switch'},
      {'name': 'security_lan_ip_filter',        'kind': 'tree',  'url': '/api/security/lan-ip-filter'},
      {'name': 'security_upnp',                 'kind': 'flat',  'url': '/api/security/upnp'},
      {'name': 'security_sip',                  'kind': 'flat',  'url': '/api/security/sip'},
      {'name': 'security_nat',                  'kind': 'flat',  'url': '/api/security/nat'},
      {'name': 'pin_status',                    'kind': 'flat',  'url': '/api/pin/status'},
      {'name': 'pin_simlock',                   'kind': 'flat',  'url': '/api/pin/simlock'}, # enable SIM lock
      {'name': 'user_state_login',              'kind': 'flat',  'url': '/api/user/state-login'},
      {'name': 'config_global',                 'kind': 'config','url': '/config/global/config.xml'},
      {'name': 'config_sms',                    'kind': 'config','url': '/config/sms/config.xml'},
      {'name': 'config_dialup_connectmode',     'kind': 'config','url': '/config/dialup/connectmode.xml'},
      {'name': 'config_wifi_countryChannel',    'kind': 'config','url': '/config/wifi/countryChannel.xml'},
    ]

    def __init__(self, host='192.168.1.1'):
        self.host = host
        self.home_url = self.HOME_URL.format(host=host)
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.opener.open(self.home_url)
        self.base_url = self.BASE_URL.format(host=host)

    def _api_by_name(self, name):
        return [api for api in self.XML_APIS if api['name'] == name][0]

    def _get(self, url):
        with self.opener.open(url) as response:
           rtext = response.read()
           return rtext

    def wlan_host_list(self):
        host_list = []
        api = self._api_by_name('wlan_host_list')
        url = urllib.parse.urljoin(self.base_url, api['url'])
        dom = xml.dom.minidom.parseString(self._get(url))
        assert dom.getElementsByTagName("response")[0]
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

    def tree_properties(self):
        properties = []
        tree_apis = [api for api in self.XML_APIS if api['kind'] == 'tree']
        for api in tree_apis:
            url = urllib.parse.urljoin(self.base_url, api['url'])
            dom = xml.dom.minidom.parseString(self._get(url))
            response = dom.getElementsByTagName("response")[0]
            properties.append((api['name'], HuaweiE5332.recursive_checknodes(response)))
        return properties

    def recursive_checknodes(node):
        """
        A class method to go through the XML tree structures
        as provided by the E5332. Returns a dict().
        Similar to: http://stackoverflow.com/a/10231610/183995
        """
        ret_dict = {}
        childlen = len(node.childNodes)
        for cnode in node.childNodes:
            if len(cnode.childNodes) == 1:
                ret_dict[cnode.tagName] = cnode.firstChild.data if cnode.firstChild is not None else None
                if ret_dict[cnode.tagName].strip() == '': ret_dict[cnode.tagName] = None
                continue
            if cnode.firstChild is None: continue
            val = HuaweiE5332.recursive_checknodes(cnode)
            if type(ret_dict) is list or cnode.tagName in ret_dict or cnode.tagName + 's' == node.tagName:
                try:
                    ret_dict.append(val)
                except AttributeError:
                    try:
                        ret_dict = [ret_dict[cnode.tagName], val]
                    except KeyError:
                        ret_dict = [val]
            else:
                ret_dict[cnode.tagName] = val
        return ret_dict

    def flat_properties(self):
        properties = []
        flat_apis = [api for api in self.XML_APIS if api['kind'] == 'flat']
        for api in flat_apis:
            url = urllib.parse.urljoin(self.base_url, api['url'])
            dom = xml.dom.minidom.parseString(self._get(url))
            try:
                response = dom.getElementsByTagName("response")[0]
            except IndexError:
                sys.stderr.write('Could not parse API {name}\n'.format(**api))
                continue
            for cn in response.childNodes:
                if type(cn) is not xml.dom.minidom.Element: continue
                prop, val = cn.tagName, cn.firstChild.data if cn.firstChild is not None else None
                properties.append((api['name'] + '_' + prop, val))
        for host in self.wlan_host_list():
            hid = host['ID']
            for key in host:
                properties.append(('wlan_host_list' + '_' + hid + '_' + key, host[key]))
        return properties

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch all kinds of status information from the Huawei E5332 UMTS Hotspot.')
    parser.add_argument('host', nargs='?', default='192.168.1.1', help='The hostname / IP address your E5332 is reachable at')
    parser.add_argument('--tree', action='store_true', help='Read tree-style APIs')
    
    args = parser.parse_args()
    e5332 = HuaweiE5332(host=args.host)
    if args.tree:
        for prop, val in e5332.tree_properties():
            print("\n--------------\n{}:\n".format(prop))
            pprint.pprint(val)
    if not args.tree:
        fp = e5332.flat_properties()
        for prop, val in fp:
            print("{}: {}".format(prop, val))

if __name__ == "__main__":
    main()
