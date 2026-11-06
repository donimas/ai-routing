"""Offline test for router.py: the real anthropic SDK client, a fake HTTP transport.

No API key, no network. Checks the request bodies the SDK actually serialises.
Run: pip install anthropic pytest && pytest -q examples/test_router.py
by @donimas · AI Levels series
"""
import json

import anthropic

try:  # anthropic 2.x ships on httpx2; older releases use httpx
    import httpx2 as httpx
except ImportError:
    import httpx

import router


def fake_client(classifier_reply):
    sent = []

    def handler(request):
        body = json.loads(request.content)
        sent.append(body)
        text = classifier_reply if body["model"] == router.CLASSIFIER and len(sent) == 1 else "done"
        return httpx.Response(200, json={
            "id": "msg_test", "type": "message", "role": "assistant", "model": body["model"],
            "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
            "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 1},
        })

    client = anthropic.Anthropic(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    return client, sent


def test_risky_task_goes_to_opus_high():
    client, sent = fake_client("risky")
    label, model, effort, _ = router.route(client, "Change the password hashing in auth.py")
    assert (label, model, effort) == ("risky", "claude-opus-5-5", "high")
    assert sent[0]["model"] == "claude-haiku-5-5"
    assert sent[0]["output_config"] == {"effort": "low"}
    assert sent[0]["thinking"] == {"type": "disabled"}
    assert sent[1]["output_config"] == {"effort": "high"}


def test_lookup_goes_to_haiku_low():
    client, sent = fake_client(" Lookup\n")
    assert router.route(client, "Where is parse_date defined?")[1:3] == ("claude-haiku-5-5", "low")


def test_unknown_label_falls_back_to_middle_tier():
    client, sent = fake_client("I think this is probably an edit")
    label, model, effort, _ = router.route(client, "Do the thing")
    assert label is None
    assert (model, effort) == router.FALLBACK == ("claude-sonnet-5-5", "medium")
    assert sent[1]["model"] == "claude-sonnet-5-5"
