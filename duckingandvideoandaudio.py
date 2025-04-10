import subprocess
import os


# Input files
voice_files = ["part1.m4a", "part2.m4a", "part3.m4a"]
background_music = "Kutle_background_music2.wav"
# output_file = "final_with_ducking_looped.mp3"
# mono_output_file = "final_with_ducking_looped_mono.mp3"
image_file = "main.PNG"

# Output files
output_file = "final_with_ducking_looped.mp3"
mono_output_file = "final_with_ducking_looped_mono.mp3"
final_video_file = "final_video_for_youtube.mp4"

# Step 1: Concatenate voice files
concat_list = "voice_concat.txt"
with open(concat_list, "w") as f:
    for file in voice_files:
        f.write(f"file '{os.path.abspath(file)}'\n")

combined_voice = "combined_voice.m4a"
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", combined_voice
], check=True)

# Step 2: Get duration of combined voice
result = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", combined_voice
], capture_output=True, text=True)

voice_duration = float(result.stdout.strip())
looped_bg = "looped_background.wav"

# Step 3: Loop background music to match/exceed voice duration
subprocess.run([
    "ffmpeg", "-y", "-stream_loop", "-1", "-i", background_music,
    "-t", str(voice_duration + 1),  # +1 sec buffer
    "-c", "copy", looped_bg
], check=True)

# Step 4: Apply ducking with looped background
subprocess.run([
    "ffmpeg", "-y",
    "-i", combined_voice,
    "-i", looped_bg,
    "-filter_complex",
    "[1:a]volume=4dB[bg];[bg][0:a]sidechaincompress=threshold=0.1:ratio=4:attack=5:release=300[ducked];[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=3",
    "-c:a", "libmp3lame", "-b:a", "192k",
    output_file
], check=True)

# Step 5: Convert stereo to mono
subprocess.run([
    "ffmpeg", "-y", "-i", output_file,
    "-ac", "1", mono_output_file
], check=True)


print(f"✅ Done! Final ducked MP3 with looped background: {output_file}")

# Step 6: Create a video using image and mono audio
subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1",  # Loop the image
    "-i", image_file,
    "-i", mono_output_file,
    "-c:v", "libx264",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    final_video_file
], check=True)

print(f"🎬 Done! Final video created: {final_video_file}")


