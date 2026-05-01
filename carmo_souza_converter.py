#!/usr/bin/env python3
"""
Carmo-Souza V8 data converter.

Zero-dependency converter for exported CSV/JSON data from the Carmo-Souza
simulator or any simple numeric table. It normalizes records to:

    time,x,s

and writes:
    normalized.csv
    metrics.json
    report.md

Usage:
    python carmo_souza_converter.py input.csv -o out
    python carmo_souza_converter.py input.json -o out --alpha 1 --beta 1 --delta 1
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TIME_KEYS = {"t", "time", "tempo", "step", "iteration", "iteracao", "iteração", "frame"}
X_KEYS = {"x", "pos", "position", "posicao", "posição", "space", "i", "index", "indice", "índice"}
S_KEYS = {"s", "state", "valor", "value", "u", "psi", "solution", "solucao", "solução", "amplitude"}


def slug(key: Any) -> str:
    text = str(key).strip().lower()
    text = text.replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
    text = text.replace("é", "e").replace("ê", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ô", "o").replace("õ", "o").replace("ú", "u").replace("ç", "c")
    return re.sub(r"[^a-z0-9_]+", "_", text).strip("_")


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isfinite(float(value)):
            return float(value)
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(";", "")
    # Accept Brazilian decimal comma when there is no dot.
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        num = float(text)
    except ValueError:
        return None
    return num if math.isfinite(num) else None


def first_matching_key(row: Dict[str, Any], options: set[str]) -> Optional[str]:
    for key in row.keys():
        if slug(key) in options:
            return key
    return None


def find_records_in_json(obj: Any) -> List[Any]:
    """Find the first plausible list of records/numbers inside a JSON object."""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        preferred = ["data", "rows", "records", "points", "history", "simulations", "result", "results"]
        for key in preferred:
            if key in obj and isinstance(obj[key], list):
                return obj[key]
        for value in obj.values():
            found = find_records_in_json(value)
            if found:
                return found
    return []


def load_csv(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    sample = raw[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        return []

    # Try header mode first.
    reader = csv.DictReader(lines, dialect=dialect)
    rows = [dict(row) for row in reader if row]
    if rows and any(first_matching_key(rows[0], S_KEYS) for _ in [0]):
        return rows

    # No recognizable header: treat as a numeric matrix/vector.
    parsed: List[Dict[str, Any]] = []
    plain = csv.reader(lines, dialect=dialect)
    for i, row in enumerate(plain):
        nums = [to_float(cell) for cell in row]
        nums = [n for n in nums if n is not None]
        if not nums:
            continue
        if len(nums) == 1:
            parsed.append({"x": i, "s": nums[0]})
        elif len(nums) == 2:
            parsed.append({"x": nums[0], "s": nums[1]})
        else:
            # Wide matrix: each column is a spatial point, row is time/frame.
            for j, n in enumerate(nums):
                parsed.append({"time": i, "x": j, "s": n})
    return parsed


def load_input(path: Path) -> List[Any]:
    ext = path.suffix.lower()
    if ext == ".json":
        obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
        return find_records_in_json(obj)
    return load_csv(path)


def normalize(records: Iterable[Any]) -> List[Dict[str, float]]:
    normalized: List[Dict[str, float]] = []
    for idx, item in enumerate(records):
        if isinstance(item, dict):
            time_key = first_matching_key(item, TIME_KEYS)
            x_key = first_matching_key(item, X_KEYS)
            s_key = first_matching_key(item, S_KEYS)
            if s_key is None:
                # If no named state column exists, choose the last numeric field.
                numeric_items = [(k, to_float(v)) for k, v in item.items()]
                numeric_items = [(k, v) for k, v in numeric_items if v is not None]
                if not numeric_items:
                    continue
                s_key, _ = numeric_items[-1]
            s = to_float(item.get(s_key))
            if s is None:
                continue
            x = to_float(item.get(x_key)) if x_key else None
            t = to_float(item.get(time_key)) if time_key else None
            normalized.append({"time": t if t is not None else 0.0, "x": x if x is not None else float(idx), "s": s})
        else:
            s = to_float(item)
            if s is not None:
                normalized.append({"time": 0.0, "x": float(idx), "s": s})
    normalized.sort(key=lambda r: (r["time"], r["x"]))
    return normalized


def split_by_time(rows: List[Dict[str, float]]) -> Dict[float, List[Dict[str, float]]]:
    frames: Dict[float, List[Dict[str, float]]] = {}
    for row in rows:
        frames.setdefault(row["time"], []).append(row)
    for frame in frames.values():
        frame.sort(key=lambda r: r["x"])
    return frames


def frame_metrics(frame: List[Dict[str, float]], alpha: float, beta: float, delta: float) -> Dict[str, float]:
    values = [r["s"] for r in frame]
    xs = [r["x"] for r in frame]
    if not values:
        return {}
    dxs = [abs(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]
    dx = sum(dxs) / len(dxs) if dxs else 1.0
    if dx <= 0:
        dx = 1.0
    l2 = math.sqrt(sum(v * v for v in values) * dx)
    mean = sum(values) / len(values)
    vmin = min(values)
    vmax = max(values)
    total_variation = sum(abs(values[i + 1] - values[i]) for i in range(len(values) - 1))
    grad_energy = 0.0
    for i in range(len(values) - 1):
        local_dx = abs(xs[i + 1] - xs[i]) or dx
        grad = (values[i + 1] - values[i]) / local_dx
        grad_energy += 0.5 * beta * grad * grad * local_dx
    potential = sum((0.5 * alpha * v * v + delta * (0.25 * v ** 4 - 0.5 * v * v)) * dx for v in values)
    return {
        "n": float(len(values)),
        "l2_norm": l2,
        "energy_functional": grad_energy + potential,
        "min": vmin,
        "max": vmax,
        "mean": mean,
        "total_variation": total_variation,
    }


def compute_metrics(rows: List[Dict[str, float]], alpha: float, beta: float, delta: float) -> Dict[str, Any]:
    frames = split_by_time(rows)
    frame_list = []
    for t, frame in sorted(frames.items()):
        item = {"time": t}
        item.update(frame_metrics(frame, alpha, beta, delta))
        frame_list.append(item)
    final = frame_list[-1] if frame_list else {}
    return {
        "schema": "carmo-souza-v8-normalized",
        "parameters": {"alpha": alpha, "beta": beta, "delta": delta},
        "epistemic_status": "E8 - Resultado computacional; requer validacao externa para alegacoes cientificas fortes.",
        "frames": frame_list,
        "final": final,
    }


def write_outputs(rows: List[Dict[str, float]], metrics: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "normalized.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "x", "s"])
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    final = metrics.get("final", {})
    report = [
        "# Carmo-Souza V8 - Relatorio de Conversao",
        "",
        f"Pontos normalizados: {len(rows)}",
        f"Frames temporais: {len(metrics.get('frames', []))}",
        f"Status epistemologico: {metrics.get('epistemic_status')}",
        "",
        "## Metricas finais",
        "",
    ]
    for key in ["l2_norm", "energy_functional", "min", "max", "mean", "total_variation"]:
        if key in final:
            report.append(f"- {key}: {final[key]:.12g}")
    report.append("")
    report.append("## Arquivos gerados")
    report.append("- normalized.csv")
    report.append("- metrics.json")
    (out_dir / "report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Converte CSV/JSON para o formato Carmo-Souza V8 normalizado.")
    parser.add_argument("input", help="Arquivo CSV ou JSON de entrada")
    parser.add_argument("-o", "--out", default="converted", help="Pasta de saida")
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--delta", type=float, default=1.0)
    args = parser.parse_args()

    rows = normalize(load_input(Path(args.input)))
    if not rows:
        raise SystemExit("Nenhum dado numerico reconhecido. Use colunas como x,s,time ou envie uma matriz numerica.")
    metrics = compute_metrics(rows, alpha=args.alpha, beta=args.beta, delta=args.delta)
    write_outputs(rows, metrics, Path(args.out))
    print(f"OK: {len(rows)} pontos convertidos em {os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
