import os
import sys
import time
import requests
import subprocess
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

TOKEN = "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"

def convert_to_mp3(input_file):
    """Converts an audio file to MP3 format, ensuring compatibility."""
    output_file = os.path.splitext(input_file)[0] + ".mp3"
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', input_file,  # Input file
        '-acodec', 'libmp3lame',  # Use MP3 codec
        '-ar', '44100',  # Set audio sample rate to 44100 Hz
        '-ac', '2',  # Set audio to stereo
        output_file  # Output file
    ]
    subprocess.run(command, check=True)
    os.remove(input_file)  # Remove original file to save space
    return output_file

def generate_speech(text, OUTPUT_NAME, model="facebook/fastspeech2-en-ljspeech", api_key=TOKEN, retries=5):
    """Generates speech from text using the Hugging Face API."""
    time.sleep(15)
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": text, "options": {"use_cache": False}}
    
    for attempt in range(retries):
        response = requests.post(f"https://api-inference.huggingface.co/models/{model}", headers=headers, json=payload)
        if response.status_code == 200:
            file_path = os.path.join(OUTPUT_NAME, f"{text[:15].replace(' ', '_')}.wav")
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            # Convert to MP3 if necessary
            return convert_to_mp3(file_path)
        else:
            print(f"Attempt {attempt + 1} failed: {response.status_code} - {response.text}")
            time.sleep(50)  # Wait before retrying
    return None

def create_silent_audio(temp_dir, duration=1, sample_rate=44100, channels=2):
    """Creates a silent audio file."""
    silent_file_path = os.path.join(temp_dir, 'silent.mp3')
    command = [
        'ffmpeg',
        '-y',
        '-f', 'lavfi',
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ar', str(sample_rate),
        '-ac', str(channels),
        '-ab', '192k',
        silent_file_path
    ]
    subprocess.run(command, check=True)
    return silent_file_path

def concat_audio_files(audio_files, silent_file_path, output_file_name):
    """Concatenates audio files with silent intervals between them."""
    concat_string = '|'.join([f"{file}" for pair in zip(audio_files, [silent_file_path] * (len(audio_files) - 1)) for file in pair] + [audio_files[-1]])
    command = [
        'ffmpeg',
        '-y',
        '-i', f"concat:{concat_string}",
        '-acodec', 'libmp3lame',
        '-b:a', '320k',
        output_file_name + '.mp3'
    ]
    subprocess.run(command, check=True)

def remove_title_from_markdown(file_path):
    """Removes the title from the markdown file."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    title_removed = False
    content_without_title = []
    for line in lines:
        if line.startswith('#') and not title_removed:
            title_removed = True
            continue
        content_without_title.append(line)

    modified_content = ''.join(content_without_title)
    return modified_content

def main(text, OUTPUT_NAME):
    temp_dir = OUTPUT_NAME
    os.makedirs(temp_dir, exist_ok=True)
    sentences = sent_tokenize(text)
    audio_files = []

    for sentence in sentences:
        mp3_filename = os.path.join(temp_dir, f"{sentence[:15].replace(' ', '_')}.mp3")
        if not os.path.exists(mp3_filename):
            file_path = generate_speech(sentence, temp_dir)
            if file_path:
                audio_files.append(file_path)
        else:
            audio_files.append(mp3_filename)
            print(f"File already exists: {mp3_filename}")
        

    if audio_files:
        silent_file_path = create_silent_audio(temp_dir)
        concat_audio_files(audio_files, silent_file_path, OUTPUT_NAME)
        print("Audio concatenation complete. Output saved in:", OUTPUT_NAME + '.mp3')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py [tpo/neo] [number] [passage number]")
        sys.exit()

    tpo_neo, number, pnum = sys.argv[1], sys.argv[2], sys.argv[3]
    text_base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}', 'Text')
    audio_base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}', 'Audio')
    OUTPUT_NAME = os.path.join(audio_base_dir, f'{tpo_neo.upper()}{number}-Reading-P{pnum}')
    markdown_path = f'{os.path.join(text_base_dir, f"{tpo_neo.upper()}{number}-Reading-P{pnum}")}.md'
    print(OUTPUT_NAME)
    os.makedirs(audio_base_dir, exist_ok=True)
    
    with open(markdown_path, 'r') as file:
        passage = file.read()

    passage = remove_title_from_markdown(markdown_path)
    main(passage, OUTPUT_NAME)
