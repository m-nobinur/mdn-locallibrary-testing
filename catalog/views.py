import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from catalog.forms import RenewBookForm

from .models import Author, Book, BookInstance, Genre, Language
from .services import BorrowWorkflowError, borrow_book_copy, return_book_copy


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    num_visits += 1
    request.session["num_visits"] = num_visits

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        "index.html",
        context={
            "num_books": num_books,
            "num_instances": num_instances,
            "num_instances_available": num_instances_available,
            "num_authors": num_authors,
            "num_visits": num_visits,
        },
    )


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""

    model = Book
    paginate_by = 10

    def get_queryset(self):
        queryset = Book.objects.select_related("author").order_by("title")
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""

    model = Book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""

    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""

    model = Author


class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""

    model = Genre


class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""

    model = Genre
    paginate_by = 10


class LanguageDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""

    model = Language


class LanguageListView(generic.ListView):
    """Generic class-based list view for a list of genres."""

    model = Language
    paginate_by = 10


class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""

    model = BookInstance
    paginate_by = 10


class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""

    model = BookInstance


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing all books on loan.
    Only visible to users with can_mark_returned permission.
    """

    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by("due_back")


def _safe_next_url(request, fallback_url):
    """Return a local next URL when provided, otherwise return fallback URL."""
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback_url


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("all-borrowed"))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


@login_required
def borrow_book(request, pk):
    """Allow authenticated members to borrow an available copy."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    fallback_url = reverse("my-borrowed")
    redirect_url = _safe_next_url(request, fallback_url)

    if request.method != "POST":
        return HttpResponseRedirect(redirect_url)

    try:
        borrow_book_copy(book_instance, request.user)
    except BorrowWorkflowError as exc:
        messages.error(request, str(exc))
    else:
        due_back = (
            book_instance.due_back.isoformat() if book_instance.due_back else "N/A"
        )
        messages.success(
            request,
            f'Borrowed "{book_instance.book}" successfully. Due back on {due_back}.',
        )

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def return_book_librarian(request, pk):
    """Allow librarians to mark an on-loan copy as returned."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    redirect_url = _safe_next_url(request, reverse("all-borrowed"))

    if request.method != "POST":
        return HttpResponseRedirect(redirect_url)

    try:
        return_book_copy(book_instance)
    except BorrowWorkflowError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request, f'"{book_instance.book}" has been marked as returned.'
        )

    return HttpResponseRedirect(redirect_url)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": "11/11/2023"}
    permission_required = "catalog.add_author"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = "__all__"
    permission_required = "catalog.change_author"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.delete_author"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(self.request, str(e))
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.add_book"


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.change_book"


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = "catalog.delete_book"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(self.request, str(e))
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = [
        "name",
    ]
    permission_required = "catalog.add_genre"


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = [
        "name",
    ]
    permission_required = "catalog.change_genre"


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy("genres")
    permission_required = "catalog.delete_genre"


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = [
        "name",
    ]
    permission_required = "catalog.add_language"


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = [
        "name",
    ]
    permission_required = "catalog.change_language"


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy("languages")
    permission_required = "catalog.delete_language"


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ["book", "imprint", "due_back", "borrower", "status"]
    permission_required = "catalog.add_bookinstance"


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "__all__"
    fields = ["imprint", "due_back", "borrower", "status"]
    permission_required = "catalog.change_bookinstance"


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy("bookinstances")
    permission_required = "catalog.delete_bookinstance"
