import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
import tarfile
import gzip
import bz2
import shutil
import os
import threading
import time
from pathlib import Path

# Optional imports
try:
    import py7zr
    HAS_7Z = True
except ImportError:
    HAS_7Z = False

try:
    import rarfile
    HAS_RAR = True
except ImportError:
    HAS_RAR = False


# Palette & Font constants
BG         = "#0F0F13"
BG2        = "#17171F"
BG3        = "#1E1E2A"
CARD       = "#1A1A24"
BORDER     = "#2A2A3A"
ACCENT     = "#7C6AF7"
ACCENT2    = "#A594F9"
SUCCESS    = "#4ADE80"
WARN       = "#FACC15"
ERR        = "#F87171"
FG         = "#E8E8F0"
FG2        = "#9090A8"
FG3        = "#5A5A72"

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_MONO   = ("Courier New", 10)
FONT_LABEL  = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_BIG    = ("Segoe UI", 12, "bold")


def get_icon_for_ext(ext: str) -> str:
    icons = {
        ".zip": "📦", ".rar": "🗜", ".7z": "🔷",
        ".tar": "📁", ".gz": "🌀", ".bz2": "🔵",
        ".xz": "⬛", ".tgz": "🌀",
    }
    return icons.get(ext.lower(), "📄")


def format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def detect_archive_type(path: str) -> str | None:
    p = Path(path)
    name = p.name.lower()
    if name.endswith(".tar.gz") or name.endswith(".tgz"):  return "tar.gz"
    if name.endswith(".tar.bz2"):                          return "tar.bz2"
    if name.endswith(".tar.xz"):                           return "tar.xz"
    ext = p.suffix.lower()
    if ext in (".zip",):   return "zip"
    if ext in (".rar",):   return "rar"
    if ext in (".7z",):    return "7z"
    if ext in (".tar",):   return "tar"
    if ext in (".gz",):    return "gz"
    if ext in (".bz2",):   return "bz2"
    return None


def list_archive(path: str) -> list[dict]:
    """Return list of {name, size, is_dir} dicts."""
    atype = detect_archive_type(path)
    entries = []

    if atype == "zip":
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                entries.append({"name": info.filename,
                                 "size": info.file_size,
                                 "is_dir": info.filename.endswith("/")})

    elif atype in ("tar", "tar.gz", "tar.bz2", "tar.xz", "tgz"):
        mode = {"tar": "r:", "tar.gz": "r:gz", "tar.bz2": "r:bz2",
                "tar.xz": "r:xz", "tgz": "r:gz"}.get(atype, "r:*")
        with tarfile.open(path, mode) as tf:
            for m in tf.getmembers():
                entries.append({"name": m.name, "size": m.size,
                                 "is_dir": m.isdir()})

    elif atype == "7z" and HAS_7Z:
        with py7zr.SevenZipFile(path, mode="r") as sz:
            for name, info in sz.list():
                entries.append({"name": name,
                                 "size": info.uncompressed if info.uncompressed else 0,
                                 "is_dir": info.is_directory})

    elif atype == "rar" and HAS_RAR:
        with rarfile.RarFile(path) as rf:
            for info in rf.infolist():
                entries.append({"name": info.filename,
                                 "size": info.file_size,
                                 "is_dir": info.is_dir()})

    elif atype in ("gz", "bz2"):
        stem = Path(path).stem
        entries.append({"name": stem, "size": 0, "is_dir": False})

    return entries


def extract_archive(path: str, dest: str,
                    progress_cb=None, done_cb=None, error_cb=None):
    """Extract archive in a thread, calling callbacks."""
    def _run():
        try:
            atype = detect_archive_type(path)
            os.makedirs(dest, exist_ok=True)

            if atype == "zip":
                with zipfile.ZipFile(path) as zf:
                    members = zf.infolist()
                    total = len(members)
                    for i, m in enumerate(members):
                        zf.extract(m, dest)
                        if progress_cb:
                            progress_cb(int((i + 1) / total * 100), m.filename)

            elif atype in ("tar", "tar.gz", "tar.bz2", "tar.xz", "tgz"):
                mode = {"tar": "r:", "tar.gz": "r:gz", "tar.bz2": "r:bz2",
                        "tar.xz": "r:xz", "tgz": "r:gz"}.get(atype, "r:*")
                with tarfile.open(path, mode) as tf:
                    members = tf.getmembers()
                    total = len(members)
                    for i, m in enumerate(members):
                        tf.extract(m, dest, filter="data")
                        if progress_cb:
                            progress_cb(int((i + 1) / total * 100), m.name)

            elif atype == "7z" and HAS_7Z:
                with py7zr.SevenZipFile(path, mode="r") as sz:
                    names = sz.getnames()
                    total = len(names)
                    sz.extractall(path=dest)
                    if progress_cb:
                        for i, n in enumerate(names):
                            progress_cb(int((i + 1) / total * 100), n)

            elif atype == "rar" and HAS_RAR:
                with rarfile.RarFile(path) as rf:
                    members = rf.infolist()
                    total = len(members)
                    for i, m in enumerate(members):
                        rf.extract(m, dest)
                        if progress_cb:
                            progress_cb(int((i + 1) / total * 100), m.filename)

            elif atype in ("gz", "bz2"):
                stem = Path(path).stem
                out_path = os.path.join(dest, stem)
                opener = gzip.open if atype == "gz" else bz2.open
                with opener(path, "rb") as src, open(out_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                if progress_cb:
                    progress_cb(100, stem)

            else:
                raise ValueError(f"Formato non supportato o libreria mancante.")

            if done_cb:
                done_cb(dest)

        except Exception as exc:
            if error_cb:
                error_cb(str(exc))

    t = threading.Thread(target=_run, daemon=True)
    t.start()


# Main Application
class ExtioApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("ExtIO")
        self.geometry("820x640")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._archive_path = tk.StringVar()
        self._dest_path    = tk.StringVar()
        self._status       = tk.StringVar(value="Pronto.")
        self._progress_var = tk.DoubleVar(value=0)
        self._entries      = []
        self._extracting   = False

        self._build_ui()
        self._apply_styles()

    # UI Construction

    def _build_ui(self):
        # Header bar
        header = tk.Frame(self, bg=BG2, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="⬡", font=("Segoe UI", 24), bg=BG2,
                 fg=ACCENT).pack(side="left", padx=(20, 8), pady=10)
        tk.Label(header, text="ExtIO", font=FONT_TITLE,
                 bg=BG2, fg=FG).pack(side="left", pady=10)

        # Badge librerie
        badge_frame = tk.Frame(header, bg=BG2)
        badge_frame.pack(side="right", padx=20)
        self._add_badge(badge_frame, "ZIP/TAR", SUCCESS)
        self._add_badge(badge_frame, "7Z",  SUCCESS if HAS_7Z  else ERR)
        self._add_badge(badge_frame, "RAR", SUCCESS if HAS_RAR else ERR)

        # Separatore
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Corpo principale
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)

        # Sezione selezione file
        self._build_file_section(body)

        # Divider
        tk.Frame(body, bg=BORDER, height=1).grid(
            row=1, column=0, sticky="ew", pady=14)

        # Contenuto extio
        self._build_content_section(body)

        # Footer
        self._build_footer()

    def _add_badge(self, parent, text, color):
        f = tk.Frame(parent, bg=color, padx=6, pady=2)
        f.pack(side="left", padx=4)
        tk.Label(f, text=text, font=("Segoe UI", 8, "bold"),
                 bg=color, fg="#000").pack()

    def _build_file_section(self, parent):
        sec = tk.Frame(parent, bg=BG)
        sec.grid(row=0, column=0, sticky="ew")
        sec.columnconfigure(1, weight=1)

        # Extio
        tk.Label(sec, text="ExtIO", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=FG3).grid(row=0, column=0, columnspan=3,
                                     sticky="w", pady=(0, 4))

        self._arc_entry = tk.Entry(sec, textvariable=self._archive_path,
                                   font=FONT_MONO, bg=BG3, fg=FG,
                                   insertbackground=ACCENT, relief="flat",
                                   bd=0, highlightthickness=1,
                                   highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self._arc_entry.grid(row=1, column=0, columnspan=2,
                             sticky="ew", ipady=8, padx=(0, 8))

        btn_browse = self._make_btn(sec, "📂  Sfoglia", self._browse_archive,
                                    ACCENT, "#fff")
        btn_browse.grid(row=1, column=2)

        # Destinazione
        tk.Label(sec, text="DESTINAZIONE", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=FG3).grid(row=2, column=0, columnspan=3,
                                     sticky="w", pady=(12, 4))

        self._dest_entry = tk.Entry(sec, textvariable=self._dest_path,
                                    font=FONT_MONO, bg=BG3, fg=FG,
                                    insertbackground=ACCENT, relief="flat",
                                    bd=0, highlightthickness=1,
                                    highlightbackground=BORDER,
                                    highlightcolor=ACCENT)
        self._dest_entry.grid(row=3, column=0, columnspan=2,
                              sticky="ew", ipady=8, padx=(0, 8))

        btn_dest = self._make_btn(sec, "📁  Scegli", self._browse_dest,
                                   BG3, FG2)
        btn_dest.grid(row=3, column=2)

    def _build_content_section(self, parent):
        sec = tk.Frame(parent, bg=BG)
        sec.grid(row=2, column=0, sticky="nsew")
        sec.columnconfigure(0, weight=1)
        sec.rowconfigure(1, weight=1)

        # Header riga
        hdr = tk.Frame(sec, bg=BG)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        tk.Label(hdr, text="CONTENUTO", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=FG3).pack(side="left")

        self._count_label = tk.Label(hdr, text="", font=FONT_SMALL,
                                      bg=BG, fg=FG3)
        self._count_label.pack(side="left", padx=8)

        self._extract_btn = self._make_btn(
            hdr, "  ESTRAI TUTTO", self._start_extract,
            ACCENT, "#fff", big=True)
        self._extract_btn.pack(side="right")

        self._preview_btn = self._make_btn(
            hdr, "  Anteprima", self._load_preview, BG3, FG2)
        self._preview_btn.pack(side="right", padx=(0, 8))

        # Treeview
        tree_frame = tk.Frame(sec, bg=CARD, bd=0,
                               highlightthickness=1,
                               highlightbackground=BORDER)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ("icon", "name", "size")
        self._tree = ttk.Treeview(tree_frame, columns=cols,
                                   show="headings", height=10,
                                   selectmode="browse")
        self._tree.heading("icon", text="")
        self._tree.heading("name", text="Nome file")
        self._tree.heading("size", text="Dimensione")
        self._tree.column("icon", width=30,  minwidth=30,  stretch=False)
        self._tree.column("name", width=480, minwidth=200, stretch=True)
        self._tree.column("size", width=100, minwidth=80,  stretch=False,
                          anchor="e")
        self._tree.grid(row=0, column=0, sticky="nsew")

        sb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)

    def _build_footer(self):
        foot = tk.Frame(self, bg=BG2, height=52)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")

        inner = tk.Frame(foot, bg=BG2)
        inner.pack(fill="both", expand=True, padx=20)

        self._status_label = tk.Label(inner, textvariable=self._status,
                                       font=FONT_SMALL, bg=BG2, fg=FG2,
                                       anchor="w")
        self._status_label.pack(side="left", fill="x", expand=True,
                                 pady=10)

        # Progress bar personalizzata
        pb_bg = tk.Frame(inner, bg=BG3, height=6, width=200)
        pb_bg.pack(side="right", pady=10)
        pb_bg.pack_propagate(False)

        self._pb_fill = tk.Frame(pb_bg, bg=ACCENT, height=6, width=0)
        self._pb_fill.place(x=0, y=0, height=6)

        self._pb_bg_ref = pb_bg
        self._progress_var.trace_add("write", self._update_pb)

    # Helpers
    
    def _make_btn(self, parent, text, cmd, bg, fg, big=False):
        font = FONT_BTN if not big else ("Segoe UI", 11, "bold")
        btn = tk.Label(parent, text=text, font=font, bg=bg, fg=fg,
                        padx=14, pady=7, cursor="hand2")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.configure(
            bg=self._lighten(bg)))
        btn.bind("<Leave>",    lambda e: btn.configure(bg=bg))
        return btn

    @staticmethod
    def _lighten(hex_color: str) -> str:
        """Slightly lighten a hex color for hover."""
        h = hex_color.lstrip("#")
        if len(h) != 6:
            return hex_color
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
                         background=CARD, foreground=FG,
                         fieldbackground=CARD, rowheight=26,
                         borderwidth=0, font=FONT_SMALL)
        style.configure("Treeview.Heading",
                         background=BG3, foreground=FG2,
                         font=("Segoe UI", 9, "bold"),
                         borderwidth=0, relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])
        style.map("Treeview.Heading",
                  background=[("active", BORDER)])
        style.configure("Vertical.TScrollbar",
                         background=BG3, troughcolor=BG3,
                         borderwidth=0, arrowsize=0)

    def _update_pb(self, *_):
        val = self._progress_var.get()
        try:
            total = self._pb_bg_ref.winfo_width()
            fill  = int(total * val / 100)
            self._pb_fill.place(x=0, y=0, height=6, width=fill)
        except Exception:
            pass

    def _set_status(self, text: str, color: str = FG2):
        self._status.set(text)
        self._status_label.configure(fg=color)

    # Actions 

    def _browse_archive(self):
        exts = [
            ("Archivi supportati",
             "*.zip *.rar *.7z *.tar *.tar.gz *.tgz *.tar.bz2 *.tar.xz *.gz *.bz2"),
            ("ZIP", "*.zip"), ("RAR", "*.rar"), ("7-Zip", "*.7z"),
            ("TAR", "*.tar *.tar.gz *.tgz *.tar.bz2 *.tar.xz"),
            ("Tutti i file", "*.*"),
        ]
        path = filedialog.askopenfilename(filetypes=exts,
                                           title="Seleziona archivio")
        if path:
            self._archive_path.set(path)
            if not self._dest_path.get():
                self._dest_path.set(str(Path(path).parent /
                                        Path(path).stem))
            self._set_status(f"Archivio caricato: {Path(path).name}")
            self._clear_tree()

    def _browse_dest(self):
        d = filedialog.askdirectory(title="Scegli cartella di destinazione")
        if d:
            self._dest_path.set(d)

    def _clear_tree(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._count_label.configure(text="")

    def _load_preview(self):
        path = self._archive_path.get().strip()
        if not path or not os.path.isfile(path):
            self._set_status("⚠ Seleziona prima un archivio valido.", WARN)
            return

        atype = detect_archive_type(path)
        if atype is None:
            self._set_status("⚠ Formato non riconosciuto.", WARN)
            return

        self._set_status("Caricamento contenuto archivio…", FG2)
        self._clear_tree()

        def _do():
            try:
                entries = list_archive(path)
                self.after(0, lambda: self._populate_tree(entries))
            except Exception as exc:
                self.after(0, lambda: self._set_status(
                    f"❌ Errore lettura: {exc}", ERR))

        threading.Thread(target=_do, daemon=True).start()

    def _populate_tree(self, entries: list[dict]):
        self._entries = entries
        dirs  = [e for e in entries if e["is_dir"]]
        files = [e for e in entries if not e["is_dir"]]
        for e in sorted(dirs,  key=lambda x: x["name"]):
            self._tree.insert("", "end",
                               values=("📂", e["name"], "—"))
        for e in sorted(files, key=lambda x: x["name"]):
            ext  = Path(e["name"]).suffix
            icon = get_icon_for_ext(ext)
            sz   = format_size(e["size"]) if e["size"] else "—"
            self._tree.insert("", "end",
                               values=(icon, e["name"], sz))

        total_files = len(files)
        total_size  = sum(e["size"] for e in files if e["size"])
        self._count_label.configure(
            text=f"{total_files} file  •  {format_size(total_size)}")
        self._set_status(
            f"✔ Anteprima caricata: {len(entries)} elementi.", SUCCESS)

    def _start_extract(self):
        if self._extracting:
            return

        src  = self._archive_path.get().strip()
        dest = self._dest_path.get().strip()

        if not src or not os.path.isfile(src):
            self._set_status("⚠ Nessun archivio selezionato.", WARN)
            return
        if not dest:
            self._set_status("⚠ Nessuna destinazione selezionata.", WARN)
            return

        atype = detect_archive_type(src)
        if atype is None:
            self._set_status("⚠ Formato non supportato.", WARN)
            return
        if atype == "7z" and not HAS_7Z:
            messagebox.showerror("Libreria mancante",
                                  "Installa py7zr:\n  pip install py7zr")
            return
        if atype == "rar" and not HAS_RAR:
            messagebox.showerror("Libreria mancante",
                                  "Installa rarfile:\n  pip install rarfile")
            return

        self._extracting = True
        self._progress_var.set(0)
        self._set_status("⏳ Estrazione in corso…", ACCENT2)

        def on_progress(pct: int, name: str):
            self.after(0, lambda: self._progress_var.set(pct))
            self.after(0, lambda: self._set_status(
                f"[{pct:3d}%]  {Path(name).name}", ACCENT2))

        def on_done(dest_path: str):
            self._extracting = False
            self.after(0, lambda: self._progress_var.set(100))
            self.after(0, lambda: self._set_status(
                f"✔ Estrazione completata → {dest_path}", SUCCESS))
            self.after(0, lambda: self._flash_success())

        def on_error(msg: str):
            self._extracting = False
            self.after(0, lambda: self._set_status(
                f"❌ Errore: {msg}", ERR))
            self.after(0, lambda: messagebox.showerror(
                "Errore estrazione", msg))

        extract_archive(src, dest, on_progress, on_done, on_error)

    def _flash_success(self):
        """Briefly highlight the status bar."""
        original = BG2
        self.configure(bg=BG)
        for widget in (self._status_label,):
            widget.configure(fg=SUCCESS)
        self.after(1500, lambda: None)



if __name__ == "__main__":
    app = ExtioApp()
    app.mainloop()