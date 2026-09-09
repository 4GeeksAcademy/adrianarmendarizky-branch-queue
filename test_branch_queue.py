"""
Quick automated checks for BranchQueue.

Not required by the assignment, but useful to confirm everything works
before you push. Run with:

    python3 test_branch_queue.py
"""

from branch_queue import BranchQueue, EmptyQueueError, InvalidServiceTypeError


def test_empty_queue_errors():
    b = BranchQueue()
    try:
        b.call_next("deposit")
        raise AssertionError("call_next() on empty queue should have raised")
    except EmptyQueueError:
        pass

    try:
        b.peek_next("withdrawal")
        raise AssertionError("peek_next() on empty queue should have raised")
    except EmptyQueueError:
        pass

    print("OK: call_next/peek_next on an empty queue raise EmptyQueueError")


def test_invalid_service_type_rejected():
    b = BranchQueue()
    try:
        b.issue_ticket("Ana", "loan")
        raise AssertionError("invalid service type should have raised")
    except InvalidServiceTypeError:
        pass
    print("OK: an invalid service type is rejected at issuance")


def test_global_sequential_numbering():
    b = BranchQueue()
    t1 = b.issue_ticket("Ana", "deposit")
    t2 = b.issue_ticket("Ben", "withdrawal")
    t3 = b.issue_ticket("Cara", "deposit")
    assert [t1.number, t2.number, t3.number] == [1, 2, 3]
    print("OK: ticket numbers are globally sequential across service types")


def test_same_queue_fifo_order():
    b = BranchQueue()
    b.issue_ticket("Ana", "deposit")
    b.issue_ticket("Ben", "withdrawal")
    b.issue_ticket("Cara", "deposit")

    first = b.call_next("deposit")
    second = b.call_next("deposit")
    assert first.client_name == "Ana"
    assert second.client_name == "Cara"

    only_withdrawal = b.call_next("withdrawal")
    assert only_withdrawal.client_name == "Ben"
    print("OK: each service queue is served in strict arrival order, independently")


def test_rejected_issuance_does_not_consume_a_number():
    b = BranchQueue()
    b.issue_ticket("Ana", "deposit")  # ticket #1
    try:
        b.issue_ticket("Dev", "not_a_service")
    except InvalidServiceTypeError:
        pass
    t = b.issue_ticket("Eve", "account_management")
    assert t.number == 2, f"expected next valid ticket to be #2, got #{t.number}"
    print("OK: a rejected issuance does not consume a ticket number")


def test_stats():
    b = BranchQueue()
    b.issue_ticket("Ana", "deposit")
    b.issue_ticket("Ben", "withdrawal")
    b.issue_ticket("Cara", "deposit")
    stats = b.stats()
    assert stats == {"deposit": 2, "withdrawal": 1, "account_management": 0, "total": 3}, stats
    print("OK: stats() counts per service type and total are correct")


if __name__ == "__main__":
    test_empty_queue_errors()
    test_invalid_service_type_rejected()
    test_global_sequential_numbering()
    test_same_queue_fifo_order()
    test_rejected_issuance_does_not_consume_a_number()
    test_stats()
    print("All checks passed.")
