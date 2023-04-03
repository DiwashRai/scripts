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
            style = "bold #f2f2f2"
            if e.type_raw_name == "modified":
                if e.selected_for_commit:
                    style = "bold #98BB6C"
                else:
                    style = "bold #E82424"
            elif e.type_raw_name == "unversioned":
                style = "bold #b3b3b3"

            cursor = " "
            if i == self.model.selected_status and self._is_focused:
                cursor = "[bold white]>"
                style += " on #333333"
            table.add_row(
                cursor,
                e.name,
                e.type_raw_name,
                style=style)

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


    def next_item(self):
        if self.model.selected_status < len(self.model.status_list) - 1:
            self.model.selected_status += 1
        else:
            self.model.selected_status = 0
        self.refresh()


    def prev_item(self):
        if self.model.selected_status > 0:
            self.model.selected_status -= 1
        else:
            self.model.selected_status = len(self.model.status_list) - 1
        self.refresh()


    def toggle_selected_for_commit(self):
        idx = self.model.selected_status
        if not self.model.status_list[idx].type_raw_name == "modified":
            return
        self.model.status_list[idx].selected_for_commit = not self.model.status_list[idx].selected_for_commit
        self.refresh()


    async def handle_key(self, event: events.Key) -> None:
        event.stop()
        key = event.key
        bind = self.key_manager.get_method(key)
        if bind:
            if hasattr(self, bind.func_name):
                func = getattr(self, bind.func_name)
                func(*bind.params)

