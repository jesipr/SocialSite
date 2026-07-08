from django.forms import ModelForm

from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['host', 'topic', 'name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
