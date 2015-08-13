#!/usr/bin/bash


# Start with clean slate
rm -rf gnuplot* > /dev/null 2>&1 # Supress errors

repos="src/gz all http://repo.opkg.net/edison/repo/all \n
src/gz edison http://repo.opkg.net/edison/repo/edison \n
src/gz core2-32 http://repo.opkg.net/edison/repo/core2-32 \n"

cat /etc/opkg/base-feeds.conf  | gerp 'core2-32'

if  [[ $? != 0 ]]; then
    echo "Updating the repo "
    echo -e $repos > /etc/opkg/base-feeds.conf 
    opkg update
fi

opkg install libgd-staticdev

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
rm ez_setup.py  > /dev/null 2>&1 

wget     http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py

echo "Installing required python packages "

# Install twython
easy_install twython





