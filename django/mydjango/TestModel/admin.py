from django.contrib import admin
from TestModel.models import Test, Contact, Tag


# Register your models here.
class TagInline(admin.TabularInline):
    model = Tag

class ContactAdmin(admin.ModelAdmin):
    search_fields = ('name',) # 添加搜索功能
    list_display = ('name', 'age', 'email')  # list
    inlines = [TagInline]  # Inline
    fieldsets = (
        ['Main', {
            'fields': ('name', 'email'),
        }],
        ['Advance', {
            'classes': ('collapse',),  # CSS
            'fields': ('age',),
        }]
    )


admin.site.register(Contact, ContactAdmin)
# admin.site.register([Test, Contact, Tag])
admin.site.register([Test, Tag])
