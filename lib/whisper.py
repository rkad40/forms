from cryptography.fernet import Fernet
import sys 

SECRET_KEY = 'L4JpZYFo5jt3JetLUVLAJ9JG1ARWuNjyT1FKPLeicBU='

def generate_key():
    """
    Generates a key
    """
    key = Fernet.generate_key()
    print(key)

def encrypt(message):
    """
    Encrypts a message
    """
    key = SECRET_KEY
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return(encrypted_message)

def decrypt(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = SECRET_KEY
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return(decrypted_message.decode())

if __name__ == "__main__":
    value = sys.argv[1]
    print(f'Encrypting "{value}" ...')
    encrypted_message = encrypt(value)
    print(f'- encrypted value: "{encrypted_message}"')
    decrypted_message = decrypt(encrypted_message)
    print(f'- decrypted value: "{decrypted_message}"')
