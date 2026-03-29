"""Package initialization."""

import asyncio

from .methods import rpc_server


def main():
    asyncio.run(rpc_server.serve())


if __name__ == "__main__":
    main()
