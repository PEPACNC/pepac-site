"""One-time import of images and blog posts from the old Wix site.
Runs in GitHub Actions (see .github/workflows/import-wix.yml)."""
import os, re, json, html
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://www.peoplesempowermentpac.org"
IMG_DIR = "assets/img/wix"
POST_DIR = "_posts"
UA = {"User-Agent": "Mozilla/5.0 (pepac-site importer)"}
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(POST_DIR, exist_ok=True)
report = []

ID_RE = re.compile(r"([0-9a-f]{6}_[0-9a-f]{32}|[0-9a-f]{32})[^/]*?\.(jpg|jpeg|png|gif|webp)", re.I)

def media_id(url):
    m = re.search(r"wixstatic\.com/media/([^/?]+)", url or "")
    return m.group(1) if m else None

def local_name(mid):
    m = ID_RE.match(mid)
    if not m:
        return re.sub(r"[^A-Za-z0-9_.-]", "", mid)
    return f"{m.group(1)}.{m.group(2).lower().replace('jpeg','jpg')}"

def fetch_image(mid):
    name = local_name(mid)
    path = os.path.join(IMG_DIR, name)
    if os.path.exists(path):
        return name
    ext = name.rsplit(".", 1)[-1]
    urls = [f"https://static.wixstatic.com/media/{mid}/v1/fit/w_2000,h_2000,q_85/img.{ext}",
            f"https://static.wixstatic.com/media/{mid}"]
    for u in urls:
        try:
            r = requests.get(u, headers=UA, timeout=60)
            if r.ok and r.headers.get("content-type", "").startswith("image"):
                with open(path, "wb") as f:
                    f.write(r.content)
                report.append(f"- image `{name}` ({len(r.content)//1024} KB)")
                return name
        except Exception as e:
            report.append(f"- image ERROR {mid}: {e}")
    report.append(f"- image FAILED {mid}")
    return None

# 1) Page images
for line in open("tools/wix_images.txt"):
    mid = line.strip()
    if mid:
        fetch_image(mid)

# 2) Blog posts
sm = requests.get(f"{BASE}/blog-posts-sitemap.xml", headers=UA, timeout=60).text
post_urls = re.findall(r"<loc>([^<]+/post/[^<]+)</loc>", sm)
report.append(f"\n## Posts found: {len(post_urls)}")
for url in post_urls:
    slug = url.rstrip("/").split("/post/")[-1]
    soup = BeautifulSoup(requests.get(url, headers=UA, timeout=60).text, "html.parser")
    meta = lambda p: (soup.find("meta", property=p) or soup.find("meta", attrs={"name": p}) or {}).get("content", "")
    title = html.unescape(meta("og:title") or (soup.find("h1").get_text(strip=True) if soup.find("h1") else slug))
    published = meta("article:published_time")[:10]
    desc = html.unescape(meta("og:description"))
    og = media_id(meta("og:image"))
    author = "Stacey Motley"
    a = soup.select_one('[data-hook="user-name"]')
    if a and a.get_text(strip=True):
        author = a.get_text(strip=True)
    body = None; used = "article"
    for sel in ['[data-hook="post-description"]', '[data-id="content-viewer"]', '[data-id="rich-content-viewer"]', "article"]:
        body = soup.select_one(sel)
        if body and len(body.get_text(strip=True)) > 400:
            used = sel
            break
    if body is None:
        report.append(f"- post FAILED {slug}"); continue
    for t in body.select("script, style, svg, button, noscript"):
        t.decompose()
    for h1 in body.find_all("h1"):
        if h1.get_text(strip=True) == title:
            h1.decompose()
    # images -> local
    for img in body.find_all("img"):
        mid = media_id(img.get("src", "")) or media_id(img.get("data-src", ""))
        if not mid:
            img.decompose(); continue
        name = fetch_image(mid)
        img.attrs = {"src": f"/assets/img/wix/{name}", "alt": img.get("alt", "")}
    for wix in body.find_all("wow-image"):
        wix.unwrap()
    text = md(str(body), heading_style="ATX", strip=["span", "div", "figure"])
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.sub(r"\(/assets/img/wix/", "({{ '/assets/img/wix/", text)
    text = re.sub(r"(\{\{ '/assets/img/wix/[^)\s]+)\)", r"\1' | relative_url }})", text)
    image = fetch_image(og) if og else None
    fm = {"layout": "post", "title": title, "date": published, "author": author,
          "description": desc, "permalink": f"/post/{slug}"}
    if image:
        fm["image"] = f"/assets/img/wix/{image}"
    front = "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()) + "---\n\n"
    fname = os.path.join(POST_DIR, f"{published}-{slug[:60].rstrip('-')}.md")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(front + text + "\n")
    report.append(f"- post `{fname}` via `{used}` ({len(text)} chars)")

with open("tools/import-report.md", "w") as f:
    f.write("# Wix import report\n\n" + "\n".join(report) + "\n")
print("\n".join(report))
