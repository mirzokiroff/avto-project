from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    phone_validator = RegexValidator(
        regex=r'^\+998[123456789]\d{8}$',
        message='Telefon raqamingizni to\'g\'ri kiriting, masalan: +998901234567',
        code='invalid_phone_number'
    )
    try:
        phone_validator(value)
    except ValidationError as e:
        raise ValidationError(e.messages)
