import base64
import os

from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

backend = default_backend()

#enter the password to encrypt
password = getpass('Please enter password to encrypt: ')

print('Generating random salt and getting secret key...')
#Salt and secret key
salt = os.urandom(16)
secret_key = PBKDF2HMAC(
    algorithm = hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=backend
).derive(password.encode())

print('Generating Fernet object...')
#Create a Fernet object using the secret key
fernet = Fernet(base64.urlsafe_b64encode(secret_key))

print('Encrypting password...')
#Encrypt the password
encrypted_password = fernet.encrypt(password.encode())

print('Saving encrypted password to file "encrypted_password.txt"...')
#Save the encrypted password to a file
with open('encrypted_password.txt', 'wb') as f:
    f.write(encrypted_password)

print('Saving salt and secret key to file "salt_and_secret_key.bin"...')
#Save the salt and secret key to a file
with open('salt_and_secret_key.bin', 'wb') as f:
    f.write(salt)
    f.write(secret_key)

print('Success!')
