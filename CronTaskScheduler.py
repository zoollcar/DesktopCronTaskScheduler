import os
import json
import subprocess
import threading
import time
from datetime import datetime
from tkinter import *
from tkinter import messagebox, filedialog
from croniter import croniter, CroniterBadCronError
import pystray
from PIL import Image, ImageDraw

CONFIG_FILE = "tasks.json"
HISTORY_FILE = "task_history.log"


class CronTaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Cron Task Scheduler")
        self.tasks = []

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.canvas = Canvas(self.root)
        self.scrollbar = Scrollbar(
            self.root, orient=VERTICAL, command=self.canvas.yview
        )
        self.task_frame = Frame(self.canvas)
        self.task_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.add_task_button = Button(
            self.root, text="Add Task", command=self.add_task_ui
        )
        self.add_task_button.pack(pady=5)

        self.save_button = Button(
            self.root, text="Save Tasks", command=self.save_and_reload_tasks
        )
        self.save_button.pack(pady=5)

        self.example_label = Text(self.root, height=6, wrap=WORD)
        self.example_label.insert(
            END, "Examples (cron format: min hour day month weekday):\n"
        )
        self.example_label.insert(END, "* * * * * = every minute\n")
        self.example_label.insert(END, "*/5 * * * * = every 5 minutes\n")
        self.example_label.insert(END, "0 9 * * * = every day at 9:00 AM\n")
        self.example_label.insert(END, "0 0 * * 0 = every Sunday at midnight\n")
        self.example_label.insert(END, "0 12 1 * * = every month on the 1st at noon\n")
        self.example_label.insert(
            END, "15 14 1 * * = 14:15 on the 1st of every month\n"
        )
        self.example_label.insert(END, "0 18 * * 1-5 = weekdays at 6 PM\n")
        self.example_label.insert(
            END, "Note: Seconds field is not supported by croniter\n"
        )
        self.example_label.config(state=DISABLED)
        self.example_label.pack(fill=BOTH, padx=10, pady=(0, 10))

        self.status_frame = Frame(self.root)
        self.status_frame.pack(fill=X, padx=5)

        self.load_tasks()

        threading.Thread(target=self.task_runner, daemon=True).start()
        threading.Thread(target=self.create_tray_icon, daemon=True).start()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon, item):
        self.root.quit()
        self.root.destroy()
        icon.stop()

    def add_task_ui(self, task=None):
        frame = Frame(self.task_frame, bd=2, relief=SUNKEN, pady=5)
        frame.pack(fill=X, padx=5, pady=5)

        cron_label = Label(frame, text="Cron Expression (min hour day month weekday):")
        cron_label.pack(anchor=W)
        cron_entry = Entry(frame, width=50)
        cron_entry.insert(0, "* * * * *")
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
        browse_button = Button(
            folder_frame,
            text="Browse",
            command=lambda: self.browse_folder(folder_entry),
        )
        browse_button.pack(side=LEFT)

        next_run_label = Label(frame, text="Next run: calculating...", fg="blue")
        next_run_label.pack(anchor=W, padx=5, pady=2)

        delete_button = Button(
            frame,
            text="Delete Task",
            fg="red",
            command=lambda: self.delete_task(task_data),
        )
        delete_button.pack(pady=2)

        task_data = {
            "cron_entry": cron_entry,
            "cmd_entry": cmd_entry,
            "folder_entry": folder_entry,
            "frame": frame,
            "next_run_label": next_run_label,
            "next_run": None,
        }

        def update_next_run(*args):
            try:
                expr = cron_entry.get().strip()
                task_data["next_run"] = croniter(expr, datetime.now()).get_next(
                    datetime
                )
                next_run_label.config(
                    text=f"Next run: {task_data['next_run'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
            except Exception:
                task_data["next_run"] = None
                next_run_label.config(text="Invalid cron expression")

        cron_entry.bind("<KeyRelease>", update_next_run)

        if task:
            cron_entry.delete(0, END)
            cron_entry.insert(0, task["cron"].strip())
            cmd_entry.insert(0, task["command"])
            folder_entry.insert(0, task["folder"])
            update_next_run()

        self.tasks.append(task_data)

    def delete_task(self, task_data):
        task_data["frame"].destroy()
        self.tasks.remove(task_data)

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, END)
            entry.insert(0, folder)

    def save_and_reload_tasks(self):
        self.save_tasks()
        for task in self.tasks:
            task["frame"].destroy()
        self.tasks.clear()
        self.load_tasks()

    def save_tasks(self):
        data = []
        for task in self.tasks:
            cron = task["cron_entry"].get().strip()
            command = task["cmd_entry"].get()
            folder = task["folder_entry"].get()
            if cron and command and folder:
                data.append({"cron": cron, "command": command, "folder": folder})
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Saved", "Tasks saved successfully! Reloaded.")

    def load_tasks(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    for task in data:
                        self.add_task_ui(task)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Invalid JSON in config file")

    def log_execution(self, command, folder):
        with open(HISTORY_FILE, "a") as f:
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executed: {command} in {folder}\n"
            )

    def task_runner(self):
        while True:
            now = datetime.now()
            for task in self.tasks:
                try:
                    cron_expr = task["cron_entry"].get().strip()
                    if not task.get("next_run"):
                        task["next_run"] = croniter(cron_expr, now).get_next(datetime)
                    if now >= task["next_run"]:
                        print(f"Running command: {task['cmd_entry'].get()} at {now}")
                        threading.Thread(
                            target=self.run_command,
                            args=(task["cmd_entry"].get(), task["folder_entry"].get()),
                        ).start()
                        self.log_execution(
                            task["cmd_entry"].get(), task["folder_entry"].get()
                        )
                        task["next_run"] = croniter(cron_expr, now).get_next(datetime)
                    task["next_run_label"].config(
                        text=f"Next run: {task['next_run'].strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                except (ValueError, CroniterBadCronError):
                    task["next_run_label"].config(text="Invalid cron expression")
            time.sleep(30)

    def run_command(self, command, folder):
        try:
            full_path = os.path.join(folder, command)
            final_cmd = f'start "" "{full_path}"'
            subprocess.Popen(final_cmd, shell=True)
        except Exception as e:
            print(f"Command execution failed: {e}")

    def create_tray_icon(self):
        image = Image.new("RGB", (64, 64), color="white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 63, 63), fill="lightblue")
        draw.text((10, 20), "CRON", fill="black")

        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Quit", self.quit_app),
        )

        icon = pystray.Icon("CronTaskScheduler", image, "Cron Scheduler", menu)

        icon.run()


if __name__ == "__main__":
    root = Tk()
    app = CronTaskScheduler(root)
    root.mainloop()
