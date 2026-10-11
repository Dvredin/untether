"""A provider failure must not turn the next Codex message into a new chat."""

import pytest

from tests.test_exec_bridge import FakeTransport
from untether.markdown import MarkdownPresenter
from untether.model import ResumeToken
from untether.runner_bridge import ExecBridgeConfig, IncomingMessage, handle_message
from untether.runners.mock import ErrorReturn, Return, ScriptRunner
from untether.telegram.chat_sessions import ChatSessionStore

COOLDOWN_ERROR = (
    "unexpected status 503 Service Unavailable: HTTP responses session bridge "
    "is cooling down after repeated upstream timeouts; retry shortly."
)


@pytest.mark.anyio
@pytest.mark.parametrize("usage", [None, {}, {"input_tokens": 42}, {"num_turns": 0}])
@pytest.mark.parametrize(
    "error",
    [
        COOLDOWN_ERROR,
        "429 rate limit exceeded",
        "stream disconnected",
        "error_during_execution",
    ],
)
async def test_codex_failure_keeps_persisted_thread_for_followup(
    tmp_path, monkeypatch, error, usage
):
    monkeypatch.setattr("untether.settings.load_settings_if_exists", lambda: None)
    path = tmp_path / "chat_sessions.json"
    store = ChatSessionStore(path)
    resume = ResumeToken(engine="codex", value="retained-thread")
    await store.set_session_resume(123, 45, resume)
    other = ResumeToken(engine="codex", value="other-topic")
    await store.set_session_resume(123, 46, other)
    transport = FakeTransport()
    cfg = ExecBridgeConfig(
        transport=transport, presenter=MarkdownPresenter(), final_notify=True
    )
    failing = ScriptRunner([ErrorReturn(error=error, usage=usage)], engine="codex")
    cleared = []

    async def clear(token):
        cleared.append(token)
        await store.clear_engine_session(123, 45, token.engine)

    async def save(token, done):
        await store.set_session_resume(123, 45, token)

    await handle_message(
        cfg,
        runner=failing,
        incoming=IncomingMessage(
            channel_id=123, message_id=10, text="task", thread_id=45
        ),
        resume_token=resume,
        on_resume_failed=clear,
        on_thread_known=save,
    )
    assert cleared == []
    assert len(failing.calls) == 1  # Never automatically replay side effects.
    final = transport.send_calls[-1]["message"].text
    assert "conversation link is retained" in final
    assert "/new" not in final
    if error == COOLDOWN_ERROR:
        assert "Wait at least a minute" in final

    # Simulate a bridge restart: reload the on-disk store and route the next turn.
    reloaded = ChatSessionStore(path)
    saved = await reloaded.get_session_resume(123, 45, "codex")
    assert saved == resume
    assert await reloaded.get_session_resume(123, 46, "codex") == other
    followup = ScriptRunner([Return(answer="continued")], engine="codex")
    await handle_message(
        cfg,
        runner=followup,
        incoming=IncomingMessage(
            channel_id=123, message_id=11, text="continue", thread_id=45
        ),
        resume_token=saved,
    )
    assert followup.calls[0][1] == resume

    # The user's explicit reset remains available and topic-scoped.
    await reloaded.clear_sessions(123, 45)
    assert await reloaded.get_session_resume(123, 45, "codex") is None
    assert await reloaded.get_session_resume(123, 46, "codex") == other


@pytest.mark.anyio
async def test_legacy_other_engine_zero_turn_handling_is_unchanged(monkeypatch):
    monkeypatch.setattr("untether.settings.load_settings_if_exists", lambda: None)
    transport = FakeTransport()
    cfg = ExecBridgeConfig(
        transport=transport, presenter=MarkdownPresenter(), final_notify=True
    )
    resume = ResumeToken(engine="claude", value="broken-thread")
    runner = ScriptRunner(
        [ErrorReturn(error="error_during_execution", usage={"num_turns": 0})],
        engine="claude",
    )
    cleared = []

    async def clear(token):
        cleared.append(token)

    await handle_message(
        cfg,
        runner=runner,
        incoming=IncomingMessage(channel_id=123, message_id=12, text="task"),
        resume_token=resume,
        on_resume_failed=clear,
    )
    assert cleared == [resume]
