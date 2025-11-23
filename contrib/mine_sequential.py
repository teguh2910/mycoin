#!/usr/bin/env python3
"""
Single-threaded sequential miner for difficulty 1
More stable for slow mining
"""

import subprocess
import json
import time
import signal
import sys
from datetime import datetime, timedelta

# Configuration
MYCOIN_CLI = "./bin/mycoin-cli"

# Global flag
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global shutdown_flag
    print("\n\n🛑 Stopping mining after current block...")
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
        # Wallet might not be loaded, try to handle it
        if "Wallet not found" in str(e.stderr) or "Requested wallet does not exist" in str(e.stderr):
            return "WALLET_ERROR"
        return None
    except Exception:
        return None

def mine_one_block(address):
    """Mine a single block and return result"""
    start_time = time.time()
    
    try:
        print(f"⛏️  Mining block... (Started: {datetime.now().strftime('%H:%M:%S')})")
        
        # Run mining command
        result = subprocess.run(
            [MYCOIN_CLI, "generatetoaddress", "1", address],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour max per block
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # Parse result
            try:
                output = result.stdout.strip()
                if output and output != "[]":
                    block_data = json.loads(output)
                    block_hash = block_data[0] if isinstance(block_data, list) and len(block_data) > 0 else "unknown"
                else:
                    block_hash = "unknown"
            except:
                block_hash = "unknown"
            
            return {
                'success': True,
                'elapsed': elapsed,
                'hash': block_hash
            }
        else:
            print(f"❌ Mining failed: {result.stderr}")
            return {'success': False, 'elapsed': elapsed}
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"⏰ Timeout after {elapsed/60:.1f} minutes!")
        return {'success': False, 'elapsed': elapsed}
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error: {e}")
        return {'success': False, 'elapsed': elapsed}

def format_time(seconds):
    """Format seconds to readable time"""
    if seconds < 60:
        return f"{seconds:.1f} detik"
    elif seconds < 3600:
        return f"{seconds/60:.1f} menit"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def estimate_next_block(avg_time):
    """Estimate when next block will be found"""
    if avg_time > 0:
        eta = datetime.now() + timedelta(seconds=avg_time)
        return eta.strftime('%H:%M:%S')
    return "Unknown"

def main():
    """Main mining loop"""
    print("=" * 80)
    print("⛏️  MYCOIN CPU MINER (Difficulty 1)")
    print("=" * 80)
    print()
    
    # Check daemon
    print("🔌 Connecting to daemon...")
    for i in range(10):
        blockcount = run_rpc("getblockcount")
        if blockcount is not None and blockcount != "WALLET_ERROR":
            print("✅ Daemon connected!")
            break
        print(f"   Waiting... ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ Cannot connect to daemon!")
        print("   Start with: ./bin/mycoind -daemon")
        sys.exit(1)
    
    # Ensure wallet exists
    print("📝 Checking wallet...")
    wallets = run_rpc("listwallets")
    if not wallets or "mywallet" not in (wallets if isinstance(wallets, list) else []):
        print("   Creating wallet 'mywallet'...")
        run_rpc("createwallet mywallet")
        time.sleep(2)
    
    # Get address
    address = run_rpc("getnewaddress")
    if not address or address == "WALLET_ERROR":
        print("❌ Failed to get address!")
        print("   Try manually: ./bin/mycoin-cli createwallet mywallet")
        sys.exit(1)
    
    print(f"🔑 Mining Address: {address}")
    print()
    
    # Initial stats
    initial_blocks = run_rpc("getblockcount") or 0
    initial_balance = float(run_rpc("getbalance") or 0)
    mining_info = run_rpc("getmininginfo") or {}
    
    print(f"📊 Current Stats:")
    print(f"   Blocks: {initial_blocks}")
    print(f"   Balance: {initial_balance:.8f} MYC")
    print(f"   Difficulty: {mining_info.get('difficulty', 'unknown')}")
    print()
    
    print("🚀 Starting mining...")
    print("   ⚠️  With difficulty 1, each block may take 10-30+ minutes")
    print("   💡 Press Ctrl+C to stop after current block")
    print("=" * 80)
    print()
    
    blocks_mined = 0
    total_time = 0
    session_start = time.time()
    block_times = []
    
    while not shutdown_flag:
        # Mine one block
        result = mine_one_block(address)
        
        if result['success']:
            blocks_mined += 1
            block_times.append(result['elapsed'])
            total_time += result['elapsed']
            
            # Get updated stats
            current_blocks = run_rpc("getblockcount") or 0
            current_balance = float(run_rpc("getbalance") or 0)
            
            # Calculate averages
            avg_time = sum(block_times) / len(block_times)
            session_elapsed = time.time() - session_start
            
            # Display results
            print()
            print("=" * 80)
            print(f"✅ BLOCK #{current_blocks} MINED!")
            print("=" * 80)
            print(f"⏱️  Time: {format_time(result['elapsed'])}")
            if result['hash'] != "unknown":
                print(f"🔗 Hash: {result['hash'][:16]}...")
            print(f"💰 Balance: {current_balance:.8f} MYC")
            print(f"📈 Session Stats:")
            print(f"   Blocks Mined: {blocks_mined}")
            print(f"   Total Earned: {blocks_mined * 50} MYC")
            print(f"   Average Time: {format_time(avg_time)}/block")
            print(f"   Session Time: {format_time(session_elapsed)}")
            if blocks_mined > 0:
                rate = blocks_mined / session_elapsed * 3600
                print(f"   Mining Rate: {rate:.2f} blocks/jam")
            print(f"⏰ Next Block ETA: ~{estimate_next_block(avg_time)}")
            print("=" * 80)
            print()
            
            # Show progress to next difficulty adjustment
            blocks_until_adjust = 2016 - (current_blocks % 2016)
            if blocks_until_adjust <= 100:
                print(f"⚠️  Difficulty adjustment in {blocks_until_adjust} blocks!")
                print()
        else:
            print(f"⚠️  Block mining failed after {format_time(result['elapsed'])}")
            print("   Retrying in 10 seconds...")
            time.sleep(10)
    
    # Final summary
    print()
    print("=" * 80)
    print("📊 MINING SESSION ENDED")
    print("=" * 80)
    final_blocks = run_rpc("getblockcount") or 0
    final_balance = float(run_rpc("getbalance") or 0)
    session_time = time.time() - session_start
    
    print(f"⏱️  Total Session Time: {format_time(session_time)}")
    print(f"⛏️  Blocks Mined: {blocks_mined}")
    print(f"💰 Total Earned: {blocks_mined * 50} MYC")
    print(f"💵 Final Balance: {final_balance:.8f} MYC")
    if blocks_mined > 0:
        print(f"📈 Average Time: {format_time(sum(block_times)/len(block_times))}/block")
        print(f"🚀 Mining Rate: {blocks_mined/session_time*3600:.2f} blocks/hour")
    print("=" * 80)
    print("\n👋 Happy mining!")

if __name__ == "__main__":
    main()
