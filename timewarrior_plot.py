#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime, date, timezone, timedelta

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

def format_time_blocks(time_blocks):
    """Format time blocks for display with a visual representation."""
    output = []
    max_duration = max((end - start).total_seconds() for start, end, _ in time_blocks)
    
    for i, (start, end, tags) in enumerate(time_blocks, 1):
        duration = end - start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Calculate the bar length proportional to the duration
        bar_length = int((duration.total_seconds() / max_duration) * 40)
        bar = '█' * bar_length
        
        output.append(f"Block {i}:")
        output.append(f"  Start: {start.strftime('%H:%M:%S')}")
        output.append(f"  End: {end.strftime('%H:%M:%S')}")
        output.append(f"  Duration: {int(hours):02d}:{int(minutes):02d}")
        output.append(f"  Tags: {', '.join(tags)}")
        output.append(f"  {bar} {duration}")
        output.append("")
    return "\n".join(output)

def main():
    data = get_timewarrior_data()
    time_blocks = parse_timewarrior_data(data)
    formatted_output = format_time_blocks(time_blocks)
    print(formatted_output)

if __name__ == "__main__":
    main()
