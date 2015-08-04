#!/usr/bin/bash

# Start with clean slate
rm -rf gnuplot* > /dev/null 2>&1 # Suprees errors
rm -rf zlib* > /dev/null 2>&1
rm -rf libpng* > /dev/null 2>&1
rm -rf libgd* > /dev/null 2>&1
rm -rf gd-* > /dev/null 2>&1
rm -rf lpng1618 > /dev/null 2>&1

# Install zlib
#-----------------------------------------------------
# Getting zlib
echo "Getting zlib..."
curl -L -O http://zlib.net/zlib-1.2.8.tar.gz

ret=$?
if [[ $ret != 0 ]]; then
    echo "Could not get the archive, try again"
fi

tar -zxvf zlib-1.2.8.tar.gz
cd  zlib-1.2.8
sh configure
echo "Compiling zlib and installing it..."
make
make install
cd -
#----------------------------------------------------

# Install libpng
#----------------------------------------------------
echo "Getting libpng"
curl -L -O http://download.sourceforge.net/libpng/lpng1618.zip

ret=$?
if [[ $ret != 0 ]]; then
    echo "Could not get the archive, try again"
    exit $ret
fi

unzip lpng1618.zip
cd lpng1618
cp scripts/makefile.linux Makefile
echo "Compiling and installing libpng..."
make
make install 
cd -
#----------------------------------------------------

# Install libgd
#----------------------------------------------------
echo "Getting the libgd archive"
curl -L -O https://bitbucket.org/libgd/gd-libgd/downloads/libgd-2.1.1.tar.xz

ret=$?
if [[ $ret != 0 ]]; then
    echo "Could not get the archive, try again"
    exit $ret
fi

tar xvf libgd-2.1.1.tar.xz
echo "Compiling and installing the backages..."
sh configure
make 
make install
cd -
#----------------------------------------------------

# Install gnuplot
#----------------------------------------------------
echo "Getting archive...."
curl -L -O curl -L -O "http://downloads.sourceforge.net/project/gnuplot/gnuplot/5.0.1/gnuplot-5.0.1.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fgnuplot%2Ffiles%2Fgnuplot%2F5.0.1%2Fgnuplot-5.0.1.tar.gz%2Fdownload&ts=1438680516&use_mirror=liquidtelecom"

ret=$?
if [[ $ret != 0 ]]; then
    echo "Could not get the archive, try again"
    exit $ret
fi

echo "Extracting....."
tar -zxvf gnuplot*
cd gnuplot*
echo "Running config...."
sh configure
echo "Compiling and installing source..."
make
make install
#----------------------------------------------------

echo "Installing required python packages "

# Install twython
easy_install twython

# Fix the freetype error ref https://gist.github.com/shingonoide/8172291
cd /usr/include
ln -s freetype2 freetype

cd - 

# Install python imaging library
easy_install PIL



