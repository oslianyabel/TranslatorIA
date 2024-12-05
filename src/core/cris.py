import cv2
import numpy as np
from ffmpeg import ffmpeg

def remove_video_sections(input_path, output_path, start_times, end_times):
    # Read the input video
    cap = cv2.VideoCapture(input_path)
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create an FFmpeg pipeline
    pipeline = ffmpeg.input(input_path)
    
    # Add a filter to remove sections
    for start_time, end_time in zip(start_times, end_times):
        pipeline = pipeline.filter('atrim', start=start_time, duration=end_time-start_time)
    
    # Output the modified video
    pipeline.output(output_path, vcodec='copy')
    
    # Run the FFmpeg pipeline
    ffmpeg.run(pipeline)

# Example usage
input_video = "original_video.mp4"
output_video = "modified_video.mp4"
start_times = [30, 60]  # Start times in seconds
end_times = [45, 75]    # End times in seconds

remove_video_sections(input_video, output_video, start_times, end_times)