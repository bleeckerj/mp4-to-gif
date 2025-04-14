import os
import sys
import subprocess

def mp4_to_gif(input_path, output_path=None, start_time=None, end_time=None, resize_factor=1.0, fps=10):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".gif"
        
    filters = []
    
    # Add resizing if needed
    if resize_factor != 1.0:
        filters.append(f"scale=iw*{resize_factor}:ih*{resize_factor}")
        
    # Add fps filter
    filters.append(f"fps={fps}")
    
    # Combine filters
    filter_string = ",".join(filters)
    
    # Build FFmpeg command
    cmd = ["ffmpeg", "-y"]  # -y to overwrite output files
    
    # Add start time if specified
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    
    # Add input file
    cmd.extend(["-i", input_path])
    
    # Add end time/duration if specified
    if end_time is not None:
        if start_time is not None:
            duration = end_time - start_time
            cmd.extend(["-t", str(duration)])
        else:
            cmd.extend(["-to", str(end_time)])
    
    # Add filters
    if filters:
        cmd.extend(["-vf", filter_string])
    
    # Output options and file
    cmd.append(output_path)
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        print(f"GIF saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e.stderr}")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MP4 to animated GIF")
    parser.add_argument("input", help="Path to input MP4 file")
    parser.add_argument("--output", help="Path to output GIF file")
    parser.add_argument("--start", type=float, help="Start time in seconds")
    parser.add_argument("--end", type=float, help="End time in seconds")
    parser.add_argument("--resize", type=float, default=1.0, help="Resize factor (e.g. 0.5 for 50%)")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the GIF")

    args = parser.parse_args()

    mp4_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps)
