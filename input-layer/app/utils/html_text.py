from bs4 import BeautifulSoup
from typing import Optional

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # remove scripts/styles
    for tag in soup(["script","style","header","footer","nav","aside","form"]):
        tag.decompose()
    # main text fallback
    texts = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
    if texts:
        return "\n\n".join(texts)[:20000]
    return soup.get_text(separator=" ", strip=True)[:20000]
