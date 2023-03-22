import psutil

import ansys.motorcad.core as pymotorcad
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from jsonrpcserver import Success, method, Error, dispatch


import threading


MAX_INSTANCES = 4
PORT = 34000


num_instances = 0
motor_launch_lock = threading.Lock()

motor_instances = []

motor_instant_lock = threading.Lock()


def get_mc_from_port(a_port):
    for mc in motor_instances:
        if mc.connection._port == a_port:
            return mc


def remove_mc_from_list(a_port):
    for mc in motor_instances:
        if mc.connection._port == a_port:
            motor_instances.remove(mc)
            return


@method
def send_command_remote(a_port, a_method, a_params):
    mc = get_mc_from_port(a_port)
    if mc is not None:
        result = mc.connection.send_and_receive(a_method, a_params)
        return Success(result)
    else:
        return Error(1)


@method
def close_motor_cad(aPort):

    print(str(aPort) + ": attempting to close")

    try:
        mc = get_mc_from_port(aPort)
        mc.quit()

        print(str(aPort) + ": closed successfully ")
        result = Success()
    except:
        print(str(aPort) + ": failed to close")
        result = Error(1, "failed to close")
    finally:
        remove_mc_from_list(aPort)
        return result


@method
def open_motor_cad():

    motor_launch_lock.acquire()

    try:
        if pymotorcad.how_many_open() < MAX_INSTANCES:
            mc_object = pymotorcad.MotorCAD()  # , Port=freePort)
            print("started MotorCAD")

        else:
            print("server is full")
            return Success(-1)

    finally:
        motor_launch_lock.release()

    mc_object.connection._wait_for_server_to_start(psutil.Process(mc_object.connection.pid))
    mc_object.connection._wait_for_response(30)

    port = mc_object.connection._port

    motor_instant_lock.acquire()
    try:
        motor_instances.append(mc_object)
    finally:
        motor_instant_lock.release()

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
