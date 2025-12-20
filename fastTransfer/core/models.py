from django.db import models
from shortuuid import ShortUUID
from django.conf import settings

class TimeStampMixin(models.Model):
    created_at = models.DateField()
    updated_at = models.DateField()
    deleted_at = models.DateField()
    class Meta:
        abstract = True



class TypeTransaction(models.TextChoices):
    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"
    WITHDRAWAL = "WITHDRAWAL"
    FEE = "FEE"

class TransactionStatus(models.TextChoices):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AccountOwner(TimeStampMixin):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

class Platform(models.Model):
    name = models.CharField(max_length=255)
    withdrawal_fee_rate = models.IntegerField()


class VirtualAccount(TimeStampMixin):
    balance = models.IntegerField()
    is_active = models.BooleanField()

    owner = models.OneToOneField(
        AccountOwner,
        on_delete=models.CASCADE
    )

class Transactions(TimeStampMixin):
    reference = models.CharField(max_length=255)
    types = models.CharField(
        max_length=20,
        choices=TypeTransaction.choices
    )
    amount = models.CharField(max_length=50)
    fee = models.IntegerField()
    net_amount = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices
    )

    sender_account = models.ForeignKey(
        VirtualAccount,
        related_name="sent_transactions",
        on_delete=models.PROTECT
    )

    receiver_account = models.ForeignKey(
        VirtualAccount,
        related_name="received_transactions",
        on_delete=models.PROTECT
    )