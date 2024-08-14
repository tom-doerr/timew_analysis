#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date, timezone, timedelta
import random
import sys
import argparse

# Define tag priority lists
LOW_PRIORITY_TAGS = ['obj', 'obj2', 'obj3', 'prof', 'ai', 'ai3']
HIGH_PRIORITY_TAGS = ['break']

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate a visual representation of TimeWarrior data.')
parser.add_argument('--blocks-per-minute', type=int, default=4, help='Number of blocks to represent each minute (default: 4)')
args = parser.parse_args()

BLOCKS_PER_MINUTE = args.blocks_per_minute

def prioritize_tags(tags):
    """Prioritize tags based on predefined lists."""
    for tag in HIGH_PRIORITY_TAGS:
        if tag in tags:
            return [tag]
    
    for tag in tags:
        if tag not in LOW_PRIORITY_TAGS:
            return [tag]
    
    for tag in reversed(LOW_PRIORITY_TAGS):
        if tag in tags:
            return [tag]
    
    return tags  # If no prioritization applies, return all tags

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
            prioritized_tags = prioritize_tags(entry.get('tags', []))
            time_blocks.append((start, end, prioritized_tags))
    return time_blocks

def get_color(tag):
    """Generate a consistent color for a given tag."""
    random.seed(tag)
    return f"\033[38;5;{random.randint(1, 255)}m"

def format_time_blocks(time_blocks):
    """Format time blocks for display with a visual representation."""
    output = []
    blocks_per_hour = 60 * BLOCKS_PER_MINUTE
    hours = {i: [(" ", None, None) for _ in range(blocks_per_hour)] for i in range(24)}
    colors = {}
    tag_blocks = {}

    for start, end, tags in time_blocks:
        bg_color = get_color(tags[0] if tags else "default")
        colors[tags[0] if tags else "default"] = bg_color
        tag = tags[0] if tags else "default"
        
        start_index = start.hour * blocks_per_hour + start.minute * BLOCKS_PER_MINUTE
        end_index = end.hour * blocks_per_hour + end.minute * BLOCKS_PER_MINUTE

        for i in range(start_index, end_index):
            hour = i // blocks_per_hour
            hours[hour][i % blocks_per_hour] = ("█", bg_color, tag)
        
        if tag not in tag_blocks:
            tag_blocks[tag] = []
        tag_blocks[tag].append((start_index, end_index))

    total_width = 24 * (blocks_per_hour // 12) + 6  # Adjust width based on blocks per hour
    output.append("┌" + "─" * (total_width - 2) + "┐")
    for hour in range(24):
        text_line = f"│{hour:02d}:00"
        block_line = "│    "
        i = 0
        while i < blocks_per_hour:
            char, bg_color, tag = hours[hour][i]
            if bg_color:
                # Find the end of this block
                end = i
                while end < blocks_per_hour and hours[hour][end][1] == bg_color:
                    end += 1
                block_width = end - i
                
                # Add the block to the block line
                block_line += f"{bg_color}{'█' * block_width}\033[0m"
                
                # Check if we should add the tag text
                hour_start = hour * blocks_per_hour
                for start, end in tag_blocks[tag]:
                    if start <= hour_start + i < end:
                        text_to_add = tag[:block_width].center(block_width)
                        text_line += f"{bg_color}{text_to_add}\033[0m"
                        break
                else:
                    text_line += " " * block_width
                
                i = end
            else:
                text_line += " "
                block_line += " "
                i += 1
        
        text_line = text_line.ljust(total_width - 1) + "│"
        block_line = block_line.ljust(total_width - 1) + "│"
        output.append(text_line)
        output.append(block_line)
    output.append("└" + "─" * (total_width - 2) + "┘")

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
