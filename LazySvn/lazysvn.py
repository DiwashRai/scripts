from textual.app import App, ComposeResult
from textual import events
from textual.screen import ModalScreen
from textual.widgets import Input
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
    def __init__(self, date, msg, revision, author, changelist, full_msg):
        self.date = date
        self.msg = msg
        self.revision = revision
        self.author = author
        self.changelist = changelist
        self.full_msg = full_msg
        self.rich_output = Text("")
        self.diff_loaded = False


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
        self.selected_status = 0
        self.selected_commit = 0
        self.status_list = self.load_status(self.local)
        self.commit_list = self.load_commits(self.local)
        if (len(self.output) == 0 and len(self.status_list) > 0):
            self.output = self.status_list[0].diff


    def commit(self, commit_msg):
        if len(commit_msg) == 0:
            return "Commit message cannot be empty"
        to_commit = []
        for status in self.status_list:
            if status.selected_for_commit:
                to_commit.append(status.name)

        if len(to_commit) == 0:
            return "No files selected for commit"

        commit_lines = self.my_commit(message=commit_msg, rel_filepaths=to_commit)
        out_str = ""
        for line in commit_lines:
            out_str += line + "\n"
        return out_str


    def svn_update(self):
        self.local.update()
        self.setup()


    def load_status(self, local: svn.local.LocalClient):
        status_list = []
        for e in local.status():
            if e.type_raw_name == "unversioned":
                continue
            relative_path = e.name[len(local.path):].removeprefix("\\")
            path_key = local.path.replace("\\", "/") + '/' + relative_path
            diff = self.diff_path(path_key)
            status_list.append(Status(relative_path, path_key, e.revision, e.type, e.type_raw_name, self.diff_to_rich_text(diff)))
        return status_list


    def diff_to_rich_text(self, diff):
        text = Text()
        for line in diff:
            if line.startswith("+"):
                text.append(line + "\n", style="green")
            elif line.startswith("-"):
                text.append(line + "\n", style="#E82424")
            elif line.startswith("@"):
                text.append(line + "\n", style="#7FB4CA")
            else:
                text.append(line + "\n")
        return text


    def load_commits(self, local: svn.local.LocalClient):
        commit_list = []
        for log in local.log_default(limit=100, changelist=True):
            short_msg = log.msg.splitlines()[0]
            commit = Commit(log.date, short_msg, log.revision, log.author, log.changelist, log.msg)
            self.create_commit_rich_text(commit)
            commit_list.append(commit)
        return commit_list


    def create_commit_rich_text(self, commit: Commit):
        text = Text()
        text.append(f"Revision: {commit.revision}\n", style="#E6C384")
        text.append(f"Author: {commit.author}\n", style="#957FB8")
        text.append(f"Date: {commit.date}\n\n")
        text.append("Message:\n", style="bold")
        text.append(commit.full_msg + "\n\n")
        text.append("Changelist:\n", style="bold")
        for cl in commit.changelist:
            if cl[0] == "A":
                text.append(f"  {cl[1]}  {cl[0]}\n", style="green")
            elif cl[0] == "D":
                text.append(f"  {cl[1]}  {cl[0]}\n", style="#E82424")
            elif cl[0] == "M":
                text.append(f"  {cl[1]}  {cl[0]}\n", style="#e98a00")
            else:
                text.append(f"  {cl[1]}  {cl[0]}\n")
        commit.rich_output = text


    def diff_path(self, path):
        arguments = [
            '--old', f"{path}@BASE",
            '--new', path,
        ]
        return self.local.run_command("diff", arguments)


    def diff_revision(self, revision):
        arguments = [
            '--old', f"{self.local.path}@{revision - 1}",
            '--new', f"{self.local.path}@{revision}",
        ]
        return self.local.run_command("diff", arguments)


    def diff_obj_to_string(self, diff):
        diff_str = ""
        for line in diff:
            diff_str += line

        return diff_str


    def load_diff_for_commit(self):
        commit = self.commit_list[self.selected_commit]
        if commit.diff_loaded:
            return
        commit.rich_output.append(Text("\nDiff:\n", style="bold"))
        diff = self.diff_revision(commit.revision)
        rich_diff = self.diff_to_rich_text(diff)
        commit.rich_output.append("\n")
        commit.rich_output.append(rich_diff)
        commit.diff_loaded = True


    def my_commit(self, message, rel_filepaths=[]):
        args = ['-m', message] + rel_filepaths

        return self.local.run_command(
            'commit',
            args,
            wd=self.local.path)


model = Model()
model.setup()

class CommitScreen(ModalScreen):
    def __init__(self, model: Model, output_box: OuputBox):
        super().__init__()
        self.model = model
        self.output_box = output_box
        self.input_msg = Input()
        self.input_msg.focus()

    def compose(self) -> ComposeResult:
        yield self.input_msg


    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == 'escape':
            self.app.pop_screen()
        if event.key == 'backspace':
            self.input_msg.action_delete_left()
        if event.key == 'enter':
            commit_res = self.model.commit(self.input_msg.value)
            if (commit_res == "" or commit_res == None):
                commit_res = "Commit successful"
            self.model.output = Text(commit_res)
            self.app.pop_screen()
            self.model.svn_update()
            self.app.refresh_widgets()


class SVNTui(App):
    CSS_PATH = "lazysvn.css"

    def __init__ (self):
        super().__init__()
        self.model = model
        self.output_box = OuputBox(model)
        self.status_grid = StatusList(model, self.output_box)
        self.commit_grid = CommitList(model, self.output_box)


    def compose(self) -> ComposeResult:
        yield self.status_grid
        yield self.output_box
        yield self.commit_grid


    def toggle_focus(self):
        self.status_grid.toggle_focus()
        self.commit_grid.toggle_focus()


    def refresh_widgets(self):
        self.status_grid.refresh()
        self.commit_grid.refresh()
        self.output_box.refresh()


    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.exit()
        elif event.key == "r":
            self.model.setup()
            self.refresh_widgets()
        elif event.key == "u":
            self.model.svn_update()
            self.model.setup()
            self.refresh_widgets()
        elif event.key == "c":
            self.push_screen(CommitScreen(self.model, self.output_box))
        elif event.key == "d" and self.commit_grid._is_focused:
            self.model.load_diff_for_commit()
            self.refresh_widgets()
        elif self.status_grid._is_focused:
            await self.status_grid.handle_key(event)
        elif self.commit_grid._is_focused:
            await self.commit_grid.handle_key(event)


if __name__ == "__main__":
    app = SVNTui()
    app.run()
