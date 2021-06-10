import sys
import grpc
import time
import random
import sxutil
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

def demandCallback(client, dm):
    sxutil.log('需要を受け取りました： {}'.format(dm.demand_name))
    if dm.target_id != 0:
        sxutil.log('getSelect')
        client.Confirm(dm.id)
    else:
        sxutil.log('供給：このスペースを使ってください！')
        spo = sxutil.SupplyOpts(dm.id, 'このスペースを使ってください！')
        pid = client.ProposeSupply(spo)
        sxutil.log(pid)

def subscribeDemand(client):
    sxutil.log('需要を受け取ります')
    client.SubscribeDemand(demandCallback)

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
        # 需要を受け取る
        subscribeDemand(sxClient)

if __name__ == '__main__':
    run(sys.argv)
