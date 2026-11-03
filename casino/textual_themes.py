"""Textual themes for Terminal Casino.

Each theme is a regular Textual `Theme`. Widgets pick up its colors through
the theme variables in their CSS ($primary, $accent, $success, $error, ...),
so registering a theme here is enough to recolor every screen.

To add a theme: append it to CASINO_THEMES and give it a description in
THEME_DESCRIPTIONS. It will show up in the theme picker automatically.
"""

from textual.theme import Theme

CASINO_FELT = Theme(
    name="casino-felt",
    primary="#D4AF37",     # gold trim
    secondary="#C0392B",   # card red
    accent="#F5D76E",
    foreground="#F4F1DE",
    background="#0B3D2E",  # table felt
    surface="#11513C",
    panel="#176B4F",
    success="#2ECC71",
    warning="#F39C12",
    error="#E74C3C",
    dark=True,
)

GATOR = Theme(
    name="gator",
    primary="#FA4616",     # UF orange
    secondary="#0021A5",   # UF blue
    accent="#FF8A3D",
    foreground="#FFFFFF",
    background="#00143D",
    surface="#002266",
    panel="#0A2F80",
    success="#3DDC84",
    warning="#FFC72C",
    error="#FF4D4D",
    dark=True,
)

NEON_VEGAS = Theme(
    name="neon-vegas",
    primary="#FF2A6D",     # hot pink sign
    secondary="#05D9E8",   # cyan tube light
    accent="#F9C80E",
    foreground="#F5F5FF",
    background="#0D0221",
    surface="#1A0B3D",
    panel="#2A1259",
    success="#39FF14",
    warning="#F9C80E",
    error="#FF3864",
    dark=True,
)

CASINO_THEMES: list[Theme] = [CASINO_FELT, GATOR, NEON_VEGAS]

DEFAULT_THEME = "casino-felt"

# Shown next to the preview in the theme picker. Only themes listed here
# appear in the picker, in this order.
THEME_DESCRIPTIONS: dict[str, str] = {
    "casino-felt": "Classic table: green felt, gold trim, and card-red accents.",
    "gator": "Go Gators! UF orange and blue on a deep navy background.",
    "neon-vegas": "Late night on the Strip: hot pink and cyan neon on near-black.",
    "textual-dark": "Textual's default dark theme. Neutral and easy on the eyes.",
    "textual-light": "Textual's default light theme for bright terminals.",
    "dracula": "The popular Dracula palette: purple, pink, and soft contrast.",
    "nord": "Cool arctic blues with low contrast for long sessions.",
    "gruvbox": "Warm retro browns and oranges.",
    "solarized-light": "Solarized's light variant: beige background, muted colors.",
}
