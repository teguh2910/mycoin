#!/usr/bin/env python3
"""
Multi-threaded CPU mining for MyCoin
Allows precise CPU usage control
"""

import subprocess
import json
import multiprocessing
import time
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
MYCOIN_CLI = "./bin/mycoin-cli"
CPU_USAGE_PERCENT = 80  # Target CPU usage
UPDATE_INTERVAL = 2     # Seconds between checks

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_flag
    print("\n\n🛑 Stopping mining... (Tunggu mining yang sedang berjalan selesai)")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)

def run_rpc(command):
    """Execute mycoin-cli RPC command"""
    try:
        result = subprocess.run(
            [MYCOIN_CLI] + command.split(),
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout per block
        )
        return json.loads(result.stdout) if result.stdout.strip() else None
    except subprocess.TimeoutExpired:
        print("⚠️  Mining timeout - retrying...")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ RPC Error: {e.stderr}")
        return None
    except json.JSONDecodeError:
        return result.stdout.strip()

def mine_single_block(address, worker_id):
    """Mine a single block"""
    if shutdown_flag:
        return None
    
    start_time = time.time()
    print(f"[Worker-{worker_id}] ⛏️  Mining block...")
    
    try:
        result = subprocess.run(
            [MYCOIN_CLI, "generatetoaddress", "1", address],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            elapsed = time.time() - start_time
            block_hash = json.loads(result.stdout)[0] if result.stdout.strip() != "[]" else None
            return {
                'worker_id': worker_id,
                'elapsed': elapsed,
                'hash': block_hash,
                'success': True
            }
    except Exception as e:
        print(f"[Worker-{worker_id}] ❌ Error: {e}")
    
    return {'worker_id': worker_id, 'success': False}

def get_mining_address():
    """Get or create mining address"""
    # Check if wallet exists
    wallets = run_rpc("listwallets")
    if not wallets or "mywallet" not in wallets:
        print("📝 Membuat wallet 'mywallet'...")
        run_rpc("createwallet mywallet")
        time.sleep(1)
    
    # Get new address
    address = run_rpc("getnewaddress")
    return address

def get_stats():
    """Get current blockchain stats"""
    blockcount = run_rpc("getblockcount")
    balance = run_rpc("getbalance")
    mining_info = run_rpc("getmininginfo")
    
    return {
        'blocks': blockcount,
        'balance': float(balance) if balance else 0,
        'difficulty': mining_info.get('difficulty', 0) if mining_info else 0
    }

def main():
    """Main mining loop with multi-threading"""
    print("=" * 80)
    print("🚀 MYCOIN MULTI-THREADED CPU MINER")
    print("=" * 80)
    print()
    
    # Calculate number of workers
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * CPU_USAGE_PERCENT / 100))
    
    print(f"💻 CPU Cores Detected: {total_cores}")
    print(f"🎯 Target CPU Usage: {CPU_USAGE_PERCENT}%")
    print(f"⚙️  Mining Threads: {num_workers}")
    print()
    
    # Get mining address
    print("🔑 Getting mining address...")
    address = get_mining_address()
    print(f"   Address: {address}")
    print()
    
    # Initial stats
    initial_stats = get_stats()
    print(f"📊 Initial Stats:")
    print(f"   Blocks: {initial_stats['blocks']}")
    print(f"   Balance: {initial_stats['balance']:.8f} MYC")
    print(f"   Difficulty: {initial_stats['difficulty']}")
    print()
    
    print("⛏️  Starting mining...")
    print(f"   (Using {num_workers} parallel workers)")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    blocks_mined = 0
    start_time = time.time()
    
    # Mining loop
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        worker_id = 0
        
        while not shutdown_flag:
            # Submit mining jobs
            while len(futures) < num_workers and not shutdown_flag:
                future = executor.submit(mine_single_block, address, worker_id)
                futures.append(future)
                worker_id += 1
            
            # Check completed jobs
            done_futures = []
            for future in as_completed(futures, timeout=1):
                result = future.result()
                if result and result.get('success'):
                    blocks_mined += 1
                    
                    # Get updated stats
                    stats = get_stats()
                    elapsed_total = time.time() - start_time
                    
                    print(f"\n✅ Block #{stats['blocks']} mined!")
                    print(f"   Worker: {result['worker_id']}")
                    print(f"   Time: {result['elapsed']:.2f}s")
                    if result.get('hash'):
                        print(f"   Hash: {result['hash'][:16]}...")
                    print(f"   Balance: {stats['balance']:.8f} MYC")
                    print(f"   Total Mined: {blocks_mined} blocks")
                    if elapsed_total > 0:
                        rate = blocks_mined / elapsed_total * 3600
                        print(f"   Rate: {rate:.2f} blocks/jam")
                    print("-" * 80)
                
                done_futures.append(future)
            
            # Remove completed futures
            for future in done_futures:
                futures.remove(future)
            
            # Small delay
            time.sleep(0.1)
    
    print("\n" + "=" * 80)
    print("📊 MINING SESSION SUMMARY")
    print("=" * 80)
    
    final_stats = get_stats()
    elapsed = time.time() - start_time
    
    print(f"⏱️  Total Time: {elapsed/60:.2f} minutes")
    print(f"⛏️  Blocks Mined: {blocks_mined}")
    print(f"💰 Total Earned: {blocks_mined * 50:.2f} MYC")
    print(f"💵 Final Balance: {final_stats['balance']:.8f} MYC")
    if elapsed > 0:
        print(f"📈 Average Rate: {blocks_mined / elapsed * 3600:.2f} blocks/hour")
    print("=" * 80)
    print("\n👋 Mining stopped. Goodbye!")

if __name__ == "__main__":
    main()
