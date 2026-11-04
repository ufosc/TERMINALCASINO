from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label, Select
from textual.containers import Horizontal

from . import utils


class Settings(App):
    CSS = """
    #title {
        text-align: center;
        width: 100%;
        color: gold;
        text-style: bold;
        margin-top: 2;
    }
    #subtitle {
        text-align: center;
        width: 100%;
        color: cyan;
        text-style: bold;
    }
    #color-select {
        margin: 1 2;
    }
    Horizontal {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        self.title = "Terminal Casino"
        yield Header()
        yield Footer()
        yield Label("Settings", id="title")
        yield Label("Choose your game text color", id="subtitle")

        # each option contains a display name and a value
        options = [("Terminal Default", "default")]
        current_theme = "default"

        # get the available colors from both theme folders
        for folder in ("ansi", "custom"):
            theme_files = sorted((utils.THEME_DIR / folder).glob("*.json"))

            for theme_file in theme_files:
                name = theme_file.stem
                value = f"{folder}/{name}"
                options.append((f"{folder.title()}: {name}", value))

                # select the theme that is currently being used
                if utils.load_theme(folder, name) == utils.theme:
                    current_theme = value

        yield Select(
            options,
            value=current_theme,
            allow_blank=False,
            id="color-select",
        )

        with Horizontal():
            yield Button("Apply", id="apply")
            yield Button("Back", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply":
            selected = self.query_one("#color-select", Select).value

            if selected == "default":
                utils.reset_theme()
            else:
                # separate the folder and filename to load the theme
                folder, name = str(selected).split("/", 1)
                utils.set_theme(folder, name)

            self.notify("Game text color updated for this session.")

        elif event.button.id == "back":
            # return to the main menu
            self.exit()