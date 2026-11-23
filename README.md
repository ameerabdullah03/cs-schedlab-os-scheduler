# SchedLab Operating System Scheduler

Compare FCFS, non-preemptive SJF, and Round Robin on the same process set. The simulator reports completion time, turnaround time, waiting time, response time, and CPU utilization, plus a compact execution timeline.

## Course connection

Operating Systems and Lab, Data Structures & Algorithms, and Discrete Mathematics.

## Run

```bash
python scheduler.py --policy all --quantum 2
python scheduler.py --policy rr --quantum 4 --processes 'P1:0:5,P2:1:3,P3:2:1'
```

Each process is written as `name:arrival:burst`. The built-in workload is deterministic. Idle CPU time is shown explicitly. Round Robin requires a positive time quantum.

## Assumptions

This is a discrete event model for one CPU, with no context-switch cost, I/O blocking, priorities, or multiprocessor behavior. Metrics therefore explain scheduling trade-offs without claiming to predict a particular operating system.
