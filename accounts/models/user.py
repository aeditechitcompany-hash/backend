import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", _("Student")
        COUNSELOR = "counselor", _("Counselor")
        ADMIN = "admin", _("Admin")
        UNIVERSITY_PARTNER = "university_partner", _("University Partner")

    class Province(models.TextChoices):
        KOSHI = "koshi", _("Koshi")
        MADHESH = "madhesh", _("Madhesh")
        BAGMATI = "bagmati", _("Bagmati")
        GANDAKI = "gandaki", _("Gandaki")
        LUMBINI = "lumbini", _("Lumbini")
        KARNALI = "karnali", _("Karnali")
        SUDURPASHCHIM = "sudurpashchim", _("Sudurpashchim")

    class District(models.TextChoices):
        BHOJPUR = "bhojpur", _("Bhojpur")
        DHANKUTA = "dhankuta", _("Dhankuta")
        ILAM = "ilam", _("Ilam")
        JHAPA = "jhapa", _("Jhapa")
        KHOTANG = "khotang", _("Khotang")
        MORANG = "morang", _("Morang")
        OKHALDHUNGA = "okhaldhunga", _("Okhaldhunga")
        PANCHTHAR = "panchthar", _("Panchthar")
        SANKHUWASABHA = "sankhuwasabha", _("Sankhuwasabha")
        SOLUKHUMBU = "solukhumbu", _("Solukhumbu")
        SUNSARI = "sunsari", _("Sunsari")
        TAPLEJUNG = "taplejung", _("Taplejung")
        TEHRATHUM = "tehrathum", _("Tehrathum")
        UDAYAPUR = "udayapur", _("Udayapur")

        # Madhesh
        BARA = "bara", _("Bara")
        DHANUSHA = "dhanusha", _("Dhanusha")
        MAHOTTARI = "mahottari", _("Mahottari")
        PARSA = "parsa", _("Parsa")
        RAUTAHAT = "rautahat", _("Rautahat")
        SAPTARI = "saptari", _("Saptari")
        SARLAHI = "sarlahi", _("Sarlahi")
        SIRAHA = "siraha", _("Siraha")

        # Bagmati
        BHAKTAPUR = "bhaktapur", _("Bhaktapur")
        CHITWAN = "chitwan", _("Chitwan")
        DHADING = "dhading", _("Dhading")
        DOLAKHA = "dolakha", _("Dolakha")
        KATHMANDU = "kathmandu", _("Kathmandu")
        KAVREPALANCHOK = "kavrepalanchok", _("Kavrepalanchok")
        LALITPUR = "lalitpur", _("Lalitpur")
        MAKWANPUR = "makwanpur", _("Makwanpur")
        NUWAKOT = "nuwakot", _("Nuwakot")
        RAMECHHAP = "ramechhap", _("Ramechhap")
        RASUWA = "rasuwa", _("Rasuwa")
        SINDHULI = "sindhuli", _("Sindhuli")
        SINDHUPALCHOK = "sindhupalchok", _("Sindhupalchok")

        # Gandaki
        BAGLUNG = "baglung", _("Baglung")
        GORKHA = "gorkha", _("Gorkha")
        KASKI = "kaski", _("Kaski")
        LAMJUNG = "lamjung", _("Lamjung")
        MANANG = "manang", _("Manang")
        MUSTANG = "mustang", _("Mustang")
        MYAGDI = "myagdi", _("Myagdi")
        NAWALPUR = "nawalpur", _("Nawalpur (Nawalparasi East)")
        PARBAT = "parbat", _("Parbat")
        SYANGJA = "syangja", _("Syangja")
        TANAHUN = "tanahun", _("Tanahun")

        # Lumbini
        ARGHAKHANCHI = "arghakhanchi", _("Arghakhanchi")
        BANKE = "banke", _("Banke")
        BARDIYA = "bardiya", _("Bardiya")
        DANG = "dang", _("Dang")
        GULMI = "gulmi", _("Gulmi")
        KAPILVASTU = "kapilvastu", _("Kapilvastu")
        PARASI = "parasi", _("Parasi (Nawalparasi West)")
        PALPA = "palpa", _("Palpa")
        PYUTHAN = "pyuthan", _("Pyuthan")
        ROLPA = "rolpa", _("Rolpa")
        RUKUM_EAST = "rukum_east", _("Rukum East")
        RUPANDEHI = "rupandehi", _("Rupandehi")

        # Karnali
        DAILEKH = "dailekh", _("Dailekh")
        DOLPA = "dolpa", _("Dolpa")
        HUMLA = "humla", _("Humla")
        JAJARKOT = "jajarkot", _("Jajarkot")
        JUMLA = "jumla", _("Jumla")
        KALIKOT = "kalikot", _("Kalikot")
        MUGU = "mugu", _("Mugu")
        RUKUM_WEST = "rukum_west", _("Rukum West")
        SALYAN = "salyan", _("Salyan")
        SURKHET = "surkhet", _("Surkhet")

        # Sudurpashchim
        ACHHAM = "achham", _("Achham")
        BAITADI = "baitadi", _("Baitadi")
        BAJHANG = "bajhang", _("Bajhang")
        BAJURA = "bajura", _("Bajura")
        DADELDHURA = "dadeldhura", _("Dadeldhura")
        DARCHULA = "darchula", _("Darchula")
        DOTI = "doti", _("Doti")
        KAILALI = "kailali", _("Kailali")
        KANCHANPUR = "kanchanpur", _("Kanchanpur")
        

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    street_address = models.CharField(max_length=32,blank=True, null=True, )
    district = models.CharField(max_length=32, choices=District.choices, blank=True, null=True )
    province = models.CharField(max_length=32, choices=Province.choices, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_active_student = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
