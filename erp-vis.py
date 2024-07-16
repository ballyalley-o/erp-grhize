import os
import csv
import datetime
from tkinter import ttk, Tk, Label, Button, Text, Scrollbar, Frame, filedialog, messagebox
import matplotlib.pyplot as plt
from threading import Thread
import platform

if platform.system() == "Darwin":
    from tkmacosx import Button as MacButton
else:
    MacButton = ttk.Button

def parse_log_file(file_path, log_text):
    component_lengths = []
    coil_lengths = []
    timestamps = []
    component_wastes = []

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row_num, row in enumerate(reader, start=2):
            if len(row) >= 12:
                try:
                    timestamp = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
                    component_length = float(row[11]) / 1000
                    component_waste = float(row[12]) / 1000
                    coil_weight = float(row[5])
                    timestamps.append(timestamp)
                    component_lengths.append(component_length)
                    coil_lengths.append(coil_weight)
                    component_wastes.append(component_waste)
                except (ValueError, IndexError) as e:
                    log_text.insert('end', f"Error in file {file_path}, row {row_num}: {e}\n")
                    log_text.insert('end', f"Row content: {row}\n")
            else:
                log_text.insert('end', f"Row {row_num} has insufficient columns: {row}\n")

    log_text.insert('end', f"Found {len(timestamps)} valid entries in {file_path}\n")
    return timestamps, component_lengths, coil_lengths, component_wastes

def process_logs(directory, log_text):
    all_timestamps = []
    all_component_lengths = []
    all_coil_lengths = []
    all_component_waste = []

    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    log_text.insert('end', f"Found {len(csv_files)} CSV files in the directory\n")

    for filename in csv_files:
        file_path = os.path.join(directory, filename)
        timestamps, component_lengths, coil_lengths, component_wastes = parse_log_file(file_path, log_text)
        all_timestamps.extend(timestamps)
        all_component_lengths.extend(component_lengths)
        all_coil_lengths.extend(coil_lengths)
        all_component_waste.extend(component_wastes)

    if not all_timestamps:
        log_text.insert('end', "No valid data found in any of the CSV files.\n")
        return [], [], [], []

    sorted_data = sorted(zip(all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste))
    all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste = zip(*sorted_data)

    return all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste

def create_graph(timestamps, component_lengths, coil_lengths, component_wastes, log_text):
    if not timestamps:
        log_text.insert('end', "No data to plot.\n")
        return

    fig, ax1 = plt.subplots(figsize=(14, 8))

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Component Length (meters)', color='tab:blue')
    line1 = ax1.plot(timestamps, component_lengths, color='tab:blue', marker='o', linestyle='-', markersize=2, label='Component Length')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Coil Length', color='tab:orange')
    line2 = ax2.plot(timestamps, coil_lengths, color='tab:orange', marker='o', linestyle='-', markersize=2, label='Coil Weight')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    ax1.grid(True, linestyle='--', alpha=0.7)
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.set_ylabel('Component Waste (meters)', color='tab:green')
    line3 = ax3.plot(timestamps, component_wastes, color='tab:green', marker='o', linestyle='-', markersize=2, label='Component Waste')
    ax3.tick_params(axis='y', labelcolor='tab:green')

    plt.title('ERP Log: Component Length and Coil Weight Over Time')

    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower right', bbox_to_anchor=(1, 1.05))

    if coil_lengths:
        initial_coil_length = coil_lengths[0]
        last_coil_length = coil_lengths[-1]
        coil_length_difference = initial_coil_length - last_coil_length

    component_lengths_info = f"Total Components: $\mathbf{{{len(component_lengths)}}}$"
    component_lengths_info += f"\nTotal Length: $\mathbf{{{sum(component_lengths):.2f}}}$ m"
    component_lengths_info += f"\nTotal Waste: $\mathbf{{{sum(component_wastes):.2f}}}$ m"
    component_lengths_info += f"\nAverage Length: $\mathbf{{{sum(component_lengths)/len(component_lengths):.2f}}}$ m"
    component_lengths_info += f"\nAverage Waste: $\mathbf{{{sum(component_wastes)/len(component_lengths):.2f}}}$ m"
    component_lengths_info += f"\nInitial Waste: $\mathbf{{{component_wastes[0]:.3f}}}$ m"
    component_lengths_info += f"\nTotal Length + Waste: $\mathbf{{{sum(component_lengths) + sum(component_wastes):.2f}}}$ m"
    component_lengths_info += f"\n"
    component_lengths_info += f"\nInitial Coil Value: $\mathbf{{{initial_coil_length:.2f}}}$ m"
    component_lengths_info += f"\nCoil Deducted:  $\mathbf{{{coil_length_difference:.2f}}}$ m"
    plt.text(-0.1, 1.1, component_lengths_info, ha='left', va='bottom', transform=ax1.transAxes, fontsize=9, bbox=dict(facecolor='white', alpha=0.5))
    plt.gcf().autofmt_xdate()
    log_summary(timestamps, component_lengths, coil_lengths, component_wastes)
    save_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG Image', '*.png')])
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        log_text.insert('end', f"Graph saved in '{save_path}'\n")
    plt.close()

def select_directory():
    directory = filedialog.askdirectory(title='Select Directory Containing Log Files')
    if directory:
        Thread(target=process_and_plot, args=(directory,)).start()

def log_summary(timestamps, component_lengths, coil_lengths, component_wastes):
    log_text.insert('end', f"Total number of components: {len(component_lengths)}\n")
    log_text.insert('end', f"Total component length: {sum(component_lengths):.2f} meters\n")
    log_text.insert('end', f"Total component waste: {sum(component_wastes):.2f} meters\n")
    log_text.insert('end', f"Average component length: {sum(component_lengths)/len(component_lengths):.2f} meters\n")
    if coil_lengths:
        initial_coil_length = coil_lengths[0]
        last_coil_length = coil_lengths[-1]
        coil_length_difference = initial_coil_length - last_coil_length
        log_text.insert('end', f"Coil length deducted: {coil_length_difference:.2f} meters\n")
    else:
        log_text.insert('end', "No coil length data available.\n")

def process_and_plot(directory):
    global log_text

    timestamps, component_lengths, coil_lengths, component_wastes = process_logs(directory, log_text)
    if timestamps:
        create_graph(timestamps, component_lengths, coil_lengths, component_wastes, log_text)

def main():
    global log_text

    root = Tk()
    root.title("ERP Visualization Tool")

    Label(root, text="ERP Vis", font=("Helvetica", 16)).pack(pady=10)

    Button(root, text="Select Directory", command=select_directory).pack(pady=10)

    log_frame = Frame(root)
    log_frame.pack(pady=10, fill="both", expand=True)

    log_text = Text(log_frame, wrap="word", height=15)
    log_text.pack(side="left", fill="both", expand=True)

    log_scroll = Scrollbar(log_frame, command=log_text.yview)
    log_scroll.pack(side="right", fill="y")

    log_text.config(yscrollcommand=log_scroll.set)

    root.mainloop()

if __name__ == "__main__":
    main()