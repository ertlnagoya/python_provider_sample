import grpc
import time
import random
import concurrent.futures
import sxutil
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

def notifyDemand(client):
    sxutil.log('Notify Demand')
    while True:
        dmo = sxutil.DemandOpts('Test Demand')
        client.NotifyDemand(dmo)
        time.sleep(10)

def supplyCallback(client, sp):
    sxutil.log('Received message {}'.format(sp.supply_name))
    pid = client.SelectSupply(sp)
    sxutil.log(pid)

def subscribeSupply(client):
    sxutil.log('Subscribe Supply')
    client.SubscribeSupply(supplyCallback)

def connectSynerexServer(client):
    while True:
        subscribeSupply(client)

def run():
    channels = [1]
    srv = sxutil.RegisterNode('localhost:9990', 'Python Notifyer', channels, None)
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, 1, '')
        sxutil.futures.append(sxutil.executor.submit(connectSynerexServer, sxClient))
        sxutil.futures.append(sxutil.executor.submit(notifyDemand, sxClient))
        for future in concurrent.futures.as_completed(sxutil.futures):
            sxutil.log(future.result())
        sxutil.executor.shutdown()

if __name__ == '__main__':
    run()
