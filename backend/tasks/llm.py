"""The team's LLM wrapper.

    reply = get_llm_client().complete(prompt)

`complete` returns the model's reply as raw text. The real model is not
reliable: even when a prompt asks for JSON it sometimes replies with prose, or
with JSON that is missing a key. `complete` raises `LLMError` when the model
can't be reached or doesn't answer in time.

This exercise never calls a real model. `TASKBOARD_LLM_CLIENT` in settings
points at `FakeLLMClient`, so no API key is needed.
"""

from django.conf import settings
from django.utils.module_loading import import_string


class LLMError(Exception):
    """The model couldn't be reached or didn't answer in time."""


class FakeLLMClient:
    """Stands in for the real model and returns `reply` for every prompt.

    Tests can change what it does:

        monkeypatch.setattr(FakeLLMClient, "reply", "Sorry, I can't help with that.")
        monkeypatch.setattr(FakeLLMClient, "error", LLMError("timed out"))
    """

    reply = "This is a reply from the fake model."
    error = None
    prompts = []  # every prompt it was sent, so tests can check them

    def complete(self, prompt: str) -> str:
        FakeLLMClient.prompts.append(prompt)
        if self.error is not None:
            raise self.error
        return self.reply


def get_llm_client():
    return import_string(settings.TASKBOARD_LLM_CLIENT)()
