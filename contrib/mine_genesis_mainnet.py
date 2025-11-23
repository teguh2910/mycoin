#!/usr/bin/env python3
"""Mine genesis block for MyCoin mainnet with easy difficulty"""

import hashlib
import struct
import time

def dblsha256(data):
    """Double SHA256 hash"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def check_pow(hash_bytes, bits):
    """Check if hash meets the proof of work requirement"""
    # Convert bits to target
    exponent = bits >> 24
    mantissa = bits & 0xffffff
    
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    
    # Convert hash to number (little endian)
    hash_num = int.from_bytes(hash_bytes, byteorder='little')
    
    return hash_num < target

def mine_genesis():
    # Genesis parameters
    timestamp = 1231006505  # Bitcoin's original timestamp
    bits = 0x207fffff       # Regtest difficulty (very easy)
    version = 1
    
    # Merkle root is always the same (from coinbase tx)
    merkle_root = bytes.fromhex("4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b")
    prev_hash = b'\x00' * 32
    
    print(f"Mining genesis block...")
    print(f"Timestamp: {timestamp}")
    print(f"Bits: 0x{bits:08x}")
    print(f"Merkle root: {merkle_root.hex()}")
    print()
    
    start_time = time.time()
    nonce = 0
    
    while nonce < 1000000:
        # Build block header
        header = struct.pack("<I", version)      # version
        header += prev_hash                       # prev block hash
        header += merkle_root                     # merkle root
        header += struct.pack("<I", timestamp)    # timestamp
        header += struct.pack("<I", bits)         # bits
        header += struct.pack("<I", nonce)        # nonce
        
        # Calculate hash
        hash_result = dblsha256(header)
        hash_hex = hash_result[::-1].hex()  # Reverse for display
        
        # Check if it meets difficulty
        if check_pow(hash_result, bits):
            elapsed = time.time() - start_time
            print(f"✓ Found valid genesis block!")
            print(f"  Hash: {hash_hex}")
            print(f"  Nonce: {nonce}")
            print(f"  Time: {elapsed:.2f} seconds")
            print()
            print("Update chainparams.cpp with:")
            print(f'  genesis = CreateGenesisBlock({timestamp}, {nonce}, 0x{bits:08x}, {version}, 50 * COIN);')
            print(f'  assert(consensus.hashGenesisBlock == uint256{{"{hash_hex}"}});')
            return
        
        nonce += 1
        if nonce % 100000 == 0:
            print(f"  Tried {nonce:,} nonces... (hash: {hash_hex})")
    
    print("No valid nonce found in first 1,000,000 tries")

if __name__ == "__main__":
    mine_genesis()
