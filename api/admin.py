from django.contrib import admin

from api.models import Author, Book, PhysicalBook, Rent


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    search_fields = ("title", "author__name")
    list_filter = ("author", "created_at")
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at",)


@admin.register(PhysicalBook)
class PhysicalBookAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "status", "created_at")
    search_fields = ("book__title",)
    list_filter = ("status", "created_at")
    autocomplete_fields = ("book",)
    readonly_fields = ("created_at",)


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "physical_book",
        "user",
        "rented_at",
        "due_date",
        "returned_at",
        "is_active",
    )
    search_fields = ("physical_book__book__title", "user__username", "user__email")
    list_filter = ("rented_at", "due_date", "returned_at")
    autocomplete_fields = ("physical_book", "user")
