# python_provider_sample

Sample Synerex Provider for Python

# Install

git clone https://github.com/synerex/python_provider_sample.git  
cd python_provider_sample  
git submodule update --init --recursive  

pip install grpcio-tools  
pip install futures  

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./api/synerex.proto  
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./nodeapi/nodeapi.proto  

# before you start

You need to install or find synerex_beta NodeID Server with Synerex server runnning.

# test run

python proposer.py

python notifyer.py

