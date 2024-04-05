# Usage
- Follow [Setup.md](Setup.md) for installation

Run this to start and enter vm
```sh
vagrant up
vagrant ssh
```

**Running** the nodes (run in separate terminals/tmux)
```sh
cd ~/.config/srsran
./start_enb1.sh rr_enb1.conf
./start_enb2.sh rr_enb2.conf
./start_ue.sh
gnuradio-companion # Execute graph, then change cell strengths
```

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