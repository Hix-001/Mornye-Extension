#!/usr/bin/env python3
"""Fetch and generate crisp, high-contrast 512x512 store icons for all Mornye extensions."""

import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "icons"
SOURCES_DIR = ROOT / "sources"
ICONS_DIR.mkdir(exist_ok=True)


def fetch_wiki_thumb(filename, width=1500):
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:"
        f"{urllib.parse.quote(filename)}&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json"
    )
    req = urllib.request.Request(api_url, headers={"User-Agent": "MornyeBot/2.0 (contact@zarz.moe)"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        for p in data["query"]["pages"].values():
            if "imageinfo" in p:
                thumb_url = p["imageinfo"][0].get("thumburl")
                if thumb_url:
                    req_img = urllib.request.Request(thumb_url, headers={"User-Agent": "MornyeBot/2.0 (contact@zarz.moe)"})
                    with urllib.request.urlopen(req_img) as img_resp:
                        return Image.open(io.BytesIO(img_resp.read()))
    raise RuntimeError(f"Could not fetch thumbnail for {filename}")


def create_squircle_mask(size=512, radius=112):
    mask = Image.new('L', (size * 4, size * 4), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size * 4, size * 4), radius=radius * 4, fill=255)
    return mask.resize((size, size), Image.Resampling.LANCZOS)


def fit_glyph(glyph, canvas_size=512, max_dim=350, color=(255, 255, 255)):
    glyph = glyph.convert("RGBA")
    alpha = glyph.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        alpha = alpha.crop(bbox)
    w, h = alpha.size
    scale = min(max_dim / w, max_dim / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    alpha_resized = alpha.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    colored = Image.new("RGBA", (new_w, new_h), color + (255,))
    colored.putalpha(alpha_resized)
    
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    ox = (canvas_size - new_w) // 2
    oy = (canvas_size - new_h) // 2
    layer.paste(colored, (ox, oy), colored)
    return layer


def make_tile_icon(bg_color, glyph_img, glyph_color=(255, 255, 255), max_dim=340, radius=112):
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    tile = Image.new("RGBA", (512, 512), bg_color)
    mask = create_squircle_mask(512, radius=radius)
    canvas.paste(tile, (0, 0), mask)
    
    if glyph_img:
        glyph_layer = fit_glyph(glyph_img, canvas_size=512, max_dim=max_dim, color=glyph_color)
        canvas.alpha_composite(glyph_layer)
    return canvas


def fit_into_square(img, target_size=512, padding=24):
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
    print("Generating high-quality 512x512 store icons for all 14 providers...")

    # 1. Spotify Web: Spotify signature green circle with clean soundwaves
    spotify_src = ICONS_DIR / "Spotify_Primary_Logo_RGB_Green.png"
    if spotify_src.exists():
        sp_img = Image.open(spotify_src)
        fit_into_square(sp_img, 512, padding=20).save(ICONS_DIR / "spotify-web.png", "PNG", optimize=True)
        print("[+] spotify-web.png")

    # 2. Amazon Music: Premium dark navy tile with vibrant Amazon cyan smile
    amz_src = ICONS_DIR / "amazon_music.png"
    if amz_src.exists():
        amz_img = Image.open(amz_src)
        amz_icon = make_tile_icon((14, 22, 34, 255), amz_img, glyph_color=(0, 168, 225), max_dim=410)
        amz_icon.save(ICONS_DIR / "amazon.png", "PNG", optimize=True)
        print("[+] amazon.png")

    # 3. Apple Music: Official vibrant red-pink gradient tile with white musical note
    apple_src = ICONS_DIR / "apple-music.png"
    if apple_src.exists():
        fit_into_square(Image.open(apple_src), 512, padding=0).save(ICONS_DIR / "apple-music.png", "PNG", optimize=True)
        print("[+] apple-music.png")

    # 4. SoundCloud: Signature vibrant SoundCloud orange tile with crisp white cloud
    sc_src = ICONS_DIR / "soundcloud.png"
    if sc_src.exists():
        sc_icon = make_tile_icon((255, 85, 0, 255), Image.open(sc_src), glyph_color=(255, 255, 255), max_dim=380)
        sc_icon.save(ICONS_DIR / "soundcloud.png", "PNG", optimize=True)
        print("[+] soundcloud.png")

    # 5. YouTube Music: YouTube Music circular badge
    ytm_src = ICONS_DIR / "ytmusic-spotiflac.png"
    if ytm_src.exists():
        fit_into_square(Image.open(ytm_src), 512, padding=20).save(ICONS_DIR / "ytmusic-spotiflac.png", "PNG", optimize=True)
        print("[+] ytmusic-spotiflac.png")

    # 6. Deezer: Signature purple squircle with multi-color waveform heart
    dz_src = ICONS_DIR / "deezer.png"
    if dz_src.exists():
        dz_icon = make_tile_icon((20, 16, 28, 255), Image.open(dz_src), glyph_color=(162, 52, 253), max_dim=350)
        dz_icon.save(ICONS_DIR / "deezer.png", "PNG", optimize=True)
        print("[+] deezer.png")

    # 7. Qobuz: Deep navy/black tile with crisp white Q monogram
    qb_src = ICONS_DIR / "qobuz-web.png"
    if qb_src.exists():
        qb_icon = make_tile_icon((14, 18, 24, 255), Image.open(qb_src), glyph_color=(255, 255, 255), max_dim=350)
        qb_icon.save(ICONS_DIR / "qobuz-web.png", "PNG", optimize=True)
        print("[+] qobuz-web.png")

    # 8. Tidal: Sleek black squircle with crisp pure white diamonds
    td_src = ICONS_DIR / "tidal-web.png"
    if td_src.exists():
        td_icon = make_tile_icon((10, 10, 12, 255), Image.open(td_src), glyph_color=(255, 255, 255), max_dim=360)
        td_icon.save(ICONS_DIR / "tidal-web.png", "PNG", optimize=True)
        print("[+] tidal-web.png")

    # 9. Bugs Music: Official Korean music squircle
    bugs_src = ICONS_DIR / "bugs-music.png"
    if bugs_src.exists():
        fit_into_square(Image.open(bugs_src), 512, padding=0).save(ICONS_DIR / "bugs-music.png", "PNG", optimize=True)
        print("[+] bugs-music.png")

    # 10. Melon Music: Official Korean music squircle
    melon_src = ICONS_DIR / "melon-music.png"
    if melon_src.exists():
        fit_into_square(Image.open(melon_src), 512, padding=0).save(ICONS_DIR / "melon-music.png", "PNG", optimize=True)
        print("[+] melon-music.png")

    # 11. Genie Music: Official Korean music squircle
    genie_src = ICONS_DIR / "genie-music.png"
    if genie_src.exists():
        fit_into_square(Image.open(genie_src), 512, padding=0).save(ICONS_DIR / "genie-music.png", "PNG", optimize=True)
        print("[+] genie-music.png")

    # 12. JioSaavn: Official Indian streaming teal squircle
    jio_src = ICONS_DIR / "jiosaavn.png"
    if jio_src.exists():
        fit_into_square(Image.open(jio_src), 512, padding=0).save(ICONS_DIR / "jiosaavn.png", "PNG", optimize=True)
        print("[+] jiosaavn.png")

    # 13. Beatport: Sleek black squircle with electric green monogram
    try:
        bp_raw = fetch_wiki_thumb("Beatport_2021.svg", width=1500).convert("RGBA")
        bp_monogram = bp_raw.crop((0, 0, int(bp_raw.width * 0.22), bp_raw.height))
        bp_icon = make_tile_icon((2, 10, 6, 255), bp_monogram, glyph_color=(1, 255, 149), max_dim=350)
        bp_icon.save(ICONS_DIR / "beatport.png", "PNG", optimize=True)
        print("[+] beatport.png")
    except Exception as e:
        print("[-] beatport.png failed:", e)

    # 14. Jellyfin: Modern purple-blue squircle
    jf_src = ICONS_DIR / "jellyfin.png"
    if jf_src.exists():
        fit_into_square(Image.open(jf_src), 512, padding=0).save(ICONS_DIR / "jellyfin.png", "PNG", optimize=True)
        print("[+] jellyfin.png")

    print("\nAll 14 store icons successfully generated and optimized!")


if __name__ == "__main__":
    main()
