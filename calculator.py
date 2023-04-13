import tkinter as tk
import tkinter.ttk as ttk


DEFAULT_READTIME = 0.01
DEFAULT_MOVETIME = 45
DEFAULT_ALIGNTIME = 45


grid_options = {'padx': 3, 'pady': 3}
ctr_label = {'font': ('Arial', 14), 'anchor': tk.CENTER}
lft_label = {'font': ('Arial', 14), 'anchor': tk.W}
entry_options = {'width': 7, 'font': ('Arial', 14), 'justify': tk.CENTER}


TIPS = {
    "readout": "Time spent reading out each frame",
    "motion": "Time spent moving motors from one scan position to the next",
    "align": "Time spent realigning before each scan repetition",
    "scans": "Number of scans to be performed with these parameters",
    "pts": "Number of points to be measured for each scan",
    "exp": "Exposure time (seconds)",
    "acc": "Number of exposures accumulated at each scan point",
    "rep": "Number of times each scan will be repeated",
    "tscan": "Time that will be spent on each scan",
    "trow": "Total time to complete all scans in this row",
    "ttot": "Total time to complete all scans in all rows"
}
LABELS = {
    "readout": "Readout",
    "motion": "Motion",
    "align": "Alignment",
    "scans": "Scans",
    "pts": "Points",
    "exp": "Exp.",
    "acc": "Accum.",
    "rep": "Repeat",
    "tscan": "Scan time",
    "trow": "Total time",
    "ttot": "Overall time"
}


class Scan:
    def __init__(self):
        self.n_peaks = tk.IntVar()
        self.pts = tk.IntVar()
        self.exp = tk.DoubleVar()
        self.accs = tk.IntVar()
        self.reps = tk.IntVar()
        self.scantime = tk.DoubleVar()
        self.scantime_str = tk.StringVar()
        self.peaktime = tk.DoubleVar()
        self.peaktime_str = tk.StringVar()
        self.read = 0.0
        self.move = 0.0
        self.align = 0.0

        for var in [self.n_peaks, self.pts, self.exp, self.accs, self.reps]:
            var.trace("w", callback=self.calculate)

        self.calculate()

    def calculate(self, *_):
        try:
            self.peaktime.set(
                ((((self.pts.get() + 1) * (self.exp.get()+self.read) * self.accs.get() + self.align)
                  * self.reps.get()) + self.move)
            )
            self.peaktime_str.set(f"{round(self.peaktime.get() // 3600)}h {round((self.peaktime.get() % 3600) // 60)}m")
            self.scantime.set(self.n_peaks.get() * self.peaktime.get())
            self.scantime_str.set(f"{round(self.scantime.get() // 3600)}h {round((self.scantime.get() % 3600) // 60)}m")
        except tk.TclError:
            self.scantime.set(0.0)
            self.scantime_str.set("")


class App:
    def __init__(self):
        root = tk.Tk()
        root.title("Merry Christmas from Nick")

        row = 0
        ttk.Label(root, text="Overhead (in seconds)", **lft_label
                  ).grid(column=0, row=row, columnspan=3, **grid_options, sticky=tk.W)

        self.readtime = tk.DoubleVar(value=DEFAULT_READTIME)
        self.movetime = tk.IntVar(value=DEFAULT_MOVETIME)
        self.aligntime = tk.IntVar(value=DEFAULT_ALIGNTIME)

        for key, var in zip(("readout", "motion", "align"), (self.readtime, self.movetime, self.aligntime)):
            row += 1
            label = ttk.Label(root, text=LABELS[key], **lft_label)
            label.grid(column=0, row=row, **grid_options)
            CreateToolTip(label, TIPS[key])
            ttk.Entry(root, textvariable=var, **entry_options).grid(column=1, row=row, **grid_options)

        for overhead in [self.readtime, self.movetime, self.aligntime]:
            overhead.trace("w", self.update_overheads)

        row += 1
        ttk.Separator(root, orient="horizontal"
                      ).grid(column=0, row=row, columnspan=7, **grid_options, sticky=tk.EW)

        row += 1
        for i, key in enumerate(("scans", "pts", "exp", "acc", "rep", "tscan", "trow")):
            label = ttk.Label(root, text=LABELS[key], **ctr_label)
            label.grid(column=i, row=row, **grid_options)
            CreateToolTip(label, TIPS[key])

        self.time = 0.0
        self.time_str = tk.StringVar()

        self.scans = [Scan() for _ in range(4)]
        for scan in self.scans:
            row += 1
            ttk.Entry(root, textvariable=scan.n_peaks, **entry_options).grid(column=0, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.pts, **entry_options).grid(column=1, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.exp, **entry_options).grid(column=2, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.accs, **entry_options).grid(column=3, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.reps, **entry_options).grid(column=4, row=row, **grid_options)
            ttk.Label(root, textvariable=scan.peaktime_str, **ctr_label).grid(column=5, row=row, **grid_options)
            ttk.Label(root, textvariable=scan.scantime_str, **ctr_label).grid(column=6, row=row, **grid_options)
            scan.scantime.trace("w", callback=self.calculate_total)

        row += 1
        ttk.Separator(root, orient="horizontal"
                      ).grid(column=0, row=row, columnspan=7, **grid_options, sticky=tk.EW)

        row += 1
        ttk.Label(root, textvariable=self.time_str, font=("Arial", 20), anchor=tk.W
                  ).grid(column=0, row=row, columnspan=3, **grid_options, sticky=tk.W)
        self.calculate_total()

        root.mainloop()

    def update_overheads(self, *_):
        for scan in self.scans:
            try:
                scan.read = self.readtime.get()
                scan.move = self.movetime.get()
                scan.align = self.aligntime.get()
            except tk.TclError:
                scan.read = 0.0
                scan.move = 0.0
                scan.align = 0.0
            scan.calculate()

    def calculate_total(self, *_):
        self.time = sum([scan.scantime.get() for scan in self.scans])
        self.time_str.set(f"Overall time: {round(self.time//3600)}hrs, {round((self.time%3600)//60)}min")


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #milliseconds
        self.wraplength = 300   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


if __name__ == "__main__":
    App()
