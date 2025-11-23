#!/usr/bin/env python3
"""
Calculate correct Merkle Root for MyCoin Genesis Block
"""

import hashlib

def sha256(data):
    return hashlib.sha256(data).digest()

def sha256d(data):
    """Double SHA256"""
    return sha256(sha256(data))

def calculate_mycoin_merkle_root():
    """
    Calculate merkle root for MyCoin genesis coinbase transaction
    Based on CreateGenesisBlock in chainparams.cpp
    """
    
    print("=" * 70)
    print("MyCoin Genesis Block Merkle Root Calculator")
    print("=" * 70)
    
    # Genesis message
    message = b"MyCoin 22/Nov/2025 A New Cryptocurrency Network Is Born"
    
    print(f"Genesis message: {message.decode()}")
    print(f"Message length: {len(message)} bytes")
    print()
    
    # Build coinbase transaction (simplified version)
    # This matches CreateGenesisBlock function
    
    # Transaction version (4 bytes, little endian)
    version = (1).to_bytes(4, 'little')
    
    # Input count
    input_count = b'\x01'
    
    # Previous output (null for coinbase)
    prev_output = b'\x00' * 32  # Previous tx hash
    prev_output += b'\xff\xff\xff\xff'  # Previous tx output index (-1)
    
    # ScriptSig length and data
    # From CreateGenesisBlock: CScript() << 486604799 << CScriptNum(4) << message
    script_data = b'\x04'  # Push 4 bytes
    script_data += (486604799).to_bytes(4, 'little')  # nBits compact
    script_data += b'\x01\x04'  # CScriptNum(4) = push 1 byte value 4
    script_data += bytes([len(message)]) + message  # Push message
    
    script_sig_len = len(script_data).to_bytes(1, 'little')
    script_sig = script_sig_len + script_data
    
    # Sequence
    sequence = b'\xff\xff\xff\xff'
    
    # Output count
    output_count = b'\x01'
    
    # Output value (50 BTC = 50 * 100000000 satoshis)
    value = (50 * 100000000).to_bytes(8, 'little')
    
    # Output scriptPubKey
    # From code: genesisOutputScript = CScript() << pubkey_hex << OP_CHECKSIG
    pubkey = bytes.fromhex("04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f")
    script_pubkey = bytes([len(pubkey)]) + pubkey + b'\xac'  # OP_CHECKSIG = 0xac
    script_pubkey_len = len(script_pubkey).to_bytes(1, 'little')
    
    # Locktime
    locktime = b'\x00\x00\x00\x00'
    
    # Build complete transaction
    tx = version
    tx += input_count
    tx += prev_output
    tx += script_sig
    tx += sequence
    tx += output_count
    tx += value
    tx += script_pubkey_len + script_pubkey
    tx += locktime
    
    print(f"Coinbase transaction length: {len(tx)} bytes")
    print(f"Coinbase transaction hex: {tx.hex()}")
    print()
    
    # Calculate transaction hash (merkle root for genesis = single tx hash)
    tx_hash = sha256d(tx)
    
    # Reverse for display (Bitcoin displays hashes in reverse byte order)
    merkle_root_hex = tx_hash[::-1].hex()
    
    print("=" * 70)
    print("✅ MERKLE ROOT CALCULATED")
    print("=" * 70)
    print(f"Merkle Root: {merkle_root_hex}")
    print("=" * 70)
    print()
    print("Use this in mine_genesis_v2.py:")
    print(f'MERKLE_ROOT_HEX = "{merkle_root_hex}"')
    print()
    
    return merkle_root_hex

if __name__ == "__main__":
    calculate_mycoin_merkle_root()
