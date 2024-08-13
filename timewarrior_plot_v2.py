#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date, timezone, timedelta
import random
import sys


def get_timewarrior_data():
    """Execute TimeWarrior export command and return the output."""
    result = subprocess.run(['timew', 'export'], capture_output=True, text=True)
    return json.loads(result.stdout)

def parse_timewarrior_data(data):
    """Parse TimeWarrior data and return today's time blocks."""
    today = date.today()
    time_blocks = []
    for entry in data:
        start = datetime.strptime(entry['start'], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone()
        if 'end' in entry:
            end = datetime.strptime(entry['end'], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone()
        else:
            end = datetime.now(timezone.utc).astimezone()
        
        # Handle multi-day entries
        if start.date() < today and end.date() >= today:
            start = datetime.combine(today, datetime.min.time()).astimezone()
        elif end.date() > today:
            end = datetime.combine(today, datetime.max.time()).astimezone()
        
        if start.date() == today:
            time_blocks.append((start, end, entry.get('tags', [])))
    return time_blocks

def get_color(tag):
    """Generate a consistent color for a given tag."""
    random.seed(tag)
    return f"\033[38;5;{random.randint(1, 255)}m"

def format_time_blocks(time_blocks):
    """Format time blocks for display with a visual representation."""
    output = []
    hours = {i: [(" ", None, None) for _ in range(120)] for i in range(24)}  # Increased to 120 for 30-minute blocks
    colors = {}

    for start, end, tags in time_blocks:
        bg_color = get_color(tags[0] if tags else "default")
        colors[tags[0] if tags else "default"] = bg_color
        tag = tags[0] if tags else "default"
        
        start_hour, start_minute = start.hour, start.minute
        end_hour, end_minute = end.hour, end.minute

        start_index = start_hour * 120 + start_minute * 2
        end_index = end_hour * 120 + end_minute * 2

        for i in range(start_index, end_index):
            hour = i // 120
            minute = (i % 120) // 2
            char = tag[0].upper() if i % 2 == 0 else "█"
            hours[hour][i % 120] = (char, bg_color, tag)

    output.append("┌" + "─" * 122 + "┐")
    for hour in range(24):
        line = f"│{hour:02d}:00 "
        for char, bg_color, tag in hours[hour]:
            if bg_color:
                line += f"{bg_color}{char}\033[0m"
            else:
                line += char
        line += "│"
        output.append(line)
    output.append("└" + "─" * 122 + "┘")

    # Add legend
    output.append("\nLegend:")
    for tag, bg_color in colors.items():
        output.append(f"{bg_color}{tag[0].upper()}█{tag[0].upper()}█{tag[0].upper()}\033[0m {tag}")

    # Add timestamp
    output.append(f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(output)

def main():
    data = get_timewarrior_data()
    time_blocks = parse_timewarrior_data(data)
    formatted_output = format_time_blocks(time_blocks)
    print(formatted_output)

if __name__ == "__main__":
    main()
    sys.exit(0)
