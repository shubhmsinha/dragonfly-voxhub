"""
Remote Procedure Call (RPC) server package

RPC functionality for dragonfly is useful for interacting with the active SR engine
from other processes instead of loading grammars to do it. One use case where this
is especially useful is responsive third party GUIs for displaying what can be said
in the current context.

This sub-package requires the grpcio and grpcio-tools packages.
"""
