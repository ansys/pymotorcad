import psutil

import ansys.motorcad.core as pymotorcad
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from jsonrpcserver import Success, method, Error, dispatch


import threading


MAX_INSTANCES = 4
PORT = 34000


numInstances = 0
MotorLaunchLock = threading.Lock()

motorInstances = []

motorInstantLock = threading.Lock()


def GetMCfromPort(aPort):
    for MC in motorInstances:
        if MC.connection._port == aPort:
            return MC


def RemoveMCfromList(aPort):
    for MC in motorInstances:
        if MC.connection._port == aPort:
            motorInstances.remove(MC)
            return


@method
def SendCommandRemote(aPort, aMethod, aParams):
    MC = GetMCfromPort(aPort)
    if MC is not None:
        result = MC.connection.send_and_receive(aMethod, aParams)
        return Success(result)
    else:
        return Error(1)


@method
def CloseMotorCAD(aPort):

    print(str(aPort) + ": attempting to close")

    try:
        MC = GetMCfromPort(aPort)
        MC.quit()

        print(str(aPort) + ": closed successfully ")
        result = Success()
    except:
        print(str(aPort) + ": failed to close")
        result = Error(1, "failed to close")
    finally:
        RemoveMCfromList(aPort)
        return result


@method
def OpenMotorCAD():

    MotorLaunchLock.acquire()

    try:
        if pymotorcad.how_many_open() < MAX_INSTANCES:
            mc_object = pymotorcad.MotorCAD()  # , Port=freePort)
            print("started MotorCAD")

        else:
            print("server is full")
            return Success(-1)

    finally:
        MotorLaunchLock.release()

    mc_object.connection._wait_for_server_to_start(psutil.Process(mc_object.connection.pid))
    mc_object.connection._wait_for_response(30)

    port = mc_object.connection._port

    motorInstantLock.acquire()
    try:
        motorInstances.append(mc_object)
    finally:
        motorInstantLock.release()

    return Success(port)


class TestHttpServer(BaseHTTPRequestHandler):
    def do_POST(self):
        # Process request
        request = self.rfile.read(int(self.headers["Content-Length"])).decode()
        response = dispatch(request)
        # Return response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())


if __name__ == "__main__":
    pymotorcad.rpc_client_core.IS_REMOTE_MACHINE = True
    print("Starting RPC server on port: " + str(PORT))
    ThreadingHTTPServer(("", PORT), TestHttpServer).serve_forever()
