"""Small, reproducible comparison of common single-CPU schedulers."""
import argparse
from collections import deque

DEFAULT = [("P1", 0, 7), ("P2", 2, 4), ("P3", 4, 1), ("P4", 5, 4)]

def simulate(processes, policy, quantum=2):
    jobs = {name: {"arrival": arr, "burst": burst, "remaining": burst,
                   "first": None, "finish": None} for name, arr, burst in processes}
    ordered = sorted(processes, key=lambda p: (p[1], p[0]))
    time = 0; timeline = []; ready = deque(); admitted = set()
    def admit():
        for name, arrival, _ in ordered:
            if arrival <= time and name not in admitted:
                ready.append(name); admitted.add(name)
    if policy == "fcfs":
        sequence = [(n, a, b) for n, a, b in ordered]
        for name, arrival, burst in sequence:
            if time < arrival:
                timeline.append(("IDLE", time, arrival)); time = arrival
            jobs[name]["first"] = time; timeline.append((name, time, time + burst)); time += burst
            jobs[name]["finish"] = time
    else:
        while any(j["remaining"] for j in jobs.values()):
            admit()
            if not ready:
                next_arrival = min(a for n, a, _ in ordered if n not in admitted)
                timeline.append(("IDLE", time, next_arrival)); time = next_arrival; admit()
            if policy == "sjf":
                name = min(ready, key=lambda n: (jobs[n]["burst"], jobs[n]["arrival"], n))
                ready.remove(name); duration = jobs[name]["remaining"]
            else:
                name = ready.popleft(); duration = min(quantum, jobs[name]["remaining"])
            job = jobs[name]
            if job["first"] is None: job["first"] = time
            start = time; time += duration; job["remaining"] -= duration
            timeline.append((name, start, time)); admit()
            if job["remaining"]:
                ready.append(name)
            else:
                job["finish"] = time
    metrics = {}
    for name, job in jobs.items():
        turnaround = job["finish"] - job["arrival"]
        metrics[name] = {"completion": job["finish"], "turnaround": turnaround,
                         "waiting": turnaround - job["burst"],
                         "response": job["first"] - job["arrival"]}
    span = max(end for _, _, end in timeline)
    busy = sum(end-start for name, start, end in timeline if name != "IDLE")
    return timeline, metrics, (busy / span if span else 0)

def parse_workload(value):
    try:
        result = []
        for item in value.split(","):
            name, arrival, burst = item.split(":")
            result.append((name, int(arrival), int(burst)))
        names = [x[0] for x in result]
        if len(set(names)) != len(names) or any(a < 0 or b <= 0 for _, a, b in result): raise ValueError
        return result
    except ValueError:
        raise argparse.ArgumentTypeError("use unique name:arrival:positive_burst entries")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--policy", choices=["fcfs", "sjf", "rr", "all"], default="all")
    p.add_argument("--quantum", type=int, default=2)
    p.add_argument("--processes", type=parse_workload, default=DEFAULT)
    a = p.parse_args()
    if a.quantum <= 0: p.error("--quantum must be positive")
    for policy in (["fcfs", "sjf", "rr"] if a.policy == "all" else [a.policy]):
        timeline, metrics, utilization = simulate(a.processes, policy, a.quantum)
        print(f"\n{policy.upper()} (CPU utilization {utilization:.1%})")
        print("Timeline: " + " | ".join(f"{n}[{s}-{e}]" for n, s, e in timeline))
        print("Process  Completion  Turnaround  Waiting  Response")
        for name, m in metrics.items():
            print(f"{name:<8} {m['completion']:>10} {m['turnaround']:>11} {m['waiting']:>8} {m['response']:>9}")
        print("Average waiting: %.2f" % (sum(m["waiting"] for m in metrics.values()) / len(metrics)))

if __name__ == "__main__": main()
