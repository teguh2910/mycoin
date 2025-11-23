#!/usr/bin/env python3
"""
MyCoin Genesis Block Miner v2
Mines a new genesis block with proper hash
"""

import hashlib
import struct
import time

def sha256d(data):
    """Double SHA256"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def uint256_from_bytes(s):
    """Convert bytes to uint256 (little endian)"""
    return int.from_bytes(s[:32], byteorder='little')

def uint256_to_hex(n):
    """Convert uint256 to hex string (big endian for display)"""
    return format(n, '064x')

def mine_genesis_block():
    """Mine MyCoin genesis block"""
    
    # Genesis block parameters
    VERSION = 1
    PREV_BLOCK = b'\x00' * 32
    TIMESTAMP = 1732291200  # Nov 22, 2025
    BITS = 0x1d00ffff
    
    # Merkle root from coinbase transaction
    # This comes from the CreateGenesisBlock function
    # For MyCoin with message: "MyCoin 22/Nov/2025 A New Cryptocurrency Network Is Born"
    MERKLE_ROOT_HEX = "845d34eb785f665b39618d20f5a0d9dae6b9f007ce485788213d2d022b345be0"
    MERKLE_ROOT = bytes.fromhex(MERKLE_ROOT_HEX)[::-1]  # Reverse for little endian
    
    print("=" * 70)
    print("MyCoin Genesis Block Miner v2")
    print("=" * 70)
    print(f"Timestamp: {TIMESTAMP} ({time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(TIMESTAMP))})")
    print(f"Bits: 0x{BITS:08x}")
    print(f"Merkle Root: {MERKLE_ROOT_HEX}")
    print("=" * 70)
    print("Mining... (this may take a while)")
    print()
    
    # Target from bits
    exponent = BITS >> 24
    mantissa = BITS & 0xffffff
    target = mantissa * (256 ** (exponent - 3))
    
    print(f"Target: {uint256_to_hex(target)}")
    print()
    
    nonce = 0
    start_time = time.time()
    
    while True:
        # Build block header
        header = struct.pack('<I', VERSION)      # 4 bytes version
        header += PREV_BLOCK                      # 32 bytes prev block
        header += MERKLE_ROOT                     # 32 bytes merkle root
        header += struct.pack('<I', TIMESTAMP)    # 4 bytes timestamp
        header += struct.pack('<I', BITS)         # 4 bytes bits
        header += struct.pack('<I', nonce)        # 4 bytes nonce
        
        # Hash the header
        hash_result = sha256d(header)
        hash_int = uint256_from_bytes(hash_result)
        
        # Check if we found a valid block
        if hash_int < target:
            elapsed = time.time() - start_time
            hash_hex = uint256_to_hex(uint256_from_bytes(hash_result[::-1]))
            
            print("=" * 70)
            print("✅ GENESIS BLOCK FOUND!")
            print("=" * 70)
            print(f"Nonce: {nonce}")
            print(f"Hash: {hash_hex}")
            print(f"Time elapsed: {elapsed:.2f} seconds")
            print(f"Hash rate: {nonce/elapsed:.2f} H/s")
            print("=" * 70)
            print()
            print("📝 Update src/kernel/chainparams.cpp with these values:")
            print()
            print("MAINNET:")
            print(f"    genesis = CreateGenesisBlock({TIMESTAMP}, {nonce}, 0x{BITS:08x}, 1, 50 * COIN);")
            print(f"    consensus.hashGenesisBlock = genesis.GetHash();")
            print(f'    assert(consensus.hashGenesisBlock == uint256{{"0x{hash_hex}"}});')
            print(f'    assert(genesis.hashMerkleRoot == uint256{{"0x{MERKLE_ROOT_HEX}"}});')
            print()
            
            # Calculate testnet values (different timestamp)
            print("TESTNET (use same nonce, update timestamp if needed):")
            print(f"    genesis = CreateGenesisBlock({TIMESTAMP}, {nonce}, 0x{BITS:08x}, 1, 50 * COIN);")
            print()
            
            break
        
        # Progress update every 100000 attempts
        if nonce % 100000 == 0 and nonce > 0:
            elapsed = time.time() - start_time
            rate = nonce / elapsed if elapsed > 0 else 0
            print(f"Nonce: {nonce:,} | Hash rate: {rate:.2f} H/s | Time: {elapsed:.1f}s")
        
        nonce += 1
        
        # Safety limit (can remove if you want unlimited)
        if nonce > 100000000:
            print("Reached 100M attempts, stopping...")
            print("Try with different timestamp or parameters")
            break

if __name__ == "__main__":
    mine_genesis_block()
