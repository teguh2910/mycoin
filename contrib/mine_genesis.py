#!/usr/bin/env python3
"""
Genesis Block Miner for MyCoin
This script will mine a valid genesis block by finding the correct nonce.
"""

import hashlib
import struct
import time

def dblsha256(data):
    """Double SHA256 hash"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def build_block_header(version, prev_block, merkle_root, timestamp, bits, nonce):
    """Build block header"""
    header = struct.pack('<I', version)
    header += bytes.fromhex(prev_block)[::-1]
    header += bytes.fromhex(merkle_root)[::-1]
    header += struct.pack('<I', timestamp)
    header += struct.pack('<I', bits)
    header += struct.pack('<I', nonce)
    return header

def mine_genesis_block(merkle_root, timestamp, bits, target_prefix="000000"):
    """
    Mine genesis block by finding valid nonce
    """
    version = 1
    prev_block = "0" * 64  # All zeros for genesis block
    
    print(f"Mining genesis block...")
    print(f"Merkle Root: {merkle_root}")
    print(f"Timestamp: {timestamp}")
    print(f"Bits: 0x{bits:08x}")
    print(f"Target: Hash must start with '{target_prefix}'")
    print()
    
    nonce = 0
    start_time = time.time()
    
    while True:
        header = build_block_header(version, prev_block, merkle_root, timestamp, bits, nonce)
        block_hash = dblsha256(header)
        block_hash_hex = block_hash[::-1].hex()
        
        if nonce % 100000 == 0:
            elapsed = time.time() - start_time
            if elapsed > 0:
                hashrate = nonce / elapsed
                print(f"Nonce: {nonce:,} | Hash: {block_hash_hex[:16]}... | Rate: {hashrate:,.0f} H/s", end='\r')
        
        if block_hash_hex.startswith(target_prefix):
            print()
            print()
            print("=" * 70)
            print("SUCCESS! Genesis block found!")
            print("=" * 70)
            print(f"Block Hash: {block_hash_hex}")
            print(f"Nonce: {nonce}")
            print(f"Time taken: {time.time() - start_time:.2f} seconds")
            print()
            print("Update chainparams.cpp with:")
            print(f"  genesis = CreateGenesisBlock({timestamp}, {nonce}, 0x{bits:08x}, 1, 50 * COIN);")
            print(f"  consensus.hashGenesisBlock == uint256{{\"{block_hash_hex}\"}}")
            print(f"  genesis.hashMerkleRoot == uint256{{\"{merkle_root}\"}}")
            return nonce, block_hash_hex
        
        nonce += 1
        
        # Safety limit
        if nonce > 5000000000:
            print("\nReached nonce limit. Try different timestamp or bits.")
            return None, None

if __name__ == "__main__":
    # MyCoin genesis block parameters
    # You'll need to get the merkle root from building the project first
    # For now, we'll use a placeholder and calculate it
    
    print("MyCoin Genesis Block Miner")
    print("=" * 70)
    print()
    
    # Default parameters
    # The merkle root needs to be calculated from the coinbase transaction
    # This is just a placeholder - you'll need to run the daemon once to get the real merkle root
    merkle_root = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    timestamp = 1732291200  # Nov 22, 2025
    bits = 0x1d00ffff
    
    print("NOTE: Run the MyCoin daemon once first to get the actual merkle root hash.")
    print("      Then update the merkle_root variable in this script and run again.")
    print()
    
    mine_genesis_block(merkle_root, timestamp, bits, "000000")
