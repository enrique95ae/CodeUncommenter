import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
from pathlib import Path

class RemoveCommentsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remove Code Comments")
        self.root.geometry('600x200')  # Set the window size
        self.root.resizable(False, False)  # Make the window not resizable
        self.last_path = ""

        # Load last path if exists
        self.load_last_path()

        # Styling
        style = {'padx': 10, 'pady': 10, 'ipadx': 10, 'ipady': 5}
        font_large = ('Arial', 12)
        font_small = ('Arial', 10)

        # Label
        label = tk.Label(root, text="Find a path, select a file extension and click to delete all the comments from the matching code files", font=font_large)
        label.grid(row=0, column=0, columnspan=3, padx=style['padx'], pady=style['pady'], sticky='w')

        # Path entry
        self.path_entry = tk.Entry(root, width=40, font=font_small)
        self.path_entry.grid(row=1, column=0, padx=(style['padx'], 0), pady=style['pady'], sticky='we')

        # Browse button
        browse_button = tk.Button(root, text="Browse", command=self.browse_folder, font=font_small)
        browse_button.grid(row=1, column=1, padx=(5, 0), pady=style['pady'])

        # Dropdown for file extensions
        self.file_extension = tk.StringVar(root)
        self.file_extension.set(".ts")  # default value
        dropdown = tk.OptionMenu(root, self.file_extension, ".ts", ".cs", ".cpp", ".css", ".py")
        dropdown.grid(row=1, column=2, padx=(5, style['padx']), pady=style['pady'], sticky='w')

        # Delete comments button
        delete_button = tk.Button(root, text="Delete Comments", command=self.delete_comments, font=font_small)
        delete_button.grid(row=2, column=0, columnspan=3, padx=style['padx'], pady=style['pady'], sticky='we')

    def browse_folder(self):
        self.path = filedialog.askdirectory()
        if self.path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.path)

    def delete_comments(self):
        path = self.path_entry.get()
        extension = self.file_extension.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Invalid directory path")
            return

        # Save last path
        self.save_last_path(path)

        # Regex patterns for comments
        inline_comment_pattern = None
        multi_line_pattern = re.compile(r"/\*.*?\*/", re.DOTALL)  # Default for multi-line comments

        if extension in [".ts", ".cs", ".cpp"]:
            inline_comment_pattern = re.compile(r"(?<!:)//.*")
        elif extension == ".css":
            inline_comment_pattern = None  # CSS doesn't have single-line comments like //
        elif extension == ".py":
            inline_comment_pattern = re.compile(r"#.*")
            multi_line_pattern = None  # Python uses triple quotes for block comments, which are not tackled here

        # Process files
        files_modified = 0
        for filepath in Path(path).rglob(f'*{extension}'):
            with open(filepath, 'r+', encoding='utf-8') as file:
                content = file.read()
                if multi_line_pattern:
                    content = re.sub(multi_line_pattern, '', content)  # Remove block comments
                if inline_comment_pattern:
                    lines = content.splitlines()
                    modified_lines = [re.sub(inline_comment_pattern, '', line) for line in lines]
                    modified_content = '\n'.join(modified_lines)
                else:
                    modified_content = content

                if modified_content != content:  # Check if changes were made
                    file.seek(0)
                    file.write(modified_content)
                    file.truncate()
                    files_modified += 1
                    print(f"Comments deleted from: {filepath}")  # Log which files are being modified

        messagebox.showinfo("Complete", f"Comments deleted in {files_modified} files.")

    def save_last_path(self, path):
        with open("last_path.txt", "w") as f:
            f.write(path)

    def load_last_path(self):
        if os.path.exists("last_path.txt"):
            with open("last_path.txt", "r") as f:
                self.last_path = f.read()

# Create the main window
root = tk.Tk()
app = RemoveCommentsApp(root)
root.mainloop()
