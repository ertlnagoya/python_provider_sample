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

def demandCallback(client, demand):
    if demand.demand_name == 'to_camera':
        demand_data = json.loads(demand.arg_json)
        sxutil.log(f'demand_data: {demand_data}')
        if lane_id in demand_data['lane_available']:
            supply_data = {"lane_id": lane_id, "car_id": demand_data['car_id'], "time": demand_data['time'], "sender_id": demand.sender_id, "target_id": demand.id}
            supply_ops = sxutil.SupplyOpts(target=demand.id, name='to_controller', data=json.dumps(supply_data))
            response = client.ProposeSupply(supply_ops)

def subscribeDemand(client):
    sxutil.log('waiting for demand')
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
        subscribeDemand(sxClient)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='道路プロバイダ（道路の空き状態を提供）')
    parser.add_argument('lane_id', type=str, help='lane_id')
    args = parser.parse_args()
    lane_id = args.lane_id
    run()
