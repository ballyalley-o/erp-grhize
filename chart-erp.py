import os
import csv
import argparse
import matplotlib.pyplot as plt
import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory

def parse_log_file(file_path):
    component_lengths = []
    coil_lengths = []
    timestamps = []
    component_wastes = []

    print(f"Parsing file: {file_path}")
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
                    print(f"Error in file {file_path}, row {row_num}: {e}")
                    print(f"Row content: {row}")
            else:
                print(f"Row {row_num} has insufficient columns: {row}")

    print(f"Found {len(timestamps)} valid entries in {file_path}")
    return timestamps, component_lengths, coil_lengths, component_wastes

def process_logs(directory):
    all_timestamps = []
    all_component_lengths = []
    all_coil_lengths = []
    all_component_waste = []

    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in the directory")

    for filename in csv_files:
        file_path = os.path.join(directory, filename)
        timestamps, component_lengths, coil_lengths, component_wastes = parse_log_file(file_path)
        all_timestamps.extend(timestamps)
        all_component_lengths.extend(component_lengths)
        all_coil_lengths.extend(coil_lengths)
        all_component_waste.extend(component_wastes)

    if not all_timestamps:
        print("No valid data found in any of the CSV files.")
        return [], [], [], []

    sorted_data = sorted(zip(all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste))
    all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste = zip(*sorted_data)

    return all_timestamps, all_component_lengths, all_coil_lengths, all_component_waste

def create_graph(timestamps, component_lengths, coil_lengths, component_wastes):
    if not timestamps:
        print("No data to plot.")
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
    plt.savefig('erp_visualize.png', bbox_inches='tight')
    plt.close()
    print("Graph saved as 'erp_visualize.png'")

def main():
    root = Tk()
    root.withdraw()
    directory = askdirectory(title='Select Directory Containing Log Files')
    if not directory:
        print("No directory selected.")
        return

    timestamps, component_lengths, coil_lengths, component_wastes = process_logs(directory)

    if not timestamps:
        print("No valid data found in the CSV files.")
        return

    create_graph(timestamps, component_lengths, coil_lengths, component_wastes)

    print(f"Total number of components: {len(component_lengths)}")
    print(f"Total component length: {sum(component_lengths):.2f} meters")
    print(f"Total component waste: {sum(component_wastes):.2f} meters")
    print(f"Average component length: {sum(component_lengths)/len(component_lengths):.2f} meters")
    if coil_lengths:
        initial_coil_length = coil_lengths[0]
        last_coil_length = coil_lengths[-1]
        coil_length_difference = initial_coil_length - last_coil_length
        print(f"Coil length deducted: {coil_length_difference:.2f} meters")
    else:
        print("No coil length data available.")

if __name__ == "__main__":
    main()