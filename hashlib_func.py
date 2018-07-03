# ===========================================
# @Time    : 2018/5/19 10:40
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : hashlib_func.py
# @Software: PyCharm Community Edition
# ===========================================
import sys
import hashlib
# 最好还是用python3.6
if sys.version_info < (3, 6):
    import sha3


def sha2str(str_, hash_func=hashlib.sha3_256):
    encoded_str = str(str_).encode()
    return hash_func(encoded_str).hexdigest()