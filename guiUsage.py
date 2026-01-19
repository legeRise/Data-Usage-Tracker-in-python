import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import subprocess
import platform
import re
from collections import defaultdict
from datetime import datetime


# Global variables
notification_interval = 5  # Default interval is 5 minutes
tracking = False
connection = False
process_data = {}
last_connections = {}

#________________________________________________________________________________________________


def get_wifi_ssid():
    """Get WiFi SSID for Linux systems"""
    global connection
    
    try:
        # Try nmcli first (NetworkManager)
        cmd = 'nmcli -t -f active,ssid dev wifi | grep "^yes"'
        ssid_output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        wifi_name = ssid_output.split(':')[1].strip()
        
        if wifi_name:
            connection_status.config(text=f"Connected To: {wifi_name}", background="#2c3e50", foreground="#2ecc71")
            if not connection:
                connection = True
                tracking_Status.config(text="Not Tracking", foreground="#e67e22")
            return
    except:
        pass
    
    try:
        # Fallback to iwgetid
        cmd = 'iwgetid -r'
        wifi_name = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        
        if wifi_name:
            connection_status.config(text=f"Connected To: {wifi_name}", background="#2c3e50", foreground="#2ecc71")
            if not connection:
                connection = True
                tracking_Status.config(text="Not Tracking", foreground="#e67e22")
            return
    except:
        pass
    
    # Check if any network interface is up (Ethernet or WiFi)
    try:
        cmd = "ip link show | grep 'state UP'"
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        if result:
            connection_status.config(text="Network Connected", background="#2c3e50", foreground="#2ecc71")
            if not connection:
                connection = True
                tracking_Status.config(text="Not Tracking", foreground="#e67e22")
            return
    except:
        pass
    
    # No connection found
    connection = False
    tracking_Status.config(text="Please Connect to a Network", foreground="#e74c3c")
    connection_status.config(text="Not Connected", background="#ecf0f1", foreground="#e74c3c")
    
    connection_status.after(3000, get_wifi_ssid)


def get_process_network_usage():
    """Get network usage per process using ss command"""
    process_stats = defaultdict(lambda: {'sent': 0, 'recv': 0, 'name': 'Unknown'})
    
    try:
        # Use ss to get socket statistics with process info
        cmd = "ss -tunap 2>/dev/null | grep -v 'State'"
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        
        for line in output.split('\n'):
            if 'users:' in line:
                # Extract process info
                match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', line)
                if match:
                    proc_name = match.group(1)
                    pid = int(match.group(2))
                    process_stats[pid]['name'] = proc_name
    except:
        pass
    
    return process_stats


def update_process_list():
    """Update the process list display with network usage"""
    if not tracking:
        return
    
    try:
        # Get current connections
        connections = psutil.net_connections(kind='inet')
        current_processes = defaultdict(lambda: {'connections': 0, 'name': 'Unknown'})
        
        for conn in connections:
            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    proc_name = proc.name()
                    current_processes[conn.pid]['name'] = proc_name
                    current_processes[conn.pid]['connections'] += 1
                except:
                    pass
        
        # Update the text widget
        process_text.config(state='normal')
        process_text.delete('1.0', tk.END)
        process_text.insert('1.0', f"{'Process':<25} {'PID':<8} {'Connections':<12}\n")
        process_text.insert('2.0', "="*50 + "\n")
        
        # Sort by number of connections
        sorted_procs = sorted(current_processes.items(), key=lambda x: x[1]['connections'], reverse=True)
        
        for pid, info in sorted_procs[:15]:  # Show top 15
            line = f"{info['name']:<25} {pid:<8} {info['connections']:<12}\n"
            process_text.insert(tk.END, line)
        
        process_text.config(state='disabled')
        
    except Exception as e:
        pass
    
    if tracking:
        root.after(2000, update_process_list)


def messagebox(title, message, background_color="#27ae60", width=500, height=150):
    """Show notification window with modern styling"""
    notification_window = tk.Toplevel()
    notification_window.title(title)
    notification_window.configure(bg=background_color)
    notification_window.overrideredirect(True)  # Remove window decorations
    
    # Create frame with border
    frame = tk.Frame(notification_window, bg=background_color, highlightbackground="#2c3e50", 
                     highlightthickness=2)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Title label
    title_label = tk.Label(frame, text=title, bg=background_color, fg="white", 
                          font=("Arial", 12, "bold"))
    title_label.pack(pady=(10, 5))
    
    # Message label
    message_label = tk.Label(frame, text=message, bg=background_color, fg="white", 
                           font=("Arial", 10), wraplength=450)
    message_label.pack(pady=(5, 10), padx=20)
    
    # Close button
    close_btn = tk.Button(frame, text="✕", command=notification_window.destroy,
                         bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                         relief="flat", cursor="hand2")
    close_btn.place(x=width-30, y=5, width=25, height=25)
    
    # Position at top-right corner
    screen_width = notification_window.winfo_screenwidth()
    x = screen_width - width - 20
    y = 20
    
    notification_window.geometry(f"{width}x{height}+{x}+{y}")
    notification_window.after(5000, notification_window.destroy)
    notification_window.attributes("-topmost", True)





def toggle():
    global tracking

    if tracking and connection:
        tracking = False
        tracking_Status.config(text="Tracking Stopped!", foreground="#e74c3c")
        button.config(text="Start Tracking", bg="#27ae60")

    elif not connection:
        tracking_Status.config(text="Can't Track. No Network Connected!", foreground="#e74c3c")
    else:
        tracking = True
        tracking_Status.config(text="Tracking...", foreground="#27ae60")
        button.config(text="Stop Tracking", bg="#e74c3c")
        start_monitoring()
        update_process_list()




def calculate_data_usage():
    global notification_interval, tracking
    while tracking:
        start_network_usage = psutil.net_io_counters()
        start_bytes_sent = start_network_usage.bytes_sent
        start_bytes_received = start_network_usage.bytes_recv
        start_time = datetime.now()
        
        time.sleep(notification_interval * 60)
        
        if tracking:
            end_network_usage = psutil.net_io_counters()
            end_bytes_sent = end_network_usage.bytes_sent
            end_bytes_received = end_network_usage.bytes_recv
            
            sent_mb = (end_bytes_sent - start_bytes_sent) / (1024 * 1024)
            recv_mb = (end_bytes_received - start_bytes_received) / (1024 * 1024)
            total_mb = sent_mb + recv_mb
            
            title = "📊 Data Usage Alert"
            message = f"""Time: {start_time.strftime('%H:%M')} - {datetime.now().strftime('%H:%M')}
            
📤 Uploaded: {sent_mb:.2f} MB
📥 Downloaded: {recv_mb:.2f} MB
📶 Total: {total_mb:.2f} MB"""
            
            # Update the stats label
            total_stats_label.config(text=f"Last interval: {total_mb:.2f} MB (↑{sent_mb:.2f} MB ↓{recv_mb:.2f} MB)")
            
            messagebox(title, message)



def start_monitoring():
    global notification_interval
    notification_interval = int(notification_interval_var.get())
    monitoring_thread = threading.Thread(target=calculate_data_usage)
    monitoring_thread.daemon = True
    monitoring_thread.start()



# Create main window with modern design
root = tk.Tk()
root.title("Network Data Usage Monitor - Linux")
root.config(bg="#ecf0f1")

window_width = 650
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# Header frame
header_frame = tk.Frame(root, bg="#2c3e50", height=60)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

header_label = tk.Label(header_frame, text="📊 Network Usage Monitor", 
                       bg="#2c3e50", fg="white", font=("Arial", 16, "bold"))
header_label.pack(pady=15)

# Connection status frame
status_frame = tk.Frame(root, bg="#ecf0f1")
status_frame.pack(fill=tk.X, padx=20, pady=10)

connection_status = tk.Label(status_frame, text="Searching...", 
                            font=("Arial", 10, "bold"), 
                            bg="#ecf0f1", fg="#2c3e50",
                            relief="solid", borderwidth=1, padx=10, pady=5)
connection_status.pack()

# Control frame
control_frame = tk.Frame(root, bg="#ecf0f1")
control_frame.pack(fill=tk.X, padx=20, pady=10)

label1 = tk.Label(control_frame, text="Notification Interval (minutes):",
                 bg="#ecf0f1", fg="#2c3e50", font=("Arial", 10, "bold"))
label1.pack(pady=5)

notification_interval_var = tk.StringVar()
notification_interval_combobox = ttk.Combobox(control_frame, 
                                             textvariable=notification_interval_var, 
                                             values=[1, 2, 5, 10, 15, 30, 45, 60],
                                             state="readonly", width=15, font=("Arial", 10))
notification_interval_combobox.set(5)
notification_interval_combobox.pack(pady=5)

tracking_Status = tk.Label(control_frame, text="Not Tracking",
                          bg="#ecf0f1", fg="#e67e22", 
                          font=("Arial", 11, "bold"))
tracking_Status.pack(pady=10)

# Button with modern styling
button = tk.Button(control_frame, text="Start Tracking", command=toggle, 
                  bg="#27ae60", fg="white", 
                  font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2",
                  padx=30, pady=10,
                  activebackground="#229954",
                  activeforeground="white")
button.pack(pady=10)

# Stats frame
stats_frame = tk.Frame(root, bg="#ecf0f1")
stats_frame.pack(fill=tk.X, padx=20, pady=5)

total_stats_label = tk.Label(stats_frame, text="No data yet",
                            bg="#ecf0f1", fg="#34495e", 
                            font=("Arial", 9))
total_stats_label.pack()

# Process list frame
process_frame = tk.LabelFrame(root, text="Active Network Processes", 
                             bg="#ecf0f1", fg="#2c3e50",
                             font=("Arial", 10, "bold"),
                             relief="groove", borderwidth=2)
process_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

process_text = scrolledtext.ScrolledText(process_frame, 
                                        height=10, 
                                        bg="#ffffff", 
                                        fg="#2c3e50",
                                        font=("Courier", 9),
                                        relief="flat",
                                        state='disabled')
process_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)



get_wifi_ssid()
root.mainloop()


