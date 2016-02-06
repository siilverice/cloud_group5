from django.shortcuts import render

# Create your views here.
def index(request):
	return render(request,'starter.html')

def manage(request):
	return render(request,'requirements.html')