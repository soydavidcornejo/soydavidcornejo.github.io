#!/usr/bin/env python3
"""al_dia — pone al día las cifras y versiones de index.html. Solo biblioteca estándar.

  python3 herramientas/al_dia.py

Cambia solo el texto de los elementos con data-auto:
- data-auto="version:<dueño>/<repo>" → la versión del último Release del repo («v0.2.0»); vacío si no hay.
- data-auto="pieza:apps" | "pieza:piezas" | "pieza:listas" → las cifras de la página de Pieza (datos/proyectos.json y
  datos/catalogo.json).

Si algo cambió, también pone la fecha de hoy en sitemap.xml (<lastmod>). Si un dato no se puede leer, deja el que estaba.
Lo corre .github/workflows/al-dia.yml (cada día, a mano o cuando Pieza o una app avisa).
"""
import datetime
import json
import os
import re
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIEZA = "https://pieza-app.github.io/pieza/datos/"
REPO = re.compile(r"^[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}$")
VERSION = re.compile(r"^v?\d{1,4}(\.\d{1,4}){1,3}$")


def leer(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": "soydavidcornejo-al-dia", "Accept": "application/json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        pedido.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(pedido, timeout=20) as r:
            return json.loads(r.read(2_000_000))
    except (OSError, ValueError):
        return None


def valores(claves):
    v = {}
    proyectos, catalogo = leer(PIEZA + "proyectos.json"), leer(PIEZA + "catalogo.json")
    if isinstance(proyectos, dict) and isinstance(proyectos.get("total"), int):
        v["pieza:apps"] = str(proyectos["total"])
    if isinstance(catalogo, dict) and isinstance(catalogo.get("total"), int) and isinstance(catalogo.get("listas"), int):
        v["pieza:piezas"], v["pieza:listas"] = str(catalogo["total"]), str(catalogo["listas"])
    for clave in claves:
        if clave.startswith("version:") and REPO.match(clave[8:]):
            r = leer(f"https://api.github.com/repos/{clave[8:]}/releases/latest")
            tag = r.get("tag_name") if isinstance(r, dict) else None
            if isinstance(tag, str) and VERSION.match(tag):
                v[clave] = tag if tag.startswith("v") else "v" + tag
    return v


def main():
    ruta = os.path.join(RAIZ, "index.html")
    with open(ruta, encoding="utf-8") as f:
        html = f.read()
    patron = re.compile(r'(<(\w+)\b[^>]*\bdata-auto="([^"]+)"[^>]*>)([^<]*)(</\2>)')
    v = valores({m.group(3) for m in patron.finditer(html)})
    nuevo = patron.sub(lambda m: m.group(1) + v.get(m.group(3), m.group(4)) + m.group(5), html)
    if nuevo == html:
        print("Sin cambios.")
        return
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(nuevo)
    sitemap = os.path.join(RAIZ, "sitemap.xml")
    if os.path.isfile(sitemap):
        with open(sitemap, encoding="utf-8") as f:
            s = f.read()
        hoy = datetime.date.today().isoformat()
        s2 = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{hoy}</lastmod>", s, count=1)
        if s2 == s and "<lastmod>" not in s:
            s2 = s.replace("</loc>", f"</loc><lastmod>{hoy}</lastmod>", 1)
        with open(sitemap, "w", encoding="utf-8") as f:
            f.write(s2)
    print("✓ Al día:", ", ".join(f"{k}={x}" for k, x in sorted(v.items())))


if __name__ == "__main__":
    main()
