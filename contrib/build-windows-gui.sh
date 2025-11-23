#!/bin/bash
# Script untuk cross-compile MyCoin Qt GUI untuk Windows dari Ubuntu

set -e

echo "======================================"
echo "MyCoin Windows GUI Cross-Compile"
echo "======================================"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Error: This script requires Ubuntu/Debian"
    exit 1
fi

echo "Step 1: Installing MinGW and dependencies..."
echo "This will require sudo password"
echo ""

sudo apt update
sudo apt install -y \
    g++-mingw-w64-x86-64 \
    mingw-w64-tools \
    nsis \
    wine64 \
    wine-binfmt \
    autoconf \
    automake \
    bsdmainutils \
    curl \
    git \
    libtool \
    pkg-config \
    python3 \
    cmake

# Set MinGW alternatives
echo "Configuring MinGW for POSIX threading..."
sudo update-alternatives --set x86_64-w64-mingw32-gcc /usr/bin/x86_64-w64-mingw32-gcc-posix 2>/dev/null || true
sudo update-alternatives --set x86_64-w64-mingw32-g++ /usr/bin/x86_64-w64-mingw32-g++-posix 2>/dev/null || true

echo ""
echo "Step 2: Building dependencies for Windows..."
echo "This will take 1-2 hours. Go get some coffee! ☕"
echo ""

cd ~/mycoin/depends

# Build dependencies
make HOST=x86_64-w64-mingw32 -j$(nproc)

echo ""
echo "Step 3: Configuring MyCoin for Windows build..."
echo ""

cd ~/mycoin

# Clean old build
rm -rf build-win
mkdir build-win
cd build-win

# Check if toolchain file exists
if [ ! -f ../cmake/toolchains/x86_64-w64-mingw32.cmake ]; then
    echo "Creating MinGW toolchain file..."
    mkdir -p ../cmake/toolchains
    cat > ../cmake/toolchains/x86_64-w64-mingw32.cmake << 'EOF'
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc-posix)
set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++-posix)
set(CMAKE_RC_COMPILER x86_64-w64-mingw32-windres)

set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pthread")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
EOF
fi

# Configure
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/x86_64-w64-mingw32.cmake \
      -DBUILD_GUI=ON \
      -DCMAKE_PREFIX_PATH=$(pwd)/../depends/x86_64-w64-mingw32 \
      -DCMAKE_BUILD_TYPE=Release \
      ..

echo ""
echo "Step 4: Building MyCoin Windows GUI..."
echo "This will take 30-60 minutes..."
echo ""

# Build
cmake --build . --config Release -j$(nproc)

echo ""
echo "======================================"
echo "✅ Build Complete!"
echo "======================================"
echo ""
echo "Windows executables are in:"
echo "  ~/mycoin/build-win/src/qt/mycoin-qt.exe"
echo "  ~/mycoin/build-win/src/mycoind.exe"
echo "  ~/mycoin/build-win/src/mycoin-cli.exe"
echo ""
echo "To test on Ubuntu using Wine:"
echo "  wine ~/mycoin/build-win/src/qt/mycoin-qt.exe"
echo ""
echo "Copy these .exe files to your Windows machine to use!"
echo "======================================"
