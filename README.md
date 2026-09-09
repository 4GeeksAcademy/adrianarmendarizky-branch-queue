# Branch Queue Manager

A terminal-based ticket queue for a bank branch. Clients take a numbered
ticket for a service type (`deposit`, `withdrawal`, or
`account_management`) and are called in arrival order within their own
service type.

## Run it

```bash
python3 branch_queue.py
```

Uses only the Python standard library — no install step needed.

See `DESIGN.md` for the data structure decision and edge-case notes.
