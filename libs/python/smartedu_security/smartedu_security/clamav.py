from __future__ import annotations

import socket
import struct
from dataclasses import dataclass
from typing import BinaryIO


@dataclass(frozen=True, slots=True)
class MalwareScanResult:
    clean: bool
    signature: str | None = None
    raw_response: str = ""


class MalwareScanError(RuntimeError):
    pass


def parse_clamav_response(response: str) -> MalwareScanResult:
    value = response.strip()
    if value.endswith(" OK"):
        return MalwareScanResult(clean=True, raw_response=value)

    marker = " FOUND"
    if value.endswith(marker):
        prefix = value[: -len(marker)]
        _, _, signature = prefix.partition(": ")
        return MalwareScanResult(
            clean=False,
            signature=signature or "unknown",
            raw_response=value,
        )

    raise MalwareScanError(f"Unexpected ClamAV response: {value!r}")


class ClamAVScanner:
    def __init__(
        self,
        *,
        host: str,
        port: int = 3310,
        timeout_seconds: float = 10.0,
        chunk_size: int = 64 * 1024,
    ):
        self.host = host
        self.port = port
        self.timeout_seconds = timeout_seconds
        self.chunk_size = chunk_size

    def scan_stream(self, stream: BinaryIO) -> MalwareScanResult:
        with socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout_seconds,
        ) as sock:
            sock.settimeout(self.timeout_seconds)
            sock.sendall(b"zINSTREAM\0")

            while True:
                chunk = stream.read(self.chunk_size)
                if not chunk:
                    break
                sock.sendall(struct.pack("!I", len(chunk)))
                sock.sendall(chunk)

            sock.sendall(struct.pack("!I", 0))

            parts: list[bytes] = []
            while True:
                piece = sock.recv(4096)
                if not piece:
                    break
                parts.append(piece)
                if b"\0" in piece or b"\n" in piece:
                    break

        if not parts:
            raise MalwareScanError("ClamAV returned no response")
        raw = (
            b"".join(parts)
            .rstrip(b"\0\r\n")
            .decode(
                "utf-8",
                errors="replace",
            )
        )
        return parse_clamav_response(raw)
