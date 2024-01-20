import hashlib
import logging
from binascii import unhexlify, hexlify

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger(__name__)


def md5_hex_digest(content, do_padding):
    if do_padding:
        content = content + "00"

    try:
        message_digest = hashlib.md5()
        message_digest.update(content.encode())
        hash_result = message_digest.digest()

        hex_string = ""
        for v in hash_result:
            v1 = v if v >= 0 else v + 0x100

            if v1 < 16:
                hex_string += "0"

            hex_string += format(v1, 'x')

        return hex_string
    except Exception as e:
        logger.error("Could not compute md5 hex digest for input string=%s", content, exc_info=e)
        return None


def sha1_hex_digest(content):
    try:
        message_digest = hashlib.sha1()
        message_digest.update(content.encode())
        return message_digest.hexdigest()
    except Exception as e:
        logger.error("Could not compute sha1 hex digest for input string=%s", content, exc_info=e)
        raise RuntimeError(e)


def sha256_hex_digest(content):
    try:
        message_digest = hashlib.sha256()
        message_digest.update(content.encode())
        return message_digest.hexdigest()
    except Exception as e:
        logger.error("Could not compute sha256 hex digest for input string=%s", content, exc_info=e)
        raise RuntimeError(e)


def encrypt_aes_cbc_pkcs5_padding(content, key, iv):
    if content and key and iv:
        try:
            key_bytes = unhexlify(key)
            iv_bytes = unhexlify(iv)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            padded_content = pad(content.encode('utf-8'), AES.block_size)
            encrypted_content = cipher.encrypt(padded_content)
            return hexlify(encrypted_content).decode('utf-8')
        except Exception as e:
            logger.error("Could not encrypt content=%s", content, exc_info=e)
            raise RuntimeError(e)
    return None


def decrypt_aes_cbc_pkcs5_padding(cypher_text, key, iv):
    if cypher_text and key and iv:
        try:
            key_bytes = unhexlify(key)
            iv_bytes = unhexlify(iv)
            cypher_text_bytes = unhexlify(cypher_text)

            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            decrypted_text = unpad(cipher.decrypt(cypher_text_bytes), AES.block_size)

            return decrypted_text.decode('utf-8')
        except Exception as exception0:
            raise RuntimeError(exception0)

    return None
