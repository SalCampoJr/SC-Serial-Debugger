import sys
import os
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import *
import serial.tools.list_ports
import serial
import threading
import time
import webbrowser

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def donothing():
        return

def aboutwindow():
        aboutwin = tk.Toplevel()
        aboutwin.title('About SC Serial Debugger')
        aboutwin.geometry('450x575')
        aboutwin.iconbitmap(resource_path("SCSD.ico"))


        aboutwin.resizable(False, False)
        aboutwin.configure(padx=20, pady=20)

        # Logo placeholder
        try:
            Slogo_img = tk.PhotoImage(file=resource_path("SCSD icon.png"))
            logo_img = logo_img.subsample(4, 4)
            logo_lbl = ttk.Label(aboutwin, image=logo_img)
            logo_lbl.image = logo_img    # keep reference
            logo_lbl.pack(pady=(0, 15))
        except Exception:
            # silent fail if image not found
            pass

        # App info
        ttk.Label(aboutwin, text="SC Serial Debugger",
                font=("Bahnschrift", 18, "bold")).pack()
        ttk.Label(aboutwin, text="Version 1.0").pack(pady=(5, 0))
        ttk.Label(aboutwin, text="© 2025 Salvatore Campo")\
            .pack(pady=(0, 20))

        # Divider
        ttk.Separator(aboutwin, orient="horizontal")\
            .pack(fill="x", pady=10)

        # About the Author
        ttk.Label(aboutwin, text="About the Author",
                font=("Baskerville Old face", 14, "underline")).pack()
        author_text = (
            "Salvatore Campo is an Electrical engineer and hardware enthusiast. "
            "He’s passionate about using technology to make a positive impact on society. Albeit small, this projects serves the purpose of a minimalist program that does exactly what it needs to do. "
        )
        ttk.Label(aboutwin, text=author_text,
                wraplength=360, justify="center").pack(pady=10)

        # Links section
        links_frame = ttk.Frame(aboutwin)
        links_frame.pack(pady=10)

        def make_link(text, url):
            lbl = ttk.Label(links_frame, text=text,
                            foreground="blue", cursor="hand2",
                            font=("Arial", 10, "underline"))
            lbl.pack(anchor="center", pady=2)
            lbl.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        make_link("Personal Portfolio", "https://salvatore-campo.web.app/")
        make_link("LinkedIn Profile",   "https://www.linkedin.com/in/salvatore-campo/")
        make_link("GitHub Repository",  "https://github.com/SalCampoJr/SC-Serial-Debugger.git")

        # Close button
        ttk.Button(aboutwin, text="Close", style="Custom.TButton",
                command=aboutwin.destroy).pack(pady=10)


def add_menubar(window):
    """Attach a File/Help menubar to any tk.Tk or tk.Toplevel."""
    menu = tk.Menu(window)

    # File menu
    file_menu = tk.Menu(menu, tearoff=False)
    file_menu.add_command(label="Exit", command=window.quit)
    menu.add_cascade(label="File", menu=file_menu)

    # Help menu
    help_menu = tk.Menu(menu, tearoff=False)
    help_menu.add_command(label="About...",    command= aboutwindow)
    menu.add_cascade(label="Help", menu=help_menu)

    window.config(menu=menu)

    

class SerialMonitorApp:
    

    def __init__(self, master):
        #Setup start window
        self.master = master
        master.title('SC Serial Debugger')
        master.geometry('350x250')
        master.resizable(False, False)


        add_menubar(master)

        style = ttk.Style("flatly")  
        style.configure("Custom.TButton",
                foreground="white",
                background="#13472e")
        style.map("Custom.TButton",
          background=[("active", "#17613c"), ("pressed", "#0f3d25")])



        self.serial_port = None
        self.serial_thread = None
        self.stop_event = threading.Event()

        #port label
        self.port_label = ttk.Label(master, text="Select Port:")
        self.port_label.pack(pady=5)

        #port select
        self.port_combobox = ttk.Combobox(master, values=self.get_available_ports())
        self.port_combobox.pack(pady=5)
        self.port_combobox.set("Select a port")
        self.port_combobox.config(postcommand=lambda: self.update_combobox_ports(self.port_combobox))

        #baud label
        self.baud_label = ttk.Label(master, text="Baud Rate:")
        self.baud_label.pack(pady=5)

        #baud select
        self.baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        self.baud_combobox = ttk.Combobox(master, values=self.baud_rates)
        self.baud_combobox.pack(pady=5)
        self.baud_combobox.set("9600")

        #start menu
        ttk.Button(master, text="Open Serial Monitor",
           style="Custom.TButton", command=self.open_serial_monitor).pack(pady=10)

    def get_available_ports(self):
        try:
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            tk.messagebox.showerror("Port Scan Error", f"Could not retrieve available ports:\n{e}")
        return []
    
    def update_combobox_ports(self,combobox):
        available_ports = self.get_available_ports()
        combobox['values'] = available_ports


    def open_serial_monitor(self):
        port = self.port_combobox.get()
        baud_rate = int(self.baud_combobox.get())

        if not port or port == "Select a port":
            tk.messagebox.showerror("Error", "Please select a serial port.")
            return

        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=0.1) #
            self.start_serial_read_thread()
            self.show_serial_monitor_window()
            self.serial_port.reset_input_buffer()
        except serial.SerialException as e:
            tk.messagebox.showerror("Error", f"Could not open serial port: {e}")

    def start_serial_read_thread(self):
        self.stop_event.clear()
        self.serial_thread = threading.Thread(target=self.read_from_serial) #
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_from_serial(self):
        while not self.stop_event.is_set():
            try:
                raw = self.serial_port.readline()
                if raw:
                    data = raw.decode('utf-8').strip()
                    if data:
                        self.update_serial_monitor(data)
            except UnicodeDecodeError:
                print("Received unreadable bytes. Skipping...")
            except serial.SerialException as e:
                self.stop_event.set()
                if hasattr(self, 'monitor_status_label'):
                    self.monitor_status_label.config(text="Disconnected", foreground="red")
                tk.messagebox.showerror("Serial Read Error", f"Lost connection to serial port:\n{e}")
                break
            except Exception as e:
                print(f"Unhandled error: {e}")
            time.sleep(0.01)



    def update_serial_monitor(self, data):
       
        pass 

    def show_serial_monitor_window(self):
        monitor_window = tk.Toplevel(self.master) #
        monitor_window.title(f"Serial Monitor - {self.serial_port.name}")
        monitor_window.geometry("600x400")
        monitor_window.iconbitmap(resource_path("SCSD.ico")) 

        add_menubar(monitor_window)

        self.monitor_status_label = ttk.Label(monitor_window, text="Connected", foreground="green")
        self.monitor_status_label.pack(pady=(5, 0))


        # Text widget to display serial data
        text_widget = tk.Text(monitor_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Scrollbar for the text widget
        scrollbar = ttk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)

        input_frame = ttk.Frame(monitor_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        entry = ttk.Entry(input_frame)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        history = []        # stores sent commands
        hist_index = [0]    # mutable index (one-past-last after send)

        
        def send_from_entry(event=None):
            cmd = entry.get()
            if not cmd:
                return

            def attempt_send():
                sent_successfully = threading.Event()

                def try_write():
                    try:
                        if self.serial_port and self.serial_port.is_open:
                            self.serial_port.write((cmd + "\n").encode("utf-8"))
                            sent_successfully.set()
                    except Exception:
                        pass  # Silent failure

                send_thread = threading.Thread(target=try_write)
                send_thread.start()
                send_thread.join(timeout=5)

                # Simulate response no matter what
                update_text_widget(f">> {cmd}")
                if not sent_successfully.is_set():
                    update_text_widget(f"[Simulated: No response received]")
            
            threading.Thread(target=attempt_send).start()

            history.append(cmd)
            hist_index[0] = len(history)
            entry.delete(0, tk.END)



        send_btn = ttk.Button(input_frame, text="Send", style="Custom.TButton", command=send_from_entry)
        send_btn.pack(side=tk.RIGHT)

        def on_up(event):
            if history and hist_index[0] > 0:
                hist_index[0] -= 1
                entry.delete(0, tk.END)
                entry.insert(0, history[hist_index[0]])
            return "break"

        def on_down(event):
            if history and hist_index[0] < len(history) - 1:
                hist_index[0] += 1
                entry.delete(0, tk.END)
                entry.insert(0, history[hist_index[0]])
            else:
                hist_index[0] = len(history)
                entry.delete(0, tk.END)
            return "break"


        entry.bind("<Return>", send_from_entry)
        entry.bind("<Up>",   on_up)   # ← new
        entry.bind("<Down>", on_down) # ← new


        # Function to update the text widget 
        def update_text_widget(data):
            text_widget.insert(tk.END, data + "\n")
            text_widget.see(tk.END) # Auto-scroll to the end

        self.update_serial_monitor = update_text_widget # Update the method in the class instance

        def on_close():
            self.stop_serial_read_thread()
            monitor_window.destroy()

        monitor_window.protocol("WM_DELETE_WINDOW", on_close)

    def stop_serial_read_thread(self):
        if self.serial_thread and self.serial_thread.is_alive():
            self.stop_event.set()
            self.serial_thread.join(timeout=1) # Wait for the thread to finish
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        if hasattr(self, 'monitor_status_label'):
            self.monitor_status_label.config(text="Disconnected", foreground="red")



def main():
    root = tk.Tk()
    root.iconbitmap(resource_path("SCSD.ico"))
    app = SerialMonitorApp(root)
 
    def on_main_close():
        app.stop_serial_read_thread()  # Ensure cleanup
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_main_close)
    root.mainloop()


if __name__ == "__main__":
    main()