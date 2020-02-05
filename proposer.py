import grpc
import time
import concurrent.futures
from nodeapi import nodeapi_pb2
from nodeapi import nodeapi_pb2_grpc
from api import synerex_pb2
from api import synerex_pb2_grpc


def log(obj):
    print(obj, flush=True)

def demandCallback(client, nodeid, dm):
    log('Received message {}'.format(dm.demand_name))
    if dm.target_id != 0:
        log('getSelect')
        client.Confirm(synerex_pb2.Target(target_id=dm.id))
    else:
        pid = client.ProposeSupply(synerex_pb2.Supply(sender_id=nodeid.node_id, target_id=dm.id, channel_type=1, supply_name='Test Supply'))
        log(pid)

def subscribeDemand(client, nodeid):
    log('Subscribe Demand')
    responses = client.SubscribeDemand(synerex_pb2.Channel(client_id=nodeid.node_id, channel_type=1))
    for response in responses:
        demandCallback(client, nodeid, response)

def connectSynerexServer(nodeid):
    log("Connecting synerex Server:" + nodeid.server_info)
    with grpc.insecure_channel(nodeid.server_info) as channel:
        client = synerex_pb2_grpc.SynerexStub(channel)
        while True:
            subscribeDemand(client, nodeid)

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