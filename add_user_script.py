import base64
import json
import os

from datetime import datetime
from netmiko import ConnectHandler
from cryptography.fernet import Fernet

os.chdir("DIRECTORY")

#variable specifying command scope to configure read-only account on ASA devices
commands_asa = ['command 1','command 2','command 3']

#variable specifying command scope to configure read-only account on NXOS devices
commands_nxos = ['command 4','command 5','command 6']

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
with open('devs.json', 'r') as device_list_file:
    device_list = json.load(device_list_file)

#Iterate through device list and connect to each device
for device in device_list:

    #if connection cant be established return an 'access failed' mesage with the device name
    try:
        #connect to device using Netmiko function 'ConnectHandler' and apply it to variable
        net_connect = ConnectHandler(device_type=device['os'],host=device['ip'],username="admin",password=decrypted_password,fast_cli=True)

        #check the OS of device and configure accordingly followed by a session drop
        if device['os'] == "cisco_ios":
            net_connect.send_config_set("COMMAND")
            print("Added to "+device['hostname'])
            net_connect.disconnect()
        elif device['os'] == "cisco_asa":
            net_connect.send_config_set(commands_asa)
            print("Added to "+device['hostname'])
            net_connect.disconnect()
        elif device['os'] == "cisco_nxos":
            net_connect.send_config_set(commands_nxos)
            print("Added to "+device['hostname'])
            net_connect.disconnect()
        #unknown devices are specified as an 'Unknown device' note
        else:
            print("Unknown device - "+device['hostname']+", couldn't configure!")
            net_connect.disconnect()

    except Exception as e:
        print(device['hostname']+" failed, check if there's access to device")
