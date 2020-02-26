import grpc
import time
import random
import sxutil
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

def notifyDemand(client):
    sxutil.log('Notify Demand')
    dmo = sxutil.DemandOpts('Test Demand')
    client.NotifyDemand(dmo)

def supplyCallback(client, sp):
    sxutil.log('Received message {}'.format(sp.supply_name))
    pid = client.SelectSupply(sp)
    sxutil.log(pid)

def subscribeSupply(client):
    sxutil.log('Subscribe Supply')
    client.SubscribeSupply(supplyCallback)

def connectSynerexServer(client):
    subscribeSupply(client)

def run():
    channels = [1]
    srv = 'localhost:18000'
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, 1, '')
        notifyDemand(sxClient)
        connectSynerexServer(sxClient)

if __name__ == '__main__':
    run()
