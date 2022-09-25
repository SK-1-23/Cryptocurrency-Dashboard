from django.shortcuts import render, render_to_response
from django.http import HttpResponse,JsonResponse
from django.http import HttpResponseRedirect, HttpRequest
from final_year import models
from django.conf import settings
import json
from datetime import datetime,timedelta, date
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import authenticate,login, logout
import os
import re
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import csv
import time
import yaml
from django.core.mail import send_mass_mail
import base64

## to render home page
def index(request):
	return render_to_response('index.html')

## to render login page
def login_view(request):
	return render_to_response('login_page.html')

## to render create account page
def signup_view(request):
	return render(request,'signup.html')

## to create user account
def register_view(request):
	username=request.GET['uname']
	password=request.GET['pswd']
	email=request.GET['email']
	user=User.objects.create_user(username,email,password)
	user.save()
	return HttpResponse(json.dumps('done'))

## authenticating function for the user
@csrf_exempt
def authenticate_view(request):
	username=request.POST['uname']
	password=request.POST['pswd']
	user=authenticate(username=username,password=password)
	if user is not None:
		if user.is_active:
			login(request,user)

			return HttpResponse(json.dumps({"success":True}))
		else:
			return HttpResponse(json.dumps('The account has been disabled!'))
	else:
		return HttpResponse(json.dumps({"success":False}))

def logout(request):
    auth.logout(request)
    # return HttpResponseRedirect('/crypto_dashboard/signin')
    return HttpResponse(json.dumps('done'))

## rendering dashboard template
def render_dashboard(request):
	url_coin = "https://api.lunarcrush.com/v2?data=assets&key=84j1u9ud85a2rbka3v9vtd&symbol="
	url_inr= "https://free.currconv.com/api/v7/convert?q=USD_INR&compact=ultra&apiKey=5e1a9358700714ccd11f"
	coin_to_check=["BTC","ETH","DOGE","DAI"]
	user = request.user
	price_now=[]
	coin_overall_data = {}
	inr_price= requests.get(url_inr).json()['USD_INR']
	coin_dict={"DAI": "Dai", "DOGE": "Doge Coin","BTC":'Bitcoin',"ETH":"Ethereum"}
	coin_alert_val = {}
	for coin in coin_to_check:
		data=requests.get(url_coin+coin).json()['data'][0]
		coin_alert_val[coin.lower()]=""
		data['name'] = coin_dict[coin]
		coin_overall_data[coin] = data
		price_now.append({'curr_price':round(data['price']*inr_price,2),
						'change':data['percent_change_24h'],
						'name':data['name'],
						'symbol':coin.lower(),
						})

	##-------- This is backup code if api request is not responding----------------##
	# obj = models.backup_db.objects.first()
	# price_now = yaml.safe_load(obj.price_now)
	# coin_overall_data = yaml.safe_load(obj.coin_overall_data)
	##-----------------Backup code end ---------------##
	alert_config_obj = models.custom_alert.objects.filter(user=user).first()
	##---------------- send notification code-----------##
	if alert_config_obj:
		coin_alert_val = json.loads(alert_config_obj.alert_config)
		send_notification(coin_alert_val,price_now,user)

	if 'data_only' in request.GET:
		return HttpResponse(json.dumps({'inr_price':inr_price,
							'coin_overall_data':coin_overall_data,
							'price_now':price_now,
							'coin_alert_val':coin_alert_val
							}))
	future_data = read_future_data()
	return render(request,'dashboard.html',{'price_now':price_now,
				'inr_price': inr_price,
				'coin_overall_data':json.dumps(coin_overall_data),
				'coin_alert_val':json.dumps(coin_alert_val),
				'future_data':json.dumps(future_data),
				})

## mail notification function
def send_notification(coin_alert_val,price_now,user):
	dict_map={'eth':'Etherium','btc':"Bitcoin","doge":'Doge Coin','dai':'DAI'}
	mail_list=[]
	for coin in coin_alert_val:
		if coin_alert_val[coin][0]!="":
			config_price = float(coin_alert_val[coin][0])
			coin_price = get_coin_price(price_now,coin)
			notification_buy = coin_alert_val[coin][1]
			user_mail = user.email
			username= user.username
			subject = "{} {} Alert"
			message= "Dear {}, your {} price has {} to {} by {} % please {} as soon as possibe."
			percent = round(((coin_price-config_price)/config_price)*100,2)
			send_mail =False
			if notification_buy==True and coin_price<=config_price:
				subject= subject.format(dict_map[coin],'Buy')
				message= message.format(username,dict_map[coin],"Decreased",coin_price,percent,'Buy')
				send_mail=True
			elif notification_buy==False and coin_price>=config_price:
				subject= subject.format(dict_map[coin],'Sell')
				message= message.format(username,dict_map[coin],"Increased",coin_price,percent,'Sell')
				send_mail = True
			if send_mail:
				print(subject,message,"===send")
				mail_list.append((subject, message, 'bhattritanshu01@gmail.com', [user_mail]))
	send_mass_mail(mail_list, fail_silently=True)


def get_coin_price(price_now,coin):
	for coin_data in price_now:
		if coin_data['symbol']==coin:
			return coin_data['curr_price']

## get future prediction data from the ML model
def read_future_data():
	future_data = {}
	base_dir= os.path.join(settings.PYTH_DIR,"Data")
	for csv_file in  os.listdir(base_dir):
		coin_data= []
		if csv_file.split(".")[-1]=='csv':
			with open(os.path.join(base_dir,csv_file), 'r') as file:
				reader = csv.reader(file,delimiter = '\t')
				i=0
				for row in reader:
					i+=1
					if i==1:
						continue
					coin_data.append([to_seconds(dateutil.parser.parse(row[1])),round(float(row[2]),2)])
			future_data[csv_file.split(".")[0].upper()]=coin_data[::]
	return future_data

## saving custom alert configuration to the db
def save_custom_alert(request):
	existing_entry = models.custom_alert.objects.filter(user=request.user).first()
	data = request.GET['data']
	if not existing_entry:
		existing_entry = models.custom_alert()
		existing_entry.user = request.user
	existing_entry.alert_config = data
	existing_entry.save()
	return HttpResponse(json.dumps('done'))

def to_seconds(date):
    return time.mktime(date.timetuple())

## rendering profile content of the user
def render_profile_content(request):
	user_details_obj = models.user_profile.objects.filter(user=request.user).first()
	data = {'user_id': request.user.username,
			'name':'',
			'email':request.user.email,
			'phone':'',
			'img':None,
			}
	if user_details_obj:
		base_dir= os.path.join(settings.PYTH_DIR,"Data")
		file = '{}_profile.png'.format(request.user.username)
		if file in  os.listdir(base_dir):
			with open(os.path.join(base_dir,file), "rb") as image_file:
				encoded_string = base64.b64encode(image_file.read())
				data['img'] = encoded_string
		data['name'] = user_details_obj.name
		data['phone'] = user_details_obj.phone
	template = render_to_response("profile.html",{'data':data}).content
	return HttpResponse(json.dumps(template))

## save changes in user profile input to db
def save_user_profile(request):
	image=None
	if 'profile_img' in request.FILES:
		image = request.FILES['profile_img']
	phone= request.POST['phone']
	name = request.POST['name']
	user_details_obj = models.user_profile.objects.filter(user=request.user).first()
	if not user_details_obj:
		user_details_obj = models.user_profile()
		user_details_obj.user= request.user
	user_details_obj.phone = phone
	user_details_obj.name= name
	user_details_obj.save()
	if image:
		dest_dir = os.path.join(settings.PYTH_DIR,"Data")
		for chunk in image.chunks():
			destination = open(os.path.join(dest_dir,"{}_profile.png".format(request.user.username)), 'wb+')
			destination.write(chunk)
		destination.close()
	return HttpResponse(json.dumps("done"));

def render_faq_content(request):
	template = render_to_response("faq.html").content
	return HttpResponse(json.dumps(template))

