from django.db import models
from config import app_gv as gv
from django_countries.fields import CountryField
from django.conf import settings
from django_countries.fields import CountryField



# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    iso_4217_alpha = models.CharField(max_length=200)
    iso_4217_numeric = models.CharField(max_length=200)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    capital_city = models.CharField(max_length=200)
    telephone_calling_code = models.CharField(max_length=5)
    internet_domain_code = models.CharField(max_length=5)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'country'

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    country = models.ForeignKey(Country, related_name='country',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'state'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    state = models.ForeignKey(State, related_name='state',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'city'

class SupportPageContent(models.Model):
    support_key = models.CharField(max_length=255)
    support_value = models.CharField(max_length=255)
    support_description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    datamode = models.CharField(max_length=1, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return "{0}".format(self.support_value)

    class Meta:
        db_table = 'support_page_content'


class VersionControl(models.Model):
    app = models.CharField(choices=gv.APP_LIST, default='CUS_ANDROID_APP', max_length=100)
    version = models.CharField(max_length=10)
    released_on = models.DateTimeField(auto_now_add=True)
    datamode = models.CharField(max_length=5, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'version_control'

    def __str__(self):
        return "{0}-{1}".format(self.app, self.version)


class MasterPermission(models.Model):
    app_name = models.CharField(max_length=255, db_index=True) # App Name
    class_name = models.CharField(max_length=255, unique=True, db_index=True) # Class Name
    module_name = models.CharField(max_length=255)
    function_name = models.CharField(max_length=255) # Read, Update, delete, btn action
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return f"{self.class_name} - {self.function_name}"

    class Meta:
        db_table = 'master_permission'



class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'sub_category'

    def __str__(self):
        return self.name


class Banner(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'banner'

    def __str__(self):
        return self.name


class GalleryS(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'gallerys'

    def __str__(self):
        return self.name


class Offers(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'offers'
    
    def __str__(self):
        return self.name


class ClientFeedback(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    feedback = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    
    def __str__(self):
        return ''
    
    class Meta:
        db_table = 'client_feedback'
        


from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings


class Profile(models.Model):

    # -------------------------
    # CHOICES
    # -------------------------
    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    YES_NO_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    DOSHAM_CHOICES = [
        ('No Dosham',      'No Dosham'),
        ('Chevvai Dosham', 'Chevvai Dosham (செவ்வாய் தோஷம்)'),
        ('Rahu Dosham',    'Rahu Dosham (ராகு தோஷம்)'),
        ('Ketu Dosham',    'Ketu Dosham (கேது தோஷம்)'),
        ('Shani Dosham',   'Shani Dosham (சனி தோஷம்)'),
        ('Naga Dosham',    'Naga Dosham (நாக தோஷம்)'),
        ('Unknown',        'Unknown'),
    ]

    TAMILNADU_DISTRICTS = [
        ("Ariyalur",         "Ariyalur"),
        ("Chengalpattu",     "Chengalpattu"),
        ("Chennai",          "Chennai"),
        ("Coimbatore",       "Coimbatore"),
        ("Cuddalore",        "Cuddalore"),
        ("Dharmapuri",       "Dharmapuri"),
        ("Dindigul",         "Dindigul"),
        ("Erode",            "Erode"),
        ("Kallakurichi",     "Kallakurichi"),
        ("Kancheepuram",     "Kancheepuram"),
        ("Kanniyakumari",    "Kanniyakumari"),
        ("Karur",            "Karur"),
        ("Krishnagiri",      "Krishnagiri"),
        ("Madurai",          "Madurai"),
        ("Mayiladuthurai",   "Mayiladuthurai"),
        ("Nagapattinam",     "Nagapattinam"),
        ("Namakkal",         "Namakkal"),
        ("Nilgiris",         "Nilgiris"),
        ("Perambalur",       "Perambalur"),
        ("Pudukkottai",      "Pudukkottai"),
        ("Ramanathapuram",   "Ramanathapuram"),
        ("Ranipet",          "Ranipet"),
        ("Salem",            "Salem"),
        ("Sivaganga",        "Sivaganga"),
        ("Tenkasi",          "Tenkasi"),
        ("Thanjavur",        "Thanjavur"),
        ("Theni",            "Theni"),
        ("Thiruvallur",      "Thiruvallur"),
        ("Thiruvarur",       "Thiruvarur"),
        ("Thoothukudi",      "Thoothukudi"),
        ("Tiruchirappalli",  "Tiruchirappalli"),
        ("Tirunelveli",      "Tirunelveli"),
        ("Tirupathur",       "Tirupathur"),
        ("Tiruppur",         "Tiruppur"),
        ("Tiruvannamalai",   "Tiruvannamalai"),
        ("Vellore",          "Vellore"),
        ("Viluppuram",       "Viluppuram"),
        ("Virudhunagar",     "Virudhunagar"),
    ]

    # -------------------
    # RELIGION CHOICES
    # -------------------
    RELIGION_CHOICES = [
        ("Hindu",     "Hindu"),
        ("Muslim",    "Muslim"),
        ("Christian", "Christian"),
        ("Sikh",      "Sikh"),
        ("Buddhist",  "Buddhist"),
        ("Jain",      "Jain"),
        ("Others",    "Others"),
    ]

    # -------------------
    # CASTE CHOICES — Tamil Nadu (all religions)
    # -------------------
    CASTE_CHOICES = [
        # No Caste
        ("Jaathi Thadai Illai",       "Jaathi Thadai Illai"),  # NEW from Excel

        # Hindu — OC / Forward
        ("Brahmin",                  "Brahmin"),
        ("Vellalar",                 "Vellalar"),
        ("Mudaliar",                 "Mudaliar"),
        ("Chettiar",                 "Chettiar"),
        ("Naidu",                    "Naidu"),
        ("Pillai",                   "Pillai"),
        ("Kamma",                    "Kamma"),
        ("Reddy",                    "Reddy"),
        ("Vysya",                    "Vysya"),
        ("Sourashtra",               "Sourashtra"),

        # Hindu — BC
        ("Vanniyar",                 "Vanniyar"),
        ("Gounder",                  "Gounder"),
        ("Thevar / Mukkulathor",     "Thevar / Mukkulathor"),
        ("Nadar",                    "Nadar"),
        ("Yadava (Konar)",           "Yadava (Konar)"),
        ("Vishwakarma",              "Vishwakarma"),
        ("Kaikolar (Sengunthar)",    "Kaikolar (Sengunthar)"),
        ("Padayachi",                "Padayachi"),
        ("Ezhavar",                  "Ezhavar"),
        ("Meenavar",                 "Meenavar"),
        ("Pattinavar",               "Pattinavar"),
        ("Idaiyar",                  "Idaiyar"),
        ("Muthuraja",                "Muthuraja"),
        ("Senguntha Mudaliar",       "Senguntha Mudaliar"),
        ("Agamudayar",               "Agamudayar"),

        # Hindu — MBC
        ("Palli (Agnikula Kshatriya)", "Palli (Agnikula Kshatriya)"),
        ("Urali Gounder",            "Urali Gounder"),
        ("Vettuva Gounder",          "Vettuva Gounder"),
        ("Kongu Vellalar Gounder",   "Kongu Vellalar Gounder"),
        ("Lambadi (Brinjari)",       "Lambadi (Brinjari)"),
        ("Kumbarar",                 "Kumbarar"),
        ("Vannar (Dhobi)",           "Vannar (Dhobi)"),
        ("Korava",                   "Korava"),
        ("Paravar",                  "Paravar"),

        # Hindu — SC
        ("Paraiyar",                 "Paraiyar"),
        ("Arunthathiyar",            "Arunthathiyar"),
        ("Adi Dravida",              "Adi Dravida"),
        ("Devendra Kula Vellalar",   "Devendra Kula Vellalar"),
        ("Pallan",                   "Pallan"),
        ("Chakkiliyar",              "Chakkiliyar"),

        # Hindu — ST
        ("Irular",                   "Irular"),
        ("Toda",                     "Toda"),
        ("Kota",                     "Kota"),
        ("Kurumba",                  "Kurumba"),
        ("Palliyar",                 "Palliyar"),
        ("Paniyan",                  "Paniyan"),

        # Muslim
        ("Labbai",                   "Labbai"),
        ("Rowther",                  "Rowther"),
        ("Marakkayar",               "Marakkayar"),
        ("Marakkar",                 "Marakkar"),
        ("Mappila",                  "Mappila"),
        ("Syed",                     "Syed"),
        ("Sheik",                    "Sheik"),
        ("Tamil Muslim",             "Tamil Muslim"),

        # Christian
        ("Roman Catholic",           "Roman Catholic"),
        ("CSI Christian",            "CSI Christian"),
        ("Nadar Christian",          "Nadar Christian"),
        ("Dalit Christian",          "Dalit Christian"),
        ("Protestant",               "Protestant"),

        # Other
        ("Other",                    "Other"),
    ]

    # -------------------
    # SUB CASTE CHOICES — Tamil Nadu (comprehensive)
    # -------------------
    SUB_CASTE_CHOICES = [
        # Brahmin sub-castes
        ("Iyer",                       "Iyer"),
        ("Iyengar",                    "Iyengar"),
        ("Vadama",                     "Vadama"),
        ("Vathima",                    "Vathima"),
        ("Brihacharanam",              "Brihacharanam"),
        ("Astasahasram",               "Astasahasram"),
        ("Gurukkal",                   "Gurukkal"),
        ("Smartha Brahmin",            "Smartha Brahmin"),
        # Vellalar sub-castes
        ("Saiva Vellalar",             "Saiva Vellalar"),
        ("Kondaikatti Vellalar",       "Kondaikatti Vellalar"),
        ("Karkatta Vellalar",          "Karkatta Vellalar"),
        ("Mudali (Arcot)",             "Mudali (Arcot)"),
        ("Saiva Pillai (Tirunelveli)", "Saiva Pillai (Tirunelveli)"),
        ("Illaththu Pillai",           "Illaththu Pillai"),
        ("Nanjil Mudali",              "Nanjil Mudali"),
        ("Veerakodi Vellalar",         "Veerakodi Vellalar"),
        ("Mudaliar (OC)",              "Mudaliar (OC)"),
        # Chettiar sub-castes
        ("Nattukotai Chettiar",        "Nattukotai Chettiar"),
        ("Sozhia Chetty",              "Sozhia Chetty"),
        ("Vellan Chettiar",            "Vellan Chettiar"),
        ("Karpoora Chettiar",          "Karpoora Chettiar"),
        ("Devanga Chettiar",           "Devanga Chettiar"),
        ("Pannirandam Chettiar",       "Pannirandam Chettiar"),
        # Gounder sub-castes
        ("Kongu Vellala Gounder",      "Kongu Vellala Gounder"),
        ("Urali Gounder",              "Urali Gounder"),
        ("Vettuva Gounder",            "Vettuva Gounder"),
        ("Kulala Gounder",             "Kulala Gounder"),
        # Thevar / Mukkulathor
        ("Kallar",                     "Kallar"),
        ("Maravar",                    "Maravar"),
        ("Agamudayar",                 "Agamudayar"),
        ("Muthuraja",                  "Muthuraja"),
        ("Senaithalaivar",             "Senaithalaivar"),
        # Nadar sub-castes
        ("Shanar",                     "Shanar"),
        ("Gramani",                    "Gramani"),
        # Vishwakarma / Aasari
        ("Aasari (Carpenter)",         "Aasari (Carpenter)"),
        ("Kollar (Blacksmith)",        "Kollar (Blacksmith)"),
        ("Thachar (Mason)",            "Thachar (Mason)"),
        ("Kannar (Bronze)",            "Kannar (Bronze)"),
        ("Tattar (Goldsmith)",         "Tattar (Goldsmith)"),
        # Scheduled Caste sub-castes
        ("Adi Dravida",                "Adi Dravida"),
        ("Arunthathiyar",              "Arunthathiyar"),
        ("Devendra Kula Vellalar",     "Devendra Kula Vellalar"),
        ("Chakkiliyar",                "Chakkiliyar"),
        ("Pallan",                     "Pallan"),
        ("Paraiyar",                   "Paraiyar"),
        ("Valluvan",                   "Valluvan"),
        # Scheduled Tribe sub-castes
        ("Irular",                     "Irular"),
        ("Toda",                       "Toda"),
        ("Kota",                       "Kota"),
        ("Kurumba",                    "Kurumba"),
        ("Palliyar",                   "Palliyar"),
        ("Paniyan",                    "Paniyan"),
        ("Sholiga",                    "Sholiga"),
        # Muslim sub-castes
        ("Labbai",                     "Labbai"),
        ("Rowther",                    "Rowther"),
        ("Marakkayar",                 "Marakkayar"),
        ("Marakkar",                   "Marakkar"),
        ("Mappila",                    "Mappila"),
        ("Syed",                       "Syed"),
        ("Sheik",                      "Sheik"),
        ("Dekkani Muslim",             "Dekkani Muslim"),
        ("Nattu Muslim",               "Nattu Muslim"),
        # Christian sub-castes
        ("Latin Catholic",             "Latin Catholic"),
        ("Roman Catholic",             "Roman Catholic"),
        ("CSI",                        "CSI"),
        ("Nadar Christian",            "Nadar Christian"),
        ("Dalit Christian",            "Dalit Christian"),
        ("Jacobite Christian",         "Jacobite Christian"),
        ("Pentecost",                  "Pentecost"),
        ("Lutheran",                   "Lutheran"),
        # Other
        ("Other",                      "Other"),
    ]

    # -------------------
    # RASI CHOICES
    # -------------------
    RASI_CHOICES = [
        ("Mesham",      "Mesham (மேஷம்)"),
        ("Rishabam",    "Rishabam (ரிஷபம்)"),
        ("Midhunam",    "Midhunam (மிதுனம்)"),
        ("Kadagam",     "Kadagam (கடகம்)"),
        ("Simmam",      "Simmam (சிம்மம்)"),
        ("Kanni",       "Kanni (கன்னி)"),
        ("Thulam",      "Thulam (துலாம்)"),
        ("Viruchigam",  "Viruchigam (விருச்சிகம்)"),
        ("Dhanusu",     "Dhanusu (தனுசு)"),
        ("Magaram",     "Magaram (மகரம்)"),
        ("Kumbam",      "Kumbam (கும்பம்)"),
        ("Meenam",      "Meenam (மீனம்)"),
    ]

    # -------------------
    # NAKSHATRA CHOICES
    # -------------------
    NAKSHATRA_CHOICES = [
        ("Ashwini",          "Ashwini (அஸ்வினி)"),
        ("Bharani",          "Bharani (பரணி)"),
        ("Karthigai",        "Karthigai (கார்த்திகை)"),
        ("Rohini",           "Rohini (ரோகிணி)"),
        ("Mirugashirisham",  "Mirugashirisham (மிருகசீரிஷம்)"),
        ("Thiruvadhirai",    "Thiruvadhirai (திருவாதிரை)"),
        ("Punarpoosam",      "Punarpoosam (புனர்பூசம்)"),
        ("Poosam",           "Poosam (பூசம்)"),
        ("Ayilyam",          "Ayilyam (ஆயில்யம்)"),
        ("Magam",            "Magam (மகம்)"),
        ("Pooram",           "Pooram (பூரம்)"),
        ("Uthiram",          "Uthiram (உத்திரம்)"),
        ("Hastham",          "Hastham (ஹஸ்தம்)"),
        ("Chithirai",        "Chithirai (சித்திரை)"),
        ("Swathi",           "Swathi (சுவாதி)"),
        ("Visakam",          "Visakam (விசாகம்)"),
        ("Anusham",          "Anusham (அனுஷம்)"),
        ("Kettai",           "Kettai (கேட்டை)"),
        ("Moolam",           "Moolam (மூலம்)"),
        ("Pooradam",         "Pooradam (பூராடம்)"),
        ("Uthiradam",        "Uthiradam (உத்திராடம்)"),
        ("Thiruvonam",       "Thiruvonam (திருவோணம்)"),
        ("Avittam",          "Avittam (அவிட்டம்)"),
        ("Sadayam",          "Sadayam (சதயம்)"),
        ("Poorattathi",      "Poorattathi (பூரட்டாதி)"),
        ("Uthirattathi",     "Uthirattathi (உத்திரட்டாதி)"),
        ("Revathi",          "Revathi (ரேவதி)"),
    ]

    # -------------------
    # LAGNAM CHOICES (same as Rasi — 12 signs)
    # -------------------
    LAGNAM_CHOICES = [
        ("Mesham",      "Mesham (மேஷம்)"),
        ("Rishabam",    "Rishabam (ரிஷபம்)"),
        ("Midhunam",    "Midhunam (மிதுனம்)"),
        ("Kadagam",     "Kadagam (கடகம்)"),
        ("Simmam",      "Simmam (சிம்மம்)"),
        ("Kanni",       "Kanni (கன்னி)"),
        ("Thulam",      "Thulam (துலாம்)"),
        ("Viruchigam",  "Viruchigam (விருச்சிகம்)"),
        ("Dhanusu",     "Dhanusu (தனுசு)"),
        ("Magaram",     "Magaram (மகரம்)"),
        ("Kumbam",      "Kumbam (கும்பம்)"),
        ("Meenam",      "Meenam (மீனம்)"),
    ]

    INDIAN_STATES = [
        ("Andhra Pradesh",    "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam",             "Assam"),
        ("Bihar",             "Bihar"),
        ("Chhattisgarh",      "Chhattisgarh"),
        ("Goa",               "Goa"),
        ("Gujarat",           "Gujarat"),
        ("Haryana",           "Haryana"),
        ("Himachal Pradesh",  "Himachal Pradesh"),
        ("Jharkhand",         "Jharkhand"),
        ("Karnataka",         "Karnataka"),
        ("Kerala",            "Kerala"),
        ("Madhya Pradesh",    "Madhya Pradesh"),
        ("Maharashtra",       "Maharashtra"),
        ("Manipur",           "Manipur"),
        ("Meghalaya",         "Meghalaya"),
        ("Mizoram",           "Mizoram"),
        ("Nagaland",          "Nagaland"),
        ("Odisha",            "Odisha"),
        ("Punjab",            "Punjab"),
        ("Rajasthan",         "Rajasthan"),
        ("Sikkim",            "Sikkim"),
        ("Tamil Nadu",        "Tamil Nadu"),
        ("Telangana",         "Telangana"),
        ("Tripura",           "Tripura"),
        ("Uttar Pradesh",     "Uttar Pradesh"),
        ("Uttarakhand",       "Uttarakhand"),
        ("West Bengal",       "West Bengal"),
    ]

    # -------------------------
    # USER LINK
    # -------------------------
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profiles'
    )

    # -------------------------
    # BASIC DETAILS
    # -------------------------
    full_name          = models.CharField(max_length=150, blank=True)
    gender             = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob                = models.DateField(null=True, blank=True)
    birth_time         = models.TimeField(null=True, blank=True)
    birth_place        = models.CharField(max_length=150, choices=TAMILNADU_DISTRICTS, blank=True)

    # Current Living
    is_currently_living = models.BooleanField(default=False)
    current_location    = models.CharField(max_length=150, blank=True, null=True)

    height     = models.CharField(max_length=20, blank=True)
    weight     = models.CharField(max_length=20, blank=True)
    complexion = models.CharField(max_length=50, blank=True)

    # -------------------------
    # RELIGION & HOROSCOPE
    # -------------------------
    religion  = models.CharField(max_length=50,  choices=RELIGION_CHOICES,  blank=True)
    caste     = models.CharField(max_length=100, choices=CASTE_CHOICES,  blank=True)
    sub_caste = models.CharField(max_length=100, choices=SUB_CASTE_CHOICES,  blank=True)
    gothram   = models.CharField(max_length=50,  blank=True)

    rasi      = models.CharField(max_length=50, choices=RASI_CHOICES,     blank=True)
    nakshatra = models.CharField(max_length=50, choices=NAKSHATRA_CHOICES, blank=True)
    laknam    = models.CharField(max_length=50, choices=LAGNAM_CHOICES,   blank=True)
    dosham    = models.CharField(max_length=20, choices=DOSHAM_CHOICES,   blank=True)

    # -------------------------
    # EDUCATION & CAREER
    # -------------------------
    education     = models.CharField(max_length=150, blank=True)
    occupation    = models.CharField(max_length=150, blank=True)
    company_name  = models.CharField(max_length=150, blank=True)
    job_location  = models.CharField(max_length=150, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    JOB_LOCATION_TYPE = [
        ("India", "India"),
        ("Other", "Other Country"),
    ]
    job_location_type = models.CharField(
        max_length=20,
        choices=JOB_LOCATION_TYPE,
       
        null=True,
        blank=True
    )
    job_state   = models.CharField(max_length=100, choices=INDIAN_STATES, blank=True, null=True)
    job_country = models.CharField(max_length=100, blank=True, null=True)

    # -------------------------
    # FAMILY SECTION
    # -------------------------
    has_father_details = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='N')
    has_mother_details = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='N')
    has_siblings       = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='N')

    father_name        = models.CharField(max_length=100, blank=True)
    father_occupation  = models.CharField(max_length=100, blank=True)
    mother_name        = models.CharField(max_length=100, blank=True)
    mother_occupation  = models.CharField(max_length=100, blank=True)
    no_of_brothers     = models.IntegerField(null=True, blank=True)
    no_of_sisters      = models.IntegerField(null=True, blank=True)

    # -------------------------
    # CONTACT
    # -------------------------
    phone            = models.CharField(max_length=20, blank=True)
    whatsapp_number  = models.CharField(max_length=20, blank=True)
    email            = models.EmailField(blank=True)

    address  = models.TextField(blank=True)
    city     = models.CharField(max_length=100, blank=True)
    state    = models.CharField(max_length=100, blank=True)
    country  = models.CharField(max_length=100, blank=True)
    pincode  = models.CharField(max_length=20,  blank=True)

    # -------------------------
    # ABOUT
    # -------------------------
    bio            = models.TextField(blank=True)
    hobbies        = models.TextField(blank=True)
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        null=True
    )


        # -------------------------
    # PARTNER PREFERENCE
    # -------------------------
    wanted = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Partner Preference"
    )

    # -------------------------
    # ASSETS
    # -------------------------
    assets = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Assets"
    )

    # -------------------------
    # SAIMURAI
    # -------------------------
    saimurai = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Saimurai"
    )

    # -------------------------
    # ERPU THISAI (Facing Direction)
    # -------------------------
    erpu_thisai = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Erpu Thisai"
    )

    # -------------------------
    # PERAPU VARESAI (Birth Order)
    # -------------------------
    perapu_varesai = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Perapu Varesai"
    )

    # -------------------------
    # PARENT CONTACT
    # -------------------------
    father_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Father Phone Number"
    )

    mother_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Mother Phone Number"
    )

    # -------------------------
    # MULTIPLE PHOTOS
    # -------------------------
    photo1 = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    photo5 = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    # -------------------------
    # SYSTEM FIELDS
    # -------------------------
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, default='SYSTEM')
    updated_by = models.CharField(max_length=100, blank=True, default='SYSTEM')

    datamode = models.CharField(
        max_length=1,
        choices=[('A', 'Active'), ('I', 'Inactive'), ('D', 'Deleted')],
        default='A'
    )

    def __str__(self):
        return f"{self.full_name or self.user}"

    class Meta:
        db_table = 'profile'
     
from django.db import models
from django.conf import settings

# models.py

class Wishlist(models.Model):
    """Store user's shortlisted profiles"""
    
    # User who shortlisted the profile
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    
    # Profile that was shortlisted
    to_profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    
    # Timestamps
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlist'
        ordering = ['-created_on']
        unique_together = ['from_user', 'to_profile']  # Prevent duplicate shortlists
        
    def __str__(self):
        return f"{self.from_user.username} shortlisted {self.to_profile.full_name}"

class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('INTEREST_RECEIVED', 'Interest Received'),
        ('INTEREST_ACCEPTED', 'Interest Accepted'),
        ('INTEREST_REJECTED', 'Interest Rejected'),
        ('PROFILE_VIEW', 'Profile Viewed'),
        ('SHORTLIST', 'Shortlisted'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_sent'
    )
    
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    is_read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_on']
        
    def __str__(self):
        return f"{self.user.username}: {self.title}"

from django.utils import timezone


# ============================================================================
# UPDATED Payment model — add to mck_master/models.py
# Adds valid_until (6-month validity), is_expired property, and helpers
# ============================================================================

from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta   # pip install python-dateutil

class Payment(models.Model):
    """
    Payment model with 3-tier plan support + duration-based validity window.
    """
    PAYMENT_STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED',    'Failed'),
        ('REFUNDED',  'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY',      'Razorpay'),
        ('CASH',          'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    PLAN_CHOICES = [
        ('THREE_MONTH', '3 Months - ₹2,999'),
        ('SIX_MONTH',   '6 Months - ₹5,999'),
        ('ONE_YEAR',    '1 Year - ₹11,999'),
    ]

    PLAN_CONFIG = {
        'THREE_MONTH': {'amount': 2999,  'validity_months': 3,  'profile_limit': 40,  'label': '3 Month'},
        'SIX_MONTH':   {'amount': 5999,  'validity_months': 6,  'profile_limit': 80,  'label': '6 Month'},
        'ONE_YEAR':    {'amount': 11999, 'validity_months': 12, 'profile_limit': 120, 'label': '1 Year'},
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments'
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='THREE_MONTH'
    )

    payment_id        = models.CharField(max_length=100, unique=True, null=True, blank=True)
    order_id          = models.CharField(max_length=100, unique=True)
    payment_signature = models.CharField(max_length=200, blank=True)

    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')

    status         = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='RAZORPAY')

    created_on   = models.DateTimeField(auto_now_add=True)
    updated_on   = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # ── Validity window ──────────────────────────────────────────────────────
    valid_from  = models.DateTimeField(null=True, blank=True)   # set on mark_completed
    valid_until = models.DateTimeField(null=True, blank=True)   # payment_date + plan months

    notes         = models.TextField(blank=True)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'payment'
        ordering = ['-created_on']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['order_id']),
            models.Index(fields=['valid_until']),
        ]

    def __str__(self):
        pid = self.payment_id or 'PENDING'
        exp = self.valid_until.strftime('%d %b %Y') if self.valid_until else 'N/A'
        return f"{self.user.email} | {self.plan} | {pid} | {self.status} | expires {exp}"

    # ── Lifecycle helpers ────────────────────────────────────────────────────

    def mark_completed(self, payment_id, signature):
        now = timezone.now()
        validity_months = self.PLAN_CONFIG.get(self.plan, {}).get('validity_months', 3)
        self.status            = 'COMPLETED'
        self.payment_id        = payment_id
        self.payment_signature = signature
        self.payment_date      = now
        self.valid_from        = now
        self.valid_until       = now + relativedelta(months=validity_months)
        self.save()

    def mark_failed(self, error_message):
        self.status = 'FAILED'
        self.notes  = error_message
        self.save()

    # ── Computed properties ──────────────────────────────────────────────────

    @property
    def is_expired(self):
        """True if the plan validity window has passed."""
        if self.status != 'COMPLETED':
            return True
        if not self.valid_until:
            return False    # legacy row with no validity — treat as valid
        return timezone.now() > self.valid_until

    @property
    def is_active(self):
        """True only if payment is COMPLETED and not yet expired."""
        return self.status == 'COMPLETED' and not self.is_expired

    @property
    def days_remaining(self):
        """Returns number of days left, or 0 if expired."""
        if not self.valid_until or self.is_expired:
            return 0
        delta = self.valid_until - timezone.now()
        return max(delta.days, 0)

    @property
    def profile_limit(self):
        """Returns profile view limit based on plan: 40 / 80 / 120."""
        return self.PLAN_CONFIG.get(self.plan, {}).get('profile_limit', 40)

    @property
    def plan_label(self):
        """Returns human-readable plan label."""
        return self.PLAN_CONFIG.get(self.plan, {}).get('label', '3 Month')
# ============================================================================
# ProfileView model — unchanged, included for completeness
# ============================================================================

class ProfileView(models.Model):
    """
    Records every time a paid user views a profile detail page.
    Used to enforce per-plan view limits.
    """
    viewer  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_views'
    )
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='views_received'
    )
    viewed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table      = 'profile_view'
        unique_together = ['viewer', 'profile']
        ordering      = ['-viewed_on']

    def __str__(self):
        return f"{self.viewer} viewed {self.profile}"

    @classmethod
    def count_for_user(cls, user):
        return cls.objects.filter(viewer=user).count()

    @classmethod
    def has_viewed(cls, user, profile):
        return cls.objects.filter(viewer=user, profile=profile).exists()

    @classmethod
    def record(cls, user, profile):
        """Record a view (idempotent — won't duplicate)."""
        return cls.objects.get_or_create(viewer=user, profile=profile)