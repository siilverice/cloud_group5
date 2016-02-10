from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from tiramisu.models import Requirements, VM, Cube, Storage, State
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
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
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	template = loader.get_template('requirements.html')
	id_vm = request.GET['id']	
	context = RequestContext(request, {
		'id_vm': id_vm,
		'name': user.username,
		'id': user.id,
		'vm_list': vm, })
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
    return HttpResponseRedirect('/tiramisu/index/')

def showdetails(request):
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	template = loader.get_template('showdetails.html')
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	state = State.objects.get(vm_name=current_vm.name)
	storage = Storage.objects.get(vm_name=current_vm.name)
	if storage.current_pool != storage.appropiate_pool and storage.notice:
		notice = 1
	else:
		notice = 0
	if not storage.notice:
		turnoff = 1
	else:
		turnoff = 0
	context = RequestContext(request, {
		'id_vm': id_vm,
		'name': user.username,
		'id': user.id,
		'vm_list': vm,
		'storage': storage,
		'current_vm': current_vm,
		'state': state,
		'notice': notice,
		'turnoff': turnoff, })
   	return HttpResponse(template.render(context))

def move(request):
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	command = 'ssh -t tuck@161.246.70.75 ./call_move ' + current_vm.name
	os.system(command)
	link = "../details?id=" + id_vm
	return HttpResponseRedirect(link)

def turnoff(request):
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	storage = Storage.objects.get(vm_name=current_vm.name)
	storage.notice = 0
	storage.save()
	link = "../details?id=" + id_vm
	return HttpResponseRedirect(link)

def turnon(request):
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	storage = Storage.objects.get(vm_name=current_vm.name)
	storage.notice = 1
	storage.save()
	link = "../details?id=" + id_vm
	return HttpResponseRedirect(link)