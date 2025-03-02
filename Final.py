import threading
import queue
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil

# Define a global message queue for Inter-Process Communication (IPC)
message_queue = queue.Queue()

# Data storage for graphs
cpu_usage_data = []
memory_usage_data = []
battery_data = []
network_data = []
process_names = []
cpu_percents = []
memory_percents = []
time_stamps = []

# Task 1: Fetches real-time CPU usage
def cpu_usage_fetcher():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1, percpu=True)  # Real-time CPU cores usage
        message_queue.put(f"CPU Usage: {cpu_usage}")
        cpu_usage_data.append(cpu_usage)
        time_stamps.append(len(cpu_usage_data))
        update_gui(f"CPU Usage: {cpu_usage}")
        time.sleep(2)

# Task 2: Fetches real-time Memory usage
def memory_usage_fetcher():
    while True:
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent  # Real-time Memory usage
        message_queue.put(f"Memory Usage: {memory_usage}%")
        memory_usage_data.append(memory_usage)
        update_gui(f"Memory Usage: {memory_usage}%")
        time.sleep(3)

# Task 3: Fetches real-time Battery status
def battery_status_fetcher():
    while True:
        battery = psutil.sensors_battery()
        if battery:
            battery_status = battery.percent  # Real-time Battery status
            message_queue.put(f"Battery Status: {battery_status}%")
            battery_data.append(battery_status)
            update_gui(f"Battery Status: {battery_status}%")
        else:
            update_gui("Battery Status: Not Available")
        time.sleep(4)

# Task 4: Fetches real-time Network activity
def network_activity_fetcher():
    old_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    while True:
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        network_activity = new_value - old_value  # Real-time Network activity
        old_value = new_value
        message_queue.put(f"Network Activity: {network_activity} bytes")
        network_data.append(network_activity)
        update_gui(f"Network Activity: {network_activity} bytes")
        time.sleep(5)

# Task 5: Fetches real-time top processes by CPU and Memory usage
def task_manager_fetcher():
    while True:
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
        process_names.clear()
        cpu_percents.clear()
        memory_percents.clear()
        for proc in processes:
            process_names.append(proc.info['name'])
            cpu_percents.append(proc.info['cpu_percent'])
            memory_percents.append(proc.info['memory_percent'])
        message_queue.put("Task Manager Updated")
        update_gui("Task Manager Updated")
        time.sleep(6)

# GUI Update Function
def update_gui(message):
    global log_text
    timestamp = time.strftime("%H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text.see(tk.END)

# Error handling function
def show_error(message):
    messagebox.showerror("Error", message)

# Graphical Display
def setup_gui():
    global root, log_text, cpu_ax, memory_ax, battery_ax, network_ax, task_ax

    root = tk.Tk()
    root.title("Enhanced Embedded OS Simulation")
    root.geometry("1200x800")
    root.config(bg="#2e3b47")  # Dark background for better contrast

    frame = tk.Frame(root, bg="#2e3b47")
    frame.pack(pady=10, padx=10)

    # Log Display
    log_label = tk.Label(frame, text="System Log:", fg="white", bg="#2e3b47", font=("Arial", 12, "bold"))
    log_label.pack(anchor="w")

    log_text = scrolledtext.ScrolledText(frame, height=15, width=60, wrap=tk.WORD, font=("Courier", 10), bg="#2b2b2b", fg="white")
    log_text.pack(pady=5)

    # Graph Area
    graph_label = tk.Label(frame, text="Graphical Representations:", fg="white", bg="#2e3b47", font=("Arial", 12, "bold"))
    graph_label.pack(anchor="w", pady=5)

    fig = Figure(figsize=(12, 8), dpi=100)
    
    cpu_ax = fig.add_subplot(321)
    cpu_ax.set_title("CPU Cores Usage", fontsize=14)
    cpu_ax.set_xlabel("Time (s)", fontsize=12)
    cpu_ax.set_ylabel("Usage (%)", fontsize=12)

    memory_ax = fig.add_subplot(322)
    memory_ax.set_title("Memory Usage", fontsize=14)
    memory_ax.set_xlabel("Time (s)", fontsize=12)
    memory_ax.set_ylabel("Memory Usage (%)", fontsize=12)

    battery_ax = fig.add_subplot(323)
    battery_ax.set_title("Battery Status", fontsize=14)
    battery_ax.set_xlabel("Time (s)", fontsize=12)
    battery_ax.set_ylabel("Battery Status (%)", fontsize=12)

    network_ax = fig.add_subplot(324)
    network_ax.set_title("Network Activity", fontsize=14)
    network_ax.set_xlabel("Time (s)", fontsize=12)
    network_ax.set_ylabel("Activity (bytes)", fontsize=12)

    task_ax = fig.add_subplot(325)
    task_ax.set_title("Top Processes", fontsize=14)
    task_ax.set_xlabel("Processes", fontsize=12)
    task_ax.set_ylabel("Usage (%)", fontsize=12)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()

    def update_graph():
        # Update the graphs with dynamic scaling
        if cpu_usage_data:
            cpu_ax.clear()
            for i, core_usage in enumerate(zip(*cpu_usage_data)):
                cpu_ax.plot(time_stamps, core_usage, label=f"Core {i + 1}")
            cpu_ax.set_title("CPU Cores Usage")
            cpu_ax.set_xlabel("Time (s)")
            cpu_ax.set_ylabel("Usage (%)")
            cpu_ax.legend()

        if memory_usage_data:
            memory_ax.clear()
            memory_ax.plot(time_stamps[:len(memory_usage_data)], memory_usage_data, label="Memory Usage", color="orange")
            memory_ax.set_title("Memory Usage")
            memory_ax.set_xlabel("Time (s)")
            memory_ax.set_ylabel("Memory Usage (%)")
            memory_ax.legend()

        if battery_data:
            battery_ax.clear()
            battery_ax.plot(time_stamps[:len(battery_data)], battery_data, label="Battery Status", color="yellow")
            battery_ax.set_title("Battery Status")
            battery_ax.set_xlabel("Time (s)")
            battery_ax.set_ylabel("Battery Status (%)")
            battery_ax.legend()

        if network_data:
            network_ax.clear()
            network_ax.plot(time_stamps[:len(network_data)], network_data, label="Network Activity", color="blue")
            network_ax.set_title("Network Activity")
            network_ax.set_xlabel("Time (s)")
            network_ax.set_ylabel("Activity (bytes)")
            network_ax.legend()

        if process_names and cpu_percents and memory_percents:
            task_ax.clear()
            task_ax.barh(process_names, cpu_percents, label="CPU Usage (%)", color="red")
            task_ax.barh(process_names, memory_percents, label="Memory Usage (%)", color="green", left=cpu_percents)
            task_ax.set_title("Top Processes")
            task_ax.set_xlabel("Usage (%)")
            task_ax.set_ylabel("Processes")
            task_ax.legend()

        canvas.draw()
        root.after(2000, update_graph)

    update_graph()

    return root

# Main Scheduler
def main_scheduler():
    # Create threads for each task
    task1 = threading.Thread(target=cpu_usage_fetcher, daemon=True)
    task2 = threading.Thread(target=memory_usage_fetcher, daemon=True)
    task3 = threading.Thread(target=battery_status_fetcher, daemon=True)
    task4 = threading.Thread(target=network_activity_fetcher, daemon=True)
    task5 = threading.Thread(target=task_manager_fetcher, daemon=True)

    # Start the tasks
    task1.start()
    task2.start()
    task3.start()
    task4.start()
    task5.start()

    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("Starting Enhanced Embedded Operating System Simulation...")
    root = setup_gui()
    main_scheduler()