#
# 道路プロバイダ（道路の空き状況を供給）
#
import sys
import grpc
import time
import random
import sxutil
import json # add
import argparse # add
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

reserve = {} #時間がkey,car_idがvalueのdict
temp = {}

parser = argparse.ArgumentParser(description='道路プロバイダ（道路の空き状態を提供）')
parser.add_argument('lane_id', help='レーンのIDを指定（int型）')

def demandCallback(client, dm):
    sxutil.log(f'需要受取：{dm.demand_name}')
    global reserve
    if dm.target_id != 0:
        sxutil.log('4.マッチングしました。確定します。')
        # 予約
        reserve[temp[dm.sender_id][0]] = temp[dm.sender_id][1]
        temp.pop(dm.sender_id) #仮予約を削除
        # 4.Confirm
        client.Confirm(dm.id)
    elif dm.demand_name != '':
        data = json.loads(dm.arg_json)
        sxutil.log(data)
        # 進行可能に含まれるかどうか
        if lane_id in data['lane_available']:
            # 予約をできるかを確認
            if data['time'] in reserve:
                # 予約済みの場合
                sxutil.log('E.すでに予約済みです')
            else:
                # 未予約の場合
                sxutil.log('2.供給：予約可能です')
                # 仮予約
                temp[dm.sender_id] = [data['time'],data['car']]
                data = {"lane":lane_id, "car":data['car'], "time":data['time']}
                spo = sxutil.SupplyOpts(dm.id, 'レーン:'+lane_id+'　時間:'+data['time'], json.dumps(data))
                # 2.Propose Supply
                pid = client.ProposeSupply(spo)
                sxutil.log(pid)
        else:
            #進行可能に含まれない
            sxutil.log('E.lane_availableに含まれていません')
    else:
        sxutil.log('ELSE')
    sxutil.log('--------------------------------')
    sxutil.log(f"Temp:{temp}")
    sxutil.log(f"Resv:{reserve}")
    sxutil.log('--------------------------------')

def subscribeDemand(client):
    sxutil.log('需要待ちです...')
    sxutil.log('--------------------------------')
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
    args = parser.parse_args()
    lane_id = args.lane_id
    run()
