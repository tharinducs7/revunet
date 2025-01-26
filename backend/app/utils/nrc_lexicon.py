import os

def load_nrc_lexicon():
    """
    Load the NRC Emotion Lexicon into a dictionary.

    Returns:
        dict: A dictionary where keys are words and values are lists of associated emotions.
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../NRC-Emotion-Lexicon-Wordlevel-v0.92.txt")
    nrc_lexicon = {}
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"NRC Emotion Lexicon file not found at: {file_path}")

    with open(file_path, "r") as f:
        for line in f:
            if not line.strip() or len(line.strip().split("\t")) != 3:
                continue
            word, emotion, association = line.strip().split("\t")
            if int(association) == 1:  # Include words with emotional associations
                nrc_lexicon.setdefault(word, []).append(emotion)
    
    return nrc_lexicon
