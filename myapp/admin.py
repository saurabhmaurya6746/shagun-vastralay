from django.contrib import admin
from .models import Category, Saree, Suit ,Comment # Make sure Suit is included
from .models import Profile, CartItem ,ContactMessage ,NewsletterSubscriber

admin.site.register(Category)
admin.site.register(Saree)
admin.site.register(Suit)


admin.site.register(Profile)
admin.site.register(CartItem)
admin.site.register(ContactMessage)
admin.site.register(NewsletterSubscriber)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'is_approved', 'submitted_at')
    list_filter = ('is_approved',)
    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)

    def reject_selected(self, request, queryset):
        queryset.delete()

    approve_selected.short_description = "Approve selected comments"
    reject_selected.short_description = "Reject selected comments"

admin.site.register(Comment, CommentAdmin)
