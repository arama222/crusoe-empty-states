Crusoe Empty State — Illustration Assets
========================================

These are standalone SVG files for the empty-state illustrations.
Open any .svg in a web browser to see it (animated ones will play automatically).
They scale cleanly and have transparent backgrounds; stroke color is #111.

Files
-----
instances-cube.svg   ANIMATED — marching dashed lines (used on Instances,
                     Instance Templates, Instance Groups, Custom Images)
api-keys.svg         ANIMATED — two counter-rotating rings (Cloud API Keys, SSH Keys)
disks.svg            ANIMATED — oscillating concentric rings (Disks, Buckets)
orchestration.svg    ANIMATED — nested squares draw in sequentially + node ripples (Kubernetes, Slurm)
managed-logs.svg     ANIMATED — box, diamond & waveform draw in sequentially (Managed Logs, Infra Overview)

Notes
-----
- Animation is pure CSS embedded inside each SVG (no JS) — works in any modern
  browser and in tools that render SVG CSS (e.g. web embeds).
- Figma/Illustrator import the SHAPES but will NOT play the CSS animation —
  they'll show the first static frame. For motion in a deck or doc, embed the
  SVG in a web view or record a short screen capture of the live prototype:
  https://arama222.github.io/crusoe-empty-states/handoff.html
- Recolor: change the stroke="#111" values (and fill on the dots) to retheme.
