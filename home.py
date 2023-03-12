import subprocess
from typing import Tuple

LIGHTS_ENTITY_ID = "light.disco_group"

def lights(state: bool, brightness_percent: int | None = None, brightness_step: int | None = None, rgbww: Tuple[int, int, int, int, int] | None = None):
    arg_list = []
    if state:
        if brightness_percent is not None:
            arg_list.append(f",brightness_pct={brightness_percent}")
        if brightness_step is not None:
            arg_list.append(f",brightness_step={brightness_step}")
        if rgbww is not None:
            arg_list.append(f",rgbww='{list(rgbww)}'")
    extra_args = "".join(arg_list)
    subprocess.call(
        [
        "hass-cli", "service",
        "call", f"light.turn_{'on' if state else 'off'}",
        "--arguments", f"entity_id={LIGHTS_ENTITY_ID}{extra_args}",
        ]
    )

def cringe_alert(state):
    # hass-cli state turn_on script.cringe_alert
    subprocess.call(
        [
            "hass-cli", "state",
            f"turn_{'on' if state else 'off'}", "script.cringe_alert",
        ]
    )

def disco_mode(state):
    # hass-cli state turn_on input_boolean.disco_mode
    subprocess.call(
        [
            "hass-cli", "state",
            f"turn_{'on' if state else 'off'}", "input_boolean.disco_mode",
        ]
    )

def play_music():
    # play music
    # hass-cli service call media_player.play_media --arguments entity_id=media_player.spotify,media_content_id="https://open.spotify.com/playlist/5xddIVAtLrZKtt4YGLM1SQ?si=YcvRqaKNTxOi043Qn4LYkg",media_content_type=playlist,entity_id=media_player.spotify_emil
    url = "https://open.spotify.com/playlist/5xddIVAtLrZKtt4YGLM1SQ?si=YcvRqaKNTxOi043Qn4LYkg"
    type = "playlist"
    subprocess.call(
        [
            "hass-cli", "service",
            "call", "media_player.play_media",
            "--arguments", f"entity_id=media_player.spotify,media_content_id={url},media_content_type={type},entity_id=media_player.spotify_emil",
        ]
    )
