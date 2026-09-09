# Design Notes

## Why a separate queue per service type

`BranchQueue` keeps **one FIFO queue per service type** (`collections.deque`
for `deposit`, `withdrawal`, and `account_management`), instead of one
shared list holding every ticket.

With separate queues, `call_next(service_type)` is a direct `popleft()`
on that service's own deque — `O(1)`, regardless of how many tickets
exist for the *other* services.

If there were a single shared queue instead, calling next for, say,
`deposit` would mean scanning from the front of the list, skipping over
every `withdrawal` and `account_management` ticket in between, until the
first `deposit` ticket is found. That's `O(n)` in the worst case, and it
gets slower the busier the branch gets — exactly the "deposits agent
sits idle scanning a long list" problem described in the prompt. Giving
each service its own queue means an agent's `call_next()` never has to
look at, or skip past, tickets that aren't theirs.

The global ticket counter is separate from this — it's a single number
on `BranchQueue` itself, incremented every time `issue_ticket()`
succeeds, regardless of which service queue the ticket goes into. That's
what keeps ticket numbers sequential across the whole branch rather than
per-service.

## Concurrent mutation scenario (informal)

This project runs as a single-threaded terminal loop, so there's no real
concurrency yet. But consider two agents assigned to the same service
type — say two `deposit` agents — both calling `call_next("deposit")` at
the same moment because they've each just finished with a client.

The risk is a **check-then-act race**: both agents' calls read the same
front-of-queue ticket before either one has actually removed it, and the
same client ends up called by both agents while another client who was
waiting gets skipped entirely.

The fix is to make "read the front ticket and remove it" a single
atomic step. In practice that means wrapping each service queue's
`popleft()` in a lock (e.g. `threading.Lock()`, one per service type):
whichever agent's `call_next()` call acquires the lock first must
completely finish removing the ticket *before* the second agent's call
is allowed to even look at the queue. That guarantees the two agents
always get two different clients, and no client is ever called twice or
silently skipped.

## Invalid service type handling

`issue_ticket()` validates the service type *before* creating a `Ticket`
or incrementing the global counter. That means a rejected request (e.g.
`"loan"`) doesn't waste a ticket number — the next valid ticket issued
still gets the next sequential number as if the invalid attempt never
happened.
