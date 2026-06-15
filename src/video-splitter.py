import os
import math
import subprocess
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, ttk

# Function to select a video file
def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mov;*.avi;*.mkv")])
    if video_path:
        video_label.config(text=f"Selected: {os.path.basename(video_path)}")

# Function to select the output folder
def select_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory()
    if output_folder:
        output_label.config(text=f"Output Folder: {output_folder}")

# Function to split the video using FFmpeg
def split_video():
    if not video_path or not output_folder:
        messagebox.showerror("Error", "Please select a video file and output folder.")
        return

    try:
        # Get chunk size from user input
        chunk_size_mb = float(size_entry.get())
        if chunk_size_mb <= 0:
            raise ValueError("Chunk size must be greater than 0.")

        # Get the total file size in MB
        total_size_mb = os.path.getsize(video_path) / (1024 * 1024)  # Convert bytes to MB

        # Get video duration using FFmpeg
        video_duration = get_video_duration(video_path)
        if video_duration is None:
            messagebox.showerror("Error", "Failed to retrieve video duration. Ensure FFmpeg is installed.")
            return

        # Calculate the number of chunks and duration per chunk
        num_chunks = math.ceil(total_size_mb / chunk_size_mb)
        chunk_duration = video_duration / num_chunks

        base_name, ext = os.path.splitext(os.path.basename(video_path))
        progress['maximum'] = num_chunks

        # Split the video into chunks
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, video_duration)

            # Create output file name
            output_filename = os.path.join(output_folder, f"{base_name}_part{i + 1}{ext}")
            
            # Split video using FFmpeg
            split_video_ffmpeg(video_path, start_time, end_time, output_filename)
            
            progress['value'] += 1
            root.update_idletasks()

        messagebox.showinfo("Success", "Video split successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Helper function to split video using FFmpeg
def split_video_ffmpeg(input_file, start_time, end_time, output_file):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", str(start_time),
        "-to", str(end_time),
        "-c", "copy",  # Use copy codec to avoid re-encoding
        output_file
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Helper function to get video duration using FFmpeg
def get_video_duration(input_file):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-hide_banner",
        "-f", "null",
        "-"
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr = process.stderr

    # Extract duration from FFmpeg output
    for line in stderr.splitlines():
        if "Duration" in line:
            duration_str = line.split("Duration:")[1].split(",")[0].strip()
            time_parts = duration_str.split(":")  # Split by colon (hours:minutes:seconds)

            # Ensure we handle varying formats robustly
            if len(time_parts) == 3:
                h, m, s = map(float, time_parts)
                return h * 3600 + m * 60 + s
            else:
                raise ValueError(f"Unexpected duration format: {duration_str}")

    # If no duration line is found, return None
    return None

# GUI Setup
root = Tk()
root.title("Video Splitter by Size (FFmpeg)")

video_path = ""
output_folder = ""

# Input for video selection
Label(root, text="Step 1: Select a Video").grid(row=0, column=0, pady=5, sticky="w")
video_label = Label(root, text="No file selected")
video_label.grid(row=0, column=1, pady=5, sticky="w")
Button(root, text="Browse", command=select_video).grid(row=0, column=2, padx=5)

# Input for chunk size
Label(root, text="Step 2: Enter Chunk Size (MB)").grid(row=1, column=0, pady=5, sticky="w")
size_entry = Entry(root)
size_entry.grid(row=1, column=1, pady=5, sticky="w")

# Input for output folder selection
Label(root, text="Step 3: Select Output Folder").grid(row=2, column=0, pady=5, sticky="w")
output_label = Label(root, text="No folder selected")
output_label.grid(row=2, column=1, pady=5, sticky="w")
Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2, padx=5)

# Button to start the splitting process
Button(root, text="Start Splitting", command=split_video).grid(row=3, column=0, columnspan=3, pady=10)

# Progress bar to display progress
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
