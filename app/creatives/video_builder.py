from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VideoBuilder:
    """Build branded videos from templates using FFmpeg."""
    
    def __init__(self):
        self.settings = get_settings()
        self.temp_dir = tempfile.mkdtemp()
    
    async def render_video(self, spec: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Render a video from template specification and inputs."""
        try:
            # Extract template parameters
            width = spec.get("width", 1920)
            height = spec.get("height", 1080)
            duration = spec.get("duration", 30)  # seconds
            fps = spec.get("fps", 30)
            background = spec.get("background", {"type": "solid", "color": "#000000"})
            elements = spec.get("elements", [])
            clips = spec.get("clips", [])
            
            # Create video
            video_path = await self._render_video_ffmpeg(
                width, height, duration, fps, background, elements, clips, inputs
            )
            
            # Upload to storage
            storage_url = await self._upload_to_storage(video_path)
            
            # Cleanup temp file
            os.unlink(video_path)
            
            return {
                "type": "video",
                "url": storage_url,
                "width": width,
                "height": height,
                "duration": duration,
                "fps": fps,
                "template_spec": spec,
                "inputs": inputs,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to render video: {e}")
            raise
    
    async def _render_video_ffmpeg(
        self,
        width: int,
        height: int,
        duration: int,
        fps: int,
        background: Dict[str, Any],
        elements: List[Dict[str, Any]],
        clips: List[Dict[str, Any]],
        inputs: Dict[str, Any]
    ) -> str:
        """Render video using FFmpeg."""
        output_path = os.path.join(self.temp_dir, f"video_{datetime.now().timestamp()}.mp4")
        
        # Build FFmpeg command
        cmd = await self._build_ffmpeg_command(
            width, height, duration, fps, background, elements, clips, inputs, output_path
        )
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg failed: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
        
        return output_path
    
    async def _build_ffmpeg_command(
        self,
        width: int,
        height: int,
        duration: int,
        fps: int,
        background: Dict[str, Any],
        elements: List[Dict[str, Any]],
        clips: List[Dict[str, Any]],
        inputs: Dict[str, Any],
        output_path: str
    ) -> List[str]:
        """Build FFmpeg command for video generation."""
        cmd = ["ffmpeg", "-y"]  # -y to overwrite output file
        
        # Input filters
        filters = []
        
        # Background
        if background["type"] == "solid":
            color = background["color"].lstrip("#")
            filters.append(f"color=c={color}:s={width}x{height}:d={duration}")
        elif background["type"] == "gradient":
            filters.append(f"color=c=black:s={width}x{height}:d={duration}")
        
        # Add clips
        for i, clip in enumerate(clips):
            clip_url = self._resolve_placeholder(clip.get("url", ""), inputs)
            if clip_url:
                start_time = clip.get("start_time", 0)
                clip_duration = clip.get("duration", 5)
                
                # Add clip as input
                cmd.extend(["-i", clip_url])
                
                # Add clip filter
                filters.append(f"[{i+1}:v]scale={width}:{height},setpts=PTS-STARTPTS+{start_time}/TB[v{i}]")
        
        # Add text overlays
        for i, element in enumerate(elements):
            if element.get("type") == "text":
                text = self._resolve_placeholder(element.get("text", ""), inputs)
                x = self._resolve_position(element.get("x", 0), width)
                y = self._resolve_position(element.get("y", 0), height)
                font_size = element.get("font_size", 24)
                color = element.get("color", "white")
                
                # Escape text for FFmpeg
                text = text.replace(":", "\\:").replace("'", "\\'")
                
                filters.append(f"drawtext=text='{text}':x={x}:y={y}:fontsize={font_size}:fontcolor={color}")
        
        # Combine all filters
        if filters:
            cmd.extend(["-filter_complex", ";".join(filters)])
        
        # Output settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-t", str(duration),
            output_path
        ])
        
        return cmd
    
    async def stitch_clips(
        self,
        clip_urls: List[str],
        transitions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Stitch multiple video clips together with optional transitions."""
        output_path = os.path.join(self.temp_dir, f"stitched_{datetime.now().timestamp()}.mp4")
        
        # Build FFmpeg command for stitching
        cmd = ["ffmpeg", "-y"]
        
        # Add input files
        for url in clip_urls:
            cmd.extend(["-i", url])
        
        # Build filter complex for concatenation
        if transitions:
            # With transitions
            filters = []
            for i in range(len(clip_urls) - 1):
                filters.append(f"[{i}:v][{i+1}:v]xfade=transition=fade:duration=1:offset=0[v{i}]")
            
            # Concatenate all segments
            concat_inputs = "".join([f"[v{i}]" for i in range(len(clip_urls) - 1)])
            filters.append(f"{concat_inputs}concat=n={len(clip_urls)-1}:v=1:a=0[outv]")
            
            cmd.extend(["-filter_complex", ";".join(filters)])
            cmd.extend(["-map", "[outv]"])
        else:
            # Simple concatenation
            cmd.extend(["-filter_complex", f"concat=n={len(clip_urls)}:v=1:a=0[outv]"])
            cmd.extend(["-map", "[outv]"])
        
        cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "23", output_path])
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg stitching failed: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg stitching failed: {stderr.decode()}")
        
        return output_path
    
    async def add_captions(
        self,
        video_url: str,
        captions: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """Add captions/subtitles to a video."""
        if not output_path:
            output_path = os.path.join(self.temp_dir, f"captioned_{datetime.now().timestamp()}.mp4")
        
        # Create SRT file for captions
        srt_path = os.path.join(self.temp_dir, "captions.srt")
        await self._create_srt_file(srt_path, captions)
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-i", video_url,
            "-vf", f"subtitles={srt_path}",
            "-c:a", "copy",
            output_path
        ]
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg captioning failed: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg captioning failed: {stderr.decode()}")
        
        # Cleanup SRT file
        os.unlink(srt_path)
        
        return output_path
    
    async def _create_srt_file(self, srt_path: str, captions: List[Dict[str, Any]]):
        """Create SRT subtitle file from captions data."""
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, caption in enumerate(captions, 1):
                start_time = self._format_srt_time(caption.get("start_time", 0))
                end_time = self._format_srt_time(caption.get("end_time", caption.get("start_time", 0) + 3))
                text = caption.get("text", "")
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
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
    
    async def _upload_to_storage(self, file_path: str) -> str:
        """Upload generated video to storage (R2)."""
        # TODO: Implement R2 upload with /templates/ prefix
        # For now, return a mock URL
        return f"https://storage.example.com/templates/generated_{datetime.now().timestamp()}.mp4"
