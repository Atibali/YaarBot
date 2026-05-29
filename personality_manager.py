from typing import Any


class PersonalityManager:
    def __init__(self):
        self.humor_enabled = True
        self.dark_humor_threshold = 0.5

    def get_emotion_context_instruction(self, emotion_data: dict[str, Any]) -> str:
        """Generate emotion-aware instructions to append to system prompt."""
        emotion = emotion_data.get("emotion", "neutral")
        intensity = emotion_data.get("intensity", 0.5)

        if emotion == "joy":
            return self._get_joy_instruction(intensity)
        elif emotion == "sadness":
            return self._get_sadness_instruction(intensity)
        elif emotion == "anger":
            return self._get_anger_instruction(intensity)
        elif emotion == "curious":
            return self._get_curious_instruction()
        else:
            return self._get_neutral_instruction()

    def _get_joy_instruction(self, intensity: float) -> str:
        """Generate instruction for joyful user."""
        base = "The user seems happy and in a good mood!"
        humor = " Match their energy with upbeat, friendly responses. Light humor and wit are welcome."

        if intensity > 0.7:
            return base + " Their joy is strong!" + humor
        return base + humor

    def _get_sadness_instruction(self, intensity: float) -> str:
        """Generate instruction for sad user with empathy."""
        base = "The user seems down or sad."
        empathy = " Be genuinely empathetic and supportive. Validate their feelings."

        if intensity > 0.8:
            humor = " Avoid humor for now—focus on understanding and warmth."
            return base + empathy + humor

        if intensity > 0.6:
            humor = " You can use gentle, reassuring humor if it feels natural—but keep it light and caring."
            return base + empathy + humor

        return base + empathy + " Light humor is okay if it brings a smile."

    def _get_anger_instruction(self, intensity: float) -> str:
        """Generate instruction for frustrated user."""
        base = "The user seems frustrated or angry."
        empathy = " Acknowledge their frustration without dismissing it."

        if intensity > 0.8:
            humor = " Avoid heavy jokes, but subtle sarcasm or cynicism can help. Stay on their side."
            return base + empathy + humor

        humor = " A bit of dark humor or sarcasm can work if the timing feels right. Show you understand their frustration."
        return base + empathy + humor

    def _get_curious_instruction(self) -> str:
        """Generate instruction for inquisitive user."""
        return (
            "The user is asking questions and seems curious or interested. "
            "Be informative, conversational, and encourage their curiosity. Light humor welcome."
        )

    def _get_neutral_instruction(self) -> str:
        """Generate instruction for neutral emotion."""
        return (
            "The user has a neutral tone. Keep responses balanced and friendly. "
            "Light humor and wit are welcome to keep conversation engaging."
        )

    def get_system_prompt_with_emotion(
        self, emotion_data: dict[str, Any], base_system: str | None = None
    ) -> str:
        """Generate complete system prompt with emotion context."""
        if base_system is None:
            base_system = (
                "You are YaarBot, a friendly real-time voice assistant. "
                "Reply conversationally and briefly. Be helpful, witty when asked, and safe. "
                "You have good humor and sometimes dark humor—use it wisely based on context."
            )

        emotion_instruction = self.get_emotion_context_instruction(emotion_data)
        return base_system + "\n\n" + emotion_instruction

    def should_use_dark_humor(self, emotion: str, intensity: float) -> bool:
        """Determine if dark humor is appropriate."""
        if not self.humor_enabled:
            return False

        if emotion == "anger" and intensity > 0.6:
            return True
        elif emotion == "sadness" and intensity < 0.8:
            return True
        elif emotion == "neutral" and intensity < 0.3:
            return True

        return False
