import json
import socket
import threading
import urllib.request
from typing import Any

DOH_URL = "https://cloudflare-dns.com/dns-query"
_original = socket.getaddrinfo
_installed = False
_lock = threading.Lock()
_cache: dict[str, list[str]] = {}


def _doh_lookup(host: str) -> list[str]:
    if host in _cache:
        return _cache[host]
    request = urllib.request.Request(
        f"{DOH_URL}?name={host}&type=A", headers={"accept": "application/dns-json"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        answers = json.load(response).get("Answer", [])
    addresses = [a["data"] for a in answers if a.get("type") == 1]
    _cache[host] = addresses
    return addresses


def _getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return _original(host, port, *args, **kwargs)
    except socket.gaierror:
        if not isinstance(host, str) or host == "cloudflare-dns.com":
            raise
        addresses = _doh_lookup(host)
        if not addresses:
            raise
        results: list[Any] = []
        for address in addresses:
            results.extend(_original(address, port, *args, **kwargs))
        return results


def install_doh_fallback() -> None:
    global _installed
    with _lock:
        if not _installed:
            socket.getaddrinfo = _getaddrinfo
            _installed = True
