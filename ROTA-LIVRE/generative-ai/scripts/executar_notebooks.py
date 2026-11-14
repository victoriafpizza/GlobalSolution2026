"""Executa os notebooks com o Python do ambiente ativo e salva as saídas."""

import os
import sys
from pathlib import Path

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / ".rag-local" / "kernels" / "rota-livre"


def main():
    KERNEL.mkdir(parents=True, exist_ok=True)
    import json
    (KERNEL / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "ROTA LIVRE local", "language": "python",
        "env": {"PYTHONUTF8": "1", "HF_HUB_OFFLINE": "1"},
    }), encoding="utf-8")
    os.environ["JUPYTER_PATH"] = str(KERNEL.parents[1])
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        client = NotebookClient(notebook, timeout=180, kernel_name="rota-livre",
                                resources={"metadata": {"path": str(ROOT)}})
        client.km = client.create_kernel_manager()
        client.execute()
        nbformat.validate(notebook)
        nbformat.write(notebook, path)
        print(f"{path.name}: saídas salvas")


if __name__ == "__main__":
    main()
