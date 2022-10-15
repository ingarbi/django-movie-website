from django.contrib import admin
from .models import *
from .forms import *
from django.utils.safestring import mark_safe
# Register your models here.
from modeltranslation.admin import TranslationAdmin
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class MovieAdminForm(forms.ModelForm):
    """Форма с виджетом ckeditor"""
    description_ru = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
    description_en = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
    class Meta:
        model = Movie
        fields = '__all__'



class ReviewsInLine(admin.TabularInline): #or   StackedInline
    model = Reviews
    readonly_fields = ("name", "email")
    extra = 1

class MovieShotsInline(admin.TabularInline):
    model = MovieShots
    extra: int = 1
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="100"')
    
    get_image.short_description = "Изображение"

@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
    """Фильмы"""
    list_display = ("title","category", "url","draft")
    list_filter = ("category", "year")
    search_fields = ("title","category__name")
    inlines = [MovieShotsInline, ReviewsInLine]
    #filter_horizontal = ['actors']
    save_on_top: bool = True
    save_as: bool = True
    list_editable = ("draft",)
    actions = ["publish", "unpublish"]
    form = MovieAdminForm
    readonly_fields = ("get_image",)
    #fields = (("actors", "directors", "genres"),)
    fieldsets = (
        (None, {
            "fields": (("title", "tagline"),)
        }),

        (None, {
            "fields": ("description", ("poster", "get_image")),
        }),

        (None, {
            "fields": (("year", "world_premiere", "country"),)
        }),

        ("Actors", {
            "classes": ("collapse",),
            "fields" : (("actors", "directors", "genres", "category"),)
        }),

        (None, {
            "fields" : (("budget", "fees_in_usa", "fees_in_world"),)
        }),

        ("Options", {
            "fields" : (("url", "draft"),)
        }),
        
    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="100" height="100"')
    
    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записи были обновлены"
        self.message_user(request, f"{message_bit}")
    
    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записи были обновлены"
        self.message_user(request, f"{message_bit}")

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = ('change',)

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = ('change',)

    get_image.short_description = "Постер"
    

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("name","email", "parent","movie", "id")
    readonly_fields = ("name", "email")



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")

admin.site.site_title = "Django Movies"
admin.site.site_header = "Django Movies"

admin.site.register(RatingStar)
