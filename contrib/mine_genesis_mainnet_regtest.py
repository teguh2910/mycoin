#!/usr/bin/env python3
"""
Mine genesis block for MyCoin mainnet with regtest difficulty
"""

import hashlib
import struct
import time

def double_sha256(data):
    """Calculate SHA256(SHA256(data))"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def bits_to_target(bits):
    """Convert compact bits representation to target value"""
    exponent = bits >> 24
    mantissa = bits & 0xffffff
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    return target

def check_pow(hash_bytes, bits):
    """Check if hash meets proof-of-work requirement"""
    target = bits_to_target(bits)
    hash_num = int.from_bytes(hash_bytes, byteorder='little')
    return hash_num < target

def mine_genesis():
    """Mine genesis block"""
    # Genesis block parameters
    version = 1
    prev_block = b'\x00' * 32
    # Bitcoin's merkle root (unchanging)
    merkle_root = bytes.fromhex('4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b')[::-1]
    timestamp = 1231006505  # Bitcoin's timestamp
    bits = 0x207fffff  # Regtest difficulty
    
    print("=" * 70)
    print("MYCOIN GENESIS BLOCK MINER")
    print("=" * 70)
    print(f"Timestamp: {timestamp}")
    print(f"Bits: 0x{bits:08x}")
    print(f"Target: {bits_to_target(bits):064x}")
    print(f"Merkle Root: {merkle_root[::-1].hex()}")
    print()
    print("Mining genesis block...")
    print()
    
    nonce = 0
    start_time = time.time()
    
    while True:
        # Build block header
        header = struct.pack('<I', version)
        header += prev_block
        header += merkle_root
        header += struct.pack('<I', timestamp)
        header += struct.pack('<I', bits)
        header += struct.pack('<I', nonce)
        
        # Calculate hash
        hash_result = double_sha256(header)
        
        # Check if valid
        if check_pow(hash_result, bits):
            elapsed = time.time() - start_time
            hash_hex = hash_result[::-1].hex()
            
            print("=" * 70)
            print("✅ GENESIS BLOCK FOUND!")
            print("=" * 70)
            print(f"Block Hash: {hash_hex}")
            print(f"Nonce: {nonce}")
            print(f"Time: {elapsed:.2f} seconds")
            print()
            print("=" * 70)
            print("UPDATE chainparams.cpp with:")
            print("=" * 70)
            print(f'genesis = CreateGenesisBlock(1231006505, {nonce}, 0x207fffff, 1, 50 * COIN);')
            print(f'assert(consensus.hashGenesisBlock == uint256{{"{hash_hex}"}});')
            print(f'assert(genesis.hashMerkleRoot == uint256{{"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"}});')
            print("=" * 70)
            break
        
        nonce += 1
        
        # Progress indicator
        if nonce % 10000 == 0:
            elapsed = time.time() - start_time
            rate = nonce / elapsed if elapsed > 0 else 0
            print(f"Nonce: {nonce:,} | Rate: {rate:,.0f} H/s | Time: {elapsed:.1f}s", end='\r')

if __name__ == "__main__":
    mine_genesis()
