#!/usr/bin/env node
/*
  Convierte cancionero_esp/<bucket>/<artist_slug>/<song_slug>.txt en:
    <out>/index.json           [{a, s, k}]   metadatos globales para el buscador
    <out>/a/<artist_slug>.json {name, songs: {song_slug: {title, body}}}

  Uso:
    node scripts/build_cancionero.js <inputDir> <outDir>
*/
const fs = require('fs');
const path = require('path');

const [,, inDir, outDir] = process.argv;
if (!inDir || !outDir) {
  console.error('Uso: node build_cancionero.js <inputDir> <outDir>');
  process.exit(1);
}

const artistsOutDir = path.join(outDir, 'a');
fs.mkdirSync(artistsOutDir, { recursive: true });

const prettify = (slug) => slug
  .replace(/_/g, ' ')
  .replace(/\s+/g, ' ')
  .trim()
  .replace(/\b\w/g, (c) => c.toUpperCase());

const index = [];
let totalSongs = 0;
let totalArtists = 0;

const buckets = fs.readdirSync(inDir).filter((b) => fs.statSync(path.join(inDir, b)).isDirectory());
for (const bucket of buckets) {
  const bucketDir = path.join(inDir, bucket);
  const artists = fs.readdirSync(bucketDir).filter((a) => fs.statSync(path.join(bucketDir, a)).isDirectory());
  for (const artistSlug of artists) {
    const artistDir = path.join(bucketDir, artistSlug);
    const files = fs.readdirSync(artistDir).filter((f) => f.endsWith('.txt'));
    if (!files.length) continue;
    const songs = {};
    let artistDisplay = prettify(artistSlug);
    for (const file of files) {
      const songSlug = file.replace(/\.txt$/, '');
      const full = path.join(artistDir, file);
      let body;
      try { body = fs.readFileSync(full, 'utf8'); }
      catch { body = fs.readFileSync(full, 'latin1'); }
      const firstLine = body.split('\n', 1)[0].trim();
      const lines = body.split('\n');
      const secondLine = (lines[1] || '').trim();
      const title = firstLine || prettify(songSlug);
      if (secondLine && /^[a-záéíóúüñ0-9 .,'\-&()/]+$/i.test(secondLine) && secondLine.length < 80) {
        artistDisplay = secondLine;
      }
      songs[songSlug] = { t: title, b: body };
      index.push({ a: artistDisplay, s: title, k: artistSlug + '/' + songSlug });
      totalSongs++;
    }
    const artistFile = path.join(artistsOutDir, artistSlug + '.json');
    fs.writeFileSync(artistFile, JSON.stringify({ n: artistDisplay, songs }));
    totalArtists++;
  }
}

fs.writeFileSync(path.join(outDir, 'index.json'), JSON.stringify(index));
fs.writeFileSync(path.join(outDir, 'meta.json'), JSON.stringify({
  builtAt: new Date().toISOString(),
  artists: totalArtists,
  songs: totalSongs,
}));

console.log(`OK: ${totalArtists} artistas, ${totalSongs} canciones`);
