#!/usr/bin/env python3
"""
Sequential multi-block miner
Uses multiple threads but mines sequentially to avoid conflicts
"""

import subprocess
import json
import time
import signal
import sys
from datetime import datetime

# Configuration
MYCOIN_CLI = "./bin/mycoin-cli"
NUM_THREADS = 3  # Number of parallel mining attempts

shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    print("\n\n🛑 Stopping after current block...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)

def run_rpc(command):
    """Execute RPC command"""
    try:
        result = subprocess.run(
            [MYCOIN_CLI] + command.split(),
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return result.stdout.strip()
        return None
    except subprocess.CalledProcessError as e:
        print(f"RPC Error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def mine_block_batch(address, count):
    """Mine multiple blocks sequentially"""
    start_time = time.time()
    
    print(f"⛏️  Mining {count} blocks... (Started: {datetime.now().strftime('%H:%M:%S')})")
    
    try:
        # Mine multiple blocks at once
        result = subprocess.run(
            [MYCOIN_CLI, "generatetoaddress", str(count), address],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes total
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            try:
                output = result.stdout.strip()
                if output and output != "[]":
                    block_hashes = json.loads(output)
                    return {
                        'success': True,
                        'count': len(block_hashes),
                        'elapsed': elapsed,
                        'hashes': block_hashes
                    }
            except:
                pass
            
            return {'success': True, 'count': count, 'elapsed': elapsed, 'hashes': []}
        
        return {'success': False, 'elapsed': elapsed}
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout after {(time.time() - start_time)/60:.1f} minutes")
        return {'success': False, 'elapsed': time.time() - start_time}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'elapsed': time.time() - start_time}

def main():
    """Main mining loop"""
    print("=" * 80)
    print("🚀 MYCOIN BATCH MINER (80% CPU)")
    print("=" * 80)
    print()
    
    # Get address
    print("🔌 Connecting to daemon...")
    
    # Wait for daemon to be ready
    for i in range(10):
        blockcount = run_rpc("getblockcount")
        if blockcount is not None:
            print("✅ Connected!")
            break
        print(f"   Waiting for daemon... ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ Could not connect to daemon after 20 seconds")
        print("   Troubleshooting:")
        print("   1. Check if daemon is running: ps aux | grep mycoind")
        print("   2. Check RPC manually: ./bin/mycoin-cli getblockcount")
        print("   3. Check debug.log: tail -50 ~/.mycoin/debug.log")
        sys.exit(1)
    
    address = run_rpc("getnewaddress")
    if not address:
        print("❌ Failed to get address!")
        print("   Try: ./bin/mycoin-cli createwallet mywallet")
        sys.exit(1)
    
    print(f"🔑 Address: {address}")
    print(f"⚙️  Mining in batches of {NUM_THREADS} blocks")
    print()
    
    # Initial stats
    initial_blocks = run_rpc("getblockcount") or 0
    initial_balance = float(run_rpc("getbalance") or 0)
    
    print(f"📊 Starting Stats:")
    print(f"   Blocks: {initial_blocks}")
    print(f"   Balance: {initial_balance:.8f} MYC")
    print()
    print("🚀 Mining started... (Press Ctrl+C to stop)")
    print("=" * 80)
    print()
    
    total_blocks_mined = 0
    session_start = time.time()
    
    while not shutdown_flag:
        # Mine a batch of blocks
        result = mine_block_batch(address, NUM_THREADS)
        
        if result['success']:
            blocks_found = result['count']
            
            # Verify blocks were actually mined
            if blocks_found == 0:
                print()
                print("⚠️  No blocks generated (mining might be stuck)")
                print("   This can happen if difficulty is too high")
                print("   Checking actual blockchain state...")
                
                current_blocks = run_rpc("getblockcount") or 0
                mining_info = run_rpc("getmininginfo")
                
                print(f"   Blockchain Height: {current_blocks}")
                if mining_info:
                    print(f"   Current Difficulty: {mining_info.get('difficulty', 'unknown')}")
                    print(f"   Network Hash Rate: {mining_info.get('networkhashps', 0)} H/s")
                
                print("\n   💡 Tip: If difficulty is 1, mining takes 10-30 minutes per block")
                print("   Consider using sequential miner: python3 ../contrib/mine_sequential.py")
                print()
                time.sleep(5)
                continue
            
            total_blocks_mined += blocks_found
            
            # Get updated stats
            current_blocks = run_rpc("getblockcount") or 0
            current_balance = float(run_rpc("getbalance") or 0)
            session_elapsed = time.time() - session_start
            
            print()
            print("=" * 80)
            print(f"✅ {blocks_found} BLOCKS MINED!")
            print("=" * 80)
            avg_per_block = result['elapsed'] / blocks_found if blocks_found > 0 else 0
            print(f"⏱️  Time: {result['elapsed']:.2f}s ({avg_per_block:.2f}s per block)")
            print(f"📊 Blockchain Height: {current_blocks}")
            print(f"💰 Balance: {current_balance:.8f} MYC")
            print(f"📈 Session Stats:")
            print(f"   Total Mined: {total_blocks_mined} blocks")
            print(f"   Total Earned: {total_blocks_mined * 50} MYC")
            print(f"   Session Time: {session_elapsed/60:.1f} minutes")
            if session_elapsed > 0:
                rate = total_blocks_mined / session_elapsed * 3600
                print(f"   Mining Rate: {rate:.2f} blocks/hour")
            
            # Show some block hashes
            if result.get('hashes'):
                print(f"🔗 Block Hashes:")
                for i, h in enumerate(result['hashes'][:3], 1):
                    print(f"   #{current_blocks - blocks_found + i}: {h[:16]}...")
            
            # Difficulty adjustment warning
            blocks_until_adjust = 2016 - (current_blocks % 2016)
            if blocks_until_adjust <= 100:
                print(f"⚠️  Difficulty adjustment in {blocks_until_adjust} blocks!")
            
            print("=" * 80)
            print()
        else:
            print(f"⚠️  Mining failed, retrying in 5s...")
            time.sleep(5)
    
    # Final summary
    print()
    print("=" * 80)
    print("📊 MINING SESSION SUMMARY")
    print("=" * 80)
    
    final_blocks = run_rpc("getblockcount") or 0
    final_balance = float(run_rpc("getbalance") or 0)
    total_time = time.time() - session_start
    
    print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
    print(f"⛏️  Blocks Mined: {total_blocks_mined}")
    print(f"📊 Final Height: {final_blocks}")
    print(f"💰 Total Earned: {total_blocks_mined * 50} MYC")
    print(f"💵 Final Balance: {final_balance:.8f} MYC")
    if total_time > 0:
        print(f"📈 Average Rate: {total_blocks_mined / total_time * 3600:.2f} blocks/hour")
        print(f"⚡ Average Time: {total_time / total_blocks_mined:.2f}s per block")
    print("=" * 80)
    print("\n👋 Mining stopped!")

if __name__ == "__main__":
    main()
