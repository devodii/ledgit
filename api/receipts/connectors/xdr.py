import base64
import struct

CONTRACT_DATA = 6
SC_ADDRESS_CONTRACT = 1
SCV_LEDGER_KEY_CONTRACT_INSTANCE = 20
DURABILITY_PERSISTENT = 1


def decode_contract_id(strkey: str) -> bytes:
    raw = base64.b32decode(strkey + "=" * (-len(strkey) % 8))
    if len(raw) != 35 or raw[0] != 2 << 3:
        raise ValueError(f"not a contract strkey: {strkey}")
    return raw[1:33]


def contract_instance_key(contract_id: str) -> str:
    key = (
        struct.pack(">II", CONTRACT_DATA, SC_ADDRESS_CONTRACT)
        + decode_contract_id(contract_id)
        + struct.pack(">II", SCV_LEDGER_KEY_CONTRACT_INSTANCE, DURABILITY_PERSISTENT)
    )
    return base64.b64encode(key).decode()
