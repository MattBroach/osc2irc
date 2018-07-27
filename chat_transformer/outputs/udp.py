import logging
import asyncio

from .base import BaseOutput

logger = logging.getLogger(__name__)


class UDPProtocol(asyncio.DatagramProtocol):
    def error_Received(self, exc):
        logger.error('Protocol Error: {}'.format(exc))


class UDPOutput(BaseOutput):
    def __init__(self, ip='127.0.0.1', port=6789, loop=None):
        self.port = port
        self.ip = ip
        self.loop = loop if loop is not None else asyncio.get_event_loop()

    def connect(self):
        """
        use `asyncio` to create an OSC connection
        """
        connection = self.loop.create_datagram_endpoint(
            lambda: UDPProtocol(), remote_addr=(self.ip, self.port)
        )
        self.transport, _ = self.loop.run_until_complete(connection)

    def send(self, value):
        """
        send data to target UD
        """
        self.transport.sendto(value)
