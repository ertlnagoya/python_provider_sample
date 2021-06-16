#
# 道路プロバイダ（道路の空き状況を供給）
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

lane_state = True # 空:Truw 満:False
lane_id = "0"

def demandCallback(client, dm):
    sxutil.log(f'需要を受け取りました：{dm.demand_name}')
    sxutil.log(dm.arg_json)
    if dm.target_id != 0:
        sxutil.log('マッチングしました。確定します。')
        # 4.Confirm
        global lane_state
        lane_state = False # 占有状態に
        client.Confirm(dm.id)
    else:
        sxutil.log('供給：このスペースを使ってください！')
        data = {"lane":lane_id, "state": lane_state}
        spo = sxutil.SupplyOpts(dm.id, 'レーン:'+lane_id+" 状態:"+str(lane_state), json.dumps(data))
        # 2.Propose Supply
        pid = client.ProposeSupply(spo)
        sxutil.log(pid)

def subscribeDemand(client):
    sxutil.log('需要を受け取ります')
    client.SubscribeDemand(demandCallback)

def run():
    channels = [1]
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
    lane_id = input("lane_id:")
    run()
