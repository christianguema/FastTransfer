from django.db import models
from shortuuid import ShortUUID

class TimeStampMixin(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    deleted_at = models.DateField(null=True, blank=True)
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
    platform = models.OneToOneField('Platform', on_delete=models.CASCADE, blank=True, null=True)
    owner = models.OneToOneField(
        "userauths.User",
        on_delete=models.CASCADE
    )

class Platform(models.Model):
    name = models.CharField(max_length=255)
    withdrawal_fee_rate = models.IntegerField()

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"


    def __str__(self):
        return f'{self.name}'

class VirtualAccount(TimeStampMixin):
    balance = models.IntegerField()
    is_active = models.BooleanField()

    owner = models.OneToOneField(
        AccountOwner,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"

class Transactions(TimeStampMixin):
    reference = models.CharField(max_length=255)
    types = models.CharField(
        max_length=20,
        choices=TypeTransaction.choices
    )
    amount = models.CharField(max_length=50,)
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

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.reference}"