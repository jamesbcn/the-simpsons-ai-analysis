from glob import glob 
import pandas as pd
import re, os


def load_subtitles_dataset(dataset_path):
    subtitles_paths = glob(dataset_path + "/*.srt")

    print(subtitles_paths)
    scripts = []
    episode_num = []

    for path in subtitles_paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        try:
            sentences = parse_srt(path)
            if sentences:
                print(f"Loaded {len(sentences)} sentences from {path}")

                script = " ".join(sentences).strip()
                season_episode = get_season_episode_code(os.path.basename(path))

                scripts.append(script)
                episode_num.append(season_episode)
                
        
            else:
                print(f"No valid sentences found in {path}")
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    df = pd.DataFrame.from_dict({
                    "episode": episode_num,
                    "script": scripts
                })
    return df


def parse_srt(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin-1') as f:
            lines = f.readlines()

    blocks = []
    block = []
    for line in lines:
        line = line.strip()
        if line == '':
            if block:
                blocks.append(block)
                block = []
        else:
            block.append(line)
    if block:
        blocks.append(block)

    sentences = []
    for block in blocks:
        text_lines = [
            l for l in block
            if not re.match(r'^\d+$', l)
            and not re.match(r'^\d{2}:\d{2}:\d{2},\d{3}', l)
            and '♪' not in l
            and not re.search(r'<.*?>', l)  # Remove lines with HTML tags
            and not re.search(r'www\.', l, re.IGNORECASE)  # Remove lines with URLs
        ]
        text_lines = [re.sub(r'{\\an\d+}', '', l) for l in text_lines]
        if text_lines:
            sentences.append(' '.join(text_lines))
    return sentences

def get_season_episode_code(filename):
    # Try SxxEyy format first
    match = re.search(r'[Ss](\d{2})[Ee](\d{2})', filename)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    # Try xxXyy format (e.g., 20x01)
    match = re.search(r'(\d{2})[xX](\d{2})', filename)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return None  # or handle missing code as needed

# Example usage:
files = glob("../data/subtitles/*.srt")
codes = [get_season_episode_code(os.path.basename(f)) for f in files]
codes = [c for c in codes if c is not None]
print(codes.__len__()   )