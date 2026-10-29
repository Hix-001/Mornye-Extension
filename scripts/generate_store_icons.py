#!/usr/bin/env python3
"""Fetch and generate crisp 512x512 store icons for all Mornye extensions."""

import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "icons"
SOURCES_DIR = ROOT / "sources"
ICONS_DIR.mkdir(exist_ok=True)


def fetch_wiki_thumb(filename, width=1024):
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:"
        f"{urllib.parse.quote(filename)}&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json"
    )
    req = urllib.request.Request(api_url, headers={"User-Agent": "MornyeBot/1.0 (https://github.com/mornyeapp/Mornye-Extension)"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        for p in data["query"]["pages"].values():
            if "imageinfo" in p:
                thumb_url = p["imageinfo"][0].get("thumburl")
                if thumb_url:
                    req_img = urllib.request.Request(thumb_url, headers={"User-Agent": "MornyeBot/1.0"})
                    with urllib.request.urlopen(req_img) as img_resp:
                        return Image.open(io.BytesIO(img_resp.read()))
    raise RuntimeError(f"Could not fetch thumbnail for {filename}")


def fit_into_square(img, target_size=512, padding=32):
    """Fit image into target_size x target_size transparent canvas with padding."""
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    max_dim = target_size - (padding * 2)
    w, h = img.size
    scale = min(max_dim / w, max_dim / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)
    return canvas


def main():
    print("Generating store icons...")

    # 1. Spotify Web
    spotify_src = ICONS_DIR / "Spotify_Primary_Logo_RGB_Green.png"
    if spotify_src.exists():
        sp_img = Image.open(spotify_src)
        fit_into_square(sp_img, 512, padding=24).save(ICONS_DIR / "spotify-web.png", "PNG", optimize=True)
        print("[+] spotify-web.png")

    # 2. Amazon Music
    amz_img = fetch_wiki_thumb("Amazon_Music_logo.svg", width=1200)
    fit_into_square(amz_img, 512, padding=36).save(ICONS_DIR / "amazon.png", "PNG", optimize=True)
    # also update amazon_music.png
    fit_into_square(amz_img, 512, padding=36).save(ICONS_DIR / "amazon_music.png", "PNG", optimize=True)
    print("[+] amazon.png & amazon_music.png")

    # 3. Apple Music
    apple_src = ICONS_DIR / "apple_music.png"
    if apple_src.exists():
        ap_img = Image.open(apple_src)
        fit_into_square(ap_img, 512, padding=24).save(ICONS_DIR / "apple-music.png", "PNG", optimize=True)
        print("[+] apple-music.png")

    # 4. SoundCloud
    sc_full = fetch_wiki_thumb("Soundcloud_logo.svg", width=2000).convert("RGBA")
    sc_cloud = sc_full.crop((0, 0, 1005, sc_full.height))
    fit_into_square(sc_cloud, 512, padding=40).save(ICONS_DIR / "soundcloud.png", "PNG", optimize=True)
    print("[+] soundcloud.png")

    # 5. YouTube Music
    ytm_img = fetch_wiki_thumb("Youtube_Music_icon.svg", width=1024)
    fit_into_square(ytm_img, 512, padding=24).save(ICONS_DIR / "ytmusic-spotiflac.png", "PNG", optimize=True)
    print("[+] ytmusic-spotiflac.png")

    # 6. Deezer
    dz_img = fetch_wiki_thumb("Deezer_New_Icon.svg", width=1024)
    fit_into_square(dz_img, 512, padding=28).save(ICONS_DIR / "deezer.png", "PNG", optimize=True)
    print("[+] deezer.png")

    # 7. Qobuz
    qb_img = fetch_wiki_thumb("Qobuz_qbz_icon.svg", width=1024)
    fit_into_square(qb_img, 512, padding=28).save(ICONS_DIR / "qobuz-web.png", "PNG", optimize=True)
    print("[+] qobuz-web.png")

    # 8. Tidal
    td_full = fetch_wiki_thumb("Tidal_(service)_logo.svg", width=2000).convert("RGBA")
    td_diamonds = td_full.crop((19, 0, 775, td_full.height))
    fit_into_square(td_diamonds, 512, padding=40).save(ICONS_DIR / "tidal-web.png", "PNG", optimize=True)
    print("[+] tidal-web.png")

    # 9. Bugs Music
    bugs_src = SOURCES_DIR / "bugs-music" / "icon.png"
    if bugs_src.exists():
        fit_into_square(Image.open(bugs_src), 512, padding=0).save(ICONS_DIR / "bugs-music.png", "PNG", optimize=True)
        print("[+] bugs-music.png")

    # 10. Melon Music
    melon_src = SOURCES_DIR / "melon-music" / "icon.png"
    if melon_src.exists():
        fit_into_square(Image.open(melon_src), 512, padding=0).save(ICONS_DIR / "melon-music.png", "PNG", optimize=True)
        print("[+] melon-music.png")

    # 11. Genie Music
    genie_src = SOURCES_DIR / "genie-music" / "icon.png"
    if genie_src.exists():
        fit_into_square(Image.open(genie_src), 512, padding=0).save(ICONS_DIR / "genie-music.png", "PNG", optimize=True)
        print("[+] genie-music.png")

    # 12. JioSaavn
    jio_full = fetch_wiki_thumb("JioSaavn_Logo.svg", width=1024).convert("RGBA")
    jio_icon = jio_full.crop((0, 0, jio_full.height, jio_full.height))
    fit_into_square(jio_icon, 512, padding=0).save(ICONS_DIR / "jiosaavn.png", "PNG", optimize=True)
    print("[+] jiosaavn.png")

    print("\nAll 12 icons successfully generated in icons/ directory!")


if __name__ == "__main__":
    main()
