#
# 道路プロバイダ（道路の空き状況を供給）
#
from __future__ import annotations
import sys
import grpc
import time
import random
import sxutil
import json # add
import argparse # add
import threading
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc
from dataclasses import dataclass
from collections import defaultdict

reserved_lane: [int, [str]] = {} # key: lane_id int, value: time [str]
reserved_car: [int, [str]] = {} # key: sender_id int, value: time [str]. sender_idはnotifiyerに紐付けられる

def demandCallback(client, demand):
    if demand.target_id != 0:
        sxutil.log("matched")
        client.Confirm(demand.id)

def supplyCallback(client, supply):
    global reserved_lane, reserved_car
    if supply.supply_name == 'to_controller':
        supply_data_from_camera = json.loads(supply.arg_json)
        sxutil.log(supply_data_from_camera)
        if supply_data_from_camera['time'] in reserved_lane.get(int(supply_data_from_camera['lane_id']), []):
            sxutil.log(f"the lane {supply_data_from_camera['lane_id']} is already reserved")
        elif supply_data_from_camera['time'] in reserved_car.get(int(supply_data_from_camera['sender_id']), []):
            sxutil.log(f"the car has already reserved lane")
        else:
            sxutil.log('can reserve')
            if int(supply_data_from_camera['lane_id']) not in reserved_lane:
                reserved_lane[int(supply_data_from_camera['lane_id'])] = []
            if int(supply_data_from_camera['sender_id']) not in reserved_car:
                reserved_car[int(supply_data_from_camera['sender_id'])] = []            

            reserved_lane[int(supply_data_from_camera['lane_id'])].append(supply_data_from_camera['time'])
            reserved_car[int(supply_data_from_camera['sender_id'])].append(supply_data_from_camera['time'])

            supply_data_to_car = {"lane_id": supply_data_from_camera['lane_id'], "car_id": supply_data_from_camera['car_id'], "time": supply_data_from_camera['time']}
            supply_ops = sxutil.SupplyOpts(target=supply_data_from_camera["target_id"], name='to_car', data=json.dumps(supply_data_to_car))
            pid = client.ProposeSupply(supply_ops)
            sxutil.log(pid)
    
            sxutil.log('--------------------------------')
            sxutil.log(f'reserved_lane: {reserved_lane}')
            sxutil.log(f'reserved_car: {reserved_car}')
            sxutil.log('--------------------------------')

def subscribeDemand(client):
    client.SubscribeDemand(demandCallback)

def subscribeSupply(client):
    client.SubscribeSupply(supplyCallback)

def run():
    srv = 'localhost:10000'
    channel_type = 1
    sxutil.log(srv)
    with grpc.insecure_channel(srv) as channel:
        sxutil.log("Connecting synerex Server:" + srv)
        client = synerex_pb2_grpc.SynerexStub(channel)
        sxClient = sxutil.SXServiceClient(client, channel_type, '')
        t1 = threading.Thread(target=subscribeDemand, args=(sxClient,))
        t2 = threading.Thread(target=subscribeSupply, args=(sxClient,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

if __name__ == '__main__':
    run()
