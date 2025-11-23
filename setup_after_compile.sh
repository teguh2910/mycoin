#!/bin/bash
# Script untuk setup MyCoin setelah compile di Ubuntu VPS
# Author: MyCoin Team
# Usage: ./setup_after_compile.sh

set -e  # Exit on error

MYCOIN_DIR=~/BTC/bitcoin
BUILD_DIR=$MYCOIN_DIR/build/src
DATA_DIR=~/.mycoin

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   MyCoin Post-Compile Setup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. Verify binaries
echo -e "${YELLOW}[1/7] Verifying compiled binaries...${NC}"
if [ ! -f "$BUILD_DIR/mycoind" ]; then
    echo -e "${RED}ERROR: mycoind not found in $BUILD_DIR${NC}"
    exit 1
fi

if [ ! -f "$BUILD_DIR/mycoin-cli" ]; then
    echo -e "${RED}ERROR: mycoin-cli not found in $BUILD_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Binaries found${NC}"
$BUILD_DIR/mycoind --version | head -n 1
echo ""

# 2. Backup old data
echo -e "${YELLOW}[2/7] Backing up old data (if exists)...${NC}"
if [ -d "$DATA_DIR" ]; then
    BACKUP_DIR="${DATA_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  Creating backup: $BACKUP_DIR"
    cp -r "$DATA_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo "  No existing data to backup"
fi
echo ""

# 3. Clean old data
echo -e "${YELLOW}[3/7] Cleaning old blockchain data...${NC}"
read -p "  Delete all data in $DATA_DIR? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$DATA_DIR"
    mkdir -p "$DATA_DIR"
    echo -e "${GREEN}✓ Data cleaned${NC}"
else
    echo "  Skipped cleaning"
fi
echo ""

# 4. Create config file
echo -e "${YELLOW}[4/7] Creating configuration file...${NC}"
if [ ! -f "$DATA_DIR/mycoin.conf" ]; then
    cat > "$DATA_DIR/mycoin.conf" << EOF
# MyCoin Configuration
# Generated on $(date)

# Server mode
server=1
daemon=1

# RPC settings
rpcuser=mycoinduser
rpcpassword=ChangeThisPassword$(date +%s)
rpcallowip=127.0.0.1

# Network
listen=1
port=9333

# Logging
debug=1
printtoconsole=0

# Mining (set to 1 to enable)
gen=0

# Uncomment for testing:
# regtest=1
EOF
    echo -e "${GREEN}✓ Config file created: $DATA_DIR/mycoin.conf${NC}"
else
    echo "  Config file already exists"
fi
echo ""

# 5. Start node
echo -e "${YELLOW}[5/7] Starting MyCoin node...${NC}"
read -p "  Start in [M]ainnet or [R]egtest? [M/r] " -n 1 -r
echo
if [[ $REPLY =~ ^[Rr]$ ]]; then
    $BUILD_DIR/mycoind -regtest -daemon
    NETWORK="-regtest"
    echo -e "${GREEN}✓ MyCoin started in REGTEST mode${NC}"
else
    $BUILD_DIR/mycoind -daemon
    NETWORK=""
    echo -e "${GREEN}✓ MyCoin started in MAINNET mode${NC}"
fi

echo "  Waiting for node to initialize..."
sleep 10
echo ""

# 6. Verify genesis block
echo -e "${YELLOW}[6/7] Verifying genesis block...${NC}"
EXPECTED_HASH="6efc6097e26800e29b59dc214f0ae19e8314ce63eabaf00b13c5582064ecb755"
ACTUAL_HASH=$($BUILD_DIR/mycoin-cli $NETWORK getblockhash 0 2>/dev/null || echo "ERROR")

if [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ]; then
    echo -e "${GREEN}✓ Genesis block hash CORRECT!${NC}"
    echo "  Hash: $ACTUAL_HASH"
else
    echo -e "${RED}✗ Genesis block hash MISMATCH!${NC}"
    echo "  Expected: $EXPECTED_HASH"
    echo "  Got:      $ACTUAL_HASH"
    echo ""
    echo "  This means the genesis block is wrong. You need to:"
    echo "  1. Pull latest chainparams.cpp changes"
    echo "  2. Recompile the code"
    exit 1
fi
echo ""

# 7. Show node info
echo -e "${YELLOW}[7/7] Node information:${NC}"
$BUILD_DIR/mycoin-cli $NETWORK getblockchaininfo 2>/dev/null | grep -E "chain|blocks|headers|difficulty" || echo "  Node is still starting..."
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Useful commands:"
echo "  Status:     $BUILD_DIR/mycoin-cli $NETWORK getblockchaininfo"
echo "  Logs:       tail -f $DATA_DIR/debug.log"
echo "  Stop:       $BUILD_DIR/mycoin-cli $NETWORK stop"
echo ""

if [[ $REPLY =~ ^[Rr]$ ]]; then
    echo "For regtest mining:"
    echo "  Create wallet: $BUILD_DIR/mycoin-cli $NETWORK createwallet \"mywallet\""
    echo "  Mine blocks:   $BUILD_DIR/mycoin-cli $NETWORK generatetoaddress 101 \"\$($BUILD_DIR/mycoin-cli $NETWORK getnewaddress)\""
    echo ""
fi

echo -e "${GREEN}Done!${NC}"
