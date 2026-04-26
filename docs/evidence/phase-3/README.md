# Phase 3 Evidence — Search, Borrow, and Return Workflows

This folder contains verification evidence for the Phase 3 workflow features added on top of the MDN LocalLibrary baseline.

## What this phase proves

- Book list now supports title search via `?q=`
- Authenticated members can borrow an available `BookInstance`
- Librarians can mark borrowed copies as returned
- Borrow and return actions are implemented as `POST` operations with CSRF protection
- Borrow/return feedback is shown through Django flash messages
- Borrow and return state transitions are centralized in `catalog/services.py`

## Files changed in Phase 3

| File                                                            | Purpose                                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `catalog/services.py`                                           | Service layer for reusable borrow/return logic                           |
| `catalog/views.py`                                              | Search filtering, borrow action, return action, safe redirects, messages |
| `catalog/urls.py`                                               | Borrow and return endpoints                                              |
| `catalog/templates/base_generic.html`                           | Flash-message rendering                                                  |
| `catalog/templates/catalog/book_list.html`                      | Search form and result context                                           |
| `catalog/templates/catalog/book_detail.html`                    | Member borrow action for available copies                                |
| `catalog/templates/catalog/bookinstance_list.html`              | Librarian return action from copy list                                   |
| `catalog/templates/catalog/bookinstance_list_borrowed_all.html` | Librarian return action from borrowed list                               |

## Endpoints added

- `POST /catalog/bookinstance/<uuid>/borrow/`
- `POST /catalog/bookinstance/<uuid>/return/`

## Manual verification checklist

- [x] Search for a known title in `/catalog/books/?q=<term>` and confirm filtered results
- [x] Log in as regular member and borrow an available copy from book detail page
- [x] Open `/catalog/mybooks/` and verify borrowed copy appears
- [x] Log in as librarian and mark borrowed copy as returned from `/catalog/borrowed/`
- [x] Confirm success/error flash messages appear for borrow and return actions

## Screenshot evidence

| Screenshot                                                   | What it shows                                  |
| ------------------------------------------------------------ | ---------------------------------------------- |
| [search-results.png](search-results.png)                     | Search results for the Phase 3 test title      |
| [member-borrow-success.png](member-borrow-success.png)       | Successful member borrow action                |
| [my-borrowed-list.png](my-borrowed-list.png)                 | Borrowed title visible in member borrowed list |
| [librarian-return-success.png](librarian-return-success.png) | Successful librarian return action             |
| [flash-message-feedback.png](flash-message-feedback.png)     | Flash-message feedback after workflow actions  |
