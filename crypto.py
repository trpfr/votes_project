import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64


# Functions for generating master phrase for ZKP realization
def generate_phrase():
    """
    System generate a random 32 bytes - a certain string that will be used as a master phrase. The master phrase is
    essential for implementing ZKP (Zero-Knowledge Proof). What does this mean? It means that we can prove that we
    voted (or that we have the right to vote in general) without revealing any other information (like who we voted
    for, for instance). More details about our implementation can be found in the to_vote function (interface file).
    """
    phrase = os.urandom(32)
    return str(phrase)


# Function for generating private and public keys
def generate_keys():
    """
    In the system, I use asymmetric encryption. This means that we have two keys - a public key and a private key.
    The public key is used for encrypting data, while the private key is used for decryption. Encryption ensures that
    no one can determine who we voted for and also prevents anyone from tampering with our vote. If we use the public
    key for encryption, only the private key can decrypt the data (it's not stored in the database but is kept with
    us). The encryption is carried out using the RSA (Rivest, Shamir, and Adleman) algorithm.
    """
    private_key = rsa.generate_private_key(  # Private key generation
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()  # Public key generation from private key
    return public_key, private_key


# Functions for serializing keys
def serialize_private_key(private_key):
    """
    Serialization is the process of converting an object into a byte stream that can be saved to a file or
    transmitted over a network. In this case, I serialize the private key in PEM (Privacy Enhanced Mail) format.
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,  # Формат кодирования - PEM (стандартный формат для таких ключей)
        format=serialization.PrivateFormat.PKCS8,  # Формат самого ключа - PKCS8
        encryption_algorithm=serialization.NoEncryption()
    )


def serialize_public_key(public_key):
    """
    A similar function for the public key.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


# Functions for signing results
def sign_results(results, private_key):
    """
    To implement the requirement of preventing vote results tampering (and the ability to prove it to all parties),
    I use a signature. A signature is a certain string that is generated based on the data I want to sign and the
    private key. However, for the signature to be reliable, I need to use a hashing algorithm (in this case,
    SHA256). Hashing is the process of converting data into a fixed-length string (in this case, 256 bits).
    Therefore, if I want to sign the data, I need to hash it first and then sign it.

In fact, this is very similar to encrypting data, but for encryption, I would use a public key, and the data can only
be read with a private key. For signing, on the other hand, the private key is used (which no one knows),
but the signature can only be checked with a public key (which is available to everyone). This way, I can prove that
the data was signed by me and not by someone else and was not changed. At the end of the function, I get a separate
signature string, and the data remains unencrypted.

If a malicious actor can access the database and change the voting results, the signature will not match the data we
get from the database, and I can prove it.
    """
    try:
        # Creating a signature
        signature = private_key.sign(
            results.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # Returning the signature in base64 format
        return base64.b64encode(signature).decode()
    except:
        return None


def verify_signature(results, signature, public_key):
    """
    Now, a function to verify the signature. This is the reverse function of the previous one. I pass the data,
    signature, and public key to it, and it returns True if the signature is correct, and False if not.

Thus, if no one changed the data and they were signed with the correct private key (which corresponds to the public
key that I pass to the function) - then the function will return True. In case of any violation, it will return
False. This is proof that the results are valid and have not been tampered with.
    """
    try:
        # Decoding the signature from base64
        signature_bytes = base64.b64decode(signature)
        # Verifying the signature
        public_key.verify(
            signature_bytes,
            results.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


# Functions for encrypting and decrypting votes (or other data)
def encrypt_vote(vote, public_key):
    """
    Encryption function. As I mentioned earlier (in the generate_keys function), the public key is used for
    encryption, and the private key is used for decryption. Thus, I encrypt the vote using the public key and decrypt
    it using the private key. To ensure reliable encryption, I use the OAEP (Optimal Asymmetric Encryption Padding)
    algorithm. It's important to note that if I encrypt the vote using standard methods, it will look the same every
    time, allowing a malicious actor to determine the vote based on its appearance. That's why I use OAEP - an
    algorithm that adds some random data to our data, making the cipher look different each time. This way,
    a malicious actor won't be able to determine the vote, even if they gain access to the database. This process is
    called "padding" (adding random data to the data being encrypted).
    """
    try:
        encrypted_vote = public_key.encrypt(
            str(vote).encode(),
            padding.OAEP(  # OAEP padding
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_vote).decode()
    except:
        return None


def decrypt_vote(encrypted_vote, private_key):
    """
    The vote encrypted with the public key can only be decrypted using the corresponding private key. I pass the
    encrypted data and the private key to the function, and it returns the decrypted data.
    """
    try:
        decoded_vote = base64.b64decode(encrypted_vote)
        decrypted_vote = private_key.decrypt(
            decoded_vote,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_vote.decode()
    except:
        return None
