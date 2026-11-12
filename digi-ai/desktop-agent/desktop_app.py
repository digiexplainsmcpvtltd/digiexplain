from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8765"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "DigiAI"
TOKEN_FILE = DATA_DIR / "owner.token"
HERE = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
AGENT_FILE = HERE / ("DigiAI-Service.exe" if getattr(sys, "frozen", False) else "agent.py")


class LocalAPI:
    def __init__(self, token: str):
        self.token = token

    def request(self, path: str, method="GET", payload=None):
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(
            BASE + path,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            },
        )
        with urlopen(req, timeout=8) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}


class DigiAIApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Digi AI — Personal Assistant")
        self.root.geometry("1020x720")
        self.root.minsize(820, 600)
        self.root.configure(bg="#0d100d")
        self.api = None
        self.agent_process = None
        self.memories = []
        self._style()
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        threading.Thread(target=self._connect, daemon=True).start()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#171c17", foreground="#f2f6ee",
                        fieldbackground="#171c17", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#263222", foreground="#81d100",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#34452b")])
        style.configure("TCombobox", fieldbackground="#171c17", background="#171c17",
                        foreground="#f2f6ee")

    def _label(self, parent, text, size=10, color="#9aa797", bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def _build(self):
        header = tk.Frame(self.root, bg="#111611", padx=22, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="DIGI ", bg="#111611", fg="#f2f6ee",
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="AI", bg="#111611", fg="#81d100",
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="LOCAL PERSONAL ASSISTANT", bg="#111611", fg="#9aa797",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=16, pady=(8, 0))
        self.status = tk.Label(header, text="● Starting local service…", bg="#111611",
                               fg="#f3bd58", font=("Segoe UI", 9, "bold"))
        self.status.pack(side="right")

        nav = tk.Frame(self.root, bg="#111611", padx=18, pady=8)
        nav.pack(fill="x")
        for name, callback in [
            ("Memory Vault", self.show_memory),
            ("Laptop Data", self.show_laptop_data),
            ("Add Knowledge", self.show_add),
            ("About & Safety", self.show_about),
        ]:
            tk.Button(nav, text=name, command=callback, bg="#263222", fg="#d7e4d0",
                      activebackground="#34452b", activeforeground="#81d100",
                      relief="flat", padx=14, pady=8, cursor="hand2").pack(side="left", padx=(0, 8))

        self.body = tk.Frame(self.root, bg="#0d100d", padx=22, pady=20)
        self.body.pack(fill="both", expand=True)
        self.show_memory()

        footer = tk.Frame(self.root, bg="#111611", padx=20, pady=9)
        footer.pack(fill="x")
        tk.Label(footer, text="LOCAL-FIRST • OWNER CONTROLLED • BLACK + #81D100",
                 bg="#111611", fg="#70806d", font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(footer, text="STOP LOCAL AI", command=self.stop_agent,
                  bg="#4b2222", fg="#ffe4e4", relief="flat", padx=12, pady=6).pack(side="right")

    def _clear(self):
        for child in self.body.winfo_children():
            child.destroy()

    def _connect(self):
        try:
            # Reuse a companion already running; otherwise start one even when
            # the owner token exists from an earlier session.
            try:
                with urlopen(BASE + "/health", timeout=1) as response:
                    if response.status == 200:
                        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
                        self.api = LocalAPI(token)
                        self.api.request("/health")
                        self.root.after(0, self._connected)
                        self.root.after(0, self.refresh)
                        return
            except Exception:
                pass
            if not AGENT_FILE.exists():
                raise RuntimeError("agent.py was not found beside desktop_app.py.")
            service_command = [str(AGENT_FILE)] if getattr(sys, "frozen", False) else [sys.executable, str(AGENT_FILE)]
            self.agent_process = subprocess.Popen(
                service_command,
                cwd=str(HERE),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(40):
                if TOKEN_FILE.exists():
                    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
                    if token:
                        self.api = LocalAPI(token)
                        try:
                            self.api.request("/health")
                            self.root.after(0, self._connected)
                            self.root.after(0, self.refresh)
                            return
                        except Exception:
                            pass
                time.sleep(0.5)
            raise RuntimeError("Local service did not start. Check Python dependencies and try again.")
        except Exception as exc:
            self.root.after(0, lambda: self._connection_error(str(exc)))

    def _connected(self):
        self.status.configure(text="● LOCAL MEMORY CONNECTED", fg="#81d100")

    def _connection_error(self, message):
        self.status.configure(text="● CONNECTION ERROR", fg="#f07878")
        messagebox.showerror("Digi AI setup", message + "\n\nRun install.bat, then open DigiAI.bat again.")

    def _require_api(self):
        if not self.api:
            messagebox.showwarning("Not connected", "Local memory service is not connected yet.")
            return False
        return True

    def show_memory(self):
        self._clear()
        self._label(self.body, "YOUR KNOWLEDGE, STORED LOCALLY", 10, "#81d100", True).pack(anchor="w")
        tk.Label(self.body, text="Memory Vault", bg="#0d100d", fg="#f2f6ee",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(3, 3))
        self._label(self.body, "Add company rates, client details, instructions, processes and information Digi AI should remember.").pack(anchor="w")
        toolbar = tk.Frame(self.body, bg="#0d100d")
        toolbar.pack(fill="x", pady=18)
        self.search_var = tk.StringVar()
        entry = tk.Entry(toolbar, textvariable=self.search_var, bg="#171c17", fg="#f2f6ee",
                         insertbackground="#f2f6ee", relief="flat", font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        entry.insert(0, "Search your memory…")
        tk.Button(toolbar, text="Search", command=self.search, bg="#81d100", fg="#10160b",
                  relief="flat", padx=18, pady=9).pack(side="left", padx=(0, 8))
        tk.Button(toolbar, text="+ Add memory", command=self.show_add, bg="#263222", fg="#81d100",
                  relief="flat", padx=14, pady=9).pack(side="left")
        columns = ("title", "category", "tags", "updated")
        self.tree = ttk.Treeview(self.body, columns=columns, show="headings")
        for col, title, width in [
            ("title", "MEMORY TITLE", 300), ("category", "CATEGORY", 130),
            ("tags", "TAGS", 250), ("updated", "LAST UPDATED", 180)
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        actions = tk.Frame(self.body, bg="#0d100d")
        actions.pack(fill="x", pady=12)
        for title, callback in [("View", self.view_selected), ("Edit", self.edit_selected),
                                ("Delete", self.delete_selected), ("Refresh", self.refresh)]:
            tk.Button(actions, text=title, command=callback, bg="#263222", fg="#d7e4d0",
                      relief="flat", padx=14, pady=8).pack(side="left", padx=(0, 8))
        self.refresh()

    def refresh(self):
        if not self._require_api():
            return
        try:
            result = self.api.request("/memory")
            self.memories = result.get("items", [])
            if hasattr(self, "tree") and self.tree.winfo_exists():
                self._render_rows(self.memories)
        except Exception as exc:
            messagebox.showerror("Memory error", str(exc))

    def _render_rows(self, items):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for memory in items:
            self.tree.insert("", "end", iid=memory["id"], values=(
                memory.get("title", ""), memory.get("category", ""),
                ", ".join(memory.get("tags", [])), memory.get("updated_at", "")[:19].replace("T", " ")
            ))

    def search(self):
        if not self._require_api():
            return
        query = self.search_var.get().strip()
        if not query or query == "Search your memory…":
            self.refresh()
            return
        from urllib.parse import quote
        try:
            result = self.api.request("/memory/search?q=" + quote(query))
            self._render_rows(result.get("items", []))
        except Exception as exc:
            messagebox.showerror("Search error", str(exc))

    def show_add(self):
        self._clear()
        self._label(self.body, "TEACH DIGI AI SOMETHING NEW", 10, "#81d100", True).pack(anchor="w")
        tk.Label(self.body, text="Add Knowledge", bg="#0d100d", fg="#f2f6ee",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(3, 16))
        self._label(self.body, "Title").pack(anchor="w")
        title = tk.Entry(self.body, bg="#171c17", fg="#f2f6ee", insertbackground="white",
                         relief="flat", font=("Segoe UI", 11))
        title.pack(fill="x", pady=(5, 14), ipady=9)
        self._label(self.body, "Category").pack(anchor="w")
        category = ttk.Combobox(self.body, values=[
            "company", "pricing", "client", "vendor", "process", "design",
            "marketing", "personal", "general"
        ])
        category.set("general")
        category.pack(fill="x", pady=(5, 14), ipady=5)
        self._label(self.body, "Tags (comma separated)").pack(anchor="w")
        tags = tk.Entry(self.body, bg="#171c17", fg="#f2f6ee", insertbackground="white",
                        relief="flat", font=("Segoe UI", 11))
        tags.pack(fill="x", pady=(5, 14), ipady=9)
        self._label(self.body, "Information to remember").pack(anchor="w")
        content = tk.Text(self.body, height=12, bg="#171c17", fg="#f2f6ee",
                          insertbackground="white", relief="flat", font=("Segoe UI", 11),
                          wrap="word")
        content.pack(fill="both", expand=True, pady=(5, 14))

        def save():
            if not self._require_api():
                return
            payload = {
                "title": title.get().strip(),
                "content": content.get("1.0", "end").strip(),
                "category": category.get().strip() or "general",
                "tags": [x.strip() for x in tags.get().split(",") if x.strip()],
            }
            if not payload["title"] or not payload["content"]:
                messagebox.showwarning("Missing information", "Title and information are required.")
                return
            try:
                self.api.request("/memory", method="POST", payload=payload)
                messagebox.showinfo("Saved", "Knowledge has been encrypted and saved on this laptop.")
                self.show_memory()
            except Exception as exc:
                messagebox.showerror("Save failed", str(exc))

        buttons = tk.Frame(self.body, bg="#0d100d")
        buttons.pack(fill="x")
        tk.Button(buttons, text="Save to local memory", command=save, bg="#81d100",
                  fg="#10160b", relief="flat", padx=18, pady=10).pack(side="left")
        tk.Button(buttons, text="Cancel", command=self.show_memory, bg="#263222",
                  fg="#d7e4d0", relief="flat", padx=18, pady=10).pack(side="left", padx=8)

    def _selected(self):
        if not hasattr(self, "tree"):
            return None
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select memory", "Please select a memory record first.")
            return None
        return next((m for m in self.memories if m["id"] == selected[0]), None)

    def view_selected(self):
        item = self._selected()
        if item:
            messagebox.showinfo(item["title"], item["content"] + "\n\nCategory: " +
                                item.get("category", "") + "\nTags: " +
                                ", ".join(item.get("tags", [])))

    def edit_selected(self):
        item = self._selected()
        if not item or not self._require_api():
            return
        title = simpledialog.askstring("Edit title", "Memory title:", initialvalue=item["title"], parent=self.root)
        if title is None:
            return
        content = simpledialog.askstring("Edit information", "Memory content:", initialvalue=item["content"], parent=self.root)
        if content is None:
            return
        try:
            self.api.request("/memory/" + item["id"], method="PATCH",
                             payload={"title": title, "content": content})
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Update failed", str(exc))

    def delete_selected(self):
        item = self._selected()
        if not item or not self._require_api():
            return
        if not messagebox.askyesno("Confirm deletion", "Delete this saved memory permanently?"):
            return
        try:
            self.api.request("/memory/" + item["id"], method="DELETE")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Delete failed", str(exc))


    def show_laptop_data(self):
        self._clear()
        self._label(self.body, "LOCAL COMPUTER KNOWLEDGE", 10, "#81d100", True).pack(anchor="w")
        tk.Label(self.body, text="Laptop Data", bg="#0d100d", fg="#f2f6ee",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(3, 3))
        self._label(self.body, "Choose a folder to index supported business documents. Data stays on this laptop.").pack(anchor="w")
        controls = tk.Frame(self.body, bg="#0d100d")
        controls.pack(fill="x", pady=16)
        tk.Button(controls, text="Choose folder & scan", command=self.choose_and_scan,
                  bg="#81d100", fg="#10160b", relief="flat", padx=16, pady=10).pack(side="left")
        tk.Button(controls, text="Refresh index", command=self.refresh_laptop_files,
                  bg="#263222", fg="#d7e4d0", relief="flat", padx=16, pady=10).pack(side="left", padx=8)
        self.file_search = tk.StringVar()
        search = tk.Entry(self.body, textvariable=self.file_search, bg="#171c17", fg="#f2f6ee",
                          insertbackground="white", relief="flat", font=("Segoe UI", 11))
        search.pack(fill="x", ipady=9, pady=(0, 10))
        search.insert(0, "Search indexed laptop documents…")
        tk.Button(self.body, text="Search", command=self.refresh_laptop_files,
                  bg="#263222", fg="#81d100", relief="flat", padx=14, pady=7).pack(anchor="e", pady=(0, 8))
        self.file_tree = ttk.Treeview(self.body, columns=("name", "type", "size", "modified"),
                                      show="headings")
        for col, label, width in [("name", "FILE", 260), ("type", "TYPE", 90),
                                  ("size", "SIZE (KB)", 100), ("modified", "MODIFIED", 190)]:
            self.file_tree.heading(col, text=label)
            self.file_tree.column(col, width=width, anchor="w")
        self.file_tree.pack(fill="both", expand=True)
        self.file_status = self._label(self.body, "No laptop folders indexed yet.", 9, "#9aa797")
        self.file_status.pack(anchor="w", pady=8)
        self.refresh_laptop_files()

    def choose_and_scan(self):
        if not self._require_api():
            return
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Choose a folder for Digi AI to scan")
        if not folder:
            return
        try:
            result = self.api.request("/computer/scan", method="POST", payload={"folder": folder})
            messagebox.showinfo("Laptop scan complete",
                "Indexed: " + str(result.get("indexed", 0)) + "\nSkipped: " +
                str(result.get("skipped", 0)) +
                "\n\nExtracted content is encrypted and saved on this laptop.")
            self.refresh_laptop_files()
        except Exception as exc:
            messagebox.showerror("Laptop scan failed", str(exc))

    def refresh_laptop_files(self):
        if not self._require_api() or not hasattr(self, "file_tree"):
            return
        try:
            from urllib.parse import quote
            query = self.file_search.get().strip()
            if query == "Search indexed laptop documents…":
                query = ""
            result = self.api.request("/computer/files?q=" + quote(query))
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            for i, item in enumerate(result.get("items", [])):
                self.file_tree.insert("", "end", iid=str(i), values=(
                    item.get("name", ""), item.get("extension", ""),
                    round(item.get("size_bytes", 0) / 1024, 1),
                    item.get("modified_at", "")[:19].replace("T", " ")
                ))
            self.file_status.configure(text=str(result.get("count", 0)) +
                " indexed documents • Stored locally with encryption")
        except Exception as exc:
            messagebox.showerror("Laptop index error", str(exc))

    def show_about(self):
        self._clear()
        self._label(self.body, "OWNER CONTROL & PRIVACY", 10, "#81d100", True).pack(anchor="w")
        tk.Label(self.body, text="About Digi AI", bg="#0d100d", fg="#f2f6ee",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(3, 15))
        details = [
            "Your memory is stored on this Windows laptop, not in a cloud database.",
            "Memory records are encrypted before they are written to the local SQLite database.",
            "The encryption key is held by Windows Credential Manager.",
            "The local API listens only on 127.0.0.1 and requires your owner token.",
            "Laptop Data lets you select folders and index supported PDF, DOCX, XLSX, PPTX and text documents.",
            "Only folders you explicitly select are scanned. Each scan is capped at 500 files and 8 MB per file.",
            "Extracted content and metadata are encrypted and stored on this laptop; no cloud upload occurs.",
            "This release does not yet read WhatsApp/email chats, capture your screen or control other apps.",
            "Use STOP LOCAL AI to stop the companion process. Closing this window also stops a process started by this app.",
        ]
        for text in details:
            tk.Label(self.body, text="• " + text, bg="#171c17", fg="#d7e4d0",
                     justify="left", anchor="w", wraplength=850, padx=16, pady=12).pack(fill="x", pady=5)

    def stop_agent(self):
        if self.agent_process and self.agent_process.poll() is None:
            self.agent_process.terminate()
            self.agent_process = None
        self.api = None
        self.status.configure(text="● LOCAL AI STOPPED", fg="#f3bd58")
        messagebox.showinfo("Digi AI", "Local companion stopped. Your encrypted memory remains on this laptop.")

    def close(self):
        if self.agent_process and self.agent_process.poll() is None:
            self.agent_process.terminate()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    DigiAIApp(root)
    root.mainloop()
