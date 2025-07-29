from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response # adjust import as needed
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import UserSerializer, JourneySerializer
from rest_framework.views import APIView
from django.shortcuts import render,redirect
from .utils import routing_util as ru
import datetime
from geopy.geocoders import Nominatim
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def driver(req):
    return render(req,'driver.html')

def customer(req):
    return render(req,'ticket.html')


def driver_test(req):
    return render(req,'drivertracking.html')

def register(req):
    return render(req,'register.html')

def login(req):
    if req.method=="POST":
        email=req.POST.get("email")
        password=req.POST.get("pass")
        query=User.objects.all()
        matched=False
        for i in query:
            if i.email==email and i.password==password:
               matched=True
               break
        if matched==True:
           user=User.objects.filter(email=email,password=password)[0]
           req.session["user"]=user.id
           return redirect("home")
    return render(req,'login.html')

def home(req):
    user_type = "customer"
    ride_id = None
    user_id = req.session.get('user')
    if not user_id:
        return redirect('login')  
    try:
        user = User.objects.get(id=user_id)
        user_type = "driver"
        ride_id = user.group
    except ObjectDoesNotExist:
        pass 
    print(user_type, ride_id)
    return render(req, 'index.html', {"user_type": user_type,"ride_id": ride_id})

def createride(req):
    if req.method=="POST":
       user=User.objects.get(id=req.session.get('user'))
       source=req.POST.get('source')
       dest=req.POST.get('dest')
       vehicleno=req.POST.get('vehicleno')
       vehicle=req.POST.get('vehicle')
       price=req.POST.get('price')
       vacancy=req.POST.get('vacancy')
       s_lat,s_long=ru.get_coordinates(source)
       d_lat,d_long=ru.get_coordinates(dest)
       Journey.objects.create(user=user,source=source,destination=dest,vacancy=vacancy,vehicle_no=vehicleno,vehicle_type=vehicle,price=price,date=datetime.datetime.now(),source_lat=s_lat,source_lon=s_long,dest_lat=d_lat,dest_lon=d_long)
       return redirect('home')
    return render(req,'create_ride.html')

def search_ride(req):
    if req.method=="POST":
       source=req.POST.get("from")
       destination=req.POST.get("to")
       print(source,destination)
       data=ru.find_matching_routes(req,source,destination)
       print(data)
       req.session["pickup"]=source
       req.session["dropdown"]=destination
       return render(req,'display_vehicles.html',{"data":data})
    return render(req,'search_ride.html')

def ride_details(req,id):
    journey=Journey.objects.get(id=id)
    return render(req,'ride_details.html',{"ride":journey})

def display_vehicles(req):
    return render(req,'display_vehicles.html')

def ticket(req,id):
    data=Bookings.objects.filter(id=id)
    return render(req,'ticket.html',{"data":data})

def get_coordinates(city_name):
        geolocator = Nominatim(user_agent="midwayhelper/1.0 (gangarapurohith4@gmail.com)")  # You can customize the user-agent
        location = geolocator.geocode(city_name)
        if location:
            print(f"📍 {city_name} → Latitude: {location.latitude}, Longitude: {location.longitude}")
            return [location.latitude,location.longitude]
        else:
            print("❌ City not found")

def tracking(request,id):
    journey=Bookings.objects.get(id=id)
    r=User.objects.get(name=Bookings.objects.get(id=id).driver.name)
    source=get_coordinates(journey.source)
    destination=get_coordinates(journey.destination)
    pickup=get_coordinates(journey.pickup)
    dropdown=get_coordinates(journey.dropdown)
    context = {
        "ride_id": str(r.group),
        "last_lat": r.last_lat,   # use actual field names
        "last_lng": r.last_lng,
        "source":source,
        "destination":destination,
        "pickup":pickup,
        "dropdown":dropdown
    }
    print(context)
    return render(request, "tracking.html", {"context":context})

def booking_list(req):
    if req.method=="GET":
        userid=req.session.get("user")
        drive=Bookings.objects.filter(driver=User.objects.get(id=userid))
        cust=Bookings.objects.filter(customer=User.objects.get(id=userid))
        driver_bookings,customer_bookings=[],[]
        for i in drive:
            driver_bookings+=[i]
        for i in cust:
            customer_bookings+=[i]

    return render(req,'bookings.html',{"driver_bookings":driver_bookings,"customer_bookings":customer_bookings})

def book(req,driver):
    if req.method=="POST":
        seats=int(req.POST.get("seats"))
        journey=Journey.objects.get(user=User.objects.get(name=driver))
        bookings=Bookings.objects.create(customer=User.objects.get(id=req.session.get("user")),driver=User.objects.get(name=driver),source=journey.source,destination=journey.destination,vehicle_type=journey.vehicle_type,vehicle_no=journey.vehicle_no,price=journey.price,date=journey.date,booked_seats=seats,pickup=req.session.get("pickup"),dropdown=req.session.get("dropdown"))
        journey.vacancy-=seats 
        if journey.vacancy==0:
           journey.delete()
        journey.save()
        print("done")
    return render(req,'index.html')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    

class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        user = User.objects.filter(id=user_id).first()
        if not user or not user.licence or not user.upi:
            return Response({"error": "User must have uploaded licence and UPI to create a journey."}, status=400)
        return super().create(request, *args, **kwargs)

class JourneySearchView(APIView):
    def get(self, request):
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        if not source or not destination:
            return Response({"error": "Please provide source and destination."}, status=400)
        journeys = Journey.objects.filter(source=source, destination=destination)
        serializer = JourneySerializer(journeys, many=True)
        return Response(serializer.data)
