import asyncio
from urllib import robotparser
from urllib.parse import urlparse
import httpx

_user_agent = None
_parsers = {}
_lock = asyncio.Lock()

async def can_fetch(url: str, user_agent: str):
    global _user_agent
    _user_agent = user_agent
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    async with _lock:
        rp = _parsers.get(base)
        if rp is None:
            rp = robotparser.RobotFileParser()
            robots_url = base.rstrip("/") + "/robots.txt"
            try:
                async with httpx.AsyncClient(timeout=10) as c:
                    r = await c.get(robots_url, headers={"User-Agent": user_agent})
                    text = r.text if r.status_code == 200 else ""
                rp.parse(text.splitlines())
            except Exception:
                # If robots.txt unreachable, default to allow (conservative: allow)
                rp = None
            _parsers[base] = rp
    if _parsers[base] is None:
        return True
    return _parsers[base].can_fetch(user_agent, url)
