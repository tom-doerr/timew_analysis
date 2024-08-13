#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date, timezone, timedelta
import random
import sys

def get_opposite_color(color):
    """Calculate the opposite color for better readability."""
    color_num = int(color.split(';')[-1][:-1])
    opposite_color = 15 if color_num < 128 else 0  # White (15) for dark colors, Black (0) for light colors
    return f"\033[38;5;{opposite_color}m"

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
    hours = {i: [(" ", None) for _ in range(240)] for i in range(24)}
    colors = {}

    for start, end, tags in time_blocks:
        bg_color = get_color(tags[0] if tags else "default")
        text_color = get_opposite_color(bg_color)
        colors[tags[0] if tags else "default"] = (bg_color, text_color)
        tag = tags[0] if tags else "default"
        
        start_hour, start_minute = start.hour, start.minute
        end_hour, end_minute = end.hour, end.minute

        if start_hour == end_hour:
            for i in range(start_minute * 4, end_minute * 4):
                hours[start_hour][i] = ("█", bg_color, text_color)
        else:
            for i in range(start_minute * 4, 240):
                hours[start_hour][i] = ("█", bg_color, text_color)
            for hour in range(start_hour + 1, end_hour):
                hours[hour] = [("█", bg_color, text_color) for _ in range(240)]
            for i in range(end_minute * 4):
                hours[end_hour][i] = ("█", bg_color, text_color)

    output.append("┌" + "─" * 242 + "┐")
    for hour in range(24):
        line = f"│{hour:02d}:00 "
        for char, bg_color, text_color in hours[hour]:
            if bg_color:
                line += f"{bg_color}{text_color}{char}\033[0m"
            else:
                line += char
        line += "│"
        output.append(line)
    output.append("└" + "─" * 242 + "┘")

    # Add legend
    output.append("\nLegend:")
    for tag, (bg_color, text_color) in colors.items():
        output.append(f"{bg_color}{text_color}█████ {tag}\033[0m")

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
