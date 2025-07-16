import os
import sys
import subprocess

def parse_aspect(aspect_str):
    """Parse aspect ratio string like '16:9' or '1:1' and return (w, h) as floats."""
    try:
        w, h = aspect_str.split(":")
        return float(w), float(h)
    except Exception:
        raise ValueError("Aspect ratio must be in the format W:H, e.g., 16:9 or 1:1")

def mp4_to_gif(input_path, output_path=None, start_time=None, end_time=None, resize_factor=1.0, fps=10, aspect=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    # Get video info using ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error", 
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,sample_aspect_ratio,display_aspect_ratio", 
        "-of", "csv=p=0", 
        input_path
    ]
    
    try:
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        video_info = probe_result.stdout.strip().split(',')
        print(f"Video info (width,height,SAR,DAR): {video_info}")
        
        # If the file has conflicting metadata, force square output
        if len(video_info) >= 4:
            try:
                width = int(video_info[0])
                height = int(video_info[1])
                
                # If OS reports as square but dimensions aren't square, force square output
                force_square = (width != height) and (video_info[3] == "1:1")
                if force_square and not aspect:
                    print("Video appears square but has rectangular dimensions. Forcing square output.")
                    aspect = "1:1"
            except (ValueError, IndexError):
                pass
            
    except subprocess.CalledProcessError:
        print("Could not determine video dimensions")
    
    # Determine output filename if not specified
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        resize_pct = int(resize_factor * 100)
        output_path = f"{base}_{resize_pct}pct_{fps}fps.gif"
        if aspect:
            aspect_str = aspect.replace(":", "x")
            output_path = f"{base}_{resize_pct}pct_{fps}fps_{aspect_str}.gif"
    
    filters = []
    
    # Handle aspect ratio transformation
    if aspect:
        w_ratio, h_ratio = parse_aspect(aspect)
        
        # For square aspect (1:1), transform directly to square pixels
        if w_ratio == h_ratio:
            # Make a perfect square by taking the minimum dimension
            filters.append(f"scale='min(iw,ih)':'min(iw,ih)'")
        else:
            # Center crop to desired aspect ratio
            filters.append(
                f"crop='if(gt(a,{w_ratio}/{h_ratio}),ih*{w_ratio}/{h_ratio},iw)':'if(gt(a,{w_ratio}/{h_ratio}),ih,iw*{h_ratio}/{w_ratio})'"
            )
    
    # Add resizing if needed (after any aspect ratio adjustments)
    if resize_factor != 1.0:
        filters.append(f"scale=iw*{resize_factor}:ih*{resize_factor}")
    
    # Always add fps filter
    filters.append(f"fps={fps}")
    
    # Ensure square pixels in output
    filters.append("setsar=1")
    
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
    
    # Add filter chain
    filter_string = ",".join(filters)
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
    parser.add_argument("--aspect", type=str, help="Target aspect ratio (e.g. 1:1, 16:9, 4:3)")

    args = parser.parse_args()

    mp4_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps, args.aspect)
