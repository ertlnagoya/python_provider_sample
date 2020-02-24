import grpc
import time
import random
import concurrent.futures
import sxutil
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

def demandCallback(client, dm):
    sxutil.log('Received message {}'.format(dm.demand_name))
    if dm.target_id != 0:
        sxutil.log('getSelect')
        client.Confirm(dm.id)
    else:
        spo = sxutil.SupplyOpts(dm.id, 'Test Supply')
        pid = client.ProposeSupply(spo)
        sxutil.log(pid)

def subscribeDemand(client):
    sxutil.log('Subscribe Demand')
    client.SubscribeDemand(demandCallback)

def connectSynerexServer(client):
    while True:
        subscribeDemand(client)

def run():
    channels = [1]
#    srv = sxutil.RegisterNode('localhost:9990', 'Python Proposer', channels, None)
    srv = 'localhost:18000'
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, 1, '')
        connectSynerexServer(sxClient)

if __name__ == '__main__':
    run()
