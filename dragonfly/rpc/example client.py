"""
Example dragonfly RPC client.
"""

import grpc

from dragonfly_pb2 import GrammarRequest
from dragonfly_pb2_grpc import EngineStub


def main():
    # Set up an insecure channel on localhost port 50051.
    with grpc.insecure_channel('localhost:50051') as channel:
        # Ask for a list of grammars from the server.
        stub = EngineStub(channel)
        response = stub.ListGrammars(GrammarRequest())

        # Get each grammar from the response stream.
        for grammar in response:
            print("Grammar '%s' received with the following rules:" % grammar.name)
            for rule in grammar.rules:
                print("%s(name=%s, specs=%s, exported=%s, active=%s)"
                      % (rule.type, rule.name, rule.specs, rule.exported,
                         rule.active))


if __name__ == '__main__':
    main()
