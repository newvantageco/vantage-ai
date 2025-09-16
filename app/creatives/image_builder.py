from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter
# import cairo  # Commented out due to missing system dependencies
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ImageBuilder:
    """Build branded images from templates using PIL and Cairo."""
    
    def __init__(self):
        self.settings = get_settings()
        self.temp_dir = tempfile.mkdtemp()
    
    async def render_image(self, spec: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Render an image from template specification and inputs."""
        try:
            # Extract template parameters
            width = spec.get("width", 1080)
            height = spec.get("height", 1080)
            background = spec.get("background", {"type": "solid", "color": "#ffffff"})
            elements = spec.get("elements", [])
            
            # Create base image
            if spec.get("renderer") == "cairo":
                image_path = await self._render_with_cairo(width, height, background, elements, inputs)
            else:
                image_path = await self._render_with_pil(width, height, background, elements, inputs)
            
            # Upload to storage
            storage_url = await self._upload_to_storage(image_path)
            
            # Cleanup temp file
            os.unlink(image_path)
            
            return {
                "type": "image",
                "url": storage_url,
                "width": width,
                "height": height,
                "template_spec": spec,
                "inputs": inputs,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to render image: {e}")
            raise
    
    async def _render_with_pil(
        self, 
        width: int, 
        height: int, 
        background: Dict[str, Any], 
        elements: list[Dict[str, Any]], 
        inputs: Dict[str, Any]
    ) -> str:
        """Render image using PIL."""
        # Create base image
        if background["type"] == "solid":
            color = self._hex_to_rgb(background["color"])
            image = Image.new("RGB", (width, height), color)
        elif background["type"] == "gradient":
            image = self._create_gradient(width, height, background)
        else:
            image = Image.new("RGB", (width, height), (255, 255, 255))
        
        draw = ImageDraw.Draw(image)
        
        # Render elements
        for element in elements:
            await self._render_element_pil(draw, element, inputs, width, height)
        
        # Save to temp file
        temp_path = os.path.join(self.temp_dir, f"image_{datetime.now().timestamp()}.png")
        image.save(temp_path, "PNG")
        
        return temp_path
    
    async def _render_with_cairo(
        self, 
        width: int, 
        height: int, 
        background: Dict[str, Any], 
        elements: list[Dict[str, Any]], 
        inputs: Dict[str, Any]
    ) -> str:
        """Render image using Cairo for more advanced graphics."""
        # Create Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        
        # Set background
        if background["type"] == "solid":
            color = self._hex_to_rgba(background["color"])
            ctx.set_source_rgba(*color)
            ctx.rectangle(0, 0, width, height)
            ctx.fill()
        elif background["type"] == "gradient":
            self._create_cairo_gradient(ctx, width, height, background)
        
        # Render elements
        for element in elements:
            await self._render_element_cairo(ctx, element, inputs, width, height)
        
        # Save to temp file
        temp_path = os.path.join(self.temp_dir, f"image_{datetime.now().timestamp()}.png")
        surface.write_to_png(temp_path)
        
        return temp_path
    
    async def _render_element_pil(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render a single element using PIL."""
        element_type = element.get("type")
        
        if element_type == "text":
            await self._render_text_pil(draw, element, inputs, canvas_width, canvas_height)
        elif element_type == "rectangle":
            await self._render_rectangle_pil(draw, element, inputs, canvas_width, canvas_height)
        elif element_type == "circle":
            await self._render_circle_pil(draw, element, inputs, canvas_width, canvas_height)
        elif element_type == "image":
            await self._render_image_element_pil(draw, element, inputs, canvas_width, canvas_height)
    
    async def _render_text_pil(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render text element using PIL."""
        text = self._resolve_placeholder(element.get("text", ""), inputs)
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        
        # Font settings
        font_size = element.get("font_size", 24)
        font_color = self._hex_to_rgb(element.get("color", "#000000"))
        
        try:
            font = ImageFont.truetype(element.get("font_path", "arial.ttf"), font_size)
        except:
            font = ImageFont.load_default()
        
        # Text alignment
        alignment = element.get("alignment", "left")
        if alignment == "center":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (canvas_width - text_width) // 2
        elif alignment == "right":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = canvas_width - text_width - x
        
        draw.text((x, y), text, font=font, fill=font_color)
    
    async def _render_rectangle_pil(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render rectangle element using PIL."""
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        width = self._resolve_size(element.get("width", 100), canvas_width)
        height = self._resolve_size(element.get("height", 100), canvas_height)
        
        color = self._hex_to_rgb(element.get("color", "#000000"))
        outline = element.get("outline", None)
        outline_color = self._hex_to_rgb(outline["color"]) if outline else None
        
        if outline:
            draw.rectangle([x, y, x + width, y + height], fill=color, outline=outline_color, width=outline.get("width", 1))
        else:
            draw.rectangle([x, y, x + width, y + height], fill=color)
    
    async def _render_circle_pil(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render circle element using PIL."""
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        radius = self._resolve_size(element.get("radius", 50), min(canvas_width, canvas_height))
        
        color = self._hex_to_rgb(element.get("color", "#000000"))
        
        # PIL doesn't have direct circle drawing, so we use ellipse
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    
    async def _render_image_element_pil(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render image element using PIL."""
        image_url = self._resolve_placeholder(element.get("url", ""), inputs)
        if not image_url:
            return
        
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        width = self._resolve_size(element.get("width", 100), canvas_width)
        height = self._resolve_size(element.get("height", 100), canvas_height)
        
        try:
            # Download and load image
            import requests
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Resize if needed
            if width != img.width or height != img.height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Paste onto canvas
            draw._image.paste(img, (x, y))
            
        except Exception as e:
            logger.warning(f"Failed to load image element: {e}")
    
    async def _render_element_cairo(
        self, 
        ctx: cairo.Context, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render a single element using Cairo."""
        element_type = element.get("type")
        
        if element_type == "text":
            await self._render_text_cairo(ctx, element, inputs, canvas_width, canvas_height)
        elif element_type == "rectangle":
            await self._render_rectangle_cairo(ctx, element, inputs, canvas_width, canvas_height)
        elif element_type == "circle":
            await self._render_circle_cairo(ctx, element, inputs, canvas_width, canvas_height)
    
    async def _render_text_cairo(
        self, 
        ctx: cairo.Context, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render text element using Cairo."""
        text = self._resolve_placeholder(element.get("text", ""), inputs)
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        
        font_size = element.get("font_size", 24)
        color = self._hex_to_rgba(element.get("color", "#000000"))
        
        ctx.set_font_size(font_size)
        ctx.set_source_rgba(*color)
        ctx.move_to(x, y)
        ctx.show_text(text)
    
    async def _render_rectangle_cairo(
        self, 
        ctx: cairo.Context, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render rectangle element using Cairo."""
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        width = self._resolve_size(element.get("width", 100), canvas_width)
        height = self._resolve_size(element.get("height", 100), canvas_height)
        
        color = self._hex_to_rgba(element.get("color", "#000000"))
        
        ctx.set_source_rgba(*color)
        ctx.rectangle(x, y, width, height)
        ctx.fill()
    
    async def _render_circle_cairo(
        self, 
        ctx: cairo.Context, 
        element: Dict[str, Any], 
        inputs: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int
    ):
        """Render circle element using Cairo."""
        x = self._resolve_position(element.get("x", 0), canvas_width)
        y = self._resolve_position(element.get("y", 0), canvas_height)
        radius = self._resolve_size(element.get("radius", 50), min(canvas_width, canvas_height))
        
        color = self._hex_to_rgba(element.get("color", "#000000"))
        
        ctx.set_source_rgba(*color)
        ctx.arc(x, y, radius, 0, 2 * 3.14159)
        ctx.fill()
    
    def _resolve_placeholder(self, text: str, inputs: Dict[str, Any]) -> str:
        """Resolve placeholder variables in text."""
        for key, value in inputs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def _resolve_position(self, position: Any, canvas_size: int) -> int:
        """Resolve position value (can be percentage or absolute)."""
        if isinstance(position, str) and position.endswith("%"):
            return int(canvas_size * float(position[:-1]) / 100)
        return int(position)
    
    def _resolve_size(self, size: Any, canvas_size: int) -> int:
        """Resolve size value (can be percentage or absolute)."""
        if isinstance(size, str) and size.endswith("%"):
            return int(canvas_size * float(size[:-1]) / 100)
        return int(size)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Convert hex color to RGBA tuple."""
        r, g, b = self._hex_to_rgb(hex_color)
        return (r/255.0, g/255.0, b/255.0, alpha)
    
    def _create_gradient(self, width: int, height: int, gradient_spec: Dict[str, Any]) -> Image.Image:
        """Create gradient background using PIL."""
        # Simple vertical gradient implementation
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        start_color = self._hex_to_rgb(gradient_spec.get("start_color", "#ffffff"))
        end_color = self._hex_to_rgb(gradient_spec.get("end_color", "#000000"))
        
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def _create_cairo_gradient(self, ctx: cairo.Context, width: int, height: int, gradient_spec: Dict[str, Any]):
        """Create gradient background using Cairo."""
        start_color = self._hex_to_rgba(gradient_spec.get("start_color", "#ffffff"))
        end_color = self._hex_to_rgba(gradient_spec.get("end_color", "#000000"))
        
        pattern = cairo.LinearGradient(0, 0, 0, height)
        pattern.add_color_stop_rgba(0, *start_color)
        pattern.add_color_stop_rgba(1, *end_color)
        
        ctx.set_source(pattern)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
    
    async def _upload_to_storage(self, file_path: str) -> str:
        """Upload generated image to storage (R2)."""
        # TODO: Implement R2 upload with /templates/ prefix
        # For now, return a mock URL
        return f"https://storage.example.com/templates/generated_{datetime.now().timestamp()}.png"
