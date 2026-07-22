# Crusoe Cloud — Empty States Prototype

Interactive HTML prototype of the redesigned empty states for the Crusoe Cloud console: hero illustration + headline + CTA + docs link per surface, with animated line-art illustrations, edge-case states, and light/dark themes.

## Live links (GitHub Pages)

| What | URL |
|---|---|
| **Full console prototype** | https://arama222.github.io/crusoe-empty-states/handoff.html |
| **Animations gallery** (just the 6 animated illustrations, side by side) | https://arama222.github.io/crusoe-empty-states/animations.html |
| Per-state exports index | https://arama222.github.io/crusoe-empty-states/fragments/index.html |

## Repo map

```
handoff.html        ← THE prototype. Single self-contained file (source of truth):
                       all markup, CSS, JS. No build step, no dependencies.
index.html          ← identical copy of handoff.html (serves the Pages root URL)
animations.html     ← standalone gallery of the 6 Phase 2 illustration animations,
                       extracted from handoff.html (self-contained, dark-mode aware)
fragments/          ← one standalone HTML file per individual empty state
                       (for viewing/sharing a single state in isolation)
build-fragments.py  ← regenerates fragments/ from handoff.html
animations/         ← Phase 1 illustrations as standalone SVG files
```

## How the prototype works

- Everything is in `handoff.html`. Each page is a `<div class="view" id="view-…">` inside `.main`; `navigate(id)` (see the `ROUTES` map) toggles the active view and rebuilds the sidebar (`SIDEBARS`, `mainNav()`, `settingsNav()`).
- **Pages covered** — Phase 1: Instances (+ edge cases), Instance Templates, Instance Groups, Custom Images, Kubernetes (+ edge cases), Slurm, Disks, Buckets, Managed Logs, SSH Keys, Cloud API Keys, Infra Overview. Phase 2: VPC Networks, VPC Subnets, Load Balancers, User Access, MFA, Reservations, Billing, Audit Logs, All Notifications (+ bell dropdown), Container Registry.
- **Dark mode**: toggle sets `data-theme="dark"` on `<html>`; all colors are CSS variables.

## The illustration animations

All animation CSS lives in **one labeled block** in `handoff.html` — search for
`PHASE 2 EMPTY-STATE ILLUSTRATION ANIMATIONS`:
https://github.com/arama222/crusoe-empty-states/blob/main/handoff.html#L778

Implementation is plain CSS keyframes on inline SVGs (plus one SMIL gradient animation), no JS libraries:

| Surface | Illustration | Motion |
|---|---|---|
| Networking (VPC / Subnets / Load Balancers) | node mesh | dashed spokes march (`p2-dash`); nodes fill in clockwise (`p2-node-fill`); center dot blinks every other node fill (`p2-blink`) |
| User Access / MFA | woven diamond | dark band sweeps left→right via an animated `<linearGradient>` (SMIL `animateTransform`, restarted on page open in `showView()`); dashed ellipse marches |
| Billing / Reservations | circle flower | whole glyph slow-spins (`p2-spin` reversed); dashed circles' dashes march |
| Audit Logs | starburst | middle lines static; outer-ray group rotates (`p2-spin`) with a staggered opacity wave (`p2-ray`) |
| All Notifications | log-line checklist | bottom line fades out, stack steps down, new line fades in at top (`p2-log-step/-out/-in`, starts mid-cycle); dashes march |
| Container Registry | stacked discs | discs bob in a staggered wave (`p2-disc-bob`); dashed top ellipse marches |

Sizing: illustrations render 178–186 px wide (dense shapes slightly smaller, airy shapes slightly larger, optically matched to Phase 1's 160 px-tall heroes), uniform 24 px gap to the 44 px title.

Theming: "hollow" fills use `var(--glyph-bg)` and the sweep uses `var(--sweep-pale/--sweep-ink)`, with `[data-theme="dark"]` overrides — so every animation renders correctly in dark mode.

## Run locally

```bash
python3 -m http.server 8090     # from the repo root
# open http://localhost:8090/handoff.html
```

(Any static server works; opening the file directly also works.)

## Editing workflow

1. Edit `handoff.html` only.
2. `cp handoff.html index.html`
3. Optionally `python3 build-fragments.py` to refresh fragments/.
4. Commit and push to `main` — GitHub Pages deploys automatically (~1 min, cached up to 10 min).
