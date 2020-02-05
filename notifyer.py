import grpc
import time
import concurrent.futures
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc


def log(obj):
    print(obj, flush=True)

def notifyDemand(client):
    while True:
      client.NotifyDemand(synerex_pb2.Demand(sender_id=nodeid.node_id, target_id=dm.id, channel_type=1, demand_name='Test Demand'))
      time.sleep(10)

def supplyCallback(client, nodeid, sp):
    log('Received message {}'.format(sp.supply_name))
    pid = client.SelectSupply(synerex_pb2.Target(target_id=sp.id))
    log(pid)

def subscribeSupply(client, nodeid):
    log('Subscribe Demand')
    while True:
        responses = client.SubscribeSupply(synerex_pb2.Channel(client_id=nodeid.node_id, channel_type=1))
        for response in responses:
            supplyCallback(client, nodeid, response)

def connectSynerexServer(nodeid):
    log("Connecting synerex Server:" + nodeid.server_info)
    with grpc.insecure_channel(nodeid.server_info) as channel:
        client = synerex_pb2_grpc.SynerexStub(channel)
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
        futures = [executor.submit(subscribeSupply(client, nodeid)), executor.submit(notifyDemand(client))]
        for future in concurrent.futures.as_completed(futures):
            log(future.result())
        executor.shutdown()

def startKeepAlive(stub, nodeid):
    update = 0
    while True:
        time.sleep(nodeid.keepalive_duration)
        res = stub.KeepAlive(nodeapi_pb2.NodeUpdate(node_id=nodeid.node_id, secret=nodeid.secret, update_count=update, node_status=0, node_arg="OK"))
        update += 1
        if res is None:
            log("Error")
            break
        else:
            log("KeepAlive OK")
            log(res)

def run():
    channels = [1]
    with grpc.insecure_channel('localhost:9990') as channel:
        stub = nodeapi_pb2_grpc.NodeStub(channel)
        nodeid = stub.RegisterNode(nodeapi_pb2.NodeInfo(node_name='python_provider', node_type=nodeapi_pb2.NodeType.PROVIDER, channelTypes=channels))
        if nodeid is None:
            log("Error connecting NodeServ.")
        else:
            log("NodeServer connect success!")
            log(nodeid)
            executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
            futures = [executor.submit(connectSynerexServer(nodeid)), executor.submit(startKeepAlive(stub, nodeid))]
            for future in concurrent.futures.as_completed(futures):
              log(future.result())
            executor.shutdown()

if __name__ == '__main__':
    run()
