import asyncio

import pytest

from casino.main import GameSelect, MenuSelect, NameSelect
from casino.textual_themes import CASINO_THEMES, DEFAULT_THEME, THEME_DESCRIPTIONS
from casino.theme_screen import ThemeScreen, set_current_theme


@pytest.fixture(autouse=True)
def reset_theme():
    set_current_theme(DEFAULT_THEME)
    yield
    set_current_theme(DEFAULT_THEME)


def run(coro):
    return asyncio.run(coro)


def test_apps_start_with_default_theme():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test():
            assert app.theme == DEFAULT_THEME

    run(scenario())


def test_every_described_theme_exists():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test():
            for name in THEME_DESCRIPTIONS:
                assert name in app.available_themes
            for theme in CASINO_THEMES:
                assert theme.name in THEME_DESCRIPTIONS

    run(scenario())


def test_binding_opens_picker_and_escape_returns_to_previous_screen():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test() as pilot:
            previous_screen = app.screen
            await pilot.press("ctrl+t")
            assert isinstance(app.screen, ThemeScreen)
            await pilot.press("escape")
            assert app.screen is previous_screen

    run(scenario())


def test_highlight_previews_and_escape_restores_original_theme():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test() as pilot:
            await pilot.press("ctrl+t")
            await pilot.press("down")
            assert app.theme != DEFAULT_THEME  # live preview
            await pilot.press("escape")
            assert app.theme == DEFAULT_THEME

    run(scenario())


def test_enter_applies_theme_and_it_carries_over_to_next_app():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test() as pilot:
            await pilot.press("ctrl+t", "down", "enter")
            chosen = app.theme
            assert chosen != DEFAULT_THEME
            assert not isinstance(app.screen, ThemeScreen)

        next_app = GameSelect(username="Tester")
        async with next_app.run_test():
            assert next_app.theme == chosen

    run(scenario())


def test_picker_shows_description_of_highlighted_theme():
    async def scenario():
        app = MenuSelect(username="Tester")
        async with app.run_test() as pilot:
            await pilot.press("ctrl+t", "down")
            description = str(app.screen.query_one("#theme-description").render())
            assert description == THEME_DESCRIPTIONS[app.theme]

    run(scenario())


def test_preview_buttons_do_not_trigger_app_buttons():
    async def scenario():
        app = GameSelect(username="Tester")
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("ctrl+t")
            await pilot.click("#preview-buttons Button")
            assert isinstance(app.screen, ThemeScreen)
            assert app.return_value is None  # GameSelect did not exit

    run(scenario())


def test_typing_name_still_works_with_theme_binding():
    async def scenario():
        app = NameSelect()
        async with app.run_test() as pilot:
            await pilot.press(*"Tet", "enter")
        assert app.return_value == "Tet"

    run(scenario())
