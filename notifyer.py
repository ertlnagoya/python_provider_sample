import sys
import grpc
import time
import random
import sxutil
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

def notifyDemand(client):
    sxutil.log('需要出します！')
    sxutil.log('需要：このスペースに１秒後入りたいです')
    dmo = sxutil.DemandOpts('このスペースに１秒後入りたいです')
    client.NotifyDemand(dmo)

def supplyCallback(client, sp):
    sxutil.log('供給を受け取りました：{}'.format(sp.supply_name))
    pid = client.SelectSupply(sp)
    sxutil.log(pid)

def subscribeSupply(client):
    sxutil.log('供給を受け取ります')
    client.SubscribeSupply(supplyCallback)

def connectSynerexServer(client):
    subscribeSupply(client)

def run(args):
    if len(args) == 1:
        channels = [1]
    else:
        channels = [int(args[1])]
    sxutil.log(f'channels : {channels}')
    srv = 'localhost:10000'
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, 1, '')
        notifyDemand(sxClient)
        connectSynerexServer(sxClient)

if __name__ == '__main__':
    run(sys.argv)
