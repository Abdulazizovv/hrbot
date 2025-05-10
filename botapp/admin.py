from django.contrib import admin
from botapp.models import BotUser, Vacancy, Application, TechnicalTask, UserTask


class TechnicalTaskInline(admin.TabularInline):
    model = TechnicalTask
    extra = 0
    fields = ('task', 'deadline')
    readonly_fields = ('created_at', 'updated_at')


class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'username', 'language_code', 'is_blocked', 'is_admin', 'created_at', 'updated_at')
    search_fields = ('user_id', 'full_name', 'username')
    list_filter = ('is_blocked', 'is_admin')
    ordering = ('-created_at',)
    list_per_page = 20
    list_display_links = ('user_id', 'full_name')
    fieldsets = (
        (None, {'fields': ('user_id', 'full_name', 'username', 'language_code')}),
        ('Permissions', {'fields': ('is_blocked', 'is_admin')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


class VacancyAdmin(admin.ModelAdmin):
    inlines = [TechnicalTaskInline]
    list_display = ('name', 'description', 'requirements', 'salary', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('-created_at',)
    list_per_page = 20
    list_display_links = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'description', 'requirements', 'salary')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number', 'age', 'vacancy', 'email', 'portfolio', 'about', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('status',)
    ordering = ('-created_at',)
    list_per_page = 20
    list_display_links = ('name',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'phone_number', 'age', 'vacancy')}),
        ('Contact Information', {'fields': ('email', 'portfolio', 'portfolio_type')}),
        ('Additional Information', {'fields': ('about',)}),
        ('Status and Timestamps', {'fields': ('status', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


class TechnicalTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'vacancy', 'deadline', 'is_active', 'created_at', 'updated_at')
    search_fields = ('task', 'vacancy__name')
    ordering = ('-created_at',)
    list_per_page = 20
    list_display_links = ('task',)
    fieldsets = (
        (None, {'fields': ('task', 'vacancy', 'deadline', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'created_at', 'updated_at')
    search_fields = ('user__full_name', 'task__task')
    ordering = ('-created_at',)
    list_per_page = 20
    list_display_links = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'task', 'status', 'user_deadline')}),
        ('User sends', {'fields': ('submission', 'submission_type')}),
        ('Timestamps', {'fields': ('started_at', 'deadline', 'finished_at', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(TechnicalTask, TechnicalTaskAdmin)
admin.site.register(UserTask, UserTaskAdmin)
