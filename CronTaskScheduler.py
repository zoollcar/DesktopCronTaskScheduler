import os
import json
import subprocess
import threading
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from croniter import croniter
from datetime import datetime
import time

CONFIG_FILE = "tasks.json"

class CronTaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Cron Task Scheduler")
        self.tasks = []

        self.task_frame = Frame(self.root)
        self.task_frame.pack(fill=BOTH, expand=True)

        self.add_task_button = Button(self.root, text="Add Task", command=self.add_task_ui)
        self.add_task_button.pack(pady=5)

        self.save_button = Button(self.root, text="Save Tasks", command=self.save_tasks)
        self.save_button.pack(pady=5)

        self.load_tasks()
        threading.Thread(target=self.task_runner, daemon=True).start()

    def add_task_ui(self, task=None):
        frame = Frame(self.task_frame, bd=2, relief=SUNKEN, pady=5)
        frame.pack(fill=X, padx=5, pady=5)

        cron_label = Label(frame, text="Cron Expression:")
        cron_label.pack(anchor=W)
        cron_entry = Entry(frame, width=50)
        cron_entry.pack(fill=X, padx=5)

        cmd_label = Label(frame, text="Command:")
        cmd_label.pack(anchor=W)
        cmd_entry = Entry(frame, width=50)
        cmd_entry.pack(fill=X, padx=5)

        folder_label = Label(frame, text="Folder:")
        folder_label.pack(anchor=W)
        folder_frame = Frame(frame)
        folder_frame.pack(fill=X, padx=5)

        folder_entry = Entry(folder_frame, width=40)
        folder_entry.pack(side=LEFT, fill=X, expand=True)
        browse_button = Button(folder_frame, text="Browse", command=lambda: self.browse_folder(folder_entry))
        browse_button.pack(side=LEFT)

        task_data = {
            "cron_entry": cron_entry,
            "cmd_entry": cmd_entry,
            "folder_entry": folder_entry,
            "frame": frame
        }

        if task:
            cron_entry.insert(0, task['cron'].strip())
            cmd_entry.insert(0, task['command'])
            folder_entry.insert(0, task['folder'])
            try:
                task_data['next_run'] = croniter(task['cron'].strip(), datetime.now()).get_next(datetime)
            except Exception as e:
                print(f"Invalid cron expression: {e}")
                task_data['next_run'] = None
        else:
            task_data['next_run'] = None

        self.tasks.append(task_data)

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, END)
            entry.insert(0, folder)

    def save_tasks(self):
        data = []
        for task in self.tasks:
            cron = task['cron_entry'].get().strip()
            command = task['cmd_entry'].get()
            folder = task['folder_entry'].get()
            if cron and command and folder:
                data.append({"cron": cron, "command": command, "folder": folder})
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Saved", "Tasks saved successfully!")

    def load_tasks(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    for task in data:
                        self.add_task_ui(task)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Invalid JSON in config file")

    def task_runner(self):
        while True:
            now = datetime.now()
            for task in self.tasks:
                try:
                    cron_expr = task['cron_entry'].get().strip()
                    if not task['next_run']:
                        task['next_run'] = croniter(cron_expr, now).get_next(datetime)
                    elif now >= task['next_run']:
                        print(f"Running command: {task['cmd_entry'].get()} at {now}")
                        threading.Thread(target=self.run_command, args=(
                            task['cmd_entry'].get(),
                            task['folder_entry'].get()
                        )).start()
                        task['next_run'] = croniter(cron_expr, now).get_next(datetime)
                except Exception as e:
                    print(f"Error with task: {e}")
            time.sleep(1)

    def run_command(self, command, folder):
        try:
            subprocess.Popen(command, shell=True, cwd=folder)
        except Exception as e:
            print(f"Command execution failed: {e}")

if __name__ == '__main__':
    root = Tk()
    app = CronTaskScheduler(root)
    root.mainloop()