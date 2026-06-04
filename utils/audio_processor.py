import yt_dlp
import ffmpeg
import os
import wave
from urllib.parse import urlparse, urlunparse, parse_qs

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def normalize_youtube_url(url: str) -> str:
    """Normalize YouTube share URLs and strip transient query params."""
    parsed = urlparse(url)
    if parsed.netloc in ('youtu.be', 'www.youtu.be'):
        video_id = parsed.path.lstrip('/')
        return f'https://www.youtube.com/watch?v={video_id}'

    if parsed.netloc.endswith('youtube.com'):
        query = parse_qs(parsed.query)
        if 'v' in query:
            video_id = query['v'][0]
            return f'https://www.youtube.com/watch?v={video_id}'

    return url

def download_youtube_audio(url :str) ->str:
    url = normalize_youtube_url(url)
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "js_runtimes": {"deno": {}, "node": {}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "geo_bypass": True,
        "nocheckcertificate": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using ffmpeg."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    (
        ffmpeg.input(input_path)
        .output(output_path, format="wav", ac=1, ar=16000)
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    chunk_ms = chunk_minutes * 60 * 1000

    with wave.open(wav_path, "rb") as source:
        params = source.getparams()
        frame_rate = source.getframerate()
        total_frames = source.getnframes()
        chunk_frames = int(chunk_ms * frame_rate / 1000)

        chunks = []
        for i, start_frame in enumerate(range(0, total_frames, chunk_frames)):
            source.setpos(start_frame)
            frames = source.readframes(chunk_frames)

            chunk_path = f"{wav_path}_chunk_{i}.wav"
            with wave.open(chunk_path, "wb") as out_f:
                out_f.setparams(params)
                out_f.writeframes(frames)

            chunks.append(chunk_path)

    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks