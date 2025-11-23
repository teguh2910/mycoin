#!/usr/bin/env python3
"""
Verify and mine genesis block for MyCoin
This script will calculate the ACTUAL hash for given parameters
"""

import hashlib
import struct

def dblsha256(data):
    """Double SHA256 hash"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def build_header(version, prev_hash, merkle_root, timestamp, bits, nonce):
    """Build block header"""
    header = struct.pack("<I", version)
    header += prev_hash
    header += merkle_root
    header += struct.pack("<I", timestamp)
    header += struct.pack("<I", bits)
    header += struct.pack("<I", nonce)
    return header

def get_hash(version, prev_hash, merkle_root, timestamp, bits, nonce):
    """Get block hash"""
    header = build_header(version, prev_hash, merkle_root, timestamp, bits, nonce)
    hash_result = dblsha256(header)
    return hash_result[::-1].hex()  # Reverse for display (big endian)

def check_pow(hash_bytes, bits):
    """Check if hash meets proof of work requirement"""
    exponent = bits >> 24
    mantissa = bits & 0xffffff
    
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    
    hash_num = int.from_bytes(hash_bytes, byteorder='little')
    return hash_num < target

# Genesis parameters
version = 1
prev_hash = b'\x00' * 32
merkle_root = bytes.fromhex("4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b")
timestamp = 1231006505
bits = 0x207fffff

print("=" * 70)
print("GENESIS BLOCK VERIFICATION & MINING")
print("=" * 70)
print()
print(f"Version:     {version}")
print(f"Prev Hash:   {prev_hash.hex()}")
print(f"Merkle Root: {merkle_root.hex()}")
print(f"Timestamp:   {timestamp}")
print(f"Bits:        0x{bits:08x}")
print()

# Test nonce = 0
print("-" * 70)
print("Testing nonce = 0:")
hash_0 = get_hash(version, prev_hash, merkle_root, timestamp, bits, 0)
print(f"  Hash: {hash_0}")
header_0 = build_header(version, prev_hash, merkle_root, timestamp, bits, 0)
valid_0 = check_pow(dblsha256(header_0), bits)
print(f"  Valid PoW: {valid_0}")
print()

# Test nonce = 1
print("-" * 70)
print("Testing nonce = 1:")
hash_1 = get_hash(version, prev_hash, merkle_root, timestamp, bits, 1)
print(f"  Hash: {hash_1}")
header_1 = build_header(version, prev_hash, merkle_root, timestamp, bits, 1)
valid_1 = check_pow(dblsha256(header_1), bits)
print(f"  Valid PoW: {valid_1}")
print()

# Test nonce = 2 (Bitcoin regtest default)
print("-" * 70)
print("Testing nonce = 2 (Bitcoin regtest):")
hash_2 = get_hash(version, prev_hash, merkle_root, timestamp, bits, 2)
print(f"  Hash: {hash_2}")
header_2 = build_header(version, prev_hash, merkle_root, timestamp, bits, 2)
valid_2 = check_pow(dblsha256(header_2), bits)
print(f"  Valid PoW: {valid_2}")
print()

# Mine to find valid nonce
print("=" * 70)
print("MINING FOR VALID NONCE...")
print("=" * 70)

found = False
for nonce in range(1000000):
    header = build_header(version, prev_hash, merkle_root, timestamp, bits, nonce)
    hash_result = dblsha256(header)
    
    if check_pow(hash_result, bits):
        hash_hex = hash_result[::-1].hex()
        print(f"\n✓ FOUND VALID GENESIS BLOCK!")
        print(f"  Nonce: {nonce}")
        print(f"  Hash:  {hash_hex}")
        print()
        print("=" * 70)
        print("UPDATE chainparams.cpp WITH:")
        print("=" * 70)
        print(f'genesis = CreateGenesisBlock({timestamp}, {nonce}, 0x{bits:08x}, {version}, 50 * COIN);')
        print(f'consensus.hashGenesisBlock = genesis.GetHash();')
        print(f'assert(consensus.hashGenesisBlock == uint256{{"{hash_hex}"}});')
        print(f'assert(genesis.hashMerkleRoot == uint256{{"{merkle_root.hex()}"}});')
        print("=" * 70)
        found = True
        break
    
    if nonce % 100000 == 0 and nonce > 0:
        print(f"  Tried {nonce:,} nonces...")

if not found:
    print("\nNo valid nonce found in first 1,000,000 tries")
