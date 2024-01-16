from django.contrib import admin
from .models import Board, Column, Ticket, User, Usergroup, UsergroupUser

class BoardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['boardid']}),
        (None,               {'fields': ['description']}),
        (None,               {'fields': ['title']}),
        (None,               {'fields': ['creator']}),
        (None,               {'fields': ['creation_date']}),
        (None,               {'fields': ['passwordhash']}),
        (None,               {'fields': ['salt']}),
    ]
    list_display = ('title',)
admin.site.register(Board, BoardAdmin)

class ColumnAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['columnid']}),
        (None,               {'fields': ['boardid']}),
        (None,               {'fields': ['wip_limit']}),
        (None,               {'fields': ['color']}),
        (None,               {'fields': ['description']}),
        (None,               {'fields': ['title']}),
        (None,               {'fields': ['ordernum']}),
        (None,               {'fields': ['creation_date']}),
    ]
    list_display = ('title',)
admin.site.register(Column, ColumnAdmin)

class TicketAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['ticketid']}),
        (None,               {'fields': ['columnid']}),
        (None,               {'fields': ['title']}),
        (None,               {'fields': ['description']}),
        (None,               {'fields': ['color']}),
        (None,               {'fields': ['storypoints']}),
        (None,               {'fields': ['size']}),
        (None,               {'fields': ['order']}),
        (None,               {'fields': ['creation_date']}),
    ]
    list_display = ('title',)
admin.site.register(Ticket, TicketAdmin)

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['userid']}),
        (None,               {'fields': ['name']}),

    ]
    list_display = ('name',)
admin.site.register(User, UserAdmin)

class UsergroupAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['usergroupid']}),
        (None,               {'fields': ['boardid']}),
        (None,               {'fields': ['ticketid']}),
        (None,               {'fields': ['type']}),
    ]
    list_display = ('usergroupid',)
admin.site.register(Usergroup, UsergroupAdmin)

class UsergroupUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['usergroupid']}),
        (None,               {'fields': ['userid']}),
    ]
    list_display = ('usergroupid',)
admin.site.register(UsergroupUser, UsergroupUserAdmin)