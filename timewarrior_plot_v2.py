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
    hours = {i: [(" ", None, None) for _ in range(120)] for i in range(24)}  # 120 for 30-minute blocks
    colors = {}
    tag_positions = {}

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
            hours[hour][i % 120] = ("█", bg_color, tag)
            
        # Store the middle position of each tag for text placement
        middle_index = (start_index + end_index) // 2
        tag_positions[tag] = middle_index

    output.append("┌" + "─" * 122 + "┐")
    for hour in range(24):
        text_line = f"│{hour:02d}:00 "
        block_line = "│     "
        i = 0
        while i < 120:
            char, bg_color, tag = hours[hour][i]
            if bg_color:
                # Find the end of this block
                end = i
                while end < 120 and hours[hour][end][1] == bg_color:
                    end += 1
                block_width = end - i
                
                # Add the block to the block line
                block_line += f"{bg_color}{'█' * block_width}\033[0m"
                
                # Add the tag to the text line if this is where it should be placed
                if tag_positions.get(tag) in range(hour * 120 + i, hour * 120 + end):
                    text_to_add = tag[:block_width].center(block_width)
                    text_line += f"{bg_color}{text_to_add}\033[0m"
                else:
                    text_line += " " * block_width
                
                i = end
            else:
                text_line += " "
                block_line += " "
                i += 1
        
        text_line += "│"
        block_line += "│"
        output.append(text_line)
        output.append(block_line)
    output.append("└" + "─" * 122 + "┘")

    # Add legend
    output.append("\nLegend:")
    for tag, bg_color in colors.items():
        output.append(f"{bg_color}{tag.center(10)}\033[0m {tag}")
        output.append(f"{bg_color}{'█' * 10}\033[0m")

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
