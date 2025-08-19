from netmiko import ConnectHandler
import argparse
import re

DEVICE_TEMPLATE = {'device_type': 'cisco_ios_telnet', 'ip': '192.168.117.128', 'port': 5000, 'timeout': 60}

DEVICE_TEMPLATE_SERIAL = {
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        "port": "X",
        "baudrate": 9600,
    },
}

# generate rsa (+ "general-keys" if physical) ....
COMMANDS = [
    "ip domain-name sede.local", "enable secret level 15 Admin1234.", "username admin privilege 15 secret Admin1234.",
    "ip ssh version 2", "ip ssh time-out 60", "crypto key generate rsa general-keys modulus 2048", "interface vlan 99",
    "ip address 10.0.99.0 255.255.255.0", "no shutdown", "line console 0", "password cisco", "login", "line vty 0 4",
    "transport input ssh", "login local", "exec-timeout 10 0"
]

parser = argparse.ArgumentParser(description='Initial device setup')
parser.add_argument('--p', type=str, help='List of telnet ports to which connect', required=False)
parser.add_argument('--s', type=str, help='List of serial ports to which connect', required=False)
parser.add_argument('--ip',
                    type=str,
                    help='List of ending number of ip for each device in same order as ports',
                    required=True)

args = parser.parse_args()
ip_list = [f'ip address 10.0.99.{ip} 255.255.255.0' for ip in args.ip.split(',')]
port_list = []
serial_list = []
if args.p:
    port_list = [port for port in args.p.split(',')]
if args.s:
    serial_list = [serial for serial in args.s.split(',')]

if (len(port_list) != 0 != len(serial_list)):
    raise Exception('Choose only one type between serial and telnet port')

if not (max(len(port_list), len(serial_list)) == len(ip_list)):
    raise Exception('Number of arguments do not match each other')

for i in range(0, len(port_list) + len(serial_list)):
    if serial_list:
        device = DEVICE_TEMPLATE_SERIAL
        device['serial_settings']['port'] = serial_list[i]
    if port_list:
        device = DEVICE_TEMPLATE
        device['port'] = port_list[i]
    print(device)
    commands = COMMANDS
    commands[7] = ip_list[i]
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        print("Connected")
        net_connect.send_command("terminal length 0")
        int_output = net_connect.send_command('show ip int brief')
        interfaces = re.findall(r'\b\S*thernet\S*\b', int_output, re.IGNORECASE)
        print("Looping...")
        for match in interfaces:
            commands.append(f"interface {match}")
            commands.append(f"switchport access vlan 99")

        output = net_connect.send_config_set(commands, cmd_verify=False, read_timeout=120)
        print(output)
        net_connect.disconnect()
    except Exception as e:
        raise Exception(e)
