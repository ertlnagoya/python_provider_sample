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

reserve = {'00:00:00': 'car_0'} #時間がkey,lane_idがvalueのdict

def reserveTime(delay=0):
    # 予約する時間を算出する(delayでさらに何秒後かを)
    now = dt.datetime.now()
    # 次の枠(10秒後)を指定
    now += dt.timedelta(seconds=10+delay)
    return str(now.hour)+":"+str(now.minute)+":"+str(round(now.second,-1))

def notifyDemand(client):
    sxutil.log('1.需要：このスペースに１秒後入りたいです')
    # lane_available = input("lane_available:").split(',')
    data = {"car":car_id, "lane_available":lane_available,"time":reserveTime()}
    dmo = sxutil.DemandOpts('車両:'+car_id+" 進行可能:"+str(lane_available), json.dumps(data))
    # 1. Notify Demand
    client.NotifyDemand(dmo)

def supplyCallback(client, sp):
    sxutil.log(f'供給受取：{sp.supply_name}')
    data = json.loads(sp.arg_json)
    sxutil.log(data)

    # 占有済みかどうかで分岐
    if data['state']:
        ## 3.Select Supply
        pid = client.SelectSupply(sp)
        sxutil.log(pid)
        sxutil.log('3.マッチング完了しました')
    else:
        sxutil.log('E.マッチング失敗です。すでに占有されています。')
    sxutil.log('--------------------------------')

def subscribeSupply(client):
    sxutil.log('供給待ちです...')
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
    lane_available = input('lane_available:').split(',')
    run()
    sxutil.log('ENDEND')
