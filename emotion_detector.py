from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Any
import re
import nltk


class EmotionDetector:
    def __init__(self):
        try:
            self.analyzer = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
            self.analyzer = SentimentIntensityAnalyzer()

        self.emotion_history = []

    def detect(self, text: str) -> dict[str, Any]:
        """Analyze user text and return emotion label + intensity."""
        vader_scores = self.analyzer.polarity_scores(text)

        emotion = self._map_to_emotion(text, vader_scores)
        polarity = vader_scores["compound"]
        intensity = abs(polarity)
        is_question = self._is_question(text)

        result = {
            "emotion": emotion,
            "polarity": polarity,
            "intensity": intensity,
            "is_question": is_question,
        }

        self.emotion_history.append(emotion)
        if len(self.emotion_history) > 5:
            self.emotion_history.pop(0)

        return result

    def _map_to_emotion(self, text: str, vader_scores: dict) -> str:
        """Convert VADER scores to human emotion label."""
        compound = vader_scores["compound"]
        text_lower = text.lower()

        angry_keywords = ["hate", "angry", "furious", "disgusted", "broken", "stupid", "useless", "terrible"]
        sad_keywords = ["sad", "down", "depressed", "unhappy", "miserable", "lonely", "crying", "feeling really sad"]
        happy_keywords = ["happy", "great", "wonderful", "awesome", "excellent", "love", "amazing", "fantastic"]

        has_angry = any(word in text_lower for word in angry_keywords)
        has_sad = any(word in text_lower for word in sad_keywords)
        has_happy = any(word in text_lower for word in happy_keywords)

        if compound > 0.5 or has_happy:
            return "joy"
        elif has_sad:
            return "sadness"
        elif has_angry or compound < -0.5:
            return "anger"
        elif compound < -0.3:
            return "sadness"
        elif self._is_question(text):
            return "curious"
        else:
            return "neutral"

    def _is_question(self, text: str) -> bool:
        """Check if text is a question."""
        return "?" in text or text.strip().startswith(("how ", "what ", "why ", "where ", "when ", "who "))

    def get_emotion_trend(self) -> str:
        """Get overall mood trend from recent emotions."""
        if not self.emotion_history:
            return "neutral"

        joy_count = self.emotion_history.count("joy")
        sadness_count = self.emotion_history.count("sadness")
        anger_count = self.emotion_history.count("anger")

        if joy_count > 2:
            return "upbeat"
        elif sadness_count > 2:
            return "down"
        elif anger_count > 2:
            return "frustrated"
        else:
            return "neutral"
