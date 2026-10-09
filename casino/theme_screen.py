"""Theme picker screen and the base App that every Terminal Casino app uses.

The casino runs several small Textual apps one after another (name entry,
menu, game select), so the chosen theme is kept in this module and applied
by each app when it starts.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.theme import Theme
from textual.widgets import Button, Label, OptionList, Static
from textual.widgets.option_list import Option

from .textual_themes import CASINO_THEMES, DEFAULT_THEME, THEME_DESCRIPTIONS

# Theme chosen by the user, shared by every app for the rest of the session.
_current_theme = DEFAULT_THEME


def get_current_theme() -> str:
    return _current_theme


def set_current_theme(name: str) -> None:
    global _current_theme
    _current_theme = name


PREVIEW_CARD = """\
┌─────────┐
|A        |
|         |
|    ♠    |
|         |
|        A|
└─────────┘"""


class ThemedApp(App):
    """Base app: registers the casino themes and adds a Themes footer binding."""

    BINDINGS = [Binding("ctrl+t", "open_themes", "Themes")]

    def __init__(self) -> None:
        super().__init__()
        for theme in CASINO_THEMES:
            self.register_theme(theme)
        self.theme = get_current_theme()

    def on_mount(self) -> None:
        # Remember the theme however it was changed (picker or command palette)
        self.theme_changed_signal.subscribe(self, self._remember_theme)

    def _remember_theme(self, theme: Theme) -> None:
        set_current_theme(theme.name)

    def action_open_themes(self) -> None:
        if not isinstance(self.screen, ThemeScreen):
            self.push_screen(ThemeScreen())


class ThemeScreen(ModalScreen[str | None]):
    """Popup for browsing themes with a live preview.

    Highlighting a theme applies it right away so the whole app (and the
    preview pane) shows what it looks like. Enter keeps it, Escape restores
    the theme the user had before opening the popup.
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ThemeScreen {
        align: center middle;
    }
    #theme-dialog {
        width: 90;
        height: auto;
        max-height: 90%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #theme-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    #theme-body {
        height: auto;
    }
    #theme-list {
        width: 28;
        height: 18;
    }
    #theme-preview {
        width: 1fr;
        height: auto;
        border: round $secondary;
        background: $background;
        padding: 0 1;
        margin-left: 1;
    }
    #preview-header {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $primary;
    }
    #preview-table {
        height: auto;
    }
    #preview-card {
        width: auto;
        color: $foreground;
    }
    #preview-stats {
        height: auto;
        padding-left: 2;
    }
    #preview-balance {
        color: $success;
        text-style: bold;
    }
    #preview-bet {
        color: $accent;
    }
    #preview-loss {
        color: $error;
    }
    #preview-buttons {
        height: auto;
    }
    #preview-buttons Button {
        margin-right: 1;
    }
    #theme-description {
        margin-top: 1;
        color: $text-muted;
    }
    #theme-hint {
        width: 100%;
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._original_theme = ""

    def compose(self) -> ComposeResult:
        names = [n for n in THEME_DESCRIPTIONS if n in self.app.available_themes]
        with Vertical(id="theme-dialog"):
            yield Label("Choose a Theme", id="theme-title")
            with Horizontal(id="theme-body"):
                yield OptionList(
                    *[Option(name.replace("-", " ").title(), id=name) for name in names],
                    id="theme-list",
                )
                with Vertical(id="theme-preview"):
                    yield Static("♦ T E R M I N A L  C A S I N O ♦", id="preview-header")
                    with Horizontal(id="preview-table"):
                        yield Static(PREVIEW_CARD, id="preview-card")
                        with Vertical(id="preview-stats"):
                            yield Label("Balance: $100", id="preview-balance")
                            yield Label("Bet: $10", id="preview-bet")
                            yield Label("Dealer wins! -$10", id="preview-loss")
                    with Horizontal(id="preview-buttons"):
                        yield Button("Hit", variant="primary")
                        yield Button("Stand")
                        yield Button("Fold", variant="error")
                    yield Static("", id="theme-description")
            yield Label("↑/↓ preview   Enter apply   Esc cancel", id="theme-hint")

    def on_mount(self) -> None:
        self._original_theme = self.app.theme
        theme_list = self.query_one("#theme-list", OptionList)
        try:
            theme_list.highlighted = theme_list.get_option_index(self.app.theme)
        except KeyError:
            # Current theme isn't in the picker (e.g. set from the command palette)
            theme_list.highlighted = 0
        theme_list.focus()
        self._show_description(self.app.theme)

    def _show_description(self, name: str) -> None:
        description = THEME_DESCRIPTIONS.get(name, "")
        self.query_one("#theme-description", Static).update(description)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        name = event.option.id
        if name is not None:
            self.app.theme = name
            self._show_description(name)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.app.theme = event.option.id
        self.dismiss(event.option.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Preview buttons are just for show; don't let the press reach the app
        event.stop()

    def action_cancel(self) -> None:
        self.app.theme = self._original_theme
        self.dismiss(None)
