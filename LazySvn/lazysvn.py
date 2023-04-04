from textual.app import App, ComposeResult
from textual.widgets import Static, OptionList
from textual import events
import svn.local
from status_list import StatusList
from commit_list import CommitList

class Status:
    def __init__(self, name, revision, type, type_raw_name):
        self.name = name
        self.revision = revision
        self.type = type
        self.type_raw_name = type_raw_name
        self.selected_for_commit = False


class Commit:
    def __init__(self, date, msg, revision, author, changelist):
        self.date = date
        self.msg = msg
        self.revision = revision
        self.author = author
        self.changelist = changelist


class Model():
    """
    Model that holds the state of the application.
    """
    def __init__(self):
        self.selected_status = 0
        self.selected_commit = 0

        self.local = None
        self.status_list = []
        self.commit_list = []


    def load_status(self, local: svn.local.LocalClient):
        status_list = []
        for e in local.status():
            relative_path = e.name[len(local.path):].removeprefix("\\")
            status_list.append(Status(relative_path, e.revision, e.type, e.type_raw_name));
        return status_list


    def load_commits(self, local: svn.local.LocalClient):
        commit_list = []
        for log in local.log_default(limit=100):
            commit_list.append(Commit(log.date, log.msg, log.revision, log.author, log.changelist))
        return commit_list


    def setup(self):
        self.local = svn.local.LocalClient("C:\\projects\\svn-checkouts\\textual-test")
        self.status_list = self.load_status(self.local)
        self.commit_list = self.load_commits(self.local)


model = Model()
model.setup()


class CommitLog(OptionList):
    def on_select(self, option: str) -> None:
        self.app.model.selected_commit = option
        self.app.model.selected_diff = self.app.local.diff_default(option)
        self.app.refresh()


class SVNTui(App):
    CSS_PATH = "lazysvn.css"

    def __init__ (self):
        super().__init__()
        self.status_grid = StatusList(model)
        self.commit_grid = CommitList(model)


    def on_load(self):
        self.model = model


    def compose(self) -> ComposeResult:
        yield self.status_grid
        yield Static("diff-view", classes="box", id="diff-view")
        yield self.commit_grid


    def on_load(self):
        self.model = model


    def toggle_focus(self):
        self.status_grid.toggle_focus()
        self.commit_grid.toggle_focus()


    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            await self.exit()
        elif self.status_grid._is_focused:
            await self.status_grid.handle_key(event)
        elif self.commit_grid._is_focused:
            await self.commit_grid.handle_key(event)


if __name__ == "__main__":
    app = SVNTui()
    app.run()

