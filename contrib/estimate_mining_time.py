#!/usr/bin/env python3
"""
Estimate mining time for different difficulty levels using CPU
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

def benchmark_hashrate(duration_seconds=10):
    """Benchmark CPU hash rate"""
    print(f"Benchmarking hash rate for {duration_seconds} seconds...")
    
    # Create sample block header
    version = 1
    prev_block = b'\x00' * 32
    merkle_root = bytes.fromhex('4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b')[::-1]
    timestamp = 1231006505
    bits = 0x1d00ffff
    
    nonce = 0
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        header = struct.pack('<I', version)
        header += prev_block
        header += merkle_root
        header += struct.pack('<I', timestamp)
        header += struct.pack('<I', bits)
        header += struct.pack('<I', nonce)
        
        hash_result = double_sha256(header)
        nonce += 1
    
    elapsed = time.time() - start_time
    hashrate = nonce / elapsed
    
    return hashrate

def estimate_mining_time(hashrate, bits):
    """Estimate time to mine a block at given difficulty"""
    target = bits_to_target(bits)
    
    # Maximum possible hash value (2^256)
    max_hash = 2**256
    
    # Expected number of hashes needed
    expected_hashes = max_hash / target
    
    # Time in seconds
    time_seconds = expected_hashes / hashrate
    
    return time_seconds, expected_hashes

def format_time(seconds):
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{seconds:.2f} detik"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} menit"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.2f} jam"
    elif seconds < 31536000:
        days = seconds / 86400
        return f"{days:.2f} hari"
    else:
        years = seconds / 31536000
        return f"{years:.2f} tahun"

def main():
    print("=" * 70)
    print("ESTIMASI WAKTU MINING MYCOIN")
    print("=" * 70)
    print()
    
    # Benchmark hash rate
    hashrate = benchmark_hashrate(10)
    print(f"\n✓ Hash rate CPU Anda: {hashrate:,.0f} hash/detik ({hashrate/1000:.2f} KH/s)")
    print()
    
    # Different difficulty levels
    difficulties = [
        ("Regtest (sangat mudah)", 0x207fffff),
        ("Bitcoin Mainnet (asli)", 0x1d00ffff),
        ("Bitcoin saat ini (estimasi)", 0x1700a3b7),  # Approximate current difficulty
    ]
    
    print("=" * 70)
    print("ESTIMASI WAKTU MINING:")
    print("=" * 70)
    
    for name, bits in difficulties:
        time_seconds, expected_hashes = estimate_mining_time(hashrate, bits)
        
        print(f"\n{name} (bits: 0x{bits:08x})")
        print(f"  Target: {bits_to_target(bits)}")
        print(f"  Expected hashes: {expected_hashes:.2e}")
        print(f"  Estimasi waktu: {format_time(time_seconds)}")
        
        if time_seconds > 86400:  # More than 1 day
            print(f"  ⚠️  PERHATIAN: Terlalu lama untuk CPU mining!")
    
    print("\n" + "=" * 70)
    print("REKOMENDASI:")
    print("=" * 70)
    
    # Check Bitcoin mainnet time
    btc_time, _ = estimate_mining_time(hashrate, 0x1d00ffff)
    regtest_time, _ = estimate_mining_time(hashrate, 0x207fffff)
    
    if btc_time > 86400:  # More than 1 day
        print("\n❌ Bitcoin mainnet difficulty (0x1d00ffff) TERLALU TINGGI untuk CPU mining!")
        print(f"   Estimasi waktu: {format_time(btc_time)}")
        print("\n✅ Gunakan REGTEST mode untuk testing:")
        print("   - Difficulty sangat rendah (0x207fffff)")
        print(f"   - Estimasi waktu per block: {format_time(regtest_time)}")
        print("   - Cocok untuk development dan testing")
        print("\n💡 Atau modifikasi mainnet dengan fPowAllowMinDifficultyBlocks = true")
        print("   untuk mendapatkan difficulty rendah seperti regtest")
    else:
        print("\n✅ CPU Anda dapat mining di mainnet!")
        print(f"   Estimasi waktu per block: {format_time(btc_time)}")
    
    print("\n" + "=" * 70)
    
    # Performance comparison with ASIC
    print("\nPERBANDINGAN PERFORMA:")
    print("=" * 70)
    print(f"CPU Core i3 Gen 10:  {hashrate/1000:,.2f} KH/s")
    print(f"GPU RTX 3060:        ~50,000 KH/s (estimasi)")
    print(f"ASIC Antminer S19:   ~110,000,000 KH/s")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
