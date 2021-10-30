from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from pdfme import build_pdf
from django.core.files import File
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    '''
  The Role entries are managed by the system,
  automatically created via a Django data migration.
  '''
    INSURED = 1                # BIMESHAVANDE
    POLICYHOLDER = 2           # BIMEGOZAR 
    EXPERT = 3                 # KARSHENAS
    VALUATOR = 4               # ARZYAB
    ADMIN = 5
    ROLE_CHOICES = (
        (INSURED, 'insured'),
        (POLICYHOLDER, 'policyholder'),
        (EXPERT, 'expert'),
        (VALUATOR, 'valuator'),
        (ADMIN, 'admin'),
    )
    ROLE_NAMES = (
        ("insured", 'insured'),
        ("policyholder", 'policyholder'),
        ("expert", 'expert'),
        ("valuator", 'valuator'),
        ("admin", 'admin'),
    )
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)
    name = models.CharField(choices=ROLE_NAMES, default='insured', max_length=20)

    def __str__(self):
        return self.get_id_display()


class User(AbstractUser):
    melli_code = models.CharField(max_length=100, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(default=25, blank=True, null=True)
    is_asli = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role)


# Create your models here.
class PolicyHolder(models.Model):  # BimeGozar
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)


class Insurer(models.Model):   # BimeGar
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)


class CostCategory(MPTTModel):   #HazineCategory
    name = models.CharField(max_length=50, unique=True)
    code = models.IntegerField(blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Cost(models.Model):   # Hazine
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(CostCategory, on_delete=models.CASCADE)
    documents = models.TextField(blank=True, null=True)   # madarek
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Contract(models.Model):   # Gharardad
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE)   # bimegar
    policy_holder = models.ForeignKey(PolicyHolder, on_delete=models.CASCADE)   # bimegozar
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contract_costs = models.ManyToManyField(Cost, through='ContractCost')   # gharardad_hazines   #'HazineGharardad'
    file = models.FileField()
    expire_date = models.DateField()


class ContractCost(models.Model):   # HazineGharardad
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)   # gharardad
    cost = models.ForeignKey(Cost, on_delete=models.CASCADE)   # hazine
    contractـceiling = models.BigIntegerField()   # saghf
    documents = models.TextField(max_length=5000, blank=True, null=True)   # madarek
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InsuredContract(models.Model):   # BimeShavanadeGharardad
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)   # gharardad
    insured = models.OneToOneField(User, on_delete=models.CASCADE)   # bimeshavande
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TheCostOfInsuredContract(models.Model):   # BimeShavandeGharardadHazine
    insured_contract = models.ForeignKey(InsuredContract, on_delete=models.CASCADE) # bime shavande gharardad
    cost = models.ForeignKey(Cost, on_delete=models.CASCADE)  # hazine
    personal_contractـceiling = models.BigIntegerField()  # saghf e shakhsi
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=InsuredContract)
def insured_contract_handler(sender, instance, created, **kwargs):  # bime shavande gharardad handler
    if created:
        costs = instance.contract.contract_costs.all()
        for cost in costs:
            contract_cost = ContractCost.objects.filter(contract=instance.contract, cost=cost).first()
            if contract_cost:
                TheCostOfInsuredContract.objects.create(insured_contract=instance, cost=cost,
                                                           personal_contract_ceiling=contract_cost.contract_ceiling)


@receiver(post_save, sender=ContractCost)
def contract_cost_handler(sender, instance, created, **kwargs):
    contract_costs = TheCostOfInsuredContract.objects.filter(cost=instance.cost).all()
    for contract_cost in contract_costs:
        contract_cost.personal_contract_ceiling = instance.contract_ceiling
        contract_cost.save()


class Reception(models.Model):  # Paziresh
    the_cost_of_insured_contract = models.ForeignKey(TheCostOfInsuredContract, on_delete=models.CASCADE)  # bime shavande gharardad hazine
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    requested_cost = models.BigIntegerField()   # hazine_darkhasti
    verification_cost = models.BigIntegerField(default=0)   #hazine_taeidi
    basic_insurance = models.BooleanField(default=False)   # bime_paye
    expert = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="expert")   # karshenas
    valuator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="valuator")   # arzyab
    shomare_nezam_pezeshki = models.CharField(max_length=100, blank=True, null=True)   # ???
    markaz_darmani = models.CharField(max_length=50, blank=True, null=True)   # ???
    file = models.FileField(blank=True, null=True)
    STATUS = [
        ("awaiting expert approval", "در انتظار تایید کارشناس"),
        ("awaiting valuator approval", "در انتظار تایید ارزیاب"),
        ("accepted", "تایید برای پرداخت"),
        ("rejected", "عودت")
    ]
    status = models.CharField(choices=STATUS, max_length=20, default="waitforkarshenas")
    valuator_message = models.TextField(blank=True, null=True)   # payam arzyab

    def create_file(self):
        images = self.receptionfile_set.all()
        pdf_image_list = [{"image": img.file.path} for img in images]
        with open('media/' + str(self.id) + '.pdf', 'wb') as f:
            build_pdf({"sections": [{"content": pdf_image_list}]}, f)
        with open('media/' + str(self.id) + '.pdf', 'rb') as f:
            self.file.save('completed_pdf_' + str(self.id) + '.pdf', File(f))
        self.save()


class ReceptionFile(models.Model):   # file paziresh
    file = models.FileField()
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE)   # paziresh
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
