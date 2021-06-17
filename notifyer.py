#
# 車両プロバイダ（道路の占有を要求）
#
import sys
import grpc
import time
import random
import sxutil
import json # add
import datetime as dt # add
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc
# from proto.ganechi import ganechi_pb2
# from proto.ganechi import ganechi_pb2_grpc

reserve = {} #時間がkey,lane_idがvalueのdict

def reserveTime(delay=0):
    # 予約する時間を算出する(delayでさらに何秒後かを)
    now = dt.datetime.now()
    # 次の枠(10秒後)を指定
    now += dt.timedelta(seconds=10+delay)
    return str(now.hour)+":"+str(now.minute)+":"+str(round(now.second,-1))

def notifyDemand(client):
    lane_available = input('lane_available:').split(',')
    data = {"car":car_id, "lane_available":lane_available,"time":reserveTime()}
    sxutil.log(f'1.需要：{data}')
    dmo = sxutil.DemandOpts('車両:'+car_id+" 進行可能:"+str(lane_available), json.dumps(data))
    # 1. Notify Demand
    client.NotifyDemand(dmo)

def supplyCallback(client, sp):
    # 自分のレーン以外の情報は表示しない
    data = json.loads(sp.arg_json)
    if data['car'] != car_id:
        return

    sxutil.log(f'供給受取：{sp.supply_name}')
    sxutil.log(data)

    ## 3.Select Supply
    # 他のレーンを予約していないか確認
    if data['time'] in reserve:
        # 予約済み
        sxutil.log('E.すでに予約済みです')
    else:
        # 未予約
        sxutil.log('3.マッチングしました')
        reserve[data['time']] = data['lane'] # 予約
        pid = client.SelectSupply(sp)
        sxutil.log(pid)

    sxutil.log('--------------------------------')
    sxutil.log(reserve)
    sxutil.log('--------------------------------')

def subscribeSupply(client):
    sxutil.log('供給待ちです...')
    sxutil.log('--------------------------------')
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
        sxutil.log('END')

if __name__ == '__main__':
    car_id = input("car_id:")
    run()
    sxutil.log('ENDEND')
