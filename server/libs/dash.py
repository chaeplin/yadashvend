import binascii, re, json, copy, sys
import base64
import bitcoin
import random
from pycoin.key import Key
from hashlib import sha256
from bitcoin import SelectParams
from bitcoin.wallet import P2PKHBitcoinAddress, CBitcoinAddressError

class MainParams(bitcoin.core.CoreMainParams):
    BASE58_PREFIXES = {'PUBKEY_ADDR': 76, 'SCRIPT_ADDR': 16, 'SECRET_KEY': 204}

class TestNetParams(bitcoin.core.CoreTestNetParams):
    BASE58_PREFIXES = {'PUBKEY_ADDR': 140, 'SCRIPT_ADDR': 19, 'SECRET_KEY': 239}

bitcoin.params = bitcoin.MainParams = TestNetParams

string_types = (str, unicode)
string_or_bytes_types = string_types
int_types = (int, float, long)

code_strings = {
    2: '01',
    10: '0123456789',
    16: '0123456789abcdef',
    32: 'abcdefghijklmnopqrstuvwxyz234567',
    58: '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    256: ''.join([chr(x) for x in range(256)])
}

def JSONtoAmount(value):
    return long(round(value * 1e8))

def AmountToJSON(amount):
    return float(amount / 1e8)

def safe_hexlify(a):
    return binascii.hexlify(a)

def from_byte_to_int(a):
    return ord(a)

def get_code_string(base):
    if base in code_strings:
        return code_strings[base]
    else:
        raise ValueError("Invalid base!")

def decode(string, base):
    base = int(base)
    code_string = get_code_string(base)
    result = 0
    if base == 16:
        string = string.lower()
    while len(string) > 0:
        result *= base
        result += code_string.find(string[0])
        string = string[1:]
    return result

def json_changebase(obj, changer):
    if isinstance(obj, string_or_bytes_types):
        return changer(obj)
    elif isinstance(obj, int_types) or obj is None:
        return obj
    elif isinstance(obj, list):
        return [json_changebase(x, changer) for x in obj]
    return dict((x, json_changebase(obj[x], changer)) for x in obj)

def deserialize(tx):
    if isinstance(tx, str) and re.match('^[0-9a-fA-F]*$', tx):
        return json_changebase(deserialize(binascii.unhexlify(tx)),
                              lambda x: safe_hexlify(x))
    pos = [0]

    def read_as_int(bytez):
        pos[0] += bytez
        return decode(tx[pos[0]-bytez:pos[0]][::-1], 256)

    def read_var_int():
        pos[0] += 1

        val = from_byte_to_int(tx[pos[0]-1])
        if val < 253:
            return val
        return read_as_int(pow(2, val - 252))

    def read_bytes(bytez):
        pos[0] += bytez
        return tx[pos[0]-bytez:pos[0]]

    def read_var_string():
        size = read_var_int()
        return read_bytes(size)

    obj = {"ins": [], "outs": []}
    obj["version"] = read_as_int(4)
    ins = read_var_int()
    for i in range(ins):
        obj["ins"].append({
            "outpoint": {
                "hash": read_bytes(32)[::-1],
                "index": read_as_int(4)
            },
            "script": read_var_string(),
            "sequence": read_as_int(4)
        })
    outs = read_var_int()
    for i in range(outs):
        obj["outs"].append({
            "value": read_as_int(8),
            "script": read_var_string()
        })
    obj["locktime"] = read_as_int(4)

    return obj['outs']
#    return obj
#
#
#def gettxid(rawtx):
#    data = rawtx.decode("hex")
#    hash = sha256(sha256(data).digest()).digest()
#    return hash[::-1].encode('hex_codec')

def decoderawtx(rawtx):
    vout = deserialize(rawtx)
    txid = sha256(sha256(rawtx.decode("hex")).digest()).digest()[::-1].encode('hex_codec')

    addrval = {}

    for x in vout:
        script = x['script']
        value  = x['value']

        try:
            address = str(P2PKHBitcoinAddress.from_scriptPubKey(binascii.unhexlify(script)))
            value   = str('{0:.8f}'.format(float(value / 1e8)))
            addrval[address] = {'val': value, 'txid': txid}

        except:
            pass

    return addrval

def get_bip32_address_info(key, index):
    addr = key.subkey(index).address(use_uncompressed=False)
    return { "index": index, "addr": addr }

def get_sale_price():
    return round(random.uniform(0.02, 2), 3)
# end
