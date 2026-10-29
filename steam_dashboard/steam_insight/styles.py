"""Scoped tooltip and attainment styles for the existing dashboard."""

TOOLTIP_STYLE = """
<style>
[data-testid="stTooltipContent"] {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #D6DFEA !important;
}
[data-testid="stTooltipContent"] * {
    color: #1F2937 !important;
}
</style>
"""

ATTAINMENT_STYLE = """<style>
    .steam-attainment { display:grid; row-gap:12px; width:100%; }
    .steam-attainment-row {
        display:grid; grid-template-columns:minmax(110px,1.25fr) minmax(0,4fr);
        column-gap:16px; align-items:center; min-height:42px;
    }
    .steam-attainment-label {
        display:flex; justify-content:flex-end; align-items:center;
        gap:6px; min-width:0; font-size:12px; line-height:1.25; white-space:nowrap;
    }
    .steam-attainment-help { position:relative; display:inline-flex; align-items:center; }
    .steam-attainment-help button {
        display:inline-flex; align-items:center; justify-content:center;
        width:15px; height:15px; padding:0; border:1px solid currentColor;
        border-radius:50%; background:transparent; color:inherit;
        font-family:inherit; font-size:11px; line-height:1; cursor:help;
    }
    .steam-attainment-tooltip {
        position:absolute; bottom:calc(100% + 8px); left:0; z-index:1000;
        width:max-content; max-width:260px; padding:9px 12px;
        background:#FFFFFF; color:#1F2937; border:1px solid #D6DFEA;
        border-radius:8px; box-shadow:0 4px 16px #00000020;
        font-size:13px; line-height:1.5; white-space:normal;
        visibility:hidden; opacity:0; pointer-events:none;
    }
    .steam-attainment-help:hover .steam-attainment-tooltip,
    .steam-attainment-help:focus-within .steam-attainment-tooltip {
        visibility:visible; opacity:1;
    }
    .steam-attainment-bar {
        position:relative; height:30px; min-width:0; overflow:hidden;
        border-radius:5px; background:#1C2D43;
    }
    .steam-attainment-fill { position:absolute; inset:0 auto 0 0; opacity:.75; }
    .steam-attainment-values {
        position:relative; display:flex; justify-content:space-between; align-items:center;
        gap:12px; height:100%; padding:0 9px; color:#F4F8FC;
        font-size:12px; line-height:1.25; white-space:nowrap;
    }
    .steam-attainment-observed { min-width:0; overflow:hidden; text-overflow:ellipsis; }
    .steam-attainment-threshold { flex-shrink:0; }
    </style>"""
