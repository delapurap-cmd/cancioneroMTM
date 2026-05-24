# Cancionero MTM (privado)

Catálogo personal de ~132k canciones con cifrado. Servido por GitHub Pages (privado).

## Estructura
- `assets/repertoire/cancionero_esp.zip` — fuente única de canciones (.txt en carpetas por artista)
- `scripts/build_cancionero.py` — genera el índice y los shards JSON a partir del zip
- `index.html` — UI (buscador, listado por artista, visor con transportador)
- `.github/workflows/deploy.yml` — extrae el zip y genera los shards en cada push, luego despliega a Pages

## Setup local (opcional)
```bash
mkdir -p /tmp/cancionero_full
unzip -q assets/repertoire/cancionero_esp.zip -d /tmp/cancionero_full/
python3 scripts/build_cancionero.py /tmp/cancionero_full/cancionero_esp ./cancionero-data
python3 -m http.server 8765
# Abrir http://localhost:8765/
```

## Para actualizar el catálogo
Reemplazar `assets/repertoire/cancionero_esp.zip` y pushear. El workflow re-genera todo automáticamente.

## Requisito de despliegue
Settings → Pages → Source: **GitHub Actions** (no "Deploy from a branch").
