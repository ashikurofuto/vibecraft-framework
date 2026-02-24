"""
QwenAdapter: runs Qwen CLI via subprocess, streams output back.

Qwen CLI is invoked as:
    qwen chat --no-interactive --message "<prompt>"
    OR piped:
    echo "<prompt>" | qwen chat

Adjust QWEN_CMD if your binary has a different name or flags.
"""

import subprocess
import shutil
from pathlib import Path


# Override via env var VIBECRAFT_QWEN_CMD if needed
QWEN_CMD = "qwen"


class QwenAdapter:
    def __init__(self, stream: bool = True):
        self.stream = stream
        self._check_available()

    def _check_available(self):
        if not shutil.which(QWEN_CMD):
            raise RuntimeError(
                f"Qwen CLI not found: '{QWEN_CMD}'\n"
                f"Make sure it's installed and on your PATH.\n"
                f"Override with env var: VIBECRAFT_QWEN_CMD=<your-command>"
            )

    def call(self, prompt: str, context_files: list[Path] | None = None) -> str:
        """
        Send prompt to Qwen CLI, return full response text.
        Streams output to terminal in real time.
        """
        cmd = self._build_command(prompt, context_files)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line buffered
        )

        output_lines = []

        # Stream stdout line by line
        for line in process.stdout:
            print(line, end="", flush=True)
            output_lines.append(line)

        process.wait()

        if process.returncode != 0:
            err = process.stderr.read()
            raise RuntimeError(f"Qwen CLI error (exit {process.returncode}):\n{err}")

        return "".join(output_lines)

    def _build_command(self, prompt: str, context_files: list[Path] | None) -> list[str]:
        """
        Build the CLI command. Adjust this method if your Qwen CLI
        has different flags or invocation style.
        """
        import os
        cmd_override = os.environ.get("VIBECRAFT_QWEN_CMD", QWEN_CMD)

        # Base command — adjust to match your Qwen CLI's actual interface
        cmd = [cmd_override, "chat", "--no-interactive"]

        # Attach context files if the CLI supports @file syntax
        if context_files:
            for f in context_files:
                if f.exists():
                    cmd += ["--file", str(f)]

        # Pass prompt via stdin to avoid shell escaping issues
        # We override Popen to use stdin pipe in call() when using this approach
        # For now: pass as --message flag (adjust if your CLI differs)
        cmd += ["--message", prompt]

        return cmd

    def call_with_stdin(self, prompt: str) -> str:
        """
        Alternative: pipe prompt via stdin.
        Use if your Qwen CLI reads from stdin rather than --message flag.
        """
        import os
        cmd_override = os.environ.get("VIBECRAFT_QWEN_CMD", QWEN_CMD)

        process = subprocess.Popen(
            [cmd_override, "chat", "--no-interactive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input=prompt)

        if process.returncode != 0:
            raise RuntimeError(f"Qwen CLI error:\n{stderr}")

        return stdout
