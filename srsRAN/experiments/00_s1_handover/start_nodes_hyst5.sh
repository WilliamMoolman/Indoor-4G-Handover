tmux send-keys -t main:nodes.0 "./start_enb1.sh rr_enb1_hyst5.conf" Enter
tmux send-keys -t main:nodes.2 "./start_enb2.sh rr_enb2_hyst5.conf" Enter
sleep 2
tmux send-keys -t main:nodes.1 "./start_ue.sh" Enter

