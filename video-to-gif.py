import os
import sys
import subprocess
import re

def parse_aspect(aspect_str):
    """Parse aspect ratio string like '16:9' or '1:1' and return (w, h) as floats."""
    try:
        w, h = aspect_str.split(":")
        return float(w), float(h)
    except Exception:
        raise ValueError("Aspect ratio must be in the format W:H, e.g., 16:9 or 1:1")

def parse_resize(resize_str):
    """
    Parse resize parameter - can be:
    - Float (0.5 for 50% scaling)
    - Integer (800 for max dimension of 800px)
    Returns (scale_factor, max_dimension) where one will be None
    """
    try:
        # Check if it's a pixel dimension (integer >= 10)
        if resize_str.isdigit():
            dimension = int(resize_str)
            if dimension >= 10:  # Assume values >= 10 are pixel dimensions
                return None, dimension
        
        # Otherwise treat as scale factor
        scale = float(resize_str)
        if 0.1 <= scale <= 10.0:  # Reasonable scale factor range
            return scale, None
        else:
            raise ValueError("Scale factor should be between 0.1 and 10.0")
            
    except ValueError:
        raise ValueError("Resize must be a scale factor (e.g., 0.5) or pixel dimension (e.g., 800)")

def mp4_to_gif(input_path, output_path=None, start_time=None, end_time=None, resize_param="1.0", fps=10, aspect=None, crop_in=False, contrast=1.0, saturation=1.0):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    # Parse resize parameter
    scale_factor, max_dimension = parse_resize(resize_param)
    
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
                    crop_in = True  # Auto-enable crop-in for this case
            except (ValueError, IndexError):
                pass
            
    except subprocess.CalledProcessError:
        print("Could not determine video dimensions")
    
    # Determine output filename if not specified
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        
        if scale_factor:
            resize_pct = int(scale_factor * 100)
            size_str = f"{resize_pct}pct"
        else:
            size_str = f"{max_dimension}px"
            
        output_path = f"{base}_{size_str}_{fps}fps"
        if aspect:
            aspect_str = aspect.replace(":", "x")
            output_path += f"_{aspect_str}"
        if crop_in:
            output_path += "_cropped"
        if contrast != 1.0:
            output_path += f"_c{contrast:.1f}".replace(".", "")
        if saturation != 1.0:
            output_path += f"_s{saturation:.1f}".replace(".", "")
        output_path += ".gif"
    
    filters = []
    
    # Handle aspect ratio transformation
    if aspect:
        w_ratio, h_ratio = parse_aspect(aspect)
        
        if crop_in:
            # Crop to target aspect ratio without stretching
            print(f"Cropping to {aspect} aspect ratio (no stretching)")
            
            if w_ratio == h_ratio:
                # For square aspect (1:1), crop to a perfect square
                filters.append("crop='min(iw,ih)':'min(iw,ih)'")
            else:
                # Center crop to desired aspect ratio
                filters.append(
                    f"crop='if(gt(a,{w_ratio}/{h_ratio}),ih*{w_ratio}/{h_ratio},iw)':'if(gt(a,{w_ratio}/{h_ratio}),ih,iw*{h_ratio}/{w_ratio})'"
                )
        else:
            # Scale to target aspect ratio (may stretch/squash)
            print(f"Scaling to {aspect} aspect ratio (may stretch)")
            
            if w_ratio == h_ratio:
                # Make a perfect square by scaling
                filters.append(f"scale='min(iw,ih)':'min(iw,ih)'")
            else:
                # Scale to exact aspect ratio
                filters.append(f"scale='if(gt(a,{w_ratio}/{h_ratio}),{w_ratio}*ih/{h_ratio},iw)':'if(gt(a,{w_ratio}/{h_ratio}),ih,{h_ratio}*iw/{w_ratio})'")
    
    # Add resizing
    if scale_factor and scale_factor != 1.0:
        print(f"Scaling by factor: {scale_factor}")
        filters.append(f"scale=iw*{scale_factor}:ih*{scale_factor}")
    elif max_dimension:
        print(f"Resizing to max dimension: {max_dimension}px")
        # Scale so the largest dimension becomes max_dimension, preserving aspect ratio
        filters.append(f"scale='if(gt(iw,ih),{max_dimension},-1)':'if(gt(ih,iw),{max_dimension},-1)'")
    
    # Add color adjustments
    color_adjustments = []
    if contrast != 1.0:
        print(f"Adjusting contrast: {contrast}")
        color_adjustments.append(f"contrast={contrast}")
    
    if saturation != 1.0:
        print(f"Adjusting saturation: {saturation}")
        color_adjustments.append(f"saturation={saturation}")
    
    if color_adjustments:
        # Use eq filter for color adjustments
        filters.append(f"eq={':'.join(color_adjustments)}")
    
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
    parser.add_argument("--resize", default="1.0", help="Resize factor (e.g. 0.5 for 50%%) or pixel dimension (e.g. 800 for 800px max)")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the GIF")
    
    # Add both --aspect and --ar as options for aspect ratio
    aspect_group = parser.add_mutually_exclusive_group()
    aspect_group.add_argument("--aspect", help="Target aspect ratio (e.g., 1:1, 16:9, 4:3)")
    aspect_group.add_argument("--ar", help="Target aspect ratio (e.g., 1:1, 16:9, 4:3) - alias for --aspect")
    
    parser.add_argument("--crop-in", action="store_true", help="Crop to target aspect ratio instead of stretching (preserves pixel aspect ratio)")
    parser.add_argument("--contrast", type=float, default=1.0, help="Contrast adjustment (1.0 = normal, >1.0 = more contrast, <1.0 = less contrast)")
    parser.add_argument("--saturation", type=float, default=1.0, help="Saturation adjustment (1.0 = normal, >1.0 = more saturated, <1.0 = less saturated)")

    args = parser.parse_args()

    # Use --ar if --aspect is not provided
    aspect_ratio = args.aspect or args.ar

    mp4_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps, aspect_ratio, args.crop_in, args.contrast, args.saturation)
