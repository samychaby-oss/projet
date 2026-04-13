import pandas as pd
import random

n_samples = 500
human_templates = [
    "I remember when {person} told me about {topic}.",
    "It was a {adj} day, and I felt {emotion} while {action}.",
    "Honestly, {topic} is something I've always struggled with.",
    "I went to the {place} this morning, the {thing} was {adj}.",
    "Do you ever feel like {topic} is just too much sometimes?",
    "My {person} used to say that {topic} defines who we are.",
    "I stopped by the {place} and saw a {adj} {thing}, it made me smile.",
    "Looking at the {thing}, I realized how much I missed {place}."
]

ai_templates = [
    "Furthermore, the integration of {topic} facilitates {adj} results.",
    "It is important to emphasize that {topic} represents a significant shift.",
    "In conclusion, the socio-economic impact of {topic} is profound.",
    "The optimization of {thing} allows for enhanced {topic} performance.",
    "Moreover, the mathematical modeling of {topic} reveals {adj} patterns.",
    "Statistical analysis indicates that {topic} correlates with {thing}.",
    "The implementation of these {adj} systems transforms {topic}.",
    "Consequently, the analytical framework for {topic} must be reevaluated."
]

words = {
    "person": ["my grandfather", "the barista", "my sister", "a neighbor", "the teacher"],
    "topic": ["artificial intelligence", "global warming", "digital marketing", "daily life", "machine learning"],
    "adj": ["beautiful", "complex", "dusty", "innovative", "freezing", "strategic", "technical"],
    "emotion": ["refreshed", "confused", "happy", "nostalgic", "ready"],
    "action": ["walking the dog", "drinking coffee", "reading old letters", "working hard"],
    "place": ["park", "attic", "coffee shop", "office", "garden"],
    "thing": ["box", "algorithm", "sun", "system", "data set", "letters"]
}

def generate_text(templates):
    texts = []
    for _ in range(n_samples):
        tmpl = random.choice(templates)
        texts.append(tmpl.format(**{k: random.choice(v) for k, v in words.items()}))
    return texts

df_human = pd.DataFrame({'text': generate_text(human_templates), 'label': 0})
df_ai = pd.DataFrame({'text': generate_text(ai_templates), 'label': 1})
df_final = pd.concat([df_human, df_ai]).sample(frac=1).reset_index(drop=True)

df_final.to_csv('ghostbot_1k_balanced.csv', index=False)
print("✅ Fichier 'ghostbot_1k_balanced.csv' créé avec succès !")