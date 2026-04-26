"""Service helpers for borrow and return workflows."""

import datetime


DEFAULT_BORROW_DAYS = 14


class BorrowWorkflowError(Exception):
    """Raised when a borrow/return action cannot be completed."""


def borrow_book_copy(book_instance, borrower, borrow_days=DEFAULT_BORROW_DAYS):
    """Mark an available book copy as on loan to a borrower."""
    if borrower is None or not borrower.is_authenticated:
        raise BorrowWorkflowError('You must be logged in to borrow a copy.')

    if borrow_days < 1:
        raise BorrowWorkflowError('Borrow duration must be at least one day.')

    if book_instance.status != 'a':
        raise BorrowWorkflowError('This copy is currently unavailable for borrowing.')

    book_instance.status = 'o'
    book_instance.borrower = borrower
    book_instance.due_back = datetime.date.today() + datetime.timedelta(days=borrow_days)
    book_instance.save(update_fields=['status', 'borrower', 'due_back'])
    return book_instance


def return_book_copy(book_instance):
    """Mark an on-loan copy as returned and clear loan metadata."""
    if book_instance.status != 'o':
        raise BorrowWorkflowError('Only on-loan copies can be marked as returned.')

    book_instance.status = 'a'
    book_instance.borrower = None
    book_instance.due_back = None
    book_instance.save(update_fields=['status', 'borrower', 'due_back'])
    return book_instance