# This file is part of Dragonfly.
# (c) Copyright 2007, 2008 by Christo Butcher
# Licensed under the LGPL.
#
#   Dragonfly is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Dragonfly is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with Dragonfly.  If not, see
#   <http://www.gnu.org/licenses/>.
#

import unittest

import grpc

from dragonfly import *
from dragonfly.rpc import GrammarRequest, EngineStub, RuleData, GrammarData


class RPCMethodTests(unittest.TestCase):
    """
    Tests for RPC server methods.
    """

    def setUp(self):
        # Initialise the engine. This will start the server.
        engine = get_engine()
        self.engine = engine

        if engine.name == "sphinx":
            # Set some engine configuration for testing.
            self.engine.config.TRAINING_DATA_DIR = None
            self.engine.config.START_ASLEEP = False
            self.engine.config.LANGUAGE = "en"

        # Call connect().
        self.engine.connect()

    def tearDown(self):
        self.engine.disconnect()

    def test_ListGrammars(self):
        # Load a Grammar with three rules and check that the RPC returns the correct
        # data for them.
        g = Grammar("test", engine=self.engine)
        g.add_rule(CompoundRule(name="compound", spec="testing", exported=True))
        g.add_rule(MappingRule(name="mapping", mapping={
            "command a": ActionBase(),
            "command b": ActionBase()
        }))
        g.add_rule(Rule(name="base", element=Literal("hello world"),
                        exported=False))
        g.load()

        # Start a client, send a GrammarRequest and check the response.
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = EngineStub(channel)
            response = stub.ListGrammars(GrammarRequest())
            grammars = []
            for grammar in response:
                grammars.append(grammar)

            self.assertListEqual(grammars, [
                GrammarData(name="test", enabled=True, active=True, rules=[
                    RuleData(name="compound", specs=["testing"], exported=True,
                             active=True, type="CompoundRule"),
                    RuleData(name="mapping", specs=["command b", "command a"],
                             exported=True, active=True, type="MappingRule"),
                    RuleData(name="base", specs=[], active=True, type="Rule")
                ])
            ])


if __name__ == '__main__':
    unittest.main()
