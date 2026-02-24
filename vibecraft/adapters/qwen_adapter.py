"""
QwenAdapter: runs Qwen CLI via subprocess, streams output back.

Qwen CLI is invoked as:
    qwen chat --no-interactive --message "<prompt>"

Adjust QWEN_CMD if your binary has a different name or flags.
Override via env var: VIBECRAFT_QWEN_CMD=<your-command>
"""

import os
import subprocess
import shutil
from pathlib import Path

from .base_adapter import BaseAdapter

QWEN_CMD = "qwen"


class QwenAdapter(BaseAdapter):
    def __init__(self, stream: bool = True):
        self.stream = stream
        self._check_available()

    # ------------------------------------------------------------------

    def _check_available(self):
        cmd = os.environ.get("VIBECRAFT_QWEN_CMD", QWEN_CMD)
        if not shutil.which(cmd):
            raise RuntimeError(
                f"Qwen CLI not found: '{cmd}'\n"
                f"Install it and make sure it's on your PATH.\n"
                f"Override command: VIBECRAFT_QWEN_CMD=<your-command>\n"
                f"Use a different backend: VIBECRAFT_BACKEND=clipboard"
            )

    # ------------------------------------------------------------------

    def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
        """Send prompt to Qwen CLI, stream output to terminal, return full text."""
        cmd = self._build_command(prompt, context_files)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        output_lines: list[str] = []

        try:
            for line in process.stdout:
                print(line, end="", flush=True)
                output_lines.append(line)
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise RuntimeError("Interrupted by user (Ctrl+C)")
        finally:
            # Always wait for the process to avoid zombies
            process.wait()

        if process.returncode != 0:
            err = process.stderr.read()
            raise RuntimeError(
                f"Qwen CLI exited with code {process.returncode}:\n{err}"
            )

        return "".join(output_lines)

    # ------------------------------------------------------------------

    def _build_command(
        self, prompt: str, context_files: list[Path] | None
    ) -> list[str]:
        cmd_bin = os.environ.get("VIBECRAFT_QWEN_CMD", QWEN_CMD)
        cmd = [cmd_bin, "chat", "--no-interactive"]

        if context_files:
            for f in context_files:
                if f.exists():
                    cmd += ["--file", str(f)]

        cmd += ["--message", prompt]
        return cmd

    # ------------------------------------------------------------------

    def call_with_stdin(self, prompt: str) -> str:
        """Alternative: pipe prompt via stdin instead of --message flag."""
        cmd_bin = os.environ.get("VIBECRAFT_QWEN_CMD", QWEN_CMD)

        process = subprocess.Popen(
            [cmd_bin, "chat", "--no-interactive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = process.communicate(input=prompt, timeout=300)
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            raise RuntimeError("Interrupted by user (Ctrl+C)")
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RuntimeError("Qwen CLI timed out after 300s")

        if process.returncode != 0:
            raise RuntimeError(f"Qwen CLI error:\n{stderr}")

        return stdout
