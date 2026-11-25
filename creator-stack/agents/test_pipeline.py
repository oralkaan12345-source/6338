import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from pipeline import (
    BridgeError, BriefError, DisableRedirect, MAX_RESPONSE, OllamaBridge,
    ROLE_NAMES, load_brief, run,
)

HERE = Path(__file__).resolve().parent


def body(data):
    return io.BytesIO(json.dumps({"message": {"content": json.dumps(data)}}).encode())


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.brief = load_brief(HERE / "examples" / "gece-treni.json")

    def test_offline_fiction_no_socket(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            result = run(self.brief)
        self.assertEqual(result["trace"], ROLE_NAMES)
        self.assertEqual(result["review"]["status"], "DRAFT_OK")
        self.assertTrue(result["review"]["human_review_required"])
        self.assertFalse(result["published"])
        self.assertEqual(result["scenes"][-1]["end"], 30)

    def test_factual_note_provenance_no_fetch(self):
        brief = load_brief(HERE / "examples" / "ay-evreleri.json")
        with patch.object(socket.socket, "connect", side_effect=AssertionError("No source fetch")):
            result = run(brief)
        self.assertEqual(result["review"]["status"], "DRAFT_OK")
        self.assertEqual(result["scenes"][2]["source_ids"], ["N2"])
        self.assertTrue(result["research_notes"][1]["source_url"].startswith("https://"))
        self.assertIn("doğrulanmadı", result["review"]["verification"])

    def test_overlong_requires_revision(self):
        self.brief["hook"] = ("bir " * 14).strip()
        self.assertEqual(run(self.brief)["review"]["status"], "REVISION_NEEDED")

    def test_rejects_malformed_factual_brief(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "fixture.json"
            self.brief["kind"] = "factual"
            path.write_text(json.dumps(self.brief), encoding="utf-8")
            with self.assertRaises(BriefError):
                load_brief(path)

    def test_three_mocked_ollama_role_calls(self):
        bridge = OllamaBridge("gemma4:12b")
        lines = ["Fener neden söndü?", "Uyarı geri geldi.", "Denizin altında göz vardı.", "Fener adayı koruyordu."]
        bridge.opener = Mock()
        bridge.opener.open.side_effect = [
            body({"order": ["N2", "N1", "N3"]}), body({"lines": lines}), body({"notes": []}),
        ]
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            result = run(self.brief, bridge)
        self.assertEqual(result["trace"], ROLE_NAMES)
        self.assertEqual(result["mode"], "local-ollama")
        self.assertEqual(result["scenes"][1]["source_ids"], ["N2"])
        self.assertEqual(result["scenes"][-1]["narration"], lines[-1])
        self.assertEqual(bridge.calls, 3)
        for call in bridge.opener.open.call_args_list:
            (req,) = call.args
            self.assertEqual(req.full_url, "http://127.0.0.1:11434/api/chat")
            self.assertEqual(req.get_method(), "POST")
            data = json.loads(req.data)
            self.assertNotIn("tools", data)
            self.assertFalse(data["stream"])
            self.assertEqual(data["options"]["num_predict"], 384)
        with self.assertRaisesRegex(BridgeError, "budget"):
            bridge.ask("configuration", {})

    def test_no_redirects_or_cloud_id(self):
        with self.assertRaises(BridgeError):
            DisableRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")
        with self.assertRaises(BriefError):
            OllamaBridge("gemma4:cloud")

    def test_reject_model_tool_proposal(self):
        bridge = OllamaBridge("gemma4:12b")
        bridge.opener = Mock()
        bridge.opener.open.return_value = io.BytesIO(b'{"message":{"content":"{}","tool_calls":[{}]}}')
        with self.assertRaisesRegex(BridgeError, "tool call"):
            bridge.ask("return JSON", {})

    def test_reject_model_oversize_output(self):
        bridge = OllamaBridge("gemma4:12b")
        bridge.opener = Mock()
        bridge.opener.open.return_value = io.BytesIO(b'x' * (MAX_RESPONSE + 1))
        with self.assertRaisesRegex(BridgeError, "size limit"):
            bridge.ask("return JSON", {})

    def test_reject_model_invented_id(self):
        bridge = OllamaBridge("gemma4:12b")
        bridge.opener = Mock()
        bridge.opener.open.return_value = body({"order": ["N1", "N9", "N3"]})
        with self.assertRaisesRegex(BridgeError, "invalid source IDs"):
            run(self.brief, bridge)


if __name__ == "__main__":
    unittest.main()
