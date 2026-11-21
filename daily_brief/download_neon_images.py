"""Download actual imagery embedded in Google's Gemini 4 Neon announcement.

Run locally: uv run python daily_brief/download_neon_images.py
Images are sourced only from the linked Google article, not generated or stock.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import json

URL = "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/"
OUT = Path(__file__).resolve().parent / "assets" / "neon"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LearnWithObscure/1.0)"}


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hero = None
        self.candidates = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "meta" and data.get("property") in ("og:image", "twitter:image"):
            self.hero = self.hero or data.get("content")
        if tag == "img":
            source = data.get("src") or data.get("data-src")
            if source:
                self.candidates.append((data.get("alt", ""), source))


def fetch(url):
    with urlopen(Request(url, headers=HEADERS), timeout=35) as response:
        return response.read(), response.headers.get("Content-Type", "")


def save(name, url):
    url = urljoin(URL, url)
    if urlparse(url).scheme != "https":
        raise ValueError("Image URLs must be HTTPS")
    body, kind = fetch(url)
    if not kind.lower().startswith("image/"):
        raise ValueError(f"Expected an image from {url}, got {kind}")
    if len(body) < 5000:
        raise ValueError(f"Image too small: {url}")
    # The renderer accepts JPEG / PNG; WebP may need Pillow conversion.
    ext = ".png" if "png" in kind else ".webp" if "webp" in kind else ".jpg"
    output = OUT / (name + ext)
    output.write_bytes(body)
    return {"file": output.name, "source": url, "alt": name, "content_type": kind}


def main():
    html, _ = fetch(URL)
    parser = Images()
    parser.feed(html.decode("utf-8", errors="replace"))
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    if not parser.hero:
        raise RuntimeError("Google's article did not expose an official hero image.")
    records.append(save("launch", parser.hero))
    # One secondary visual from the actual article (if available).
    for alt, src in parser.candidates:
        if any(t in alt.lower() for t in ("benchmark", "coding", "antigravity", "neon")):
            try:
                entry = save("evidence", src)
            except (OSError, ValueError):
                continue
            entry["alt"] = alt
            records.append(entry)
            break
    (OUT / "sources.json").write_text(
        json.dumps({"article": URL, "images": records}, indent=2), encoding="utf-8"
    )
    print("Downloaded official article imagery:")
    for item in records:
        print(" ", item["file"], "←", item["source"])
    if len(records) == 1:
        print("No secondary image found. The video will reuse the official hero image.")


if __name__ == "__main__":
    main()
