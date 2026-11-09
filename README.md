# soydavidcornejo.github.io

Página personal de David Cornejo: https://soydavidcornejo.github.io/

HTML hecho a mano, sin dependencias, cookies ni seguimiento. Español e inglés (`?lang=en`).
Tipografía: Bricolage Grotesque (SIL OFL 1.1), autoalojada en `fuentes/`.

## Al día sola

`.github/workflows/al-dia.yml` corre una vez al día. Corre `herramientas/al_dia.py`, que pone al día:

- la versión de cada app (el último Release de su repo);
- las cifras de Pieza (apps, piezas y piezas listas, de la página de Pieza).

El script solo cambia el texto de los elementos con `data-auto`. Si algo cambió, hace un commit.
