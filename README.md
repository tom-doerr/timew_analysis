# TimeWarrior Plot

This project provides a visual representation of TimeWarrior data, displaying time blocks for different activities throughout the day.

## Features

- Parses TimeWarrior export data
- Prioritizes tags based on predefined lists
- Generates a colorful, ASCII-art style visualization of time blocks
- Includes a legend for easy interpretation
- Handles multi-day entries and ongoing tasks

## Requirements

- Python 3.6+
- TimeWarrior

## Usage

1. Ensure TimeWarrior is installed and configured on your system.
2. Run the script:

   ```
   python3 timewarrior_plot_v2.py [--blocks-per-minute BLOCKS]
   ```

   The `--blocks-per-minute` argument is optional and defaults to 4. It determines the number of blocks used to represent each minute in the visualization.

3. The script will execute the TimeWarrior export command, parse the data, and display the visualization in your terminal.

## Customization

You can customize the tag prioritization by modifying the `LOW_PRIORITY_TAGS` and `HIGH_PRIORITY_TAGS` lists at the beginning of the script.

You can also adjust the granularity of the time blocks by using the `--blocks-per-minute` argument when running the script. For example:

```
python3 timewarrior_plot_v2.py --blocks-per-minute 2
```

This will use 2 blocks to represent each minute, resulting in a less detailed but more compact visualization.

## Output

The script generates a 24-hour timeline with colored blocks representing different activities. Each hour is divided into 30-minute segments. The output includes:

- A visual representation of time blocks
- A legend explaining the color coding
- A timestamp indicating when the report was generated

## Acknowledgments

- TimeWarrior project (https://timewarrior.net/)
