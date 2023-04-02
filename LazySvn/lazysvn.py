from textual.app import App, ComposeResult
from textual.widgets import Static, OptionList
import svn.local


class Status:
    def __init__(self, name, revision, type, type_raw_name):
        self.name = name
        self.revision = revision
        self.type = type
        self.type_raw_name = type_raw_name


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
        self.selected_file = None
        self.selected_commit = None
        self.selected_diff = None


    def load_status(self, local: svn.local.LocalClient):
        status_list = []
        for e in local.status():
            status_list.append(Status(e.name, e.revision, e.type, e.type_raw_name));
        return status_list


    def load_commits(self, local: svn.local.LocalClient):
        commit_list = []
        for log in local.log_default():
            commit_list.append(Commit(log.date, log.msg, log.revision, log.author, log.changelist))
        return commit_list


    def setup(self):
        self.local = svn.local.LocalClient("C:/projects/svn-checkouts/textual-test")
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


    def compose(self) -> ComposeResult:
        yield OptionList(classes="box", id="files")
        yield Static("diff-view", classes="box", id="diff-view")
        yield OptionList(classes="box", id="commit-log")


    def on_load(self):
        self.model = model


    def on_mount(self, event):
        for e in self.local.status():
            self.query_one("#files").add_option(e.name)

        for log in self.local.log_default():
            self.query_one("#commit-log").add_option(log.msg)

if __name__ == "__main__":
    app = SVNTui()
    app.run()

