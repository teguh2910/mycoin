#!/bin/bash
# Script untuk reset MyCoin data setelah genesis block berubah
# WAJIB dijalankan setelah perubahan genesis block!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   MyCoin Data Reset Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo -e "${RED}WARNING: This will delete ALL MyCoin blockchain data!${NC}"
echo -e "${RED}Make sure to backup any important wallets first!${NC}"
echo ""

DATA_DIR=~/.mycoin

# 1. Stop running node
echo -e "${YELLOW}[1/5] Stopping MyCoin node...${NC}"
if pgrep -x "mycoind" > /dev/null; then
    echo "  Found running mycoind process, stopping..."
    killall -9 mycoind 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✓ Node stopped${NC}"
else
    echo "  No running node found"
fi
echo ""

# 2. Backup wallet.dat if exists
echo -e "${YELLOW}[2/5] Backing up wallet.dat (if exists)...${NC}"
WALLET_BACKUP=""
if [ -f "$DATA_DIR/wallets/wallet.dat" ]; then
    WALLET_BACKUP="$DATA_DIR/wallet.dat.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$DATA_DIR/wallets/wallet.dat" "$WALLET_BACKUP"
    echo -e "${GREEN}✓ Wallet backed up to: $WALLET_BACKUP${NC}"
elif [ -f "$DATA_DIR/wallet.dat" ]; then
    WALLET_BACKUP="$DATA_DIR/wallet.dat.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$DATA_DIR/wallet.dat" "$WALLET_BACKUP"
    echo -e "${GREEN}✓ Wallet backed up to: $WALLET_BACKUP${NC}"
else
    echo "  No wallet found (this is OK for new setup)"
fi
echo ""

# 3. Delete blockchain data
echo -e "${YELLOW}[3/5] Deleting blockchain data...${NC}"
echo "  Deleting blocks/"
rm -rf "$DATA_DIR/blocks" 2>/dev/null || true
echo "  Deleting chainstate/"
rm -rf "$DATA_DIR/chainstate" 2>/dev/null || true
echo "  Deleting indexes/"
rm -rf "$DATA_DIR/indexes" 2>/dev/null || true
echo "  Deleting mempool.dat"
rm -f "$DATA_DIR/mempool.dat" 2>/dev/null || true
echo "  Deleting peers.dat"
rm -f "$DATA_DIR/peers.dat" 2>/dev/null || true
echo "  Deleting banlist.dat"
rm -f "$DATA_DIR/banlist.dat" 2>/dev/null || true
echo "  Deleting .lock"
rm -f "$DATA_DIR/.lock" 2>/dev/null || true
echo -e "${GREEN}✓ Blockchain data deleted${NC}"
echo ""

# 4. Keep config and wallet
echo -e "${YELLOW}[4/5] Preserving configuration...${NC}"
if [ -f "$DATA_DIR/mycoin.conf" ]; then
    echo -e "${GREEN}✓ Config file preserved: $DATA_DIR/mycoin.conf${NC}"
else
    echo "  No config file found"
fi

if [ -n "$WALLET_BACKUP" ]; then
    echo -e "${GREEN}✓ Wallet backup: $WALLET_BACKUP${NC}"
fi
echo ""

# 5. Summary
echo -e "${YELLOW}[5/5] Summary${NC}"
echo -e "${GREEN}✓ MyCoin data reset complete!${NC}"
echo ""
echo "What was deleted:"
echo "  • blocks/ (blockchain data)"
echo "  • chainstate/ (UTXO database)"
echo "  • indexes/ (optional indexes)"
echo "  • mempool.dat, peers.dat, banlist.dat"
echo ""
echo "What was preserved:"
echo "  • mycoin.conf (configuration)"
if [ -n "$WALLET_BACKUP" ]; then
    echo "  • wallet.dat backup: $WALLET_BACKUP"
fi
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Ready to Start Fresh!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Start MyCoin: ./mycoind -daemon"
echo "  2. Wait 10 seconds: sleep 10"
echo "  3. Verify genesis: ./mycoin-cli getblockhash 0"
echo ""
echo "Expected genesis hash:"
echo "  0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206"
echo ""
