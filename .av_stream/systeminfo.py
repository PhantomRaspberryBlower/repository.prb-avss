#!/bin/python

from urllib.request import Request, urlopen
from collections import namedtuple
from subprocess import check_call, Popen, PIPE
import socket
import fcntl
import struct
import platform
import getpass
import os

# Written by: Phantom Raspberry Blower (The PRB)
# Date: 01-10-2018
# Description: Script for displaying system information
#              about software, CPU, hardware, memory,
#              storage, networks and addons installed.
#              Tested on Raspberry Pi.

class SystemInfo():

    # ## Software Information ## #

    @property
    def username(self):
        # Get username
        return getpass.getuser()

    @property
    def hostname(self):
        # Get hostname
        return socket.gethostname()

    @property
    def is_user_root(self):
        # Is current user root
        if os.geteuid() == 0:
            return True
        else:
            return False

    @property
    def os_platform(self):
        return platform.platform()

    @property
    def platform_system(self):
        return platform.system()

    @property
    def platform_node(self):
        return platform.node()

    @property
    def platform_release(self):
        return platform.release()

    @property
    def platform_version(self):
        return platform.version()

    @property
    def platform_machine(self):
        return platform.machine()

    @property
    def platform_processor(self):
        return platform.processor()

    @property
    def platform_architecture(self):
        return platform.architecture()

    @property
    def platform_python_build(self):
        return platform.python_build()

    @property
    def platform_python_compiler(self):
        return platform.python_compiler()

    @property
    def platform_python_branch(self):
        return platform.python_branch()

    @property
    def platform_python_implementation(self):
        return platform.python_implementation()

    @property
    def platform_python_revision(self):
        return platform.python_revision()

    @property
    def platform_python_version(self):
        return platform.python_version()

    @property
    def platform_python_version_tuple(self):
        return platform.python_version_tuple()

    @property
    def platform_win32_ver(self):
        # Windows platforms
        return platform.win32_ver()

    @property
    def platform_mac_ver(self):
        return platform.mac_ver()   

    @property
    def platform_linux_distribution(self):
        # Unix platforms
        return platform.linux_distribution()

    # ## CPU Information ## #

    @property
    def cpu_model(self):
        # Get Model Name
        return self._get_cpu_item('model name', '')

    @property
    def cpu_hardware(self):
        # Get Hardware
        return self._get_cpu_item('Hardware', '')

    @property
    def cpu_revision(self):
        # Get Revision
        return self._get_cpu_item('Revision', '')

    @property
    def cpu_serial_number(self):
        # Get CPU Serial Number
        return self._get_cpu_item('Serial', '0000000000000000')

    @property
    def cpu_cores(self):
        # Get number of cpu cores
        # Linux, Unix and MacOS:
        if hasattr(os, "sysconf"):
            if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
                # Linux and Unix:
                ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
                if isinstance(ncpus, int) and ncpus > 0:
                    return ncpus
            else: # OSX:
                return int(os.popen2("sysctl -n hw.ncpu")[1].read())

    @property
    def cpu_clock_speed(self):
        # Return CPU clock speed as a character string
        try:
            output = Popen(['vcgencmd', 'measure_clock arm'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            return str(round(int(output[14:-1]) / (1000**2))) + "Mhz"
        except:
            return 'Unable to get CPU clock speed! :('

    @property
    def cpu_max_clock_speed(self):
        # Return CPU maximum clock speed as a character string
        try:
            output = Popen(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            return str(round(int(output) / 1000)) + "Mhz"
        except:
            return 'Unable to get CPU maximum clock speed! :('

    @property
    def cpu_temp(self):
        # Return CPU temperature as a character string
        try:
            output = Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            return str(round(int(output) / 1000,0)) + "'C"
        except:
            return 'Unable to get CPU temperature! :('

    # ## GPU Information ## #

    @property
    def gpu_clock_speed(self):
        # Return GPU clock speed as a character string
        try:
            output = Popen(['vcgencmd', 'measure_clock core'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            return  str(round(int(output[13:-1]) / (1000**2))) + "Mhz"
        except:
            return 'Unable to get GPU clock speed! :('

    @property
    def gpu_temp(self):
        # Return GPU temperature as a character string
        try:
            output = Popen(['vcgencmd', 'measure_temp'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            return str(output[5:len(output)-3]) + "'C"
        except:
            return 'Unable to get GPU temperature! :('

    # ## Memory Informtion ## #

    # Get memory info
    @property
    def ram_info(self):
        _ntuple_RAMinfo = namedtuple('RAM', 'total used free')
        output = Popen(['free'], stdout=PIPE).communicate()[0].decode('utf-8')
        for line in output.split('\n'):
            if 'Mem:' in line:
                total = int(line.split()[1])
                used = int(line.split()[2])
                free = int(total) - int(used)
        return _ntuple_RAMinfo(total, used, free)

    # ## Storage Informtion ## #

    # Get hard drive(s) info
    @property
    def disk_info(self):
        devices = []
        devices.append(self.disk_usage("/root/"))
        for device in self.get_devices("/media/"):
            devices.append(self.disk_usage("/media/" + device + "/"))
        return devices

    # ## Network Informtion ## #

    @property
    def wan_ip_addr(self):
        # Get the WAN IP address
        try:
            return urlopen('http://ip.42.pl/raw').read()
        except:
            return 'Unable to get WAN IP Address! :('

    @property
    def default_gateway(self):
        # Get default gateway
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) and 2:
                    continue
                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    ## # Hardware Information ## #

    @property
    def camera_available(self):
        # Returns the enabled and detected state of the Raspberry Pi camera
        try:
            var = {}
            output = Popen(['vcgencmd', 'get_camera'],
                           stdout=PIPE).communicate()[0].decode('utf-8')
            for items in output.split('\n'):
                for item in items.split(' '):
                    try:
                        key, value = item.split('=')
                        var[key] = 'True' if value == '1' else 'False'
                    except:
                        pass
            return var
        except:
            return 'Unable to get camera status! :('

    @property
    def usb_sound_card_detected(self):
        # Returns the enabled and detected state of the USB sound card
        try:
            output = os.popen('lsmod | grep snd_usb_audio').read()
            if output:
                return 'True'
            else:
                return 'False'
        except:
            return 'Unable to get USB sound card status! :('

    @property
    def network_detected(self):
        # Returns the enabled and detected state of the network
        try:
            output default_gateway()
            if output:
                return 'True'
            else:
                return 'False'
        except:
            return 'Unable to get network status! :('

    ## # Functions # ##

    # ## Software Information ## #

    def get_platform_info(self):
        distname, dist_version, id = platform.linux_distribution()
        system, node, release, version, machine, processor = platform.uname()
        return (self.os_platform,
                distname,
                dist_version,
                id,
                system,
                node,
                release,
                version,
                machine,
                processor)

    # ## CPU Information ## #

    # Get CPU items
    def _get_cpu_item(self, item, ini_value):
        temp = ini_value
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:len(item)] == item:
                    item_value = line[len(item)+3:]
            f.close()
        except:
            item_value = 'Unable to get %s! :(' % item
        return item_value.strip()

    # ## Hard Disk Informtion ## #

    # Get Hard Drive Devices
    def get_devices(self, path):
        return next(os.walk(path))[1]

    # Get hard drive usage
    def disk_usage(self, path):
        _ntuple_diskusage = namedtuple('usage', 'path total used free')
        st = os.statvfs(path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        return _ntuple_diskusage(path, total, used, free)

    # ## Network Informtion ## #

    # Get LAN IP address for either etho or wlan
    def get_lan_ip_addr(self, ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                                    s.fileno(),
                                    0x8915, # SIOCGIFADDR
                                    struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                                    )[20:24])
        except:
                return 'Unable to get LAN IP address! :('

# Check if running stand-alone or imported
if __name__ == u'__main__':
    if platform.system() != u'Windows':
        import systeminfo
        si = SystemInfo()
        print(si.get_lan_ip_addr('eth0'))
    else:
        print(u'This script does not work with a Windows operating system. :(')
