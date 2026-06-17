#!/usr/bin/env python3
"""
build-fragments.py
------------------
Generates one standalone HTML file per empty-state "fragment" from handoff.html.

handoff.html stays the single source of truth. Each generated file in fragments/
is a full copy that, on load, navigates straight to one specific state (view +
sub-tab + edge scenario) and hides the prototype chrome (tab bars, "Show review
notes" toggles, capacity-scenario toggles) so the export shows ONLY that fragment.

Run:  python3 build-fragments.py
Then open fragments/index.html (or any individual fragments/*.html).
"""

import os
import re

SRC = "handoff.html"
OUT_DIR = "fragments"

# (filename, page title, label for index, init JS that locks the state)
FRAGMENTS = [
    # Instances
    ("instances-current",                  "Instances — Current",                  "Instances · Current",                  "navigate('instances'); setInstancesTab('current');"),
    ("instances-redesign",                 "Instances — Redesign",                 "Instances · Redesign",                 "navigate('instances'); setInstancesTab('redesign');"),
    ("instances-edge-on-demand",           "Instances — On demand",                "Instances · Edge · On demand",         "navigate('instances'); setInstancesTab('edge'); toggleEdgeState(0);"),
    ("instances-edge-reservation",         "Instances — Reservation",              "Instances · Edge · Reservation",       "navigate('instances'); setInstancesTab('edge'); toggleEdgeState(1);"),
    ("instances-edge-reservation-ondemand","Instances — Reservation + on-demand",  "Instances · Edge · Reservation+on-demand","navigate('instances'); setInstancesTab('edge'); toggleEdgeState(2);"),
    ("instances-edge-no-payment",          "Instances — No payment method",        "Instances · Edge · No payment method", "navigate('instances'); setInstancesTab('edge'); toggleEdgeState(3);"),
    ("instances-edge-simple",              "Instances — Simple state",             "Instances · Edge · Simple state",      "navigate('instances'); setInstancesTab('edge'); toggleEdgeState(4);"),

    # Disks
    ("disks-current",                      "Disks — Current",                      "Disks · Current",                      "navigate('disks'); setDisksTab('current');"),
    ("disks-redesign",                     "Disks — Redesign",                     "Disks · Redesign",                     "navigate('disks'); setDisksTab('redesign');"),

    # Kubernetes (empty + edge cases)
    ("kubernetes",                         "Kubernetes — Empty",                   "Kubernetes · Empty",                   "navigate('kubernetes'); toggleClusterState('spicy');"),
    ("kubernetes-edge-provisioning",       "Kubernetes — Provisioning",            "Kubernetes · Edge · Provisioning",     "navigate('kubernetes'); toggleClusterState('edge'); toggleClusterEdgeState(0);"),
    ("kubernetes-edge-error",              "Kubernetes — Error",                   "Kubernetes · Edge · Error",            "navigate('kubernetes'); toggleClusterState('edge'); toggleClusterEdgeState(1);"),
    ("kubernetes-edge-limit-reached",      "Kubernetes — Limit reached",           "Kubernetes · Edge · Limit reached",    "navigate('kubernetes'); toggleClusterState('edge'); toggleClusterEdgeState(2);"),
    ("kubernetes-edge-upgrading",          "Kubernetes — Upgrading",               "Kubernetes · Edge · Upgrading",        "navigate('kubernetes'); toggleClusterState('edge'); toggleClusterEdgeState(3);"),
    ("kubernetes-edge-no-kubeconfig",      "Kubernetes — No kubeconfig",           "Kubernetes · Edge · No kubeconfig",    "navigate('kubernetes'); toggleClusterState('edge'); toggleClusterEdgeState(4);"),

    # Slurm
    ("slurm",                              "Slurm — Empty",                        "Slurm · Empty",                        "navigate('slurm'); toggleSlurmState('spicy');"),

    # Single-state pages
    ("buckets",                            "Buckets — Empty",                      "Buckets",                              "navigate('buckets');"),
    ("api-keys",                           "Cloud API Keys — Empty",               "Cloud API Keys",                       "navigate('cloud-api-keys');"),
    ("managed-logs",                       "Managed Logs — Empty",                 "Managed Logs",                         "navigate('managed-logs');"),
    ("ssh-keys",                           "SSH Keys — Empty",                     "SSH Keys",                             "navigate('ssh-keys');"),
    ("instance-templates",                 "Instance Templates — Empty",           "Instance Templates",                   "navigate('instance-templates');"),
    ("instance-groups",                    "Instance Groups — Empty",              "Instance Groups",                      "navigate('instance-groups');"),
    ("custom-images",                      "Custom Images — Empty",                "Custom Images",                        "navigate('custom-images');"),
]

# Card-based pages that have hover-revealed descriptions worth capturing as a
# separate "hover" frame for Figma. (Edge/hero-only states have no cards.)
HOVER_VARIANTS = {
    "instances-redesign",
    "instances-edge-on-demand",
    "instances-edge-reservation",
    "instances-edge-reservation-ondemand",
    "disks-redesign",
    "kubernetes",
    "slurm",
    "buckets",
    "managed-logs",
    "ssh-keys",
    "instance-templates",
    "instance-groups",
    "custom-images",
}

# Injected into <head> for the "-hover" build: forces every card's hover
# description to render inline (always visible) so an HTML->Figma import
# captures the hover state as a static frame.
EXPAND_CSS = """
<style id="fragment-hover-expand">
  .med-res-card{min-height:0!important;border-radius:10px!important}
  .med-res-card .med-res-expand{position:static!important;left:auto!important;right:auto!important;top:auto!important;
    display:block!important;opacity:1!important;pointer-events:auto!important;border:none!important;border-top:none!important;
    background:transparent!important;border-radius:0!important;box-shadow:none!important;padding:8px 2px 0!important}
  .med-res-card .np-hover-hint{display:none!important}
</style>
"""

INJECT_TEMPLATE = """
<!-- ===== FRAGMENT: {label} ===== -->
<script>
/* Auto-generated by build-fragments.py — locks this file to a single empty-state fragment.
   Source of truth is handoff.html; do not hand-edit fragments/*.html. */
(function(){{
  function applyFragment(){{
    try {{
      {init_js}
    }} catch (e) {{ console.warn('fragment init failed', e); }}
    // Hide prototype chrome so only the fragment shows
    ['inst-tabs','disks-tabs','rev-toggle','disks-rev-toggle','k8s-subtabs','slurm-subtabs','disks-subtabs']
      .forEach(function(id){{ var e = document.getElementById(id); if (e) e.style.display = 'none'; }});
    document.querySelectorAll('.state-toggle').forEach(function(t){{
      var row = t.parentElement; if (row) row.style.display = 'none'; // hide the label + toggle row
    }});
  }}
  if (document.readyState === 'complete') setTimeout(applyFragment, 120);
  else window.addEventListener('load', function(){{ setTimeout(applyFragment, 120); }});
  setTimeout(applyFragment, 500); // re-assert after animation re-inits
}})();
</script>
"""


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        html = f.read()

    os.makedirs(OUT_DIR, exist_ok=True)

    outputs = []  # (filename, label) for the index, in generation order

    def write_fragment(filename, title, label, init_js, hover=False):
        doc = html

        # Set a clear <title> so the browser tab / export names the fragment
        if re.search(r"<title>.*?</title>", doc, flags=re.S):
            doc = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", doc, count=1, flags=re.S)
        else:
            doc = doc.replace("</head>", f"  <title>{title}</title>\n</head>", 1)

        # Hover build: force card descriptions to render inline (always visible)
        if hover:
            doc = doc.replace("</head>", EXPAND_CSS + "</head>", 1)

        inject = INJECT_TEMPLATE.format(label=label, init_js=init_js)
        if "</body>" in doc:
            doc = doc.replace("</body>", inject + "\n</body>", 1)
        else:
            doc += inject

        out_path = os.path.join(OUT_DIR, filename + ".html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(doc)
        outputs.append((filename, label))
        print(f"  wrote {out_path}")

    for filename, title, label, init_js in FRAGMENTS:
        # Default frame
        write_fragment(filename, title, label, init_js, hover=False)
        # Hover frame (only for card-based pages)
        if filename in HOVER_VARIANTS:
            write_fragment(
                filename + "-hover",
                title + " (hover)",
                label + " · hover",
                init_js,
                hover=True,
            )

    # Build an index page for convenient handoff browsing
    links = "\n".join(
        f'    <li><a href="{fn}.html">{label}</a> <span class="f">{fn}.html</span></li>'
        for fn, label in outputs
    )
    index = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Empty States — Fragments</title>
<style>
  body{{font-family:-apple-system,Segoe UI,sans-serif;max-width:760px;margin:48px auto;padding:0 24px;color:#111}}
  h1{{font-weight:600}}
  p{{color:#666}}
  ul{{list-style:none;padding:0}}
  li{{padding:10px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:baseline;gap:16px}}
  a{{font-size:15px;color:#111;text-decoration:none;font-weight:500}}
  a:hover{{text-decoration:underline}}
  .f{{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#999}}
</style></head>
<body>
  <h1>Crusoe Cloud — Empty State Fragments</h1>
  <p>Each link is a standalone HTML file locked to one specific state. Generated from
  <code>handoff.html</code> by <code>build-fragments.py</code> — do not hand-edit the files in this folder.</p>
  <ul>
{links}
  </ul>
</body></html>
"""
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as out:
        out.write(index)
    print(f"  wrote {OUT_DIR}/index.html")
    print(f"\nDone — {len(FRAGMENTS)} fragments generated in {OUT_DIR}/")


if __name__ == "__main__":
    main()
