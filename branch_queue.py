"""
Branch Queue Manager

Models a bank branch's ticket system. Clients take a numbered ticket for
a service type (deposit, withdrawal, account_management) and wait to be
called. Each service type has its own agent, so clients are called in
arrival order within their own service type only.

Run it with:
    python3 branch_queue.py
"""

from dataclasses import dataclass, field
from collections import deque
from datetime import datetime

VALID_SERVICE_TYPES = ("deposit", "withdrawal", "account_management")


class EmptyQueueError(Exception):
    """Raised when call_next() or peek_next() finds no one waiting."""
    pass


class InvalidServiceTypeError(Exception):
    """Raised when a service type isn't one of VALID_SERVICE_TYPES."""
    pass


@dataclass
class Ticket:
    """A single issued ticket."""
    number: int          # global sequential number, across all services
    client_name: str
    service_type: str    # "deposit", "withdrawal", or "account_management"
    issued_at: datetime = field(default_factory=datetime.now)


class BranchQueue:
    """
    Manages the branch's waiting clients.

    Internally, this keeps one FIFO queue per service type (see
    DESIGN.md for why), plus a single global counter so ticket numbers
    are sequential across every service type, not just within one.
    """

    def __init__(self):
        self._queues = {service: deque() for service in VALID_SERVICE_TYPES}
        self._next_number = 1

    def issue_ticket(self, client_name: str, service_type: str) -> Ticket:
        """Create a ticket, enqueue it in the right service queue, and return it."""
        self._validate_service_type(service_type)
        ticket = Ticket(
            number=self._next_number,
            client_name=client_name,
            service_type=service_type,
        )
        self._next_number += 1
        self._queues[service_type].append(ticket)
        return ticket

    def call_next(self, service_type: str) -> Ticket:
        """Remove and return the next client waiting for this service type."""
        self._validate_service_type(service_type)
        queue = self._queues[service_type]
        if not queue:
            raise EmptyQueueError(f"No clients waiting for {service_type}.")
        return queue.popleft()

    def peek_next(self, service_type: str) -> Ticket:
        """Return the next client for this service type, without removing them."""
        self._validate_service_type(service_type)
        queue = self._queues[service_type]
        if not queue:
            raise EmptyQueueError(f"No clients waiting for {service_type}.")
        return queue[0]

    def list_waiting(self) -> dict:
        """Return each service type mapped to its ordered list of waiting tickets."""
        return {service: list(self._queues[service]) for service in VALID_SERVICE_TYPES}

    def stats(self) -> dict:
        """Return the count of waiting clients per service type, plus a total."""
        counts = {service: len(self._queues[service]) for service in VALID_SERVICE_TYPES}
        counts["total"] = sum(counts.values())
        return counts

    def _validate_service_type(self, service_type: str) -> None:
        if service_type not in VALID_SERVICE_TYPES:
            raise InvalidServiceTypeError(
                f"'{service_type}' is not a valid service type. "
                f"Choose one of: {', '.join(VALID_SERVICE_TYPES)}."
            )


# --- CLI ---------------------------------------------------------------

def _prompt_service_type() -> str:
    print("Service types: " + ", ".join(VALID_SERVICE_TYPES))
    return input("Service type: ").strip()


def _format_ticket(ticket: Ticket) -> str:
    timestamp = ticket.issued_at.strftime("%H:%M:%S")
    return f"#{ticket.number} {ticket.client_name} ({ticket.service_type}, issued {timestamp})"


def run_cli() -> None:
    branch = BranchQueue()
    menu = """
Branch Queue Manager
1. Issue a new ticket
2. Call next client
3. View full waiting list
4. View stats
5. Exit
"""
    while True:
        print(menu)
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            client_name = input("Client name: ").strip()
            service_type = _prompt_service_type()
            try:
                ticket = branch.issue_ticket(client_name, service_type)
                print(f"Issued ticket #{ticket.number} for {ticket.client_name} ({ticket.service_type}).")
            except InvalidServiceTypeError as e:
                print(e)

        elif choice == "2":
            service_type = _prompt_service_type()
            try:
                ticket = branch.call_next(service_type)
                print(f"Now calling: {_format_ticket(ticket)}")
            except (InvalidServiceTypeError, EmptyQueueError) as e:
                print(e)

        elif choice == "3":
            waiting = branch.list_waiting()
            any_waiting = False
            for service in VALID_SERVICE_TYPES:
                tickets = waiting[service]
                print(f"\n{service}:")
                if not tickets:
                    print("  (none waiting)")
                else:
                    any_waiting = True
                    for t in tickets:
                        print(f"  {_format_ticket(t)}")
            if not any_waiting:
                print("\nNo clients are waiting anywhere.")

        elif choice == "4":
            counts = branch.stats()
            print("Clients waiting per service type:")
            for service in VALID_SERVICE_TYPES:
                print(f"  {service}: {counts[service]}")
            print(f"  total: {counts['total']}")

        elif choice == "5":
            print("Closing the branch queue. Goodbye.")
            break

        else:
            print("Please choose a number from 1 to 5.")


if __name__ == "__main__":
    run_cli()
