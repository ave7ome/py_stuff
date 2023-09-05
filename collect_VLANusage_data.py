import base64
import json
import os

from datetime import datetime
from netmiko import ConnectHandler
from cryptography.fernet import Fernet

os.chdir("DIRECTORY")

#Load the salt and secret key from a file
with open('salt_and_secret_key.bin', 'rb') as f:
    salt = f.read(16)
    secret_key = f.read()

#Create a Fernet object using the secret key
fernet = Fernet(base64.urlsafe_b64encode(secret_key))

#Load the ecnrypted password from a file
with open('encrypted_password.txt', 'rb') as f:
    encrypted_password = f.read()

#Decrypt the password
decrypted_password = fernet.decrypt(encrypted_password).decode()

#Open the device list file in read mode
with open('VTBE_L3_points.json', 'r') as device_list_file:
    device_list = json.load(device_list_file)

#Iterate through device list and connect to each device
for device in device_list:

    #if connection cant be established return an 'access failed' mesage with the device name
    try:
        #connect to device using Netmiko function 'ConnectHandler' and apply it to variable
        net_connect = ConnectHandler(device_type=device['os'],host=device['ip'],username="admin",password=decrypted_password,fast_cli=True)

        #check the OS of device and configure accordingly followed by a session drop
        if device['os'] == "cisco_ios":
            output = net_connect.send_command('sh int | i Vlan|txload.*rxload|Description|Last.input.*output|ond.*put.rate|packets.*put.*bytes|errors|drops')
            net_connect.disconnect()
        elif device['os'] == "cisco_asa":
            output = net_connect.send_command('show traffic')
            net_connect.disconnect()
        elif device['os'] == "cisco_nxos":
            output = net_connect.send_command('show ip interface vrf all | i "ded/orig|packets|bytes|Vlan"')
            net_connect.disconnect()
        #unknown devices are specified as an 'Unknown device' note
        else:
            print("Unknown device - "+device['hostname']+", couldn't configure!")
            net_connect.disconnect()

        if not os.path.exists("VLAN_L3_utilization_check/"+device['hostname']):
            os.makedirs("VLAN_L3_utilization_check/"+device['hostname'])

        with open(f"VLAN_L3_utilization_check/{device['hostname']}/{device['hostname']}-"+str(datetime.now().date())+".txt", "w") as device_file:
            device_file.write(output)
            print ("written for " + device['hostname'])

    except Exception as e:
        print(device['hostname']+" failed, check if there's access to device")
