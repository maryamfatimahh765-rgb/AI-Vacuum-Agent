"""
=======================================================
  Vacuum Cleaner Agent Simulation
  A Beginner-Friendly AI Project in Python (Tkinter)
=======================================================
  Concepts demonstrated:
    - Intelligent agent (perceive → decide → act loop)
    - Environment with multiple rooms
    - Agent actions: Clean, Move, Idle
    - GUI with Start, Next Step, and Reset buttons
=======================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# ──────────────────────────────────────────────
# AGENT LOGIC
# ──────────────────────────────────────────────

class VacuumAgent:
    """
    The intelligent agent.
    It perceives the room it is in, decides what to do,
    and acts: either CLEAN the room or MOVE to the next one.
    """

    def __init__(self, rooms):
        """
        rooms: list of dicts  e.g. [{"name": "A", "state": "dirty"}, ...]
        The agent always starts in the first room (index 0).
        """
        self.rooms      = rooms          # shared environment
        self.position   = 0              # current room index
        self.steps      = 0              # total steps taken
        self.cleaned    = 0              # rooms cleaned so far
        self.moves      = 0              # number of moves made
        self.finished   = False          # True when all rooms are clean

    # ── Perception ─────────────────────────────
    def perceive(self):
        """Return the state of the room the agent is currently in."""
        return self.rooms[self.position]["state"]

    # ── Decision + Action ──────────────────────
    def step(self):
        """
        Execute ONE step of the agent:
          • If current room is dirty  → clean it
          • If current room is clean  → move to next room
          • If already at last room and everything is clean → signal done
        Returns a log message describing the action taken.
        """
        self.steps += 1
        current_room = self.rooms[self.position]["name"]
        perception   = self.perceive()

        # ACTION 1: Clean the dirty room
        if perception == "dirty":
            self.rooms[self.position]["state"] = "clean"
            self.cleaned += 1
            return ("clean", f"Step {self.steps}: Cleaned Room {current_room} 🧹")

        # ACTION 2: Move to the next room (if one exists)
        if self.position < len(self.rooms) - 1:
            self.position += 1
            self.moves += 1
            next_room = self.rooms[self.position]["name"]
            return ("move", f"Step {self.steps}: Room {current_room} is clean → moved to Room {next_room} ➡")

        # DONE: Last room reached and it was already clean
        self.finished = True
        return ("done", f"Step {self.steps}: All rooms are clean! Task complete ✅")

    def all_clean(self):
        """Return True if every room is clean."""
        return all(r["state"] == "clean" for r in self.rooms)


# ──────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────

class VacuumGUI:
    """
    Tkinter GUI that shows:
      • Room cards with their current state
      • Action log with step-by-step output
      • Buttons: Start, Next Step, Reset
    """

    # Colour palette
    DIRTY_BG   = "#FFF0EE"
    DIRTY_BD   = "#E24B4A"
    DIRTY_TXT  = "#A32D2D"
    CLEAN_BG   = "#EAF3DE"
    CLEAN_BD   = "#639922"
    CLEAN_TXT  = "#3B6D11"
    AGENT_BG   = "#E6F1FB"
    AGENT_BD   = "#378ADD"
    AGENT_TXT  = "#185FA5"
    BG         = "#F9F9F7"        # window background
    PANEL_BG   = "#FFFFFF"
    MUTED      = "#888780"

    def __init__(self, root):
        self.root = root
        self.root.title("Vacuum Cleaner Agent Simulation")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)

        # Internal state
        self.num_rooms  = tk.IntVar(value=3)
        self.dirty_pct  = tk.IntVar(value=60)
        self.agent      = None
        self.auto_id    = None       # after() handle for auto-run

        self._build_ui()
        self._init_simulation()

    # ── Layout ─────────────────────────────────

    def _build_ui(self):
        """Construct every widget."""

        # ── Title ──────────────────────────────
        title_frm = tk.Frame(self.root, bg=self.BG)
        title_frm.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(title_frm, text="Vacuum Cleaner Agent",
                 font=("Helvetica", 18, "bold"),
                 bg=self.BG, fg="#2C2C2A").pack(anchor="w")
        tk.Label(title_frm, text="A simple intelligent agent that perceives, decides, and acts",
                 font=("Helvetica", 11),
                 bg=self.BG, fg=self.MUTED).pack(anchor="w")

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=20, pady=8)

        # ── Config row ─────────────────────────
        cfg = tk.Frame(self.root, bg=self.BG)
        cfg.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(cfg, text="Rooms:", bg=self.BG, fg=self.MUTED,
                 font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.room_slider = tk.Scale(cfg, from_=2, to=6, orient="horizontal",
                                    variable=self.num_rooms, command=self._on_config_change,
                                    bg=self.BG, fg="#2C2C2A", highlightthickness=0,
                                    troughcolor="#D3D1C7", length=110)
        self.room_slider.grid(row=0, column=1, padx=(0, 16))

        tk.Label(cfg, text="Dirty chance:", bg=self.BG, fg=self.MUTED,
                 font=("Helvetica", 11)).grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.dirty_slider = tk.Scale(cfg, from_=0, to=100, orient="horizontal",
                                     variable=self.dirty_pct, command=self._on_config_change,
                                     bg=self.BG, fg="#2C2C2A", highlightthickness=0,
                                     troughcolor="#D3D1C7", length=110, tickinterval=50)
        self.dirty_slider.grid(row=0, column=3)

        # ── Room cards ─────────────────────────
        self.room_frame = tk.Frame(self.root, bg=self.BG)
        self.room_frame.pack(fill="x", padx=20, pady=(4, 8))
        self.room_cards = []   # list of dicts with tk widgets

        # ── Button row ─────────────────────────
        btn_frm = tk.Frame(self.root, bg=self.BG)
        btn_frm.pack(fill="x", padx=20, pady=(0, 8))

        btn_style = dict(font=("Helvetica", 12, "bold"),
                         relief="flat", bd=0, padx=18, pady=7, cursor="hand2")

        self.btn_start = tk.Button(btn_frm, text="▶  Start", bg="#2C2C2A", fg="white",
                                   command=self._start, **btn_style)
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_step = tk.Button(btn_frm, text="➡  Next step", bg=self.PANEL_BG, fg="#2C2C2A",
                                  command=self._manual_step, relief="solid", bd=1,
                                  font=("Helvetica", 12), padx=16, pady=7, cursor="hand2")
        self.btn_step.pack(side="left", padx=(0, 8))

        self.btn_reset = tk.Button(btn_frm, text="↺  Reset", bg=self.PANEL_BG, fg="#2C2C2A",
                                   command=self._reset, relief="solid", bd=1,
                                   font=("Helvetica", 12), padx=16, pady=7, cursor="hand2")
        self.btn_reset.pack(side="left")

        # ── Log panel ──────────────────────────
        log_outer = tk.Frame(self.root, bg=self.BG)
        log_outer.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        log_header = tk.Frame(log_outer, bg="#F1EFE8", relief="flat", bd=0)
        log_header.pack(fill="x")
        tk.Label(log_header, text="Agent log", font=("Helvetica", 11, "bold"),
                 bg="#F1EFE8", fg="#2C2C2A", padx=12, pady=6).pack(side="left")
        self.step_lbl = tk.Label(log_header, text="Step 0",
                                 font=("Helvetica", 10), bg="#F1EFE8", fg=self.MUTED)
        self.step_lbl.pack(side="right", padx=12)

        log_body = tk.Frame(log_outer, bg=self.PANEL_BG, relief="solid", bd=1)
        log_body.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_body, height=9, bg=self.PANEL_BG, fg="#2C2C2A",
                                font=("Helvetica", 11), relief="flat", bd=6,
                                state="disabled", wrap="word")
        scroll = ttk.Scrollbar(log_body, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # colour tags for log entries
        self.log_text.tag_config("clean_tag", foreground="#3B6D11")
        self.log_text.tag_config("move_tag",  foreground="#185FA5")
        self.log_text.tag_config("done_tag",  foreground="#185FA5", font=("Helvetica", 11, "bold"))
        self.log_text.tag_config("info_tag",  foreground=self.MUTED)

        # ── Stats bar ──────────────────────────
        stats = tk.Frame(self.root, bg=self.BG)
        stats.pack(fill="x", padx=20, pady=(0, 14))
        for col, (val_attr, lbl_text) in enumerate([
            ("stat_cleaned", "Rooms cleaned"),
            ("stat_moves",   "Moves made"),
            ("stat_steps",   "Total steps"),
        ]):
            card = tk.Frame(stats, bg="#F1EFE8", relief="flat", bd=0)
            card.grid(row=0, column=col, padx=(0, 8) if col < 2 else 0, sticky="ew")
            stats.columnconfigure(col, weight=1)
            val_lbl = tk.Label(card, text="0", font=("Helvetica", 20, "bold"),
                               bg="#F1EFE8", fg="#2C2C2A", pady=6)
            val_lbl.pack()
            tk.Label(card, text=lbl_text, font=("Helvetica", 10),
                     bg="#F1EFE8", fg=self.MUTED, pady=(0, 6)).pack()
            setattr(self, val_attr, val_lbl)

    # ── Room card helpers ───────────────────────

    def _build_room_cards(self):
        """Destroy old cards and create fresh ones."""
        for w in self.room_frame.winfo_children():
            w.destroy()
        self.room_cards = []
        n = self.num_rooms.get()

        for i, room in enumerate(self.agent.rooms):
            frame = tk.Frame(self.room_frame, bg=self.DIRTY_BG if room["state"] == "dirty" else self.CLEAN_BG,
                             relief="solid", bd=2)
            frame.pack(side="left", expand=True, fill="both",
                       padx=(0, 8) if i < n - 1 else 0)

            # "AGENT HERE" badge (hidden by default)
            badge = tk.Label(frame, text="⬇  AGENT", bg=self.AGENT_BD, fg="white",
                             font=("Helvetica", 9, "bold"), padx=6, pady=2)

            name_lbl  = tk.Label(frame, text=f"Room {room['name']}",
                                 font=("Helvetica", 10), bg=self.DIRTY_BG, fg=self.MUTED, pady=(8, 0))
            name_lbl.pack()

            icon_lbl  = tk.Label(frame, text="🗑", font=("Helvetica", 24), bg=self.DIRTY_BG, pady=4)
            icon_lbl.pack()

            state_lbl = tk.Label(frame, text="Dirty", font=("Helvetica", 11, "bold"),
                                 bg=self.DIRTY_BG, fg=self.DIRTY_TXT, pady=(0, 8))
            state_lbl.pack()

            self.room_cards.append({
                "frame": frame, "badge": badge,
                "name": name_lbl, "icon": icon_lbl, "state": state_lbl,
            })

        self._refresh_room_cards()

    def _refresh_room_cards(self):
        """Update every card to match current agent/room state."""
        for i, (room, card) in enumerate(zip(self.agent.rooms, self.room_cards)):
            is_agent = (i == self.agent.position)
            state    = room["state"]

            if is_agent:
                bg, bd, txt = self.AGENT_BG, self.AGENT_BD, self.AGENT_TXT
                icon  = "🤖"
                label = "Agent here"
            elif state == "dirty":
                bg, bd, txt = self.DIRTY_BG, self.DIRTY_BD, self.DIRTY_TXT
                icon  = "🗑"
                label = "Dirty"
            else:
                bg, bd, txt = self.CLEAN_BG, self.CLEAN_BD, self.CLEAN_TXT
                icon  = "✨"
                label = "Clean"

            card["frame"].configure(bg=bg, highlightbackground=bd, bd=2)
            card["name"].configure(bg=bg, fg=self.MUTED)
            card["icon"].configure(bg=bg, text=icon)
            card["state"].configure(bg=bg, fg=txt, text=label)

            if is_agent:
                card["badge"].pack(before=card["name"])
            else:
                card["badge"].pack_forget()

    # ── Log helpers ────────────────────────────

    def _log(self, message, kind="info"):
        tag = {"clean": "clean_tag", "move": "move_tag",
               "done": "done_tag"}.get(kind, "info_tag")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ── Stats update ───────────────────────────

    def _update_stats(self):
        self.stat_cleaned.config(text=str(self.agent.cleaned))
        self.stat_moves.config(text=str(self.agent.moves))
        self.stat_steps.config(text=str(self.agent.steps))
        self.step_lbl.config(text=f"Step {self.agent.steps}")

    # ── Simulation control ─────────────────────

    def _init_simulation(self, randomise=True):
        """Build a fresh agent and environment."""
        n     = self.num_rooms.get()
        pct   = self.dirty_pct.get() / 100
        names = list("ABCDEF")[:n]
        if randomise:
            rooms = [{"name": nm, "state": "dirty" if random.random() < pct else "clean"}
                     for nm in names]
        else:
            rooms = [{"name": nm, "state": "dirty"} for nm in names]

        self.agent = VacuumAgent(rooms)
        self._build_room_cards()
        self._update_stats()

    def _on_config_change(self, _=None):
        """Called when a slider moves; resets the simulation."""
        self._stop_auto()
        self._init_simulation()
        self._clear_log()
        self._log("Configuration changed — simulation reset.", "info")
        self._set_buttons(started=False)

    def _start(self):
        """Run the agent automatically, one step every 800 ms."""
        self._stop_auto()
        if self.agent.finished:
            return
        self._log("▶ Auto-run started…", "info")
        self.btn_start.config(state="disabled")
        self.btn_step.config(state="disabled")
        self._auto_run()

    def _auto_run(self):
        """Recursive after() loop for automatic stepping."""
        if self.agent.finished or self.agent.all_clean():
            self._finish()
            return
        kind, msg = self.agent.step()
        self._log(msg, kind)
        self._refresh_room_cards()
        self._update_stats()
        if kind == "done" or self.agent.finished:
            self._finish()
        else:
            self.auto_id = self.root.after(800, self._auto_run)

    def _manual_step(self):
        """Execute exactly one step when the user clicks 'Next Step'."""
        if self.agent.finished:
            return
        kind, msg = self.agent.step()
        self._log(msg, kind)
        self._refresh_room_cards()
        self._update_stats()
        if kind == "done" or self.agent.finished:
            self._finish()

    def _finish(self):
        """Called when the agent has finished."""
        self.agent.finished = True
        self._log(f"\n🎉 Done! Cleaned {self.agent.cleaned} room(s) "
                  f"in {self.agent.steps} steps ({self.agent.moves} moves).", "done")
        self.btn_start.config(state="disabled")
        self.btn_step.config(state="disabled")
        messagebox.showinfo("All clean!",
                            f"The agent finished!\n\n"
                            f"Rooms cleaned : {self.agent.cleaned}\n"
                            f"Moves made    : {self.agent.moves}\n"
                            f"Total steps   : {self.agent.steps}")

    def _reset(self):
        """Reset everything to a fresh random environment."""
        self._stop_auto()
        self._init_simulation()
        self._clear_log()
        self._log("Simulation reset. Press Start or Next Step.", "info")
        self._set_buttons(started=False)

    def _stop_auto(self):
        """Cancel any running auto-loop."""
        if self.auto_id is not None:
            self.root.after_cancel(self.auto_id)
            self.auto_id = None

    def _set_buttons(self, started=False):
        state = "disabled" if started else "normal"
        self.btn_start.config(state="normal")
        self.btn_step.config(state="normal")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.geometry("680x580")
    root.minsize(500, 480)
    app = VacuumGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
