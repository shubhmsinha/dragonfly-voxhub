"""
Dragonfly gRPC server implementation.
"""

from concurrent import futures

import time
import grpc

from dragonfly_pb2 import GrammarData, RuleData
from dragonfly_pb2_grpc import EngineServicer, add_EngineServicer_to_server


class Servicer(EngineServicer):

    def ListGrammars(self, request, context):
        # Send the grammars.
        # TODO Send grammars from the engine.
        # TODO Use 'yield' instead of building all GrammarData objects at once.
        grammar_data = [
            GrammarData(name="test1", rules=[
                RuleData(name="mapping_rule1", specs=["test", "testing"],
                         exported=True, active=True, type="MappingRule")
            ]),
            GrammarData(name="test2", rules=[
                RuleData(name="compound_rule1", specs=["compound test"],
                         exported=True, active=True, type="CompoundRule")
            ])
        ]
        for data in grammar_data:
            yield data


class DragonflyRPCServer(object):
    """
    gRPC server class.

    This class will run a gRPC server on localhost port 50051 by default using
    HTTP. Start the server using `start()` and stop it using `stop()`.

    If a secure port is required, you can subclass this and override
    the `_add_port` method. Although it is probably easier to access the server
    via ssh port forwarding using something like:

    ssh -NTf -L 50051:localhost:50051 <system-with-rpc-server>
    """
    def __init__(self, address="localhost", port=50051):
        # Set up a gRPC server with an instance of the Servicer class above.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_EngineServicer_to_server(Servicer(), server)
        self._server = server
        self._add_port(address, port)

    def _add_port(self, address, port):
        # Specify the address and port to use.
        self._server.add_insecure_port("%s:%d" % (address, port))

    def start(self):
        """
        Start the server. This method is non-blocking, the gRPC server will
        run entirely on separate threads.
        """
        self._server.start()

    def stop(self):
        """
        Stop the server if it is running.
        """
        self._server.stop(0)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


if __name__ == '__main__':
    # Run the server if this module is run as a script.
    try:
        with DragonflyRPCServer():
            while True:
                time.sleep(10000)  # don't need to wake up much
    except KeyboardInterrupt:
        exit(0)
