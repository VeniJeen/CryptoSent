# Steps to Connect to Heisenberg

* Connect to DTU Compute VPN
* ssh s192851@heisenberg.imm.dtu.dk
* conda activate CryptoSentRemote
* jupyter notebook --no-browser --port=8888
* Localy: ssh -L 8080:localhost:8888 s192851@heisenberg.imm.dtu.dk
