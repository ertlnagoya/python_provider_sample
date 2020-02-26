import grpc
import time
import random
from google.protobuf.timestamp_pb2 import Timestamp
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

ns = []

def rand_ints_nodup():
    while True:
        global ns
        n = random.randint(0, 1000)
        if not n in ns:
            ns.append(n)
            break
    return n

myNodeId = rand_ints_nodup()

def log(obj):
    print(obj, flush=True)

class SxError(Exception):
    pass

class DemandOpts:
    def __init__(self, name):
        self.ID = 0
        self.Target = 0
        self.Name = name
        self.JSON = ''
        self.Cdata = None

class SupplyOpts:
    def __init__(self, target, name):
        self.ID = 0
        self.Target = target
        self.Name = name
        self.JSON = ''
        self.Cdata = None

class SxServerOpts:
    def __init__(self):
        self.NodeType = None
        self.ServerInfo = ''
        self.ClusterId = 0
        self.AreaId = ''
        self.GwInfo = ''

class SXServiceClient:
    def __init__(self, client, mtype, argJson):
        self.ClientID = myNodeId
        self.ChannelType = mtype
        self.Client = client
        self.ArgJson = argJson
        self.MbusID = 0

    def SubscribeDemand(self, func):
        global myNodeId
        responses = self.Client.SubscribeDemand(synerex_pb2.Channel(client_id=myNodeId, channel_type=self.ChannelType))
        log(responses)
        for response in responses:
            func(self, response)

    def SubscribeSupply(self, func):
        global myNodeId
        responses = self.Client.SubscribeSupply(synerex_pb2.Channel(client_id=myNodeId, channel_type=self.ChannelType))
        log(responses)
        for response in responses:
            func(self, response)

    def ProposeSupply(self, spo):
        timestamp = Timestamp()
        sp = synerex_pb2.Supply(id=rand_ints_nodup(), sender_id=self.ClientID, target_id=spo.Target, channel_type=self.ChannelType, supply_name=spo.Name, ts=timestamp)
        pid = self.Client.ProposeSupply(sp)
        return pid

    def Confirm(self, id):
        tg = synerex_pb2.Target(id=rand_ints_nodup(), sender_id=self.ClientID, target_id=id, channel_type=self.ChannelType)
        self.Client.Confirm(tg)

    def NotifyDemand(self, dmo):
        timestamp = Timestamp()
        dm = synerex_pb2.Demand(id=rand_ints_nodup(), sender_id=self.ClientID, channel_type=self.ChannelType, demand_name=dmo.Name, ts=timestamp)
        self.Client.NotifyDemand(dm)
        return dmo.ID

    def SelectSupply(self, sp):
        tgt = synerex_pb2.Target(id=rand_ints_nodup(), sender_id=self.ClientID, target_id=sp.id, channel_type=self.ChannelType)
        self.Client.SelectSupply(tgt)
