import grpc
import time
import random
import concurrent.futures
from google.protobuf.timestamp_pb2 import Timestamp
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc

ns = []
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
futures = []
myNodeId = None

def rand_ints_nodup():
    while True:
        global ns
        n = random.randint(0, 1000)
        if not n in ns:
            ns.append(n)
            break
    return n

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
        self.ClientID = myNodeId.node_id
        self.ChannelType = mtype
        self.Client = client
        self.ArgJson = argJson
        self.MbusID = 0

    def SubscribeDemand(self, func):
        global myNodeId
        responses = self.Client.SubscribeDemand(synerex_pb2.Channel(client_id=myNodeId.node_id, channel_type=self.ChannelType))
        for response in responses:
            func(self, response)

    def SubscribeSupply(self, func):
        global myNodeId
        responses = self.Client.SubscribeSupply(synerex_pb2.Channel(client_id=myNodeId.node_id, channel_type=self.ChannelType))
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


def startKeepAlive(nodesrv):
    global myNodeId
    log('Start Keep Alive')
    update = 0
    with grpc.insecure_channel(nodesrv) as channel:
        nodeServStub = nodeapi_pb2_grpc.NodeStub(channel)
        while True:
            time.sleep(myNodeId.keepalive_duration)
            log(myNodeId)
            res = nodeServStub.KeepAlive(nodeapi_pb2.NodeUpdate(node_id=myNodeId.node_id, secret=myNodeId.secret, update_count=update, node_status=0, node_arg="OK"))
            update += 1
            if res is None:
                log("Error")
                break
            else:
                log("KeepAlive OK")

def RegisterNode(nodesrv, nm, channels, serv):
    with grpc.insecure_channel(nodesrv) as channel:
      global myNodeId
      global executor
      global futures
      nodeServStub = nodeapi_pb2_grpc.NodeStub(channel)
      if serv is None:
        myNodeType = nodeapi_pb2.NodeType.PROVIDER
        ServerInfo = ''
        WithNodeId = -1
        ClusterId = 0
        AreaId = 'Default'
      else:
        myNodeType = serv.NodeType
        ServerInfo = serv.ServerInfo
        WithNodeId = -1
        ClusterId = 0
        AreaId = 'Default'
      nif = nodeapi_pb2.NodeInfo(node_name=nm, node_type=myNodeType, server_info=ServerInfo, with_node_id=WithNodeId, cluster_id=ClusterId, area_id=AreaId, channelTypes=channels)
      myNodeId = nodeServStub.RegisterNode(nif)
      if myNodeId is None:
          log("Error connecting NodeServ.")
          raise SxError
      else:
          log("NodeServer connect success!")
      update = 0
      futures.append(executor.submit(startKeepAlive, nodesrv))
      return myNodeId.server_info
