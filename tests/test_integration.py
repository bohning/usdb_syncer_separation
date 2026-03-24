"""Integration tests for the JSON-RPC server."""

import json
import subprocess
import unittest


class TestIntegration(unittest.TestCase):
    """Integration test cases for the usdb-syncer-separation server."""

    def setUp(self):
        self.cmd = ["uv", "run", "usdb-syncer-separation"]

    def test_basic_methods(self):
        # Spawn the process
        with subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as proc:
            self.assertIsNotNone(proc.stdin)
            self.assertIsNotNone(proc.stdout)

            requests = [
                {"jsonrpc": "2.0", "method": "get_spec_version", "id": 1},
                {"jsonrpc": "2.0", "method": "get_name", "id": 2},
                {"jsonrpc": "2.0", "method": "get_version", "id": 3},
                {"jsonrpc": "2.0", "method": "is_gpu_accelerated", "id": 4},
            ]

            for req in requests:
                proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()

            for _i, req in enumerate(requests):
                line = proc.stdout.readline()
                self.assertTrue(line, "Expected a response line")
                resp = json.loads(line)
                self.assertEqual(resp.get("jsonrpc"), "2.0")
                self.assertEqual(resp.get("id"), req["id"])
                self.assertIn("result", resp)

                if req["method"] == "get_spec_version":
                    self.assertEqual(resp["result"], "1")
                elif req["method"] == "get_name":
                    self.assertEqual(resp["result"], "usdb-syncer-separation")
                elif req["method"] == "get_version":
                    self.assertIsInstance(resp["result"], str)
                elif req["method"] == "is_gpu_accelerated":
                    self.assertIn(resp["result"], [True, False])

            proc.terminate()
            proc.wait(timeout=2)

    def test_invalid_request(self):
        with subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as proc:
            self.assertIsNotNone(proc.stdin)
            self.assertIsNotNone(proc.stdout)

            # invalid JSON-RPC
            proc.stdin.write("INVALID\n")
            proc.stdin.flush()

            line = proc.stdout.readline()
            self.assertTrue(line)
            resp = json.loads(line)
            self.assertEqual(resp.get("error").get("code"), -32700)  # Parse error

            proc.terminate()
            proc.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
