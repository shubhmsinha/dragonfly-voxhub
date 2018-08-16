"""
Python script to compile the protocol buffer modules using the grpc_tools.protoc
module.

This should be run in the dragonfly/rpc directory.
"""

import shlex

import grpc_tools.protoc


def main():
    # Run the protoc module with the following arguments.
    args = shlex.split("-I. --python_out=. --grpc_python_out=. dragonfly.proto")
    exit(grpc_tools.protoc.main(args))  # re-use protoc's exit code


if __name__ == '__main__':
    main()
