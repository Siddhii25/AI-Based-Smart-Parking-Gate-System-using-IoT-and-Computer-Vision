"""
utils/frame_smoother.py
Temporal smoothing of per-frame slot counts to reduce YOLO jitter.
"""

from collections import deque


class FrameSmoother:
    """Returns a moving-average of the last `window` empty-slot counts."""

    def __init__(self, window: int = 5):
        self._buf = deque(maxlen=window)

    def update(self, value: int) -> int:
        self._buf.append(value)
        return round(sum(self._buf) / len(self._buf))
