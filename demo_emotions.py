#!/usr/bin/env python3
"""
YaarBot Emotional Intelligence Demo
====================================

Test emotionally intelligent responses with different scenarios.
"""

import sys
sys.path.insert(0, '.')

from emotion_detector import EmotionDetector
from personality_manager import PersonalityManager


def main():
    detector = EmotionDetector()
    manager = PersonalityManager()

    test_scenarios = [
        {
            "user_input": "I just got promoted at work! I'm so excited!",
            "expected_emotion": "joy",
            "description": "Happy milestone"
        },
        {
            "user_input": "I've been trying to fix this bug all day and it's still broken",
            "expected_emotion": "anger",
            "description": "Frustrated developer"
        },
        {
            "user_input": "I'm feeling really down today, nothing seems to be going right",
            "expected_emotion": "sadness",
            "description": "Sad user needing support"
        },
        {
            "user_input": "Tell me about the latest AI developments",
            "expected_emotion": "curious",
            "description": "Inquisitive learner"
        },
        {
            "user_input": "The weather is nice today",
            "expected_emotion": "neutral",
            "description": "Casual observation"
        },
    ]

    print("\n" + "=" * 80)
    print("YaarBot Emotional Intelligence Demo".center(80))
    print("=" * 80 + "\n")

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Scenario {i}: {scenario['description']}")
        print("-" * 80)

        user_input = scenario["user_input"]
        emotion_data = detector.detect(user_input)

        print(f"\nUser Says: \"{user_input}\"")
        print(f"\nEmotion Detected: {emotion_data['emotion'].upper()}")
        print(f"   * Polarity: {emotion_data['polarity']:+.2f}")
        print(f"   * Intensity: {emotion_data['intensity']:.2%}")
        print(f"   * Is Question: {emotion_data['is_question']}")

        system_prompt = manager.get_system_prompt_with_emotion(emotion_data)
        emotion_instruction = manager.get_emotion_context_instruction(emotion_data)

        print(f"\nPersonality Instruction:")
        print(f"   {emotion_instruction}")

        should_use_dark = manager.should_use_dark_humor(
            emotion_data['emotion'],
            emotion_data['intensity']
        )
        print(f"\nDark Humor OK: {should_use_dark}")

        print("\n" + "=" * 80 + "\n")

    print("\nDemo complete! YaarBot is ready to respond with emotional intelligence.")
    print("\nTo start the full voice assistant, run: python assistant.py\n")


if __name__ == "__main__":
    main()
