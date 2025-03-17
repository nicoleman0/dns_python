import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from query import query_dns as query
import threading


class DNSpyGUI:
    def __init__(self, master):
        self.master = master
        master.title("DNSpy")

        self.target_label = tk.Label(
            master, text="Target Domain:", font="Calibri 12 bold")
        self.target_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.target_entry = tk.Entry(master, width=30)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5)

        # Options Frame
        self.options_frame = ttk.LabelFrame(master, text="Options")
        self.options_frame.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Verbose Output Checkbox
        self.verbose_var = tk.BooleanVar()
        self.verbose_var.set(False)
        self.verbose_checkbox = ttk.Checkbutton(
            self.options_frame, text="Verbose Output", variable=self.verbose_var
        )
        self.verbose_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Record Types Checkboxes
        self.record_types_label = tk.Label(
            self.options_frame, text="Record Types:", font="Calibri 10")
        self.record_types_label.grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]
        self.record_vars = {}
        for i, record in enumerate(self.record_types):
            self.record_vars[record] = tk.BooleanVar()
            self.record_vars[record].set(True)  # Set all to checked by default
            checkbox = ttk.Checkbutton(
                self.options_frame,
                text=record,
                variable=self.record_vars[record],
            )
            checkbox.grid(row=2 + (i // 4), column=i %
                          4, padx=5, pady=2, sticky="w")

        self.enumerate_button = tk.Button(
            master, text="Run", font="Calibri 10 bold", command=self.start_enumeration
        )
        self.enumerate_button.grid(
            row=3, column=0, columnspan=2, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, width=60, height=20
        )
        self.output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)

    def start_enumeration(self):
        target = self.target_entry.get()
        if not target:
            self.update_output("Please enter a target domain.")
            return

        self.update_output(f"Starting DNS Enumeration for {target}\n")
        self.enumerate_button.config(state=tk.DISABLED)
        # Run enumeration in a separate thread to prevent GUI from freezing
        threading.Thread(target=self.run_enumeration, args=(target,)).start()

    def run_enumeration(self, target):
        try:
            selected_records = [
                record
                for record, var in self.record_vars.items()
                if var.get()
            ]
            if not selected_records:
                self.update_output("No record types selected.")
                return

            for record in selected_records:
                if self.verbose_var.get():
                    self.update_output(f"Querying {record} records")
                data = query(target, record)
                if not data:
                    if self.verbose_var.get():
                        self.update_output(f"No records found for {record}")
                else:
                    for item in data:
                        self.update_output(item)
                self.update_output("\n")
        except Exception as e:
            self.update_output(f"An error occurred: {e}")
        finally:
            self.enumerate_button.config(state=tk.NORMAL)

    def update_output(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)  # Scroll to the bottom


def main():
    root = tk.Tk()
    gui = DNSpyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
