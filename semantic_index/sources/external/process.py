import subprocess
from typing import Optional
from charset_normalizer import from_bytes
import sys
import logging

logger = logging.getLogger(__name__)


def _decode_string(data: bytes) -> str:
    if not data:
        return ""
    try:
        result = from_bytes(data).best()
        if result is not None:
            return data.decode(result.encoding).strip()
    except Exception:
        logger.error(
            "Failed to decode using charset_normalizer, falling back to 'replace' decoding."
        )
    return data.decode(errors="replace").strip()


def run_subprocess_with_timeout(command_args: list[str], timeout_seconds: int) -> str:
    logger.debug(
        (
            f"Running subprocess: {' '.join(command_args)} "
            f"with timeout {timeout_seconds} seconds."
        )
    )

    process: Optional[subprocess.Popen] = None
    stdout_data: bytes = b""
    stderr_data: bytes = b""
    return_code = 999

    try:
        creation_flag = 0
        if sys.platform == "win32":
            # Windows specific flag to ensure proper termination
            creation_flag = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            command_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creation_flag,
        )

        stdout_data, stderr_data = process.communicate(timeout=timeout_seconds)
        return_code = process.returncode
        stdout = _decode_string(stdout_data)
        stderr = _decode_string(stderr_data)

        if return_code != 0 or stderr_data:
            logger.error(
                (
                    f"Subprocess failed with return code {return_code}. "
                    f" Stderr: {stderr[:200]}..."
                )
            )
            raise subprocess.CalledProcessError(
                returncode=return_code,
                cmd=command_args,
                output=stdout,
                stderr=stderr,
            )

        logger.debug(
            (
                f"Subprocess completed successfully with return code {return_code}. "
                f" Output: {stdout[:200]}..."
            )
        )
        return stdout

    except Exception as e:
        logger.error(f"Subprocess failed: {e}")
        if process and process.poll() is None:
            logger.warning("Terminate subprocess due to exception.")
            process.kill()
            process.wait()
        raise

    finally:
        if process and process.poll() is None:
            logger.debug("Terminating subprocess during cleanup.")
            process.kill()
            process.wait()
