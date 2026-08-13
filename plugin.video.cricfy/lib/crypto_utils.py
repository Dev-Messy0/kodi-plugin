import base64
import json
from dataclasses import dataclass
from typing import Optional
from lib.logger import log_error
from lib.config import ADDON_PATH
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Charger les secrets
SECRET1_FILE_PATH = ADDON_PATH / "resources" / "secret1.txt"
SECRET2_FILE_PATH = ADDON_PATH / "resources" / "secret2.txt"

SECRET1 = ""
SECRET2 = ""
if SECRET1_FILE_PATH.exists():
    SECRET1 = SECRET1_FILE_PATH.read_text(encoding="utf-8").strip()
if SECRET2_FILE_PATH.exists():
    SECRET2 = SECRET2_FILE_PATH.read_text(encoding="utf-8").strip()

@dataclass
class KeyInfo:
    key: bytes
    iv: bytes

def hex_string_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)

def parse_key_info(secret: str) -> Optional[KeyInfo]:
    try:
        key_hex, iv_hex = secret.split(":")
        return KeyInfo(
            key=hex_string_to_bytes(key_hex),
            iv=hex_string_to_bytes(iv_hex),
        )
    except:
        return None

def keys():
    keys = {}
    if SECRET1:
        key1 = parse_key_info(SECRET1)
        if key1:
            keys["key1"] = key1
    if SECRET2:
        key2 = parse_key_info(SECRET2)
        if key2:
            keys["key2"] = key2
    return keys

def decrypt_data(encrypted_base64: str) -> Optional[str]:
    try:
        clean_base64 = (
            encrypted_base64.strip()
            .replace("\n", "")
            .replace("\r", "")
            .replace(" ", "")
            .replace("\t", "")
        )
        ciphertext = base64.b64decode(clean_base64)
        for key_info in keys().values():
            result = try_decrypt(ciphertext, key_info)
            if result is not None:
                return result
        log_error("crypto_utils", "Decryption failed with all keys.")
        return None
    except Exception as e:
        log_error("crypto_utils", f"Decryption failed: {e}")
        return None

def try_decrypt(ciphertext: bytes, key_info: KeyInfo) -> Optional[str]:
    try:
        cipher = AES.new(key_info.key, AES.MODE_CBC, key_info.iv)
        decrypted = cipher.decrypt(ciphertext)
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]
        text = decrypted.decode("utf-8")
        if text.startswith("{") or text.startswith("[") or "http" in text.lower():
            return text
        return None
    except Exception:
        return None

def decrypt_content(content: str) -> str:
    try:
        if (content.startswith("#EXTM3U") or
            content.startswith("#EXTINF") or
            content.startswith("#KODIPROP")):
            return content
        
        trimmed_content = content.strip()
        if len(trimmed_content) < 79:
            return trimmed_content
        
        part1 = trimmed_content[0:10]
        part2 = trimmed_content[34:-54]
        part3 = trimmed_content[-10:]
        encrypted_data_str = part1 + part2 + part3
        iv_base64 = trimmed_content[10:34]
        key_base64 = trimmed_content[-54:-10]
        
        iv = base64.b64decode(iv_base64)
        key = base64.b64decode(key_base64)
        encrypted_bytes = base64.b64decode(encrypted_data_str)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_bytes)
        decrypted_data = unpad(decrypted_padded, AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        log_error("crypto_utils", f"Content decryption failed: {e}")
        return content