
## Huawei Router (Python)

Fetching status information from the Huawei Routers (including the UMTS WiFi
Hotspot E5332 and the LTE Stick E3372) can be easy.

This is a tool is written in plain Python3+ w/o external dependencies.

### Example call

Here is the 'help' for the CLI of the tool:


    [philipp@lion Huawei-Router_Python]$ ./huawei-router.py --help
    usage: huawei-router.py [-h] [--tree] [--flavour {default,e3372,e5332}] [host]
    
    Fetch all kinds of status information from the Huawei E5332 UMTS Hotspot.
    
    positional arguments:
      host                  The hostname / IP address your E5332 is reachable at
    
    optional arguments:
      -h, --help            show this help message and exit
      --tree                Read tree-style APIs
      --flavour {default,e3372,e5332}
                        Device flavour to use

And here's an example call showing the output
when fetching the device's status information:

    [philipp@lion Huawei-Router_Python]$ ./huawei-router.py --flavour e5332 192.168.1.1
    device_information_DeviceName: E5332
    device_information_SerialNumber: L5D4C13921101070
    device_information_Imei: 8672333678411112
    device_information_Imsi: 262996301120287
    device_information_Iccid: 89084893974902100001
    device_information_HardwareVersion: CH1E5331M
    device_information_SoftwareVersion: 21.344.19.00.1080
    device_information_WebUIVersion: 11.001.07.00.03
    device_information_MacAddress1: 00:66:4B:0C:23:DD
    monitoring_status_SignalStrength: 92
    monitoring_status_SignalIcon: 5
    monitoring_status_CurrentNetworkType: 9
    monitoring_status_CurrentServiceDomain: 3
    monitoring_status_BatteryStatus: 0
    [        .        ]
    [        .        ]
    [        .        ]
    [ many more lines ]
    [        .        ]
    [        .        ]
    [        .        ]
    pin_simlock_pSimLockRemainTimes: None
    wlan_host_list_1_ID: 1
    wlan_host_list_1_AssociatedTime: 1354
    wlan_host_list_1_MacAddress: e0:f8:47:d6:c2:41
    wlan_host_list_1_AssociatedSsid: HOTspot
    wlan_host_list_1_IpAddress: 192.168.1.101
    wlan_host_list_1_HostName: lion

### Author

* Philipp Klaus <philipp.l.klaus@web.de>

