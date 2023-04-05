from textual.app import App, ComposeResult
from textual import events
import svn.local
from status_list import StatusList
from commit_list import CommitList
from output_box import OuputBox
from rich.text import Text

class Status:
    def __init__(self, name, path_key, revision, type, type_raw_name, diff):
        self.name = name
        self.path_key = path_key
        self.revision = revision
        self.type = type
        self.type_raw_name = type_raw_name
        self.selected_for_commit = False
        self.diff = diff


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

        self.output = Text("")


    def setup(self):
        self.local = svn.local.LocalClient("C:\\projects\\svn-checkouts\\textual-test")
        self.local.update()
        self.status_list = self.load_status(self.local)
        self.commit_list = self.load_commits(self.local)


    def commit(self):
        to_commit = []
        for status in self.status_list:
            if status.selected_for_commit:
                to_commit.append(status.name)

        self.local.commit(message="test commit", rel_filepaths=to_commit)



    def load_status(self, local: svn.local.LocalClient):
        status_list = []
        for e in local.status():
            if e.type_raw_name == "unversioned":
                continue
            relative_path = e.name[len(local.path):].removeprefix("\\")
            path_key = local.path.replace("\\", "/") + '/' + relative_path
            diff = self.diff_path(path_key)
            status_list.append(Status(relative_path, path_key, e.revision, e.type, e.type_raw_name, self.diff_to_rich_text(diff)));
        return status_list


    def diff_to_rich_text(self, diff):
        text = Text()
        for line in diff:
            if line.startswith("+"):
                text.append(line + "\n", style="green")
            elif line.startswith("-"):
                text.append(line + "\n", style="red")
            else:
                text.append(line + "\n")
        return text


    def load_commits(self, local: svn.local.LocalClient):
        commit_list = []
        for log in local.log_default(limit=100):
            commit = Commit(log.date, log.msg, log.revision, log.author, log.changelist)
            commit.msg = commit.msg.splitlines()[0][:80]
            commit_list.append(commit)
        return commit_list


    def diff_path(self, path):
        arguments = [
            '--old', '{0}@{1}'.format(path, "HEAD"),
            '--new', path,
        ]
        return self.local.run_command("diff", arguments)


model = Model()
model.setup()


class SVNTui(App):
    CSS_PATH = "lazysvn.css"

    def __init__ (self):
        super().__init__()
        self.model = model
        self.output_box = OuputBox(model)
        self.status_grid = StatusList(model, self.output_box)
        self.commit_grid = CommitList(model)


    def compose(self) -> ComposeResult:
        yield self.status_grid
        yield self.output_box
        yield self.commit_grid


    def toggle_focus(self):
        self.status_grid.toggle_focus()
        self.commit_grid.toggle_focus()


    def commit(self):
        self.model.commit()


    def refresh_widgets(self):
        self.status_grid.refresh()
        self.commit_grid.refresh()
        self.output_box.refresh()


    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            await self.exit()
        if event.key == "r":
            self.model.setup()
            self.refresh_widgets()
        if event.key == "c":
            self.commit()
            self.model.setup()
            self.refresh_widgets()
        elif self.status_grid._is_focused:
            await self.status_grid.handle_key(event)
        elif self.commit_grid._is_focused:
            await self.commit_grid.handle_key(event)


if __name__ == "__main__":
    app = SVNTui()
    app.run()

