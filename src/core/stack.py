from __future__ import annotations

import time
from typing import List
from typing import Optional
from typing import Protocol


class State(Protocol):
    def on_push(self, stack: "StateStack") -> None:
        pass

    def on_pop(self) -> None:
        pass

    def handle_input(self, key: int) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        pass


class StateStack:
    def __init__(self):
        self._stack: List[State] = []
        self.quit_requested: bool = False

    def push(self, state: State) -> None:
        self._stack.append(state)
        state.on_push(self)

    def pop(self) -> None:
        if self._stack:
            st = self._stack.pop()
            st.on_pop()

    def replace(self, state: State) -> None:
        self.pop()
        self.push(state)

    def clear(self) -> None:
        while self._stack:
            self.pop()

    def top(self) -> Optional[State]:
        return self._stack[-1] if self._stack else None

    def request_quit(self) -> None:
        self.quit_requested = True

    def run_loop(self, fps: int = 30) -> None:
        dt = 0.0
        frame = 1.0 / max(1, fps)
        last = time.time()
        while not self.quit_requested and self.top() is not None:
            now = time.time()
            dt = now - last
            last = now
            st = self.top()
            if st is None:
                break
            st.update(dt)
            st.draw()
            remaining = frame - (time.time() - now)
            if remaining > 0:
                time.sleep(remaining)
