"""Utilitários dos testes adicionais (test_my_*.py).

Complementa helpers.py sem alterá-lo: aqui o CLI pode terminar com qualquer código de
saída, a tabela de taxas é configurável e é possível rodar sobre um arquivo existente.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR

DEFAULT_RATES = "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n"
DATA_DIR = PROJECT_ROOT / "data"


def write_rows(path: Path, rows: list[dict[str, str]], columns: list[str] = COLUMNS) -> Path:
    """Grava um CSV com o cabeçalho informado; cada linha parte de BASE."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)
    return path


def run_cli_process(
    tmp_path: Path,
    rows: list[dict[str, str]] | None = None,
    *,
    input_path: Path | None = None,
    input_bytes: bytes | None = None,
    rates_text: str | None = None,
    rates_path: Path | None = None,
    output_path: Path | None = None,
    args: list[str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    """Executa o CLI e devolve o processo, sem exigir código de saída 0.

    Por padrão grava `rows` em um CSV temporário, usa as mesmas taxas de helpers.py e grava o
    relatório em tmp_path/report.json. `args` substitui `--output`, permitindo testar argumentos.
    """
    if input_path is None:
        input_path = tmp_path / "reservas.csv"
        if input_bytes is not None:
            input_path.write_bytes(input_bytes)
        else:
            write_rows(input_path, rows or [])
    if rates_path is None:
        rates_path = tmp_path / "rates.csv"
        rates_path.write_text(DEFAULT_RATES if rates_text is None else rates_text, encoding="utf-8")

    command = ["--input", str(input_path), "--rates", str(rates_path)]
    if args is None:
        command += ["--output", str(output_path or tmp_path / "report.json")]
    else:
        command += args
    return run_cli_raw(command, cwd=cwd)


def run_cli_raw(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Executa `python -m onfly_report` com exatamente os argumentos informados."""
    command = [sys.executable, "-m", "onfly_report", *args]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        command,
        cwd=str(cwd or PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )


def run_cli_on_file(tmp_path: Path, input_path: Path, top: int = 5) -> dict:
    """Executa o CLI sobre um arquivo existente (ex.: data/) e devolve o relatório."""
    output_path = tmp_path / "report.json"
    process = run_cli_process(
        tmp_path,
        input_path=input_path,
        rates_path=DATA_DIR / "taxas_cambio.csv",
        args=["--output", str(output_path), "--top", str(top)],
    )
    assert process.returncode == 0, process.stderr
    return json.loads(output_path.read_text(encoding="utf-8"))


def assert_invalid_input(process: subprocess.CompletedProcess, output_path: Path | None = None) -> None:
    """Entrada inválida: exit 2, mensagem de log limpa (sem traceback) e nenhum relatório."""
    assert process.returncode == 2, f"exit={process.returncode}\n{process.stderr}"
    assert "Traceback" not in process.stderr, process.stderr
    assert process.stdout == ""
    if output_path is not None:
        assert not output_path.exists()
