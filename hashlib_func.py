# ===========================================
# @Time    : 2018/5/19 10:40
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : hashlib_func.py
# @Software: PyCharm Community Edition
# ===========================================
import hashlib


def sha2str(str_, hash_func=hashlib.sha3_256):
    encoded_str = str(str_).encode()
    return hash_func(encoded_str).hexdigest()