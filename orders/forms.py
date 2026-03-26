import re
from django import forms


class CreateOrderForm(forms.Form):

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "(000) 000-0000",
                "inputmode": "numeric",
            }
        )
    )

    requires_delivery = forms.ChoiceField(
        choices=[
            ("0", False),
            ("1", True),
        ],
        widget=forms.RadioSelect,
    )

    delivery_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )

    payment_on_get = forms.ChoiceField(
        choices=[
            ("0", "False"),
            ("1", "True"),
        ]
    )

    def clean_phone_number(self):
        import re

        data = self.cleaned_data["phone_number"]

        data = re.sub(r"\D", "", data)

        if len(data) != 10:
            raise forms.ValidationError("The phone number must contain only numbers")

        return data
