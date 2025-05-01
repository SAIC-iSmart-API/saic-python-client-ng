from __future__ import annotations

from binascii import hexlify, unhexlify
import hashlib
import logging

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger(__name__)


def md5_hex_digest(content: str, do_padding: bool) -> str:
    if do_padding:
        content = content + "00"

    try:
        message_digest = hashlib.md5()  # noqa: S324
        message_digest.update(content.encode())
        hash_result = message_digest.digest()

        hex_string = ""
        for v in hash_result:
            v1 = v if v >= 0 else v + 0x100

            if v1 < 16:
                hex_string += "0"

            hex_string += format(v1, "x")

        return hex_string
    except Exception as e:
        logger.exception(
            "Could not compute md5 hex digest for input string=%s", content, exc_info=e
        )
        raise RuntimeError(e) from e


def sha1_hex_digest(content: str) -> str:
    try:
        message_digest = hashlib.sha1()  # noqa: S324
        message_digest.update(content.encode())
        return message_digest.hexdigest()
    except Exception as e:
        logger.exception(
            "Could not compute sha1 hex digest for input string=%s", content, exc_info=e
        )
        raise RuntimeError(e) from e


def sha256_hex_digest(content: str) -> str:
    try:
        message_digest = hashlib.sha256()
        message_digest.update(content.encode())
        return message_digest.hexdigest()
    except Exception as e:
        logger.exception(
            "Could not compute sha256 hex digest for input string=%s",
            content,
            exc_info=e,
        )
        raise RuntimeError(e) from e


def encrypt_aes_cbc_pkcs5_padding(content: str | bytes, key: str, iv: str) -> str:
    try:
        key_bytes = unhexlify(key)
        iv_bytes = unhexlify(iv)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        if isinstance(content, bytes):
            content_as_bytes = content
        else:
            content_as_bytes = content.encode("utf-8")
        padded_content = pad(content_as_bytes, AES.block_size)
        encrypted_content = cipher.encrypt(padded_content)
        return hexlify(encrypted_content).decode("utf-8")
    except Exception as e:
        logger.exception("Could not encrypt content=%s", content, exc_info=e)
        raise RuntimeError(e) from e


def decrypt_aes_cbc_pkcs5_padding(cypher_text: str, key: str, iv: str) -> str:
    try:
        key_bytes = unhexlify(key)
        iv_bytes = unhexlify(iv)
        cypher_text_bytes = unhexlify(cypher_text)

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted_text = unpad(cipher.decrypt(cypher_text_bytes), AES.block_size)

        return decrypted_text.decode("utf-8")
    except Exception as e:
        logger.exception("Could not decrypt content=%s", cypher_text, exc_info=e)
        raise RuntimeError(e) from e
