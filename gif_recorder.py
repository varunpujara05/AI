"""
GIF Recorder - Captures exact GUI frames and saves as GIF animation.
This ensures pixel-perfect match between what's displayed and what's saved.
"""

import io
from PIL import Image
import numpy as np


class GIFRecorder:
    """Records GUI frames and saves them as an animated GIF."""
    
    def __init__(self):
        """Initialize the GIF recorder."""
        self.frames = []
        self.is_recording = False
        
    def start_recording(self):
        """Start recording frames."""
        self.frames = []
        self.is_recording = True
        print("🎬 Started recording GIF frames...")
        
    def stop_recording(self):
        """Stop recording frames."""
        self.is_recording = False
        print(f"⏹️ Stopped recording. Captured {len(self.frames)} frames.")
        
    def capture_frame(self, figure):
        """
        Capture the current state of the matplotlib figure.
        
        Args:
            figure: The matplotlib figure to capture
        """
        if not self.is_recording:
            return
            
        # Draw the figure to ensure it's up to date
        figure.canvas.draw()
        
        # Get the RGBA buffer from the figure canvas
        buf = figure.canvas.buffer_rgba()
        w, h = figure.canvas.get_width_height()
        
        # Convert to PIL Image
        img = Image.frombytes('RGBA', (w, h), buf)
        
        # Convert RGBA to RGB (GIF doesn't support transparency well)
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        
        self.frames.append(rgb_img)
        
    def save_gif(self, filepath, duration=500, loop=0):
        """
        Save the recorded frames as an animated GIF.
        
        Args:
            filepath: Path where the GIF should be saved
            duration: Duration of each frame in milliseconds (default: 500ms)
            loop: Number of times to loop (0 = infinite, default: 0)
        """
        if not self.frames:
            print("❌ No frames to save!")
            return False
            
        try:
            print(f"\n💾 Saving GIF with {len(self.frames)} frames to: {filepath}")
            
            # Save as GIF
            self.frames[0].save(
                filepath,
                save_all=True,
                append_images=self.frames[1:],
                duration=duration,
                loop=loop,
                optimize=False  # Keep quality high
            )
            
            print(f"✅ GIF saved successfully!")
            print(f"   Frames: {len(self.frames)}")
            print(f"   Duration per frame: {duration}ms")
            print(f"   Total duration: {len(self.frames) * duration / 1000:.1f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving GIF: {str(e)}")
            return False
            
    def clear_frames(self):
        """Clear all recorded frames."""
        self.frames = []
        self.is_recording = False
        print("🗑️ Cleared all recorded frames.")
