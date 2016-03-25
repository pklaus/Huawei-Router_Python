#!/usr/bin/env python

import xml.dom.minidom, urllib.request, urllib.parse, http.cookiejar, pprint, logging, json
from datetime import datetime as dt

logger = logging.getLogger(__name__)

class HuaweiE5332(object):

    HOME_URL = 'http://{host}'
    BASE_URL = 'http://{host}/api/'

    XML_APIS = [
      {'name': 'device_information',            'flavour': 'default', 'kind': 'flat',  'url': '/api/device/information'},
      {'name': 'device_basic_information',      'flavour': 'e3372',   'kind': 'flat',  'url': '/api/device/basic_information'},
      {'name': 'device_signal',                 'flavour': 'e3372',   'kind': 'flat',  'url': '/api/device/signal'},
      {'name': 'global_module_switch',          'flavour': 'default', 'kind': 'flat',  'url': '/api/global/module-switch'},
      {'name': 'monitoring_status',             'flavour': 'default', 'kind': 'flat',  'url': '/api/monitoring/status'},
      {'name': 'monitoring_converged_status',   'flavour': 'default', 'kind': 'flat',  'url': '/api/monitoring/converged-status'},
      {'name': 'monitoring_traffic_statistics', 'flavour': 'default', 'kind': 'flat',  'url': '/api/monitoring/traffic-statistics'},
      {'name': 'monitoring_check_notifications','flavour': 'default', 'kind': 'flat',  'url': '/api/monitoring/check-notifications'},
      {'name': 'monitoring_start_date',         'flavour': 'e3372',   'kind': 'flat',  'url': '/api/monitoring/start_date'},
      {'name': 'monitoring_month_statistics',   'flavour': 'e3372',   'kind': 'flat',  'url': '/api/monitoring/month_statistics'},
      {'name': 'dialup_connection',             'flavour': 'default', 'kind': 'flat',  'url': '/api/dialup/connection'},
      {'name': 'dialup_mobile_dataswitch',      'flavour': 'e3372',   'kind': 'flat',  'url': '/api/dialup/mobile-dataswitch'},
      {'name': 'dialup_profiles',               'flavour': 'default', 'kind': 'tree',  'url': '/api/dialup/profiles'},
      {'name': 'net_register',                  'flavour': 'default', 'kind': 'flat',  'url': '/api/net/register'},
      {'name': 'net_current_plmn',              'flavour': 'e3372',   'kind': 'flat',  'url': '/api/net/current-plmn'},
      {'name': 'net_network',                   'flavour': 'default', 'kind': 'flat',  'url': '/api/net/network'},
      {'name': 'sms_config',                    'flavour': 'default', 'kind': 'flat',  'url': '/api/sms/config'},
      {'name': 'wlan_basic_settings',           'flavour': 'e5332',   'kind': 'flat',  'url': '/api/wlan/basic-settings'},
      {'name': 'wlan_security_settings',        'flavour': 'e5332',   'kind': 'flat',  'url': '/api/wlan/security-settings'},
      {'name': 'wlan_host_list',                'flavour': 'e5332',   'kind': 'tree',  'url': '/api/wlan/host-list'},
      {'name': 'wlan_wps',                      'flavour': 'e5332',   'kind': 'flat',  'url': '/api/wlan/wps'},
      {'name': 'wlan_mac_filter',               'flavour': 'e5332',   'kind': 'flat',  'url': '/api/wlan/mac-filter'},
      {'name': 'dhcp_settings',                 'flavour': 'default', 'kind': 'flat',  'url': '/api/dhcp/settings'},
      {'name': 'security_dmz',                  'flavour': 'default', 'kind': 'flat',  'url': '/api/security/dmz'},
      {'name': 'security_firewall_switch',      'flavour': 'default', 'kind': 'flat',  'url': '/api/security/firewall-switch'},
      {'name': 'security_lan_ip_filter',        'flavour': 'default', 'kind': 'tree',  'url': '/api/security/lan-ip-filter'},
      {'name': 'security_upnp',                 'flavour': 'default', 'kind': 'flat',  'url': '/api/security/upnp'},
      {'name': 'security_sip',                  'flavour': 'default', 'kind': 'flat',  'url': '/api/security/sip'},
      {'name': 'security_nat',                  'flavour': 'default', 'kind': 'flat',  'url': '/api/security/nat'},
      {'name': 'pin_status',                    'flavour': 'default', 'kind': 'flat',  'url': '/api/pin/status'},
      {'name': 'pin_simlock',                   'flavour': 'default', 'kind': 'flat',  'url': '/api/pin/simlock'},
      {'name': 'user_state_login',              'flavour': 'default', 'kind': 'flat',  'url': '/api/user/state-login'},
      {'name': 'config_global',                 'flavour': 'default', 'kind': 'config','url': '/config/global/config.xml'},
      {'name': 'config_sms',                    'flavour': 'default', 'kind': 'config','url': '/config/sms/config.xml'},
      {'name': 'config_dialup_connectmode',     'flavour': 'default', 'kind': 'config','url': '/config/dialup/connectmode.xml'},
      {'name': 'config_wifi_countryChannel',    'flavour': 'default', 'kind': 'config','url': '/config/wifi/countryChannel.xml'},
    ]

    def __init__(self, flavour='default', host=None):
        if host is None:
            host = '192.168.1.1'
        self.host = host
        self.flavour = flavour
        self.home_url = self.HOME_URL.format(host=host)
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.opener.open(self.home_url)
        self.base_url = self.BASE_URL.format(host=host)

    def relevant_apis(self):
        return [api for api in self.XML_APIS if api['flavour'] in ('default', self.flavour)]

    def _api_by_name(self, name):
        return [api for api in self.relevant_apis() if api['name'] == name][0]

    def _get(self, url):
        with self.opener.open(url) as response:
           rtext = response.read()
           return rtext

    def wlan_host_list(self):
        host_list = []
        api = self._api_by_name('wlan_host_list')
        url = urllib.parse.urljoin(self.base_url, api['url'])
        dom = xml.dom.minidom.parseString(self._get(url))
        get_first_response(dom, api)
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
        tree_apis = [api for api in self.relevant_apis() if api['kind'] == 'tree']
        for api in tree_apis:
            url = urllib.parse.urljoin(self.base_url, api['url'])
            dom = xml.dom.minidom.parseString(self._get(url))
            try:
                response = get_first_response(dom, api)
            except InvalidResponseException:
                continue
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
        flat_apis = [api for api in self.relevant_apis() if api['kind'] == 'flat']
        for api in flat_apis:
            url = urllib.parse.urljoin(self.base_url, api['url'])
            dom = xml.dom.minidom.parseString(self._get(url))
            try:
                response = get_first_response(dom, api)
            except InvalidResponseException:
                continue
            for cn in response.childNodes:
                if type(cn) is not xml.dom.minidom.Element: continue
                prop, val = cn.tagName, cn.firstChild.data if cn.firstChild is not None else None
                properties.append((api['name'] + '_' + prop, val))
        if 'wlan_host_list' in [api['name'] for api in self.relevant_apis()]:
            for host in self.wlan_host_list():
                hid = host['ID']
                for key in host:
                    properties.append(('wlan_host_list' + '_' + hid + '_' + key, host[key]))
        return properties

def get_first_response(dom, context):
    try:
        return dom.getElementsByTagName("response")[0]
    except IndexError:
        logger.warning('Could not parse API {name}\n'.format(**context))
        raise InvalidResponseException(context['name'])

class InvalidResponseException(NameError): pass

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch all kinds of status information from the Huawei E5332 UMTS Hotspot.')
    parser.add_argument('host', nargs='?', default='192.168.1.1', help='The hostname / IP address your E5332 is reachable at')
    parser.add_argument('--tree', action='store_true', help='Read tree-style APIs')
    parser.add_argument('--format', choices=('json','text'), help='Output format', default='text')
    def flavours(): return set([api['flavour'] for api in HuaweiE5332.XML_APIS])
    parser.add_argument('--flavour', choices=flavours(), help='Device flavour to use')

    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()
    e5332 = HuaweiE5332(flavour=args.flavour, host=args.host)
    if args.tree:
        for prop, val in e5332.tree_properties():
            print("\n--------------\n{}:\n".format(prop))
            pprint.pprint(val)
    else:
        fp = e5332.flat_properties()
        if args.format == 'text':
            for prop, val in fp:
                print("{}: {}".format(prop, val))
        elif args.format == 'json':
            fp = dict(fp)
            print(json.dumps({'data': fp, 'timestamp': dt.now().isoformat()}))

if __name__ == "__main__":
    main()
