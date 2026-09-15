from django.contrib import admin
from .models import Movie, Review, Report

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class ReportInline(admin.TabularInline):
    model = Report
    extra = 0
    readonly_fields = ['user', 'reason', 'date']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'user', 'date',
                    'is_hidden', 'report_count']
    list_filter = ['is_hidden', 'movie']
    search_fields = ['comment', 'user__username']
    actions = ['hide_reviews', 'unhide_reviews']
    inlines = [ReportInline]

    @admin.display(description='Reports')
    def report_count(self, obj):
        return obj.reports.count()

    @admin.action(description='Hide selected reviews')
    def hide_reviews(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request,
            f'{updated} review(s) hidden.')

    @admin.action(description='Unhide selected reviews')
    def unhide_reviews(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request,
            f'{updated} review(s) restored.')

class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'user', 'reason', 'date']
    list_filter = ['reason', 'date']
    search_fields = ['review__comment', 'user__username']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Report, ReportAdmin)
