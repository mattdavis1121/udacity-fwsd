import hmac
from hashlib import sha256
from random import choice
from string import letters

secret = 'msP24sb1nfe$tBzxRQxwuW1V&BK5uVx95Y'

def hash_str(s):
    return hmac.new(secret, s).hexdigest()

def make_secure_val(s):
    return "{}|{}".format(str(s), hash_str(str(s)))

def check_secure_val(h):
    val, hash_val = h.split('|')
    if h == make_secure_val(val):
        return val

def make_salt():
    return ''.join(choice(letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    hash_val = hash_str(name+pw+salt)
    return "{}|{}".format(hash_val, salt)

def valid_pw(name, pw, hash_val):
    salt = hash_val.split('|')[-1]
    return hash_val == make_pw_hash(name, pw, salt)
