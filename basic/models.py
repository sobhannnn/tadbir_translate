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
    BIMESHAVANDE = 1
    BIMEGOZAR = 2
    KARSHENAS = 3
    ARZYAB = 4
    ADMIN = 5
    ROLE_CHOICES = (
        (BIMESHAVANDE, 'bimeshavande'),
        (BIMEGOZAR, 'bimegozar'),
        (KARSHENAS, 'karshenas'),
        (ARZYAB, 'arzyab'),
        (ADMIN, 'admin'),
    )
    ROLE_NAMES = (
        ("bimeshavande", 'bimeshavande'),
        ("bimegozar", 'bimegozar'),
        ("karshenas", 'karshenas'),
        ("arzyab", 'arzyab'),
        ("admin", 'admin'),
    )
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)
    name = models.CharField(choices=ROLE_NAMES, default='bimeshavande', max_length=20)

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
class BimeGozar(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)


class BimeGar(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)


class HazineCategory(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    code = models.IntegerField(blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Hazine(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(HazineCategory, on_delete=models.CASCADE)
    madarek = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Gharardad(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    bimegar = models.ForeignKey(BimeGar, on_delete=models.CASCADE)
    bimegozar = models.ForeignKey(BimeGozar, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gharardad_hazines = models.ManyToManyField(Hazine, through='HazineGharardad')
    file = models.FileField()
    expire_date = models.DateField()


class HazineGharardad(models.Model):
    gharardad = models.ForeignKey(Gharardad, on_delete=models.CASCADE)
    hazine = models.ForeignKey(Hazine, on_delete=models.CASCADE)
    saghf = models.BigIntegerField()
    madarek = models.TextField(max_length=5000, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BimeShavanadeGharardad(models.Model):
    gharardad = models.ForeignKey(Gharardad, on_delete=models.CASCADE)
    bimeshavande = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BimeShavandeGharardadHazine(models.Model):
    bimeshavande_gharardad = models.ForeignKey(BimeShavanadeGharardad, on_delete=models.CASCADE)
    hazine = models.ForeignKey(Hazine, on_delete=models.CASCADE)
    personal_saghf = models.BigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=BimeShavanadeGharardad)
def bime_shavande_gharardad_handler(sender, instance, created, **kwargs):
    if created:
        hazines = instance.gharardad.gharardad_hazines.all()
        for hazine in hazines:
            gharardad_hazine = HazineGharardad.objects.filter(gharardad=instance.gharardad, hazine=hazine).first()
            if gharardad_hazine:
                BimeShavandeGharardadHazine.objects.create(bimeshavande_gharardad=instance, hazine=hazine,
                                                           personal_saghf=gharardad_hazine.saghf)


@receiver(post_save, sender=HazineGharardad)
def hazine_gharardad_handler(sender, instance, created, **kwargs):
    hazine_gharardads = BimeShavandeGharardadHazine.objects.filter(hazine=instance.hazine).all()
    for hazine_gharardad in hazine_gharardads:
        hazine_gharardad.personal_saghf = instance.saghf
        hazine_gharardad.save()


class Paziresh(models.Model):
    bimeshavande_gharardad_hazine = models.ForeignKey(BimeShavandeGharardadHazine, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    hazine_darkhasti = models.BigIntegerField()
    hazine_taeidi = models.BigIntegerField(default=0)
    bime_paye = models.BooleanField(default=False)
    karshenas = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="karshenas")
    arzyab = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="arzyab")
    shomare_nezam_pezeshki = models.CharField(max_length=100, blank=True, null=True)
    markaz_darmani = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    STATUS = [
        ("waitforkarshenas", "در انتظار تایید کارشناس"),
        ("waitforarzyab", "در انتظار تایید ارزیاب"),
        ("accepted", "تایید برای پرداخت"),
        ("rejected", "عودت")
    ]
    status = models.CharField(choices=STATUS, max_length=20, default="waitforkarshenas")
    arzyab_message = models.TextField(blank=True, null=True)

    def create_file(self):
        images = self.pazireshfile_set.all()
        pdf_image_list = [{"image": img.file.path} for img in images]
        with open('media/' + str(self.id) + '.pdf', 'wb') as f:
            build_pdf({"sections": [{"content": pdf_image_list}]}, f)
        with open('media/' + str(self.id) + '.pdf', 'rb') as f:
            self.file.save('completed_pdf_' + str(self.id) + '.pdf', File(f))
        self.save()


class PazireshFile(models.Model):
    file = models.FileField()
    paziresh = models.ForeignKey(Paziresh, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
