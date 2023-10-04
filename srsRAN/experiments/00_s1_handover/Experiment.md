# Steps
Followed [this](https://docs.srsran.com/projects/4g/en/hoverxref_test/app_notes/source/handover/source/index.html#s1-handover) srsRAN tutorial to perform an S1 handover

1. Copy `configs/` to `~/.config/srsran`.
2. Run the enb1, enb2 and ue
3. Start gnuradio with `uav_experiments.grc`
4. Set enb1 multiply constant to a value such that the connected ue gives a `-68dBm` RSRP.
5. Increment the enb2 multiply constant, noting down its Neighbour RSRP given by the UE
6. Note when handover occurs.
7. Save the data in a csv, and run `Graph.ipynb`

# Results
As with the paper, handover occurs when the neighbour RSRP is 3dB higher than the serving RSRP. This leads us to conclude that the standard hyteresis margin is 3dB in srsRAN.

## Handover Experiments Paper Figure 4:
![Alt text](UAV_fig4.png)
## Personal Results
![Alt text](handover.png)