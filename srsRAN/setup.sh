# Usage note: all commands have been run individually, but this file has not been executed
#   directly. It is recommended to run each command individually to ensure that there are no
#   errors.
echo "Setting up X11 forwarding..."
sudo apt update
sudo apt -y install xauth
sudo apt -y install x11-apps # Verify with $ xclock (with vagrant -X -Y ssh)

echo "Building dependancies..."
# Need to press enter here twice
sudo apt-get update
sudo apt-get -y install cmake make gcc g++ pkg-config libfftw3-dev libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev
sudo apt-get -y install build-essential cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev

echo "Installing ZMQ"
sudo apt-get -y install libzmq3-dev

echo "Install SRSGUI" # Must occur before srsran
cd ~
sudo apt-get -y install libboost-system-dev libboost-test-dev libboost-thread-dev libqwt-qt5-dev qtbase5-dev # Press Enter
git clone https://github.com/srsLTE/srsGUI.git
cd srsGUI
mkdir build
cd build
cmake ../
make
sudo make install

echo "Building srsRAN project (4g version)..." # This block takes a long while. Compiles from source + tests
cd ~
git clone https://github.com/srsRAN/srsRAN.git
cd srsRAN
mkdir build
cd build
cmake ../
make
make test
sudo make install
srsran_install_configs.sh user

echo "Install mongodb [open5gs requirement]"
sudo apt update
sudo apt install gnupg
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
sudo apt install gnupg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

echo "Modifying open5gs config files..."
sudo sed -i.bkp 's/mcc: 999/mcc: 901/' /etc/open5gs/mme.yaml
sudo sed -i.bkp 's/tac: 1/tac: 7/' /etc/open5gs/mme.yaml
sudo systemctl restart open5gs-mmed

echo "Adding user to mongodb"
cd ~
wget https://raw.githubusercontent.com/open5gs/open5gs/main/misc/db/open5gs-dbctl
chmod +x open5gs-dbctl
# Format: ./open5gs-dbctl add <imsi> <key> <opc>
./open5gs-dbctl add 901700123456789 00112233445566778899aabbccddeeff 63BFA50EE6523365FF14C1F45F88737D

echo "Adding GNU radio..." # This block takes a while
sudo apt install -y python3-gi gobject-introspection gir1.2-gtk-3.0
sudo apt-get install -y gnuradio
sudo apt-get install -y xterm
