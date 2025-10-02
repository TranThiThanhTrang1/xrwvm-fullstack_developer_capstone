# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_user(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration_request(request):
    if request.method == "POST":
        try:
            # Lấy dữ liệu từ body JSON
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")
            email = data.get("email")
            first_name = data.get("firstName")
            last_name = data.get("lastName")

            # Kiểm tra nếu username đã tồn tại
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Already Registered", "status": False})

            # Tạo user mới
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Đăng nhập tự động
            login(request, user)

            return JsonResponse({"userName": username, "status": True})

        except Exception as e:
            return JsonResponse({"error": str(e), "status": False})

    # Nếu không phải POST
    return JsonResponse({"error": "Invalid request method", "status": False})


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Lấy chi tiết dealer theo id
def get_dealer_details(request, dealer_id):
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealer})

# Lấy reviews theo dealer id + phân tích sentiment
def get_dealer_reviews(request, dealer_id):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)
    review_details = []

    for review in reviews:
        sentiment = "neutral"
        if "review" in review and review["review"]:
            sentiment_response = analyze_review_sentiments(review["review"])
            if sentiment_response and "sentiment" in sentiment_response:
                sentiment = sentiment_response["sentiment"]

        review_details.append({
            "id": review.get("id"),
            "name": review.get("name"),
            "dealership": review.get("dealership"),
            "review": review.get("review"),
            "purchase": review.get("purchase"),
            "purchase_date": review.get("purchase_date"),
            "car_make": review.get("car_make"),
            "car_model": review.get("car_model"),
            "car_year": review.get("car_year"),
            "sentiment": sentiment
        })

    return JsonResponse({"status": 200, "reviews": review_details})

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})

def get_cars(request):
    if CarModel.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
            "Type": car_model.type,
            "Year": car_model.year,
            "DealerId": car_model.dealer_id,
        })
    return JsonResponse({"CarModels": cars})
