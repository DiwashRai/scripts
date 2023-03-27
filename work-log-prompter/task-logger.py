import time
import datetime
import os
import argparse
import tkinter as tk

WORKLOG_DIR = "C:\\Code\\GitHub"
WORKLOG_SECTION = "## WorkLog"

class InputWindow:
    """Creates a GUI window to input tasks"""

    def __init__(self, time, mode, log_file):
        """
        Args:
            time (str): The current time in the format "%H%M".
            mode (str): Mode of task logger. "office" outputs it to the daily worklog directory,
                "file" outputs it to a specified file.
            log_file (str): The path to the file to log to.
        """

        self.log_file = log_file
        self.time = time
        self.mode = mode

        self.root = tk.Tk()
        self.root.geometry("400x100")
        self.root.title(f"Task Logger - {self.time}")
        self.label = tk.Label(self.root, text="Current task: ")
        self.label.pack()
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack()
        self.root.bind("<Return>", lambda event=None: self.submit())


    def submit(self):
        """Saves the inputted task to the log file"""

        log_str = f"{self.time}: {self.entry.get()}"

        if (self.mode == "office"):
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            worklog_index = lines.index(WORKLOG_SECTION + "\n")
            for i in range(worklog_index + 1, len(lines)):
                if not lines[i].strip():
                    next_index = i
                    break

            lines.insert(next_index, f"{log_str}\n")
            with open(self.log_file, "w") as f:
                f.writelines(lines)

        else:
            with open(self.log_file, "a") as f:
                f.write(f"{log_str}\n")

        print(log_str)
        self.root.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices=["office", "file"], help="Mode of task logger. Office outputs it to my daily worklog directory", default="office")
    parser.add_argument("-f", "--file", help="File to log to", default="task-log.txt")
    args = parser.parse_args()
    now = datetime.datetime.now()
    date_str = now.strftime("%Y.%m.%d")
    office_log_pattern = f"daily.worklog.{date_str}.md"
    if args.mode == "office":
        args.file = os.path.join(WORKLOG_DIR, office_log_pattern)
        if not os.path.isfile(args.file):
            print("Mode selected is [office] but worklog does not exist, exiting")
            print(f"Expected path: {args.file}")
            exit(1)

    while True:
        now = datetime.datetime.now()
        if now.minute % 30 == 0:
            input_window = InputWindow(now.strftime("%H%M"), args.mode, args.file)
            input_window.root.mainloop()

        time.sleep(60)
