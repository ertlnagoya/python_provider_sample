#
# 車両プロバイダ（道路の占有を要求）
#
from __future__ import annotations
import sys
import grpc
import time
import random
import sxutil
import json # add
import datetime as dt # add
import argparse # add
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc
# from proto.ganechi import ganechi_pb2
# from proto.ganechi import ganechi_pb2_grpc
from dataclasses import dataclass


# 予約する時間を算出する
def reserveTime() -> str:
    reserved_time = dt.datetime.now() + dt.timedelta(seconds=10)
    return str(reserved_time.hour) + ":" + str(reserved_time.minute) + ":" + str(reserved_time.second-reserved_time.second%10)

def notifyDemand(client):
    lane_available = input('lane_available:').split(',')
    data = {"car_id": car_id, "lane_available": lane_available,"time": reserveTime()}
    sxutil.log(f'Demand: {data}')
    demand_ops = sxutil.DemandOpts(name='to_camera', data=json.dumps(data))
    client.NotifyDemand(demand_ops)
    sxutil.log('waiting for supply')
    sxutil.log('--------------------------------')

def supplyCallback(client, supply):
    supply_data_from_lanecontroller = json.loads(supply.arg_json)
    # 自分の車に向けられた供給でなければ，return
    if supply_data_from_lanecontroller['car_id'] != car_id:
        return
    if supply.supply_name != 'to_car':
        return

    sxutil.log('--------------------------------')
    sxutil.log(f'supply: lane_id is {supply_data_from_lanecontroller["lane_id"]}')
    sxutil.log(f'supply: time is {supply_data_from_lanecontroller["time"]}')
    sxutil.log('--------------------------------')

    client.SelectSupply(supply)
    # send next demand
    notifyDemand(client)

def subscribeSupply(client):
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
        notifyDemand(sxClient)
        subscribeSupply(sxClient)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='車両プロバイダ（道路の占有を要求）')
    parser.add_argument('car_id', type=str, help='car_id')
    args = parser.parse_args()
    car_id = args.car_id
    run()
