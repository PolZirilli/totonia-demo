# TV screen alignment

The approved master is 1672 × 941. The previous 1660 × 920 CSS stage distorted it; the old screen rectangle extended below the glass, and both art layers used an opaque master that disappeared on emulator startup.

The current glass aperture has a bounding box of x=665, y=162, width=758, height=527 in master pixels. Its actual shape follows the curved CRT interior and Toto's overlapping hair. A two-pixel inset retains the original dark glass rim. The framebuffer fills this bounding box; the persistent RGBA foreground clips the visible image to the glass. The original master remains behind it. Layer order: master → poster/game → foreground. The foreground ignores pointer events.

`assets/art-metadata.json`, its existing legacy duplicate `aart-metadata.json`, the poster, overlay and `screen-geometry.css` are generated together by `scripts/build-screen-art.py` (Python 3 + Pillow). Run from any directory with `python scripts/build-screen-art.py`. The fill is deliberately restricted to this approved master; if artwork changes, review the aperture visually before regenerating. No generative editing or repainting is used. Overlay RGB comes directly from the original image; only alpha changes. Reconstruction with the poster is asserted to match the original pixel for pixel.

## Validation

Chrome, local HTTP server, real bundled Genesis.js engine and ROM:

- 1440 × 900 desktop, 1024 × 768 tablet landscape, 768 × 1024 tablet portrait, and 1920 × 900 wide desktop (height-constrained stage).
- Emulator reaches its ready state; canvas bounds match the screen slot; overlay stays fully visible above the canvas; no browser page errors during successful startup.
- Solid magenta substituted above the framebuffer confirms that content stays inside the glass, including around Toto's hair. Cats, console and TV frame remain intact.
- Blocked ROM request retains the original blue-screen illustration through the poster, foreground and background layers.
- Master artwork, ROM, engine, application logic and control mappings remain unchanged.

Screenshots: [desktop](qa/desktop.png), [tablet portrait](qa/tablet-portrait.png), [solid aperture check](qa/aperture-check.png).

The rounded CRT perimeter intentionally masks a narrow strip at the edges of the rectangular framebuffer. Tablet portrait keeps the complete approved composition centered, with space above and below.

## Arte centrado (fix/centrado-y-audio)

La TV se movió 208 px a la izquierda: el vidrio ahora está en x=457, y=162, 758 × 527 (`--screen-left: 27.3325358852%`; `art-metadata.json` y `aart-metadata.json`: `screen.x=457`, `leftPct=0.2733253588516746`). El logo TOTONIA del fondo se quitó y el fondo derecho se completó con tribuna, farol y muro. Toto, los gatos y la consola conservan píxeles y posición.

`scripts/build-centered-art.py` genera `desktop-master.png`, `desktop-overlay-screen-hole.png` y `screen-poster.png` a partir de los assets ORIGINALES (master 1672×941 con la TV en x=665). Correrlo una sola vez sobre los originales; sobre el master ya centrado falla o da un resultado incorrecto.

**`scripts/build-screen-art.py` asume el master viejo (x=665). No correrlo sobre el master nuevo**: sobrescribiría la geometría centrada con valores obsoletos.

## Audio

`Genesis.min.js` crea el `AudioContext` al cargar, sin gesto del usuario, y solo lo reanuda en `touchstart`; en escritorio quedaba `suspended`. `app.js` lo reanuda en `pointerdown`, `keydown` y `touchstart` (capture) y reinicia `GENESIS_NEXT_AUDIO_TIME=0` y `GENESIS_AUDIO_START_TIME=null`. Mientras siga suspendido se muestra el aviso "Toca o presiona una tecla para activar el sonido". El motor no se tocó.

## QA del arte centrado

`scripts/qa-playwright.py` (Chromium headless, servidor local). Resultados:

| Viewport | Canvas = vidrio | Orden de capas | Errores de consola | AudioContext antes → después del clic/tecla |
|---|---|---|---|---|
| 1440×900 | sí (393.6, 184.3, 652.8×453.9) | slot → overlay → master | 0 | suspended → running |
| 1920×900 | sí (597.5, 154.9, 725×504) | ídem | 0 | suspended → running |
| 1024×768 | sí (279.9, 195, 464.2×322.8) | ídem | 0 | suspended → running |
| 768×1024 | sí (209.9, 370.3, 348.2×242) | ídem | 0 | suspended → running |

Capturas: `qa/centered-<ancho>x<alto>.png` (después de la interacción) y `qa/centered-<ancho>x<alto>-before-click.png` (con el aviso de audio).
