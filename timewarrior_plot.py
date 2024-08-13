#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_timewarrior_data():
    """Execute TimeWarrior export command and return the output."""
    result = subprocess.run(['timew', 'export'], capture_output=True, text=True)
    return json.loads(result.stdout)

def parse_timewarrior_data(data):
    """Parse TimeWarrior data and return today's time blocks."""
    today = date.today()
    time_blocks = []
    for entry in data:
        start = datetime.fromisoformat(entry['start'])
        end = datetime.fromisoformat(entry['end']) if 'end' in entry else datetime.now()
        if start.date() == today:
            time_blocks.append((start, end, entry.get('tags', [])))
    return time_blocks

def plot_time_blocks(time_blocks):
    """Plot time blocks for today."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, (start, end, tags) in enumerate(time_blocks):
        duration = (end - start).total_seconds() / 3600  # duration in hours
        ax.barh(i, duration, left=mdates.date2num(start), height=0.5, align='center', 
                color='skyblue', edgecolor='navy')
        ax.text(mdates.date2num(start) + duration/2, i, ', '.join(tags), 
                ha='center', va='center', fontweight='bold')

    ax.set_yticks(range(len(time_blocks)))
    ax.set_yticklabels([f"Block {i+1}" for i in range(len(time_blocks))])
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    plt.title("TimeWarrior Data for Today")
    plt.xlabel("Time")
    plt.ylabel("Time Blocks")
    plt.tight_layout()
    plt.show()

def main():
    data = get_timewarrior_data()
    time_blocks = parse_timewarrior_data(data)
    plot_time_blocks(time_blocks)

if __name__ == "__main__":
    main()
