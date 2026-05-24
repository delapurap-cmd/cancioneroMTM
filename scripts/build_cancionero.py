#!/usr/bin/env python3
"""
Convierte cancionero_esp/<bucket>/<artist_slug>/<song_slug>.txt en:
  <out>/index.json            [{a, s, k}]   metadatos globales (buscador)
  <out>/a/<artist_slug>.json  {n, songs: {song_slug: {t, b}}}
  <out>/meta.json             estadisticas del build

Uso:
  python3 scripts/build_cancionero.py <inputDir> <outDir>
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

if len(sys.argv) != 3:
    print("Uso: build_cancionero.py <inputDir> <outDir>", file=sys.stderr)
    sys.exit(1)

in_dir, out_dir = sys.argv[1], sys.argv[2]
artists_out = os.path.join(out_dir, "a")
os.makedirs(artists_out, exist_ok=True)

VALID_ARTIST_LINE = re.compile(r"^[a-záéíóúüñ0-9 .,'\-&()/]+$", re.IGNORECASE)


def prettify(slug: str) -> str:
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), slug.replace("_", " ").strip())


def read_text(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


index = []
total_songs = 0
total_artists = 0

for bucket in sorted(os.listdir(in_dir)):
    bucket_path = os.path.join(in_dir, bucket)
    if not os.path.isdir(bucket_path):
        continue
    for artist_slug in sorted(os.listdir(bucket_path)):
        artist_dir = os.path.join(bucket_path, artist_slug)
        if not os.path.isdir(artist_dir):
            continue
        files = [f for f in os.listdir(artist_dir) if f.endswith(".txt")]
        if not files:
            continue
        songs = {}
        artist_display = prettify(artist_slug)
        for fname in sorted(files):
            song_slug = fname[:-4]
            body = read_text(os.path.join(artist_dir, fname))
            lines = body.split("\n")
            first = lines[0].strip() if lines else ""
            second = lines[1].strip() if len(lines) > 1 else ""
            title = first or prettify(song_slug)
            if second and len(second) < 80 and VALID_ARTIST_LINE.match(second):
                artist_display = second
            songs[song_slug] = {"t": title, "b": body}
            index.append({"a": artist_display, "s": title, "k": f"{artist_slug}/{song_slug}"})
            total_songs += 1
        with open(os.path.join(artists_out, f"{artist_slug}.json"), "w", encoding="utf-8") as f:
            json.dump({"n": artist_display, "songs": songs}, f, ensure_ascii=False, separators=(",", ":"))
        total_artists += 1

with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, separators=(",", ":"))

with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
    json.dump({
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "artists": total_artists,
        "songs": total_songs,
    }, f, ensure_ascii=False, indent=2)

print(f"OK: {total_artists} artistas, {total_songs} canciones")
