
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

FILE = "tasks.json"

LIGHT = {
    "bg": "#EAF4FF",
    "card": "#FFFFFF",
    "title": "#1E3A8A",
    "text": "#1F2937",
    "muted": "#6B7280",
    "accent": "#3B82F6",
    "done_btn": "#BBF7D0",
    "edit_btn": "#BFDBFE",
    "del_btn": "#FECACA",
}
DARK = {
    "bg": "#111827",
    "card": "#1F2937",
    "title": "#93C5FD",
    "text": "#F3F4F6",
    "muted": "#9CA3AF",
    "accent": "#60A5FA",
    "done_btn": "#166534",
    "edit_btn": "#1E40AF",
    "del_btn": "#991B1B",
}
PRIORITY_COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

tasks = []
theme = LIGHT

# ---------- Window ----------
root = tk.Tk()
root.title("TasKora - To Do List")
root.geometry("620x780")
root.minsize(560, 700)

# ---------- Data ----------
def save_tasks():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

def load_tasks():
    global tasks
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)

# ---------- Actions ----------
def add_task():
    name = task_entry.get().strip()
    due = due_entry.get().strip()
    if not name:
        messagebox.showwarning("TasKora", "Enter a task first!")
        return
    if due and due != "DD-MM-YYYY":
        try:
            datetime.strptime(due, "%d-%m-%Y")
        except ValueError:
            messagebox.showwarning("TasKora", "Date format must be DD-MM-YYYY")
            return
    else:
        due = ""
    tasks.append({
        "name": name,
        "done": False,
        "priority": priority_var.get(),
        "category": category_var.get(),
        "due": due,
    })
    task_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    due_entry.insert(0, "DD-MM-YYYY")
    save_tasks()
    show_tasks()

def toggle_done(task):
    task["done"] = not task["done"]
    save_tasks()
    show_tasks()

def delete_task(task):
    if messagebox.askyesno("TasKora", "Delete this task?"):
        tasks.remove(task)
        save_tasks()
        show_tasks()

def edit_task(task):
    new_name = simpledialog.askstring("Edit Task", "New task name:", initialvalue=task["name"])
    if new_name and new_name.strip():
        task["name"] = new_name.strip()
        save_tasks()
        show_tasks()

def toggle_theme():
    global theme
    theme = DARK if theme is LIGHT else LIGHT
    apply_theme()
    show_tasks()

def on_due_focus_in(event):
    if due_entry.get() == "DD-MM-YYYY":
        due_entry.delete(0, tk.END)

# ---------- Display ----------
def is_overdue(task):
    if task["done"] or not task.get("due"):
        return False
    try:
        return datetime.strptime(task["due"], "%d-%m-%Y").date() < datetime.now().date()
    except ValueError:
        return False

def show_tasks(*args):
    for w in task_frame.winfo_children():
        w.destroy()

    search = search_var.get().strip().lower()
    flt = filter_var.get()

    visible = []
    for t in tasks:
        if search and search not in t["name"].lower():
            continue
        if flt == "Pending" and t["done"]:
            continue
        if flt == "Completed" and not t["done"]:
            continue
        visible.append(t)

    if not visible:
        tk.Label(task_frame, text="No tasks to show", font=("Segoe UI", 12),
                 bg=theme["bg"], fg=theme["muted"]).pack(pady=30)

    for t in visible:
        card = tk.Frame(task_frame, bg=theme["card"], highlightthickness=1,
                        highlightbackground=PRIORITY_COLORS.get(t.get("priority", "Medium")))
        card.pack(fill="x", pady=5, padx=2)

        top = tk.Frame(card, bg=theme["card"])
        top.pack(fill="x", padx=10, pady=(8, 0))

        mark = "✓" if t["done"] else "○"
        name_font = ("Segoe UI", 12, "overstrike") if t["done"] else ("Segoe UI", 12, "bold")
        tk.Label(top, text=mark + " " + t["name"], font=name_font,
                 bg=theme["card"],
                 fg=theme["muted"] if t["done"] else theme["text"]).pack(side="left")

        info = tk.Frame(card, bg=theme["card"])
        info.pack(fill="x", padx=10, pady=(2, 4))
        pr = t.get("priority", "Medium")
        tk.Label(info, text="● " + pr, font=("Segoe UI", 9, "bold"),
                 bg=theme["card"], fg=PRIORITY_COLORS[pr]).pack(side="left")
        tk.Label(info, text="  |  " + t.get("category", "Personal"), font=("Segoe UI", 9),
                 bg=theme["card"], fg=theme["muted"]).pack(side="left")
        if t.get("due"):
            overdue = is_overdue(t)
            tk.Label(info, text="  |  Due: " + t["due"] + (" (Overdue)" if overdue else ""),
                     font=("Segoe UI", 9), bg=theme["card"],
                     fg="#EF4444" if overdue else theme["muted"]).pack(side="left")

        btns = tk.Frame(card, bg=theme["card"])
        btns.pack(fill="x", padx=10, pady=(0, 8))
        tk.Button(btns, text="Undo" if t["done"] else "Done", bg=theme["done_btn"],
                  fg=theme["text"], relief="flat", padx=10,
                  command=lambda x=t: toggle_done(x)).pack(side="left", padx=(0, 5))
        tk.Button(btns, text="Edit", bg=theme["edit_btn"], fg=theme["text"],
                  relief="flat", padx=10,
                  command=lambda x=t: edit_task(x)).pack(side="left", padx=5)
        tk.Button(btns, text="Delete", bg=theme["del_btn"], fg=theme["text"],
                  relief="flat", padx=10,
                  command=lambda x=t: delete_task(x)).pack(side="left", padx=5)

    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    percent = int(done / total * 100) if total else 0
    progress["value"] = percent
    progress_label.config(text=str(percent) + "% completed (" + str(done) + "/" + str(total) + ")")

# ---------- Theme ----------
def apply_theme():
    root.config(bg=theme["bg"])
    for w in (header, form, filter_bar, progress_area, list_area):
        w.config(bg=theme["bg"])
    title_label.config(bg=theme["bg"], fg=theme["title"])
    tagline.config(bg=theme["bg"], fg=theme["muted"])
    progress_label.config(bg=theme["bg"], fg=theme["text"])
    task_frame.config(bg=theme["bg"])
    canvas.config(bg=theme["bg"])
    for lbl in form_labels + filter_labels:
        lbl.config(bg=theme["bg"], fg=theme["text"])
    for row in form_rows:
        row.config(bg=theme["bg"])
    theme_btn.config(text="☀ Light" if theme is DARK else "🌙 Dark",
                     bg=theme["accent"])

# ---------- Header ----------
header = tk.Frame(root)
header.pack(fill="x", pady=(15, 5), padx=20)
title_label = tk.Label(header, text="TasKora", font=("Segoe UI", 28, "bold"))
title_label.pack(side="left")
theme_btn = tk.Button(header, text="🌙 Dark", fg="white", relief="flat",
                      font=("Segoe UI", 10, "bold"), padx=12, pady=4,
                      command=toggle_theme)
theme_btn.pack(side="right")
tagline = tk.Label(root, text="Plan it. Track it. Complete it.", font=("Segoe UI", 11))
tagline.pack()

# ---------- Form ----------
form = tk.Frame(root)
form.pack(fill="x", padx=20, pady=10)

row1 = tk.Frame(form)
row1.pack(fill="x", pady=3)
lbl_task = tk.Label(row1, text="Task", width=9, anchor="w", font=("Segoe UI", 10, "bold"))
lbl_task.pack(side="left")
task_entry = tk.Entry(row1, font=("Segoe UI", 12), relief="solid", bd=1)
task_entry.pack(side="left", fill="x", expand=True, ipady=4)

row2 = tk.Frame(form)
row2.pack(fill="x", pady=3)
lbl_due = tk.Label(row2, text="Due date", width=9, anchor="w", font=("Segoe UI", 10, "bold"))
lbl_due.pack(side="left")
due_entry = tk.Entry(row2, font=("Segoe UI", 11), width=14, relief="solid", bd=1)
due_entry.pack(side="left", ipady=3)
due_entry.insert(0, "DD-MM-YYYY")
due_entry.bind("<FocusIn>", on_due_focus_in)

row3 = tk.Frame(form)
row3.pack(fill="x", pady=3)
lbl_pri = tk.Label(row3, text="Priority", width=9, anchor="w", font=("Segoe UI", 10, "bold"))
lbl_pri.pack(side="left")
priority_var = tk.StringVar(value="Medium")
ttk.Combobox(row3, textvariable=priority_var, values=["High", "Medium", "Low"],
             state="readonly", width=10).pack(side="left")
lbl_cat = tk.Label(row3, text="  Category", anchor="w", font=("Segoe UI", 10, "bold"))
lbl_cat.pack(side="left")
category_var = tk.StringVar(value="Studies")
ttk.Combobox(row3, textvariable=category_var, values=["Studies", "Personal", "Work"],
             state="readonly", width=10).pack(side="left")

tk.Button(form, text="+ Add Task", font=("Segoe UI", 12, "bold"), bg="#3B82F6",
          fg="white", relief="flat", pady=6, command=add_task).pack(fill="x", pady=(8, 0))

form_labels = [lbl_task, lbl_due, lbl_pri, lbl_cat]
form_rows = [row1, row2, row3]

# ---------- Search and Filter ----------
filter_bar = tk.Frame(root)
filter_bar.pack(fill="x", padx=20, pady=5)
lbl_search = tk.Label(filter_bar, text="Search", font=("Segoe UI", 10, "bold"))
lbl_search.pack(side="left")
search_var = tk.StringVar()
search_var.trace_add("write", show_tasks)
tk.Entry(filter_bar, textvariable=search_var, font=("Segoe UI", 11), relief="solid",
         bd=1, width=18).pack(side="left", padx=8, ipady=3)
lbl_filter = tk.Label(filter_bar, text="Filter", font=("Segoe UI", 10, "bold"))
lbl_filter.pack(side="left")
filter_var = tk.StringVar(value="All")
filter_box = ttk.Combobox(filter_bar, textvariable=filter_var,
                          values=["All", "Pending", "Completed"], state="readonly", width=10)
filter_box.pack(side="left", padx=8)
filter_box.bind("<<ComboboxSelected>>", show_tasks)
filter_labels = [lbl_search, lbl_filter]

# ---------- Progress ----------
progress_area = tk.Frame(root)
progress_area.pack(fill="x", padx=20, pady=5)
progress_label = tk.Label(progress_area, text="0% completed", font=("Segoe UI", 10))
progress_label.pack(anchor="w")
progress = ttk.Progressbar(progress_area, mode="determinate")
progress.pack(fill="x", pady=3)

# ---------- Scrollable task list ----------
list_area = tk.Frame(root)
list_area.pack(fill="both", expand=True, padx=20, pady=(5, 15))
canvas = tk.Canvas(list_area, highlightthickness=0)
scrollbar = ttk.Scrollbar(list_area, orient="vertical", command=canvas.yview)
task_frame = tk.Frame(canvas)
task_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
window_id = canvas.create_window((0, 0), window=task_frame, anchor="nw")
canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------- Start ----------
load_tasks()
apply_theme()
show_tasks()
root.mainloop()
