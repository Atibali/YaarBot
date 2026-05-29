#!/usr/bin/env python3
"""Test emotion detection and personality manager"""

import sys
sys.path.insert(0, 'c:/Users/minha/Documents/atib/Charusat/sem7/YaarBot')

from emotion_detector import EmotionDetector
from personality_manager import PersonalityManager

detector = EmotionDetector()
manager = PersonalityManager()

test_cases = [
    "I'm so happy today!",
    "This is terrible and I hate it",
    "I'm feeling really sad right now",
    "How are you doing?",
    "That's amazing and wonderful!",
    "I'm so angry at this broken system",
]

print("Testing Emotion Detection & Personality Manager:\n")
print("-" * 70)

for text in test_cases:
    emotion_data = detector.detect(text)
    emotion = emotion_data["emotion"]
    polarity = emotion_data["polarity"]
    intensity = emotion_data["intensity"]

    system_prompt = manager.get_system_prompt_with_emotion(emotion_data)

    print(f"\nUser: {text}")
    print(f"Detected Emotion: {emotion} (polarity: {polarity:.2f}, intensity: {intensity:.2f})")
    print(f"\nSystem Prompt Addition:\n{system_prompt.split('---')[-1].strip() if '---' in system_prompt else system_prompt.split(chr(10)*2)[-1]}")
    print("-" * 70)

print("\nAll tests completed successfully!")
