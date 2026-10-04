import logging
import os

import yaml
from elevenlabs import ElevenLabs

logger = logging.getLogger(__name__)


def generate_audio_brief(text: str):
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    if not os.path.exists(config_path):
        return None

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    api_key = cfg.get("integrations", {}).get("elevenlabs_api_key")
    if not api_key:
        return None

    try:
        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            voice_id="JBFqnCBcs6RMkjGVYIV_",  # George
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        )

        output_dir = os.path.join(os.path.dirname(__file__), "..", "web", "static")
        output_path = os.path.join(output_dir, "brief.mp3")

        with open(output_path, "wb") as f:
            f.writelines(audio)

        return output_path
    except Exception as e:  # noqa: BLE001
        logger.error(f"ElevenLabs TTS failed: {e}")
        return None
