from textual.widget import Widget
from rich.text import Text
from rich.console import RenderableType
from rich.panel import Panel
from rich.box import SQUARE


class OuputBox(Widget):
    def __init__ (self, model):
        super().__init__(id="output-box")
        self.model = model


    def render(self) -> RenderableType:
        return Panel(
            self.model.output,
            box=SQUARE,
            expand=True,
            border_style="d #e5e9f0",
        )

