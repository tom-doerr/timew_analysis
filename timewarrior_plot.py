#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date, timezone, timedelta
import random

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
        end = datetime.strptime(entry['end'], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone() if 'end' in entry else datetime.now(timezone.utc).astimezone()
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
    hours = {i: [" " * 60 for _ in range(60)] for i in range(24)}
    colors = {}

    for start, end, tags in time_blocks:
        color = get_color(tags[0] if tags else "default")
        colors[tags[0] if tags else "default"] = color
        
        start_hour, start_minute = start.hour, start.minute
        end_hour, end_minute = end.hour, end.minute

        if start_hour == end_hour:
            for i in range(start_minute, end_minute):
                hours[start_hour][i] = color + "█" + "\033[0m"
        else:
            for i in range(start_minute, 60):
                hours[start_hour][i] = color + "█" + "\033[0m"
            for hour in range(start_hour + 1, end_hour):
                hours[hour] = [color + "█" + "\033[0m"] * 60
            for i in range(end_minute):
                hours[end_hour][i] = color + "█" + "\033[0m"

    for hour in range(24):
        output.append(f"{hour:02d}:00 {''.join(hours[hour])}")

    # Add legend
    output.append("\nLegend:")
    for tag, color in colors.items():
        output.append(f"{color}█████{tag}\033[0m")

    return "\n".join(output)

def main():
    data = get_timewarrior_data()
    time_blocks = parse_timewarrior_data(data)
    formatted_output = format_time_blocks(time_blocks)
    print(formatted_output)

if __name__ == "__main__":
    main()
