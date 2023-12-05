import os
import psutil
import time

import asyncio
import sys
from datetime import datetime
import functools
import pandas as pd
import matplotlib.pyplot as plt


def print_process_info(pid):
    p = psutil.Process(current_process_pid)

    print(f"Nombre: {p.name()}")
    print(f"ID: {pid}")
    print(f"Proceso padre: {p.ppid()}")
    print(f"User: {p.username()}")
    print(f"CPU %: {p.cpu_percent(interval=1.0)}")
    print(f"Memory %: {p.memory_percent()}")
    print(f"Estado: {p.status()}")
    print(f"Path: {p.exe()}")


def execute_and_monitor_program(process_name, command):
    pid = os.fork()  # Works on Unix-like systems, this is the child id

    if pid:
        # Parent
        p = psutil.Process(pid)

        while True:
            if p.status() != psutil.STATUS_STOPPED:
                time.sleep(1)
            else:
                pid = os.fork()
                p = psutil.Process(pid)

    else:
        # Child
        os.system(command)


def create_log_headers(file_path):
    with open(file_path, "w") as file:
        file.write("timestamp,% cpu,% memory\n")


def stats_to_file(file_path, timestamp, values):
    with open(file_path, "a") as file:
        file.write(str(timestamp) + "," + functools.reduce(lambda a, b: str(a) + "," + str(b), values) + "\n")

def plot_stats(file_path):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    # headers = ['timestamp', '% cpu', '% memory']

    df = pd.read_csv(
        file_path,
        decimal=".",
        dtype={
            'timestamp': 'string',
            '% cpu': 'float64',
            '% memory': 'float64',
        }
    )

    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')

    df.set_index('timestamp').plot()

    plt.show()

async def execute_and_monitor_cpu_memory(executable_path):
    stats_save_file = ".\\monitor_cpu_memory.csv"
    create_log_headers(stats_save_file)

    subprocess = await asyncio.create_subprocess_exec(executable_path)
    subprocess_id = subprocess.pid
    p = psutil.Process(subprocess_id)

    while psutil.pid_exists(subprocess_id) and p.status() != psutil.STATUS_STOPPED:
        try:
            stats_to_file(stats_save_file, datetime.now().isoformat(),
                        (p.cpu_percent(interval=1.0), p.memory_percent()))
            time.sleep(1)
        except psutil.NoSuchProcess:
            print("Process closed")

    plot_stats(stats_save_file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    current_process_pid = os.getpid()
    # 1
    # print_process_info(current_process_pid)
    # 2
    # execute_and_monitor_program("process_name", "command")
    # 3
    asyncio.run(execute_and_monitor_cpu_memory("D:\\programs\\Notepad++\\notepad++.exe"))
    #plot_stats(".\\monitor_cpu_memory.csv")
