"""
Dragonfly gRPC server implementation.
"""

from concurrent import futures

import grpc

from dragonfly_pb2 import GrammarData, RuleData
from dragonfly_pb2_grpc import EngineServicer, add_EngineServicer_to_server


class Servicer(EngineServicer):
    def __init__(self, engine):
        self.engine = engine

    def ListGrammars(self, request, context):
        # Send rule and grammar data back to the client.
        for grammar in self.engine.grammars:
            rules = []
            for rule in grammar.rules:
                # Check rule type through available attributes instead of types to
                # avoid cyclic import problems.
                if hasattr(rule, "spec"):
                    type_ = "CompoundRule"
                    specs = [rule.spec]
                elif hasattr(rule, "specs"):
                    specs = rule.specs
                    type_ = "MappingRule"
                else:
                    specs = []
                    type_ = "Rule"
                rules.append(RuleData(name=rule.name, specs=specs,
                                      exported=rule.exported, active=rule.active,
                                      type=type_))

            # Yield each grammar to send them to the client as a stream.
            is_active = any([r.active for r in rules])
            yield GrammarData(name=grammar.name, rules=rules,
                              enabled=grammar.enabled, active=is_active)


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
    def __init__(self, engine, address="localhost", port=50051):
        # Set up a gRPC server with an instance of the Servicer class above.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_EngineServicer_to_server(Servicer(engine), server)
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
