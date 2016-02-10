from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from tiramisu.models import Requirements, VM, Cube
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def index(request):
	if not request.session.is_empty() or request.user.is_anonymous():
		user = User.objects.get(id=request.session['user_id'])
		user_id = user.id
		vm = VM.objects.filter(owner=user_id)
		template = loader.get_template('index.html')
		context = RequestContext(request, {
			'name': user.username,
			'id': user.id,
			'vm_list': vm,
		})
		return HttpResponse(template.render(context))
	else:
		return HttpResponseRedirect('tiramisu/login')

def home(request):
	return render(request,'home.html')

def login(request):
	return render(request,'login.html')

def loginsuccess(request):
	usr = request.POST['username']
	passwd = request.POST['password']
	user = authenticate(username=usr, password=passwd)
	if user is not None:
		# the password verified for the user
		if user.is_active:
			u = User.objects.get(username=usr)
			request.session['user_id'] = u.id
			print request.session['user_id']
			return HttpResponseRedirect('/tiramisu/index')
		else:
			return HttpResponse("The password is valid, but the account has been disabled!")
	else:
		# the authentication system was unable to verify the username and password
		return HttpResponse("The username and password were incorrect.<br><br><a href=\"/\"><button>LOGIN</button></a>")

def logout(request):
	if not request.session.is_empty():
		request.session.delete()
		return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('login/')

def manage(request):
	template = loader.get_template('requirements.html')
	id = request.GET['id']	
	context = RequestContext(request, {
		'id': id })
   	return HttpResponse(template.render(context))

def test(request):
	return HttpResponseRedirect("/tiramisu/index")

def cal_percent(pc, data):
	return (data * pc) / 100.00

def change_requirements(request):
	if request.method == 'POST':
		id_vm 	= request.POST['name']
		name = VM.objects.get(pk=id_vm)
		req = Requirements.objects.get(pk=name.name)
		req.latency 	= request.POST['latency']
		req.latency_max = request.POST['latency_max']
		req.percentl 	= request.POST['percentl']
		req.iops_min 	= request.POST['iops_min']
		req.iops 		= request.POST['iops']
		req.percenti 	= request.POST['percenti']
		req.cost 		= request.POST['cost']
		req.cost_max 	= request.POST['cost_max']
		req.percentc 	= request.POST['percentc']
		req.app_type 	= request.POST['type']
		req.save()

		cube = Cube.objects.get(pk=name.name)
		cube.latency_min	= float(request.POST['latency']) - cal_percent(float(request.POST['percentl']), float(request.POST['latency']))
		cube.latency 		= request.POST['latency']
		cube.latency_max 	= request.POST['latency_max']
		cube.percentl 		= request.POST['percentl']
		cube.iops_min 		= request.POST['iops_min']
		cube.iops 			= request.POST['iops']
		cube.iops_max 		= float(request.POST['iops']) + cal_percent(float(request.POST['percenti']), float(request.POST['iops']))
		cube.percenti 		= request.POST['percenti']
		cube.cost_min 		= float(request.POST['cost']) - cal_percent(float(request.POST['percentc']), float(request.POST['cost']))
		cube.cost 			= request.POST['cost']
		cube.cost_max 		= request.POST['cost_max']
		cube.percentc 		= request.POST['percentc']
		cube.app_type 		= request.POST['type']
		cube.save()

		command = 'ssh tuck@161.246.70.75 ./call_model ' + name.name
		os.system(command)
		return HttpResponseRedirect("/tiramisu/index/")

def create_vm(request):
	if request.method == 'POST':
		vm = VM()
		vm.owner 	= request.POST['owner']
		vm.name 	= request.POST['name']
		vm.ip 		= request.POST['ip']
		vm.status 	= request.POST['status']
		vm.save()
		return HttpResponseRedirect("/tiramisu/index/")

def register(request):
    return render(request,'register.html')

def registersuccess(request):
    usr = request.POST['username']
    passwd = request.POST['password']
    user = User.objects.create_user(usr, '', passwd)
    user.save()
    return HttpResponseRedirect('/tiramisu/login/')

@csrf_exempt
def vmname_availability(request):
	if not request.session.is_empty() or request.user.is_anonymous():
		user = User.objects.get(id=request.session['user_id'])	
		if request.method == 'POST':
			vm_name = str(user.id)+request.POST.get('vm_name')
			#vmObject = VM.objects.get(name=vm_name)
			#vmObject = get_object_or_404(VM, name=vm_name)
			try:
				vmObject = VM.objects.get(name=vm_name)
			except VM.DoesNotExist:
				vmObject = None
			if vmObject == None:
				response_data = {'result' : 'pos'}
			else:
				response_data = {'result' : 'neg'}
			return JsonResponse(response_data)

def createvm(request):
	if not request.session.is_empty() or request.user.is_anonymous():
		user = User.objects.get(id=request.session['user_id'])	
		if request.method == 'GET':
			template = loader.get_template('createvm.html')	
			context = RequestContext(request)
   			return HttpResponse(template.render(context))

		if request.method == 'POST':
			vm_name = str(user.id)+request.POST['name']
			vm = VM()
			vm.owner 	= user.id
			vm.name 	= vm_name
			vm.ip 		= request.POST['ip']
			vm.status 	= request.POST['status']
			vm.save()
			
			req = Requirements()
			req.vm_name		= vm_name
			req.latency 	= request.POST['latency']
			req.latency_max = request.POST['latency_max']
			req.percentl 	= request.POST['percentl']
			req.iops_min 	= request.POST['iops_min']
			req.iops 		= request.POST['iops']
			req.percenti 	= request.POST['percenti']
			req.cost 		= request.POST['cost']
			req.cost_max 	= request.POST['cost_max']
			req.percentc 	= request.POST['percentc']
			req.app_type 	= request.POST['type']
			req.save()

			cube = Cube()
			cube.vm_name		= vm_name
			cube.latency_min	= float(request.POST['latency']) - cal_percent(float(request.POST['percentl']), float(request.POST['latency']))
			cube.latency 		= request.POST['latency']
			cube.latency_max 	= request.POST['latency_max']
			cube.percentl 		= request.POST['percentl']
			cube.iops_min 		= request.POST['iops_min']
			cube.iops 			= request.POST['iops']
			cube.iops_max 		= float(request.POST['iops']) + cal_percent(float(request.POST['percenti']), float(request.POST['iops']))
			cube.percenti 		= request.POST['percenti']
			cube.cost_min 		= float(request.POST['cost']) - cal_percent(float(request.POST['percentc']), float(request.POST['cost']))
			cube.cost 			= request.POST['cost']
			cube.cost_max 		= request.POST['cost_max']
			cube.percentc 		= request.POST['percentc']
			cube.app_type 		= request.POST['type']
			cube.save()

			command = 'ssh tuck@161.246.70.75 ./call_model ' + name.name
			os.system(command)
			return HttpResponseRedirect("/tiramisu/index/")
	else:
		return HttpResponseRedirect('tiramisu/login')