from django.db import  models
import uuid
class User(models.Model):
    name = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=True)
    upi = models.CharField(max_length=50, default=None, null=True, blank=True)
    licence = models.FileField(upload_to='licences/', null=True, blank=True,default=None)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    group = models.UUIDField(default=uuid.uuid4, editable=False)
    last_lat = models.FloatField(null=True, blank=True)
    last_lng = models.FloatField(null=True, blank=True)

    
class Journey(models.Model):
    vehicle_choices = (
        ('Bus', 'bus'),
        ('Bike', 'bike'),
        ('Van', 'van'),
        ('Car', 'car'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=10, choices=vehicle_choices)
    vehicle_no = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vacancy = models.IntegerField()
    date = models.DateTimeField()
    source_lat = models.FloatField(default=None)
    source_lon = models.FloatField(default=None)
    dest_lat = models.FloatField(default=None)
    dest_lon = models.FloatField(default=None)

class History(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driven_histories')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taken_histories')
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=10)
    vehicle_no = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Bookings(models.Model):
        status_choices=(("Pending","pending"),("InProgress","InProgress"),("Completed","completed"))
        vehicle_choices = (('Bus', 'bus'),('Bike', 'bike'),('Van', 'van'),('Car', 'car'),)
        customer=models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
        driver=models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver')
        status=models.CharField(choices=status_choices,default="Pending",max_length=20)
        source = models.CharField(max_length=50)
        destination = models.CharField(max_length=50)
        pickup=models.CharField(max_length=25)
        dropdown=models.CharField(max_length=25)
        vehicle_type = models.CharField(max_length=10, choices=vehicle_choices)
        vehicle_no = models.CharField(max_length=25)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        date = models.DateTimeField(default=None)
        booked_seats=models.IntegerField()

   

