import argparse
import csv
import hashlib
import importlib.util
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs/wrangled/u2m/00_combined_test_to_methods.csv"
IMPLS = {
    "original": ROOT / "M4_Design/evidence/2-Overlap-JUnit-original.py",
    "optimised": ROOT / "analysis/2-Overlap-JUnit.py",
}
FROZEN_TAG = "PRE_EVENT_B"
PROJECT = "byte-buddy"

# frozen protocol (Event_B/Prediction.md)
SCALES = [0.25, 0.5, 1, 2, 4]
SEED = 4928
REPS_OPTIMISED = 5
REPS_ORIGINAL = 3
CAP_SECONDS = 15 * 60
TOLERANCE = 1e-12

RESULT_FIELDS = [
    "scale", "implementation", "mode", "run", "status", "tests",
    "test_pairs", "rows", "nan_objects", "seconds", "peak_mib",
    "overlap_ratio",
]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_base():
    """byte-buddy rows read exactly as the frozen JUnit overlap script reads them."""
    reader = load_module("frozen_reader", IMPLS["optimised"])
    df = reader.read_test_to_methods(str(INPUT))
    return df[df["Project Name"] == PROJECT]


def nan_objects(df):
    """Number of distinct NaN objects among the method entries."""
    return len({id(m) for m in df["Methods"] if isinstance(m, float)})


def build_dataset(base, scale):
    """Return byte-buddy's coverage rows scaled to `scale` times its tests.

    Below 1x: a seeded random sample of whole tests.
    Above 1x: k copies of the suite; each extra copy gets new test names and
    new method names (suffix #copyN). Empty/NaN entries are left unchanged.
    """
    if scale < 1:
        tests = pd.Series(base["Test Name"].unique())
        keep = tests.sample(n=round(scale * len(tests)), random_state=SEED)
        return base[base["Test Name"].isin(set(keep))]
    if scale == 1:
        return base
    copies = int(scale)
    if copies != scale:
        raise ValueError("scales above 1 must be whole numbers")
    parts = [base]
    for n in range(2, copies + 1):
        copy = base.copy()
        copy["Test Name"] = copy["Test Name"] + f"#copy{n}"
        copy["Methods"] = copy["Methods"].where(
            copy["Methods"].isna(), copy["Methods"] + f"#copy{n}"
        )
        parts.append(copy)
    return pd.concat(parts, ignore_index=True)


def worker(implementation, scale, mode):
    """Measure one run and print the result as one JSON line."""
    module = load_module(implementation, IMPLS[implementation])
    df = build_dataset(load_base(), scale)
    tests = df["Test Name"].nunique()
    seconds = peak_mib = None
    if mode == "memory":
        tracemalloc.start()
        ratio = module.calculate_overlap_ratio(df)
        peak_mib = tracemalloc.get_traced_memory()[1] / 2**20
        tracemalloc.stop()
    else:
        start = time.perf_counter()
        ratio = module.calculate_overlap_ratio(df)
        seconds = time.perf_counter() - start
    print(json.dumps({
        "tests": tests, "test_pairs": tests * (tests - 1) // 2,
        "rows": len(df), "nan_objects": nan_objects(df), "seconds": seconds, "peak_mib": peak_mib,
        "overlap_ratio": repr(float(ratio)),
    }))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(path):
    rel = path.relative_to(ROOT).as_posix()
    try:
        return subprocess.run(
            ["git", "show", f"{FROZEN_TAG}:{rel}"], cwd=ROOT,
            capture_output=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def git_head():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class Log:
    def __init__(self, path):
        self.file = open(path, "w", encoding="utf-8")

    def __call__(self, line=""):
        print(line, flush=True)
        self.file.write(line + "\n")
        self.file.flush()


def run_once(implementation, scale, mode, run):
    cmd = [sys.executable, str(Path(__file__).resolve()), "--worker",
           implementation, str(scale), mode]
    row = {"scale": scale, "implementation": implementation, "mode": mode,
           "run": run}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CAP_SECONDS)
    except subprocess.TimeoutExpired:
        row["status"] = "timeout"
        return row, ""
    if proc.returncode != 0:
        row["status"] = "error"
        return row, proc.stderr.strip()
    row.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    row["status"] = "ok"
    return row, ""


def fmt(value, digits=3):
    return "" if value is None else f"{value:.{digits}f}"


def summarise(rows, scales):
    summary = []
    for scale in scales:
        entry = {"scale": scale}
        for impl in ("optimised", "original"):
            timed = [r for r in rows if r["scale"] == scale
                     and r["implementation"] == impl and r["mode"] == "time"]
            ok = [r["seconds"] for r in timed if r["status"] == "ok"]
            mem = [r for r in rows if r["scale"] == scale
                   and r["implementation"] == impl and r["mode"] == "memory"]
            ratios = {r["overlap_ratio"] for r in timed + mem
                      if r["status"] == "ok"}
            entry[f"{impl}_median_s"] = statistics.median(ok) if ok else None
            entry[f"{impl}_runs_ok"] = f"{len(ok)}/{len(timed)}"
            entry[f"{impl}_timeout"] = any(r["status"] == "timeout"
                                           for r in timed)
            entry[f"{impl}_peak_mib"] = (mem[0].get("peak_mib")
                                         if mem and mem[0]["status"] == "ok"
                                         else None)
            entry[f"{impl}_memory_status"] = mem[0]["status"] if mem else ""
            entry[f"{impl}_ratio"] = (ratios.pop() if len(ratios) == 1
                                      else ("inconsistent" if ratios else None))
            for r in timed + mem:
                if r["status"] == "ok":
                    entry["tests"] = r["tests"]
                    entry["test_pairs"] = r["test_pairs"]
        o, p = entry["optimised_median_s"], entry["original_median_s"]
        entry["speedup"] = p / o if o and p else None
        om, pm = entry["optimised_peak_mib"], entry["original_peak_mib"]
        entry["memory_ratio_opt_to_orig"] = om / pm if om and pm else None
        ro, rp = entry["optimised_ratio"], entry["original_ratio"]
        try:
            diff = abs(float(ro) - float(rp))
            entry["abs_ratio_difference"] = diff
            entry["equivalent"] = diff < TOLERANCE
        except (TypeError, ValueError):
            entry["abs_ratio_difference"] = None
            entry["equivalent"] = None
        summary.append(entry)
    for prev, cur in zip(summary, summary[1:]):
        for impl in ("optimised", "original"):
            a, b = prev[f"{impl}_median_s"], cur[f"{impl}_median_s"]
            cur[f"{impl}_growth_vs_previous"] = b / a if a and b else None
    return summary


def main():
    parser = argparse.ArgumentParser(description="Event B: scaled JUnit workload for the JUnit overlap calculation.")
    parser.add_argument("--worker", nargs=3, metavar=("IMPL", "SCALE",
                        "MODE"), help=argparse.SUPPRESS)
    parser.add_argument("--scales", type=float, nargs="+", default=SCALES)
    parser.add_argument("--reps-optimised", type=int, default=REPS_OPTIMISED)
    parser.add_argument("--reps-original", type=int, default=REPS_ORIGINAL)
    parser.add_argument("--outdir", default=str(Path(__file__).parent))
    args = parser.parse_args()

    if args.worker:
        impl, scale, mode = args.worker
        worker(impl, float(scale), mode)
        return

    scales = [int(s) if float(s).is_integer() else s for s in args.scales]
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    log = Log(outdir / "run_log.txt")
    reps = {"optimised": args.reps_optimised, "original": args.reps_original}

    log("Event B run log - CS4928 G17 P23")
    log(f"Started (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    log(f"Platform: {platform.platform()} | CPUs: {os.cpu_count()}")
    log(f"Python {platform.python_version()} | pandas {pd.__version__} | numpy {np.__version__}")
    log(f"Repository HEAD: {git_head()} (frozen state compared: {FROZEN_TAG})")
    log(f"Protocol: project={PROJECT} scales={scales} seed={SEED} "
        f"reps optimised={reps['optimised']} original={reps['original']} "
        f"cap={CAP_SECONDS}s tolerance={TOLERANCE}")
    for name, path in [("input", INPUT), *IMPLS.items()]:
        data = path.read_bytes()
        frozen = git_blob(path)
        match = ("not checked" if frozen is None else
                 "identical to " + FROZEN_TAG if frozen == data else
                 "DIFFERS from " + FROZEN_TAG)
        log(f"{name}: {path.relative_to(ROOT).as_posix()} sha256={sha256(data)} ({match})")

    base = load_base()
    log(f"{PROJECT} at 1x: {base['Test Name'].nunique()} tests, {len(base)} rows, "
        f"{int(base['Methods'].isna().sum())} rows with no recorded method (NaN), "
        f"{nan_objects(base)} distinct NaN object(s)")
    log("")

    rows = []
    with open(outdir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writeheader()

        def record(row, err):
            rows.append(row)
            writer.writerow({k: row.get(k, "") for k in RESULT_FIELDS})
            f.flush()
            log(f"[{datetime.now().strftime('%H:%M:%S')}] scale={row['scale']} "
                f"{row['implementation']:9s} {row['mode']:6s} run={row['run']} "
                f"{row['status']:7s} nan_obj={row.get('nan_objects', '')} "
                f"s={fmt(row.get('seconds'))} "
                f"peakMiB={fmt(row.get('peak_mib'), 2)} ratio={row.get('overlap_ratio', '')}")
            if err:
                log("    error: " + err.splitlines()[-1])

        for scale in scales:
            stopped = set()
            for run in range(1, max(reps.values()) + 1):
                for impl in ("optimised", "original"):
                    if run > reps[impl] or impl in stopped:
                        continue
                    row, err = run_once(impl, scale, "time", run)
                    record(row, err)
                    if row["status"] != "ok":
                        stopped.add(impl)
            for impl in ("optimised", "original"):
                record(*run_once(impl, scale, "memory", 1))

    summary = summarise(rows, scales)
    fields = list(dict.fromkeys(k for s in summary for k in s))
    with open(outdir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)

    log("")
    log("Summary (median seconds; peak MiB from tracemalloc runs)")
    for s in summary:
        log(f"scale={s['scale']}: tests={s.get('tests')} "
            f"opt={fmt(s['optimised_median_s'])}s orig={fmt(s['original_median_s'])}s"
            f"{' (timeout)' if s['original_timeout'] else ''} "
            f"speedup={fmt(s['speedup'], 1)} "
            f"peak opt={fmt(s['optimised_peak_mib'], 2)} orig={fmt(s['original_peak_mib'], 2)} "
            f"equivalent={s['equivalent']}")
    log(f"Finished (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
