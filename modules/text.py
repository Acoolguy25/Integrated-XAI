import re
import sys
import shutil


class RichTextProcessorNew:
    def __init__(self):
        self.text = ""
        self.previous_output_lines = 0  # Track the number of lines displayed previously

    def add_text(self, new_text):
        self.text += new_text

    def format_text(self):
        # ANSI escape codes for formatting
        BOLD = "\033[1m"
        ITALIC = "\033[3m"
        STRIKETHROUGH = "\033[9m"
        RESET = "\033[0m"

        # Process bold, italic, and strikethrough text
        formatted_text = re.sub(r"\*\*(.*?)\*\*", rf"{BOLD}\1{RESET}", self.text)
        formatted_text = re.sub(r"_(.*?)_", rf"{ITALIC}\1{RESET}", formatted_text)
        formatted_text = re.sub(r"~~(.*?)~~", rf"{STRIKETHROUGH}\1{RESET}", formatted_text)

        return formatted_text

    def display_lines(self):
        # Get terminal width to calculate the required number of lines
        terminal_width = shutil.get_terminal_size().columns
        formatted_text = self.format_text()

        # Split text into lines that fit within the terminal width
        lines = []
        for line in formatted_text.splitlines():
            # Split long lines to fit the terminal width
            lines.extend([line[i:i + terminal_width] for i in range(0, len(line), terminal_width)])

        # Clear previous output by moving up and clearing each line
        if self.previous_output_lines > 0:
            # Ensure we only move up enough lines, not more or less
            for _ in range(self.previous_output_lines):
                sys.stdout.write("\033[F")  # Move cursor up one line
                sys.stdout.write("\033[K")  # Clear the line

        # Print the new lines
        for line in lines:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

        # Update the count of previously printed lines
        self.previous_output_lines = len(lines)

class RichTextProcessor:
    def __init__(self):
        self.text = ""
        self.latest = ""

    def add_text(self, text):
        self.text += text
        self.latest = text

    def display_lines(self):
        # Just print out the latest!
        sys.stdout.write(self.latest)