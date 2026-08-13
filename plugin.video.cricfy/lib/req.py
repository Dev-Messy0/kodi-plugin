import requests

custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Cache-Control": "no-cache, no-store",
}

def fetch_url(url: str, timeout: int = 15, user_agent: str = None) -> str:
    headers = custom_headers.copy()
    if user_agent:
        headers["User-Agent"] = user_agent
    
    try:
        response = requests.get(
            url=url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        if response.status_code != 200:
            return ""
        return response.text
    except Exception:
        return ""