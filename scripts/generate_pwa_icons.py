#!/usr/bin/env python3
"""
Generate PWA icons from a base logo.
This script creates placeholder icons for development.
In production, replace with actual logo-based icons.
"""

from PIL import Image, ImageDraw
import os

def create_icon(size, filename):
    """Create a simple placeholder icon with the specified size."""
    # Create a blue square with white "V" for Vantage
    img = Image.new('RGBA', (size, size), (59, 130, 246, 255))  # Blue background
    draw = ImageDraw.Draw(img)
    
    # Draw a white "V" in the center
    font_size = size // 3
    # Simple V shape using lines
    margin = size // 4
    points = [
        (margin, margin),
        (size // 2, size - margin),
        (size - margin, margin)
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Save the icon
    img.save(filename, 'PNG')
    print(f"Generated {filename} ({size}x{size})")

def main():
    """Generate all required PWA icons."""
    icon_dir = "/Users/saban/Desktop/NVC LAB/VANTAGE AI/web/public/icons"
    
    # Ensure directory exists
    os.makedirs(icon_dir, exist_ok=True)
    
    # Generate icons in various sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = os.path.join(icon_dir, f"icon-{size}x{size}.png")
        create_icon(size, filename)
    
    # Generate shortcut icons
    shortcut_icons = [
        ("shortcut-new-post.png", "📝"),
        ("shortcut-calendar.png", "📅"),
        ("shortcut-inbox.png", "📬")
    ]
    
    for filename, emoji in shortcut_icons:
        create_shortcut_icon(emoji, os.path.join(icon_dir, filename))
    
    print("All PWA icons generated successfully!")

def create_shortcut_icon(emoji, filename):
    """Create a shortcut icon with emoji."""
    img = Image.new('RGBA', (96, 96), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw emoji (simplified - in production use proper emoji rendering)
    draw.text((48, 48), emoji, fill=(0, 0, 0, 255), anchor="mm")
    
    img.save(filename, 'PNG')
    print(f"Generated {filename}")

if __name__ == "__main__":
    main()
