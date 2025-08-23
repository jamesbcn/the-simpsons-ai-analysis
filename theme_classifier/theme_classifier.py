import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from transformers import pipeline 
import nltk
from nltk.tokenize import sent_tokenize
from time import time
import matplotlib.pyplot as plt
import torch
import re
import os, sys

import pathlib
folder_path = pathlib.Path(__file__).parent.resolve() # Get the directory of the current script
sys.path.append(os.path.join(folder_path,'../')) # Add the parent directory to sys.path to allow imports from there
from utils import load_subtitles_dataset

# Function to check if running in a virtual environment
def in_venv():
    return sys.prefix != sys.base_prefix


# Ensure NLTK resources are available. If not, download them to the appropriate location.
def ensure_nltk_resources(resources=("punkt", "punkt_tab")):
    
    for resource in resources:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            if in_venv():
                venv_nltk_path = os.path.join(sys.prefix, "nltk_data")
                nltk.download(resource, download_dir=venv_nltk_path)
                nltk.data.path.append(venv_nltk_path)
            else:
                nltk.download(resource)

ensure_nltk_resources()


class ThemeClassifier():
    
    def __init__(self, theme_list):
        self.model_name = "facebook/bart-large-mnli"
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        self.theme_list = theme_list
        self.theme_classifier = self.load_model(self.device)
    
    def load_model(self,device):
        theme_classifier = pipeline(
            "zero-shot-classification",
            model=self.model_name,
            device=device
        )

        return theme_classifier

    def get_themes_inference(self, script):
        
        script_sentences = sent_tokenize(script)

        # Batch Sentence
        sentence_batch_size=20
        script_batches = []
        for index in range(0,len(script_sentences),sentence_batch_size):
            sent = " ".join(script_sentences[index:index+sentence_batch_size])
            script_batches.append(sent)
        
        # Run Model
        theme_output = self.theme_classifier(
            script_batches,
            self.theme_list,
            multi_label=True
        )

        # Wrangle Output 
        themes = {}
        for output in theme_output:
            for label,score in zip(output['labels'],output['scores']):
                if label not in themes:
                    themes[label] = []
                themes[label].append(score)

        themes = {key: np.mean(np.array(value)) for key,value in themes.items()}

        return themes

    def get_themes(self, dtaset_path, save_path=None):
        
        # Read Save Output if Exists
        if save_path is not None and os.path.exists(save_path):
            df = pd.read_csv(save_path)
            return df

        # load Dataset
        df = load_subtitles_dataset(dtaset_path)

        # Run Inference
        output_themes = df['script'].apply(self.get_themes_inference)

        themes_df = pd.DataFrame(output_themes.tolist())
        df[themes_df.columns] = themes_df

        # Save output
        if save_path is not None:
            df.to_csv(save_path,index=False)
        
        return df