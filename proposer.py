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
reserve = {'00:00:00': 'car_0'} #時間がkey,car_idがvalueのdict

def demandCallback(client, dm):
    sxutil.log(f'需要受取：{dm.demand_name}')
    # sxutil.log(dm)
    if dm.target_id != 0:
        sxutil.log('4.マッチングしました。確定します。')

        global lane_state
        lane_state = False # 占有状態に
        # 4.Confirm
        client.Confirm(dm.id)
    elif dm.demand_name != '':
        data = json.loads(dm.arg_json)
        sxutil.log(data)
        # 進行可能に含まれるかどうか
        if lane_id in data['lane_available']:
            # 予約をできるかを確認
            global reserve
            if data['time'] in reserve:
                # 予約済み
                sxutil.log('E.供給：すでに予約済みです')
            else:
                # 未予約
                sxutil.log('2.供給：予約可能です')
                data = {"lane":lane_id, "car":data['car'], "time":data['time'], "state": lane_state}
                spo = sxutil.SupplyOpts(dm.id, 'レーン:'+lane_id+" 状態:"+str(lane_state), json.dumps(data))
                # 2.Propose Supply
                pid = client.ProposeSupply(spo)
                sxutil.log(pid)
        else:
            #進行可能に含まれない
            sxutil.log('E.lane_availableに含まれていません。')
    else:
        sxutil.log('ELSE')
    sxutil.log('--------------------------------')

def subscribeDemand(client):
    sxutil.log('需要待ちです...')
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
