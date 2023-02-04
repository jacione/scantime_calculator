import tkinter as tk
import tkinter.ttk as ttk


DEFAULT_READTIME = 0.01
DEFAULT_MOVETIME = 45
DEFAULT_ALIGNTIME = 45


grid_options = {'padx': 5, 'pady': 5}
ctr_label = {'font': ('Arial', 14), 'anchor': tk.CENTER}
lft_label = {'font': ('Arial', 14), 'anchor': tk.W}
entry_options = {'width': 10, 'font': ('Arial', 14), 'justify': tk.CENTER}


class Scan:
    def __init__(self):
        self.peaks = tk.IntVar()
        self.pts = tk.IntVar()
        self.exp = tk.DoubleVar()
        self.accs = tk.IntVar()
        self.reps = tk.IntVar()
        self.time = tk.DoubleVar()
        self.time_str = tk.StringVar()
        self.read = 0.0
        self.move = 0.0
        self.align = 0.0

        for var in [self.peaks, self.pts, self.exp, self.accs, self.reps]:
            var.trace("w", callback=self.calculate)

        self.calculate()

    def calculate(self, *_):
        try:
            self.time.set(self.peaks.get()
                          * ((((self.pts.get() + 1)
                               * (self.exp.get()+self.read)
                               * self.accs.get()
                               + self.align)
                              * self.reps.get())
                             + self.move)
                          )
            self.time_str.set(f"{round(self.time.get()//3600)}h {round((self.time.get()%3600)//60)}m")
        except tk.TclError:
            self.time.set(0.0)
            self.time_str.set("")


class App:
    def __init__(self):
        root = tk.Tk()
        root.title("Merry Christmas from Nick")

        row = 0
        ttk.Label(root, text="Overhead (in seconds)", **lft_label
                  ).grid(column=0, row=row, columnspan=3, **grid_options, sticky=tk.W)

        self.readtime = tk.DoubleVar(value=DEFAULT_READTIME)
        row += 1
        ttk.Label(root, text="Readout", **lft_label).grid(column=0, row=row, **grid_options)
        ttk.Entry(root, textvariable=self.readtime, **entry_options).grid(column=1, row=row, **grid_options)

        self.movetime = tk.IntVar(value=DEFAULT_MOVETIME)
        row += 1
        ttk.Label(root, text="Motion", **lft_label).grid(column=0, row=row, **grid_options)
        ttk.Entry(root, textvariable=self.movetime, **entry_options).grid(column=1, row=row, **grid_options)

        self.aligntime = tk.IntVar(value=DEFAULT_ALIGNTIME)
        row += 1
        ttk.Label(root, text="Alignment", **lft_label).grid(column=0, row=row, **grid_options)
        ttk.Entry(root, textvariable=self.aligntime, **entry_options).grid(column=1, row=row, **grid_options)

        for overhead in [self.readtime, self.movetime, self.aligntime]:
            overhead.trace("w", self.update_overheads)

        row += 1
        ttk.Separator(root, orient="horizontal"
                      ).grid(column=0, row=row, columnspan=6, **grid_options, sticky=tk.EW)

        row += 1
        ttk.Label(root, text="# of peaks", **ctr_label).grid(column=0, row=row, **grid_options)
        ttk.Label(root, text="Scan points", **ctr_label).grid(column=1, row=row, **grid_options)
        ttk.Label(root, text="Exposure", **ctr_label).grid(column=2, row=row, **grid_options)
        ttk.Label(root, text="Accum.", **ctr_label).grid(column=3, row=row, **grid_options)
        ttk.Label(root, text="Repetitions", **ctr_label).grid(column=4, row=row, **grid_options)
        ttk.Label(root, text="Time", **ctr_label).grid(column=5, row=row, **grid_options)

        self.time = 0.0
        self.time_str = tk.StringVar()

        self.scans = [Scan() for _ in range(4)]
        for scan in self.scans:
            row += 1
            ttk.Entry(root, textvariable=scan.peaks, **entry_options).grid(column=0, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.pts, **entry_options).grid(column=1, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.exp, **entry_options).grid(column=2, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.accs, **entry_options).grid(column=3, row=row, **grid_options)
            ttk.Entry(root, textvariable=scan.reps, **entry_options).grid(column=4, row=row, **grid_options)
            ttk.Label(root, textvariable=scan.time_str, **ctr_label).grid(column=5, row=row, **grid_options)
            scan.time.trace("w", callback=self.calculate_total)

        row += 1
        ttk.Separator(root, orient="horizontal"
                      ).grid(column=0, row=row, columnspan=6, **grid_options, sticky=tk.EW)

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
        self.time = sum([scan.time.get() for scan in self.scans])
        self.time_str.set(f"Total time: {round(self.time//3600)}hrs, {round((self.time%3600)//60)}min")


if __name__ == "__main__":
    App()
