#!/bin/bash
# Parallel CPU mining script for MyCoin
# Uses multiple processes to maximize CPU usage

# Configuration
NUM_WORKERS=3  # Adjust based on CPU cores (3 = ~75%, 4 = 100%)
MYCOIN_CLI="./bin/mycoin-cli"

echo "======================================"
echo "MyCoin Parallel CPU Miner"
echo "======================================"
echo ""

# Get mining address
echo "Getting mining address..."
ADDR=$($MYCOIN_CLI getnewaddress 2>/dev/null)

if [ -z "$ADDR" ]; then
    echo "Error: Could not get address"
    echo "Make sure daemon is running and wallet exists"
    exit 1
fi

echo "Mining Address: $ADDR"
echo "Number of Workers: $NUM_WORKERS"
echo ""
echo "Starting parallel mining..."
echo "Press Ctrl+C to stop all workers"
echo "======================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all mining workers..."
    killall mycoin-cli 2>/dev/null
    echo "Mining stopped."
    exit 0
}

trap cleanup INT TERM

# Start multiple mining workers
for i in $(seq 1 $NUM_WORKERS); do
    echo "Starting Worker #$i..."
    (
        while true; do
            $MYCOIN_CLI generatetoaddress 1 $ADDR >/dev/null 2>&1
        done
    ) &
done

echo ""
echo "All workers started!"
echo ""

# Monitor progress
LAST_HEIGHT=0
START_TIME=$(date +%s)
BLOCKS_MINED=0

while true; do
    sleep 5
    
    # Get current stats
    HEIGHT=$($MYCOIN_CLI getblockcount 2>/dev/null)
    BALANCE=$($MYCOIN_CLI getbalance 2>/dev/null)
    
    if [ -z "$HEIGHT" ]; then
        echo "Warning: Cannot connect to daemon"
        continue
    fi
    
    # Check if new block was mined
    if [ "$HEIGHT" != "$LAST_HEIGHT" ]; then
        BLOCKS_MINED=$((HEIGHT - LAST_HEIGHT))
        LAST_HEIGHT=$HEIGHT
        
        # Calculate stats
        ELAPSED=$(($(date +%s) - START_TIME))
        if [ $ELAPSED -gt 0 ]; then
            RATE=$(echo "scale=2; $HEIGHT / $ELAPSED * 3600" | bc)
        else
            RATE="N/A"
        fi
        
        # Display update
        echo "==============================================="
        echo "✅ NEW BLOCK MINED! (#$HEIGHT)"
        echo "==============================================="
        echo "Time: $(date '+%H:%M:%S')"
        echo "Balance: $BALANCE MYC"
        echo "Total Blocks: $HEIGHT"
        echo "Mining Rate: $RATE blocks/hour"
        echo "Workers Active: $NUM_WORKERS"
        echo "Elapsed: $((ELAPSED / 60)) minutes"
        echo "==============================================="
        echo ""
    fi
done
