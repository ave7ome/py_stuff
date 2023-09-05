#import required libraries 

#encryption
import base64
#working with json files
import json
#os-level requests
import os

#retrieve current date and time
from datetime import datetime
#netmiko function to ssh to device
from netmiko import ConnectHandler
#module that is used in password encryption/decryption
from cryptography.fernet import Fernet

#change directory of execution, used to be able to run python from the specified directory when utilized via crontab
#specify full directory between ""
os.chdir("")

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

#print ("Reading JSON device list..."+"\n"+'-'*75)

#Open the device list file in read mode
with open('devs.json', 'r') as device_list_file:
    device_list = json.load(device_list_file)

#Iterate through device list and connect to each device
for device in device_list:
    #print ("Logging in to "+device['hostname']+" to collect the configuration...")

    #if connection cant be established return a 'no access' message
    try:
        net_connect = ConnectHandler(device_type=device['os'],host=device['ip'],username="admin",password=decrypted_password,fast_cli=True)
        #print ("Connected successfully! Sending the command.")
        start_time=datetime.now()
        output = net_connect.send_command("show running-config",read_timeout=60)
        net_connect.disconnect()

        #check if folder exists for the current device
        if not os.path.exists("configurations/"+device['hostname']):
            os.makedirs("configurations/"+device['hostname'])
            #print ("Creating directory for the host...")
        #print ("Writing the configuration to file...")
        with open(f"configurations/{device['hostname']}/{device['hostname']}-"+str(datetime.now().date())+".txt", "w") as device_file:
            device_file.write(output)
            end_time=datetime.now()
            print (f"{device['hostname']} done in {end_time-start_time}")
            #print (f"### configurations/{device['hostname']}.txt created successfully\n"+'-'*75)
    except Exception as e:
        print(device['hostname']+" failed, check if there's access to device")












