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
