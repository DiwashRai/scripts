from textual.widget import Widget
from textual import events
from rich.console import RenderableType
from rich.table import Table, Column
from rich.panel import Panel
from rich.box import SQUARE
from keymanager import KeyManager


class CommitList(Widget):
    key_manager = KeyManager()


    def __init__(self, model, output_box):
        super().__init__(id="commit-box")
        self.model = model
        self.output_box = output_box
        self._is_focused = False
        self.lower_bound = 0
        self.upper_bound = 0


    def toggle_focus(self):
        self._is_focused = not self._is_focused
        if (self._is_focused):
            self.model.output = self.model.commit_list[self.model.selected_commit].rich_output
            self.output_box.refresh()
        self.refresh()


    def render(self) -> RenderableType:
        self.upper_bound = self.lower_bound + self._size.height - 2
        table = Table(
            Column(header="cursor", min_width=1, no_wrap=True),
            Column(header="revision", min_width=10, no_wrap=True, justify="right"),
            Column(header="author", min_width=9, no_wrap=True),
            Column(header="date", min_width=14, no_wrap=True),
            Column(header="message", width=80, no_wrap=True),
            show_header=False,
            box=None,
            min_width=150,
            padding=[0, 1, 0, 0],
            )
        for i, e in enumerate(self.model.commit_list[self.lower_bound:self.upper_bound], self.lower_bound):
            cursor = " "
            row_style = None
            if i == self.model.selected_commit and self._is_focused:
                cursor = ">"
                row_style = "on #333333"
            table.add_row(
                cursor,
                f"[bold #FF9E3B]{str(e.revision)}",
                f"[bold #7E9CD8]{e.author}" if self._size.width > 12 else None,
                f"[bold #957FB8]{e.date.strftime('%d/%m/%y %H:%M')}" if self._size.width > 30 else None,
                e.msg if self._size.width > 41 else None,
                style=row_style
                )

        return Panel(
            table,
            box=SQUARE,
            expand=True,
            border_style="b #98BB6C" if self._is_focused else "d #e5e9f0",
            title="Commits",
            title_align="left",
        )


    def next_item(self):
        if (len(self.model.commit_list) == 0):
            return
        if self.model.selected_commit < len(self.model.commit_list) - 1:
            self.model.selected_commit += 1
        if self.model.selected_commit >= self.upper_bound:
            self.lower_bound += 1
        self.model.output = self.model.commit_list[self.model.selected_commit].rich_output
        self.refresh()
        self.output_box.refresh()


    def prev_item(self):
        if (len(self.model.commit_list) == 0):
            return
        if self.model.selected_commit > 0:
            self.model.selected_commit -= 1
        if self.model.selected_commit < self.lower_bound:
            self.lower_bound -= 1
        self.model.output = self.model.commit_list[self.model.selected_commit].rich_output
        self.refresh()
        self.output_box.refresh()


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

