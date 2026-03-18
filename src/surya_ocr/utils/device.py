"""Device detection and CPU optimization."""

from __future__ import annotations

import os
import platform
import logging

log = logging.getLogger(__name__)


def get_physical_cores() -> int:
    """Return the number of physical CPU cores."""
    try:
        count = os.cpu_count()
        # On macOS, sysctl gives accurate physical core count
        if platform.system() == "Darwin":
            import subprocess
            result = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        # On Linux, count physical cores from /proc/cpuinfo
        if platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    cores = set()
                    for line in f:
                        if line.startswith("core id"):
                            cores.add(line.strip())
                    if cores:
                        return len(cores)
            except OSError:
                pass
        # Fallback: assume half of logical cores are physical
        return max(1, (count or 2) // 2)
    except Exception:
        return 4  # Safe default


def detect_device(requested: str = "auto") -> str:
    """Detect the best available device for inference.

    Returns one of: "cuda", "mps", "cpu".
    """
    import torch

    if requested != "auto":
        return requested

    if torch.cuda.is_available():
        log.info("CUDA GPU detected")
        return "cuda"

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        arch = platform.machine()
        if arch == "arm64":
            log.info("Apple Silicon MPS detected")
            return "mps"
        else:
            log.info("Intel Mac detected - MPS disabled for AMD GPU stability, using CPU")
            return "cpu"

    log.info("No GPU acceleration available, using CPU")
    return "cpu"


def configure_cpu_threads() -> None:
    """Configure optimal thread count for CPU inference."""
    cores = get_physical_cores()
    log.info(f"Configuring {cores} threads (physical cores)")

    os.environ["OMP_NUM_THREADS"] = str(cores)
    os.environ["MKL_NUM_THREADS"] = str(cores)

    try:
        import torch
        torch.set_num_threads(cores)
        torch.set_num_interop_threads(min(2, cores))
    except Exception as e:
        log.warning(f"Could not set torch thread count: {e}")
