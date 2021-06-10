# ganechi - enshuEF
Synerexを用いた、合流調停システムの開発

## Program
* synerexのpython_provider_sampleがベース


### Install

git clone https://github.com/ertlnagoya/python_provider_sample.git  
cd python_provider_sample  
git submodule update --init --recursive  

pip install grpcio-tools  
pip install futures  
pip install protobuf3

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./api/synerex.proto  
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./nodeapi/nodeapi.proto  

### before you start

1. You need to install or find synerex_beta NodeID Server with Synerex server runnning.

2. run proxy on localhost

### test run

python3 proposer.py

python3 notifyer.py
