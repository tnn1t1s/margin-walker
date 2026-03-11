"""AbletonOSC client — sends OSC messages and receives replies."""

import time
import threading
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


_DEFAULT_SEND_PORT = 11000
_DEFAULT_RECV_PORT = 11001
_DEFAULT_HOST = "127.0.0.1"
_TIMEOUT = 5.0


class AbletonOSCClient:
    def __init__(
        self,
        host: str = _DEFAULT_HOST,
        send_port: int = _DEFAULT_SEND_PORT,
        recv_port: int = _DEFAULT_RECV_PORT,
    ):
        self._host = host
        self._send_port = send_port
        self._recv_port = recv_port
        self._client = SimpleUDPClient(host, send_port)
        self._responses: dict[str, list] = {}
        self._lock = threading.Lock()
        self._dispatcher = Dispatcher()
        self._dispatcher.set_default_handler(self._handle_response)
        self._server = BlockingOSCUDPServer(
            (host, recv_port), self._dispatcher
        )
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def _handle_response(self, address: str, *args):
        with self._lock:
            self._responses[address] = list(args)

    def send(self, address: str, *args) -> None:
        self._client.send_message(address, list(args))

    def query(self, address: str, *args, timeout: float = _TIMEOUT) -> list:
        with self._lock:
            self._responses.pop(address, None)

        self._client.send_message(address, list(args))

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                if address in self._responses:
                    return self._responses.pop(address)
            time.sleep(0.01)
        raise TimeoutError(f"No response for {address} within {timeout}s")

    def close(self):
        self._server.shutdown()


_instance: AbletonOSCClient | None = None


def get_client() -> AbletonOSCClient:
    global _instance
    if _instance is None:
        _instance = AbletonOSCClient()
    return _instance
