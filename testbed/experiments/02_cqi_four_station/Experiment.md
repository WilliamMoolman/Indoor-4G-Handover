# Extracting Info from logs
|Line Example | Description | filter | Lines remaining |
| -- | -- | --| -- |
|`2024-02-27T13:28:43.965760 [MAC    ] [D] [   34] SCHED: CQI=15,...` | gets cqi | `SCHED: CQI` | ~200000 |
|`2024-02-27T13:46:50.331505 [MAC    ] [D] [    1] ra_tbs=72/144,...` | ??? | `\] ra_tbs=` | 1765028 |
|`2024-02-27T14:02:40.395541 [MAC    ] [D] [  511] SCHED: Allocated PRACH RBs...` | ??? | `SCHED: Allocated PRACH RBs` | 1387498 |
│`2024-02-27T13:46:50.345298 [MAC    ] [D] [   15] SCHED: SI message, cc=1...` | ??? │ `SCHED: SI message` | 1151486 |
|`2024-02-27T13:47:29.611803 [MAC    ] [I] [ 8561] SCHED: Added user rnti=0x46` | new UE connected | -- |
|`2024-02-27T13:47:29.611866 [MAC    ] [I] [ 8561] RACH:  tti=8561, cc=0, pci=2, preamble=18, offset=1, temp_crnti=0x46`| displays PIC2