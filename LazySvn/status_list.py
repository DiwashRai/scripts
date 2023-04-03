from textual.widget import Widget
from textual import events
from rich.text import Text, TextType
from rich.console import RenderableType
from textual.widgets import Static
from rich.table import Table
from rich.panel import Panel
from rich.box import SQUARE
from keymanager import KeyManager


class StatusList(Widget):
    key_manager = KeyManager()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._is_focused = True


    def toggle_focus(self):
        self._is_focused = not self._is_focused
        self.refresh()


    def render(self) -> RenderableType:
        table = Table("cursor", "path", "type", show_header=False, box=None)
        for i, e in enumerate(self.model.status_list):
            if i == self.model.selected_status and self._is_focused:
                table.add_row(">", e.name, e.type_raw_name, style="bold #f2f2f2")
            else:
                table.add_row(" ", e.name, e.type_raw_name, style="bold #666666")
        return Panel(
            table,
            box=SQUARE,
            expand=True,
            border_style="b #98BB6C" if self._is_focused else "d #e5e9f0",
        )


    def prev_grid(self):
        self.app.commit_grid.toggle_focus()
        self.app.status_grid.toggle_focus()


    def next_grid(self):
        self.app.commit_grid.toggle_focus()
        self.app.status_grid.toggle_focus()


    async def handle_key(self, event: events.Key) -> None:
        event.stop()
        key = event.key
        bind = self.key_manager.get_method(key)
        if bind:
            if hasattr(self, bind.func_name):
                func = getattr(self, bind.func_name)
                func(*bind.params)

