import psutil
import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess,platform,re


# Global variables
notification_interval = 5  # Default interval is 5 minutes
tracking = False
connection = False

#________________________________________________________________________________________________


def get_wifi_ssid():
    global connection
    if platform.system() == "Windows":
        cmd = 'netsh wlan show interfaces'
    else:
        return "Only Windows operating system is supported"
    
    try:
        ssid_output = subprocess.check_output(cmd, shell=True, text=True)
        ssid_output =ssid_output.replace(" ","")
        wifi_name = re.search(r'SSID:(.*?)(?:\s|\n)', ssid_output).group(1)
        connection_status.config(text=f"Connected To: {wifi_name}",background="black",foreground="yellow")
        if not connection:
            connection=True
            tracking_Status.config(text="Not Tracking")
        

    except Exception as e:
        connection=False
        tracking_Status.config(text="Please Connect to a Network",foreground="red")
        connection_status.config(text="Not Connected",background="white",foreground="black")

    connection_status.after(2000,get_wifi_ssid)


def messagebox(title, message, background_color="#008000", width=470, height=100):
    notification_window = tk.Toplevel()
    notification_window.title(title)
    
    # Set the background color
    notification_window.configure(bg=background_color)
    
    # Use a custom style for the notification window
    style = ttk.Style()
    style.configure("Custom.TLabel", background="yellow", font=("Arial", 14, "bold"))
    
    notification_label = ttk.Label(notification_window, text=message, style="Custom.TLabel")
    notification_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Center the notification window on the screen and set its size
    screen_width = notification_window.winfo_screenwidth()
    screen_height = notification_window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    notification_window.geometry(f"{width}x{height}+{x}+{y}")
    
    notification_window.after(3000, notification_window.destroy)  # Close after 3 seconds (3000 milliseconds)
    notification_window.attributes("-topmost", True)  # Set the window to be always on top





def toggle():
    global tracking

    if tracking and connection:
        tracking = False
        tracking_Status.config(text="Tracking Stopped!",foreground="red")

    elif not connection:
        tracking_Status.config(text="Can't Track. No Network Connected!")
        
        
    else:
        tracking = True
        tracking_Status.config(text="Tracking...",foreground="darkgreen")
        start_monitoring()




def calculate_data_usage():
    global notification_interval, tracking
    while tracking:
        start_network_usage = psutil.net_io_counters()
        start_bytes_sent = start_network_usage.bytes_sent
        start_bytes_received = start_network_usage.bytes_recv
        time.sleep(notification_interval * 60)
        if tracking:
            end_network_usage = psutil.net_io_counters()
            end_bytes_sent = end_network_usage.bytes_sent
            end_bytes_received = end_network_usage.bytes_recv
            data_usage_interval_mb = ((end_bytes_sent - start_bytes_sent) + (end_bytes_received - start_bytes_received)) / (1024 * 1024)
            title = "Data Usage"
            message = f"Data used in the last {notification_interval} minutes: {data_usage_interval_mb:.2f} MB"
            messagebox(title,message)



def start_monitoring():
    global notification_interval
    notification_interval = int(notification_interval_var.get())
    monitoring_thread = threading.Thread(target=calculate_data_usage)
    monitoring_thread.daemon = True
    monitoring_thread.start()



root = tk.Tk()
root.title("Data Usage Monitor")
root.config(bg="yellow")

window_width = 400
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")


label1 = ttk.Label(root, text="Set your notification Interval(minutes):",background="yellow",foreground="green",font=("Arial", 11, "bold"))
label1.pack(pady=10)

tracking_Status = ttk.Label(root,background="yellow",foreground="red",font=("Arial", 11, "bold"))
tracking_Status.pack(pady=10)

style = ttk.Style()
style.configure("Custom.TCombobox", padding=5, background="lightgray", width=10, relief="flat", font=("Helvetica", 9))

notification_interval_var = tk.StringVar()
notification_interval_combobox = ttk.Combobox(root, textvariable=notification_interval_var, values=[1,2,5, 10, 15, 30, 45, 60],style="Custom.TCombobox")
notification_interval_combobox.set(5)
notification_interval_combobox.pack()



connection_status = ttk.Label(root,text="Searching...",font=("Arial", 9, "bold"))
connection_status.pack(pady=5)

button = tk.Button(root, text="Track", command=toggle, 
                  bg="green",
                  fg="white",  # Text color
                  font=("Helvetica", 9, "bold"),  # Font settings
                  relief="raised",  # Border style
                  borderwidth=5,
                  activebackground="green",
                  activeforeground="yellow"
                 )



button.pack(pady=10)



get_wifi_ssid()
root.mainloop()


