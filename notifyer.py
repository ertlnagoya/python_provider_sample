#
# 車両プロバイダ（道路の占有を要求）
#
import sys
import grpc
import time
import random
import sxutil
import json # add
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc
# from proto.ganechi import ganechi_pb2
# from proto.ganechi import ganechi_pb2_grpc

car_id = 0
lane_now = 0
lane_available = ["0"]

def notifyDemand(client):
    sxutil.log('需要出します！')
    sxutil.log('需要：このスペースに１秒後入りたいです')
    lane_available = input("lane_available:").split(',')
    data = {"lane_available":lane_available,"from":"10:00:00","to":"10:00:10"}
    dmo = sxutil.DemandOpts('このスペースに１秒後入りたいです', json.dumps(data))
    # 1. Notify Demand
    client.NotifyDemand(dmo)

def supplyCallback(client, sp):
    sxutil.log(f'供給を受け取りました：{sp.supply_name}')
    sxutil.log(sp.arg_json)
    ## 3.Select Supply
    pid = client.SelectSupply(sp)
    sxutil.log(pid)
    sxutil.log('マッチング完了しました')

def subscribeSupply(client):
    sxutil.log('供給を受け取ります')
    client.SubscribeSupply(supplyCallback)

def run():
    channels = [1]
    sxutil.log(f'channels : {channels}')
    srv = 'localhost:10000'
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, 1, '')
        # 需要を出す
        notifyDemand(sxClient)
        # 供給を受け取る
        subscribeSupply(sxClient)

if __name__ == '__main__':
    run()
