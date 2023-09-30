**Set up VM using vagrant + virtualbox with ubuntu 22.04:**
Vagrantfile:
```ruby
Vagrant.configure("2") do |config|
    config.vm.box = "bento/ubuntu-22.04"
    config.vm.network "forwarded_port", guest: 3000, host: 3000
    config.ssh.forward_agent = true 
    config.ssh.forward_x11 = true
    config.vm.provider "virtualbox" do |v|
	  v.memory = 4096
	  v.cpus = 4
	end
end
```

enter vagrant:
```bash
vagrant up
vagrant ssh # password: vagrant
```

set up x11 forwarding:
```sh
sudo apt update 
sudo apt install xauth
sudo apt install x11-apps

# Check if working (after vagrant -X -Y ssh)
xclock
```
build dependancies:
```sh
# Install build dependancies
sudo apt-get update
sudo apt-get install cmake make gcc g++ pkg-config libfftw3-dev libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev
sudo apt-get install build-essential cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev
```

zmq
```sh
# Install zmq
sudo apt-get install libzmq3-dev
```

srsgui
```sh
# Install SRSGUI
cd ~
sudo apt-get install libboost-system-dev libboost-test-dev libboost-thread-dev libqwt-qt5-dev qtbase5-dev
git clone https://github.com/srsLTE/srsGUI.git
cd srsGUI
mkdir build
cd build
cmake ../
make 
sudo make install
```

srsran 
```sh
# Build srsRAN project (4g version)
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
```

mongodb
```sh
# Install mongodb [open5gs requirement]
sudo apt update
sudo apt install gnupg
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
sudo apt install gnupg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

open5gs
```sh
# Install open5gs
sudo add-apt-repository ppa:open5gs/latest
sudo apt update
sudo apt install open5gs
```

**Modify open5gs config to interface with srsRAN**
/etc/open5gs/mme.yaml
```yaml
332 mcc: 901
338 mcc: 901
340 tac: 7
```

```shell
sudo systemctl restart open5gs-mmed
```

**Install webui for open5gs to add subscribers**
```sh
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

 # Create deb repository
NODE_MAJOR=20 
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list

 # Run Update and Install
sudo apt update
sudo apt install nodejs -y

# Install Open5gs webui
curl -fsSL https://open5gs.org/open5gs/assets/webui/install | sudo -E bash -
```

/lib/systemd/system/open5gs-webui.service
```service
9   Environment=NODE_ENV=production 
+10 Environment=HOSTNAME=0.0.0.0
```

```shell
sudo systemctl daemon-reload
```

**Add subscriber stuff**
- Navigate to 127.0.0.1:3000
- Login username: `admin` password: `1423`
- Add values:
```toml
IMSI = 901700123456789
OPC  = 63BFA50EE6523365FF14C1F45F88737D
K    = 00112233445566778899aabbccddeeff
```

**Update ue.conf**
- change imsi in ue.conf. This change is due ot the 90170 prefix (PLMN) needed for MCC/MNC???
~/.config/srsran/ue.conf
```toml
139 [usim]  
140 mode = soft  
141 algo = milenage  
142 opc  = 63BFA50EE6523365FF14C1F45F88737D  
143 k    = 00112233445566778899aabbccddeeff  
144 imsi = 901700123456789  
145 imei = 353490069873319
```

- Add zmq arguments to ue
~/.config/srsran/ue.conf:
```toml
26 [rf]  
27 freq_offset = 0  
28 tx_gain = 80  
29 device_name = zmq  
30 device_args = tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6

63 dl_earfcn = 2850
```

**Update enb.conf**
~/.config/srsran/enb.conf
```toml
23 mcc = 901  
24 mnc = 70
25 mme_addr = 127.0.0.2 # As set in /etc/open5gs/mme.yaml
```

**Setup enb RR**
```sh
cd ~/.config/srsran
cp rr.conf rr1.conf
cp rr.conf rr2.conf
```

~/.config/srsran/rr1.conf
```cpp
53 cell_list =  
54 (  
55   {  
56         // rf_port = 0;  
57         cell_id = 0x01;  
58         tac = 0x0007;  
59         pci = 1;  
60         root_seq_idx = 204;  
61         dl_earfcn = 2850;  
62         //ul_earfcn = 21400;  
63         ho_active = true;  
64         //meas_gap_period = 0; // 0 (inactive), 40 or 80  
65         //meas_gap_offset_subframe = [6, 12, 18, 24, 30];  
66         // target_pusch_sinr = -1;  
67         // target_pucch_sinr = -1;  
68         // enable_phr_handling = false;  
69         // min_phr_thres = 0;  
70         // allowed_meas_bw = 6;  
71         // t304 = 2000; // in msec. possible values: 50, 100, 150, 200, 500, 1000, 2000  
72    
73         // CA cells  
74         scell_list = (  
75         // {cell_id = 0x02; cross_carrier_scheduling = false; scheduling_cell_id = 0x02; ul_allowed = true}  
76         )  
77    
78         // Cells available for handover  
79         meas_cell_list =  
80         (  
81           {  
82             eci = 0x19B01;  
83             dl_earfcn = 2850;  
84             pci = 1;  
85             //direct_forward_path_available = false;  
86             //allowed_meas_bw = 6;  
87             //cell_individual_offset = 0;  
88           },  
89           {  
90             eci = 0x19C01;  
91             dl_earfcn = 2850;  
92             pci = 6;  
93           }  
94         );  
95    
96         // Select measurement report configuration (all reports are combined with all measurement objects)  
97         meas_report_desc =  
98         (  
99           {  
100             eventA = 3  
101             a3_offset = 6;  
102             hysteresis = 0;  
103             time_to_trigger = 480;  
104             trigger_quant = "RSRP";  
105             max_report_cells = 1;  
106             report_interv = 120;  
107             report_amount = 1;  
108           }  
109         );  
110    
111         meas_quant_desc = {  
112           // averaging filter coefficient  
113           rsrq_config = 4;  
114           rsrp_config = 4;  
115         };  
116   }  
117   // Add here more cells  
118 );
```

~/.config/srsran/rr2.conf
```cpp
cell_list =
(
  {
        // rf_port = 0;
        cell_id = 0x01;
        tac = 0x0007;
        pci = 6;
        root_seq_idx = 264;
        dl_earfcn = 2850;
        //ul_earfcn = 21400;
        ho_active = true;
        //meas_gap_period = 0; // 0 (inactive), 40 or 80
        //meas_gap_offset_subframe = [6, 12, 18, 24, 30];
        // target_pusch_sinr = -1;
        // target_pucch_sinr = -1;
        // enable_phr_handling = false;
        // min_phr_thres = 0;
        // allowed_meas_bw = 6;
        // t304 = 2000; // in msec. possible values: 50, 100, 150, 200, 500, 1000, 2000

        // CA cells
        scell_list = (
        // {cell_id = 0x02; cross_carrier_scheduling = false; scheduling_cell_id = 0x02; ul_allowed = true}
        )

        // Cells available for handover
        meas_cell_list =
        (
          {
            eci = 0x19B01;
            dl_earfcn = 2850;
            pci = 1;
            //direct_forward_path_available = false;
            //allowed_meas_bw = 6;
            //cell_individual_offset = 0;
          },
          {
            eci = 0x19C01;
            dl_earfcn = 2850;
            pci = 6;
          }
        );

        // Select measurement report configuration (all reports are combined with all measurement objects)
        meas_report_desc =
        (
          {
            eventA = 3
            a3_offset = 6;
            hysteresis = 0;
            time_to_trigger = 480;
            trigger_quant = "RSRP";
            max_report_cells = 1;
            report_interv = 120;
            report_amount = 1;
          }
        );

        meas_quant_desc = {
          // averaging filter coefficient
          rsrq_config = 4;
          rsrp_config = 4;
        };
  }
  // Add here more cells
);
```

**Creating Scripts**
~/.config/srsran/start_enb1.sh [new]
```sh
#!/bin/bash

LOG_ARGS="--log.all_level=debug"

PORT_ARGS="tx_port=tcp://*:2101,rx_port=tcp://localhost:2100"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=enb,base_srate=23.04e6\""

OTHER_ARGS="--enb_files.rr_config=rr1.conf"

sudo srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@
```

~/.config/srsran/start_enb2.sh [new]
```sh
#!/bin/bash

LOG_ARGS="--log.all_level=info"

PORT_ARGS="tx_port=tcp://*:2201,rx_port=tcp://localhost:2200"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=enb,base_srate=23.04e6\""

OTHER_ARGS="--enb_files.rr_config=rr2.conf --enb.enb_id=0x19C --enb.gtp_bind_addr=127.0.1.2 --enb.s1c_bind_addr=127.0.1.2"

sudo srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@
```

~/.config/srsran/start_ue.sh [new]
```sh
#!/bin/bash

LOG_PARAMS="--log.all_level=debug"

PORT_ARGS="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=ue,base_srate=23.04e6\" --gw.netns=ue1"


## Create netns for UE
ip netns list | grep "ue1" > /dev/null
if [ $? -eq 1 ]; then
  echo creating netspace ue1...
  sudo ip netns add ue1
  if [ $? -ne 0 ]; then
   echo failed to create netns ue1
   exit 1
  fi
fi

sudo srsue ue.conf ${LOG_PARAMS} ${ZMQ_ARGS} --rat.eutra.dl_earfcn=2850 "$@"
```

**Enable gui**
~/.config/srsran/enb.conf
```toml
160 [gui]
161 enable = true
```
~/.config/srsran/ue.conf
```toml
226 [gui]  
227 enable = true
```

**Install GNU Radio**
```sh
sudo apt install python3-gi gobject-introspection gir1.2-gtk-3.0
sudo apt-get install gnuradio
sudo apt-get install xterm

# Running
gnuradio-companion
```

# Testing
**Upload GRC**
Download file from [here](https://docs.srsran.com/projects/4g/en/hoverxref_test/_downloads/41742cf2f30ae7b90c8822332605c811/handover_broker.grc)
outside vm:
```sh
vagrant upload handover_broker.grc
```
- open `handover_broker.grc` and execute flow

**Wireshark**
- connect on ssh, in sudo, on `lo`
- filter: `ip.addr == 127.0.0.2 and sctp[12:1] != 4 and sctp[12:1] != 5`
	- the sctp is to filter out heatbeak + heartbeat ack

**Running**
in parralel
```sh
cd ~/.config/srsran
./start_enb1.sh
./start_enb2.sh
./start_ue.sh
gnuradio-companion # Execute graph, then change cell strengths
```
![[Pasted image 20230927130906.png]]
![[Pasted image 20230927130929.png]]

keeping connection alive:
```sh
sudo ip netns exec ue1 ping 10.45.0.1 # uplink
ping 10.45.0.4 # downlink (variable, check ue output)
```

iperf3
```sh
sudo apt install iperf3
sudo apt install nmap
iperf3 -s -i 1 # Start iperf server
sudo ip netns exec ue1 iperf3 -c 10.45.0.1 -b 10M -i 1 -t 60 # ue client test

```
# Sources
https://docs.srsran.com/projects/4g/en/hoverxref_test/app_notes/source/handover/source/index.html#s1-handover
https://docs.srsran.com/projects/4g/en/hoverxref_test/app_notes/source/zeromq/source/index.html#zeromq-appnote
https://open5gs.org/open5gs/docs/guide/01-quickstart/
https://docs.srsran.com/projects/4g/en/hoverxref_test/general/source/1_installation.html#gen-installation
https://github.com/srsran/srsRAN_Project


https://docs.srsran.com/projects/project/en/latest/tutorials/source/srsUE/source/index.html#srsran-gnb-with-srsue
