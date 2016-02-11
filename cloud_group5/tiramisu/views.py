from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from tiramisu.models import Requirements, VM, Cube, Storage, State
import os, subprocess
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
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	template = loader.get_template('requirements.html')
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	req = Requirements.objects.get(vm_name=current_vm.name)
	if int(req.app_type) == 1:
		web = 1
		db = 0
		bj = 0
	elif int(req.app_type) == 2:
		web = 0
		db = 1
		bj = 0
	else:
		web = 0
		db = 0
		bj = 1
	context = RequestContext(request, {
		'id_vm': id_vm,
		'name': user.username,
		'id': user.id,
		'vm_list': vm,
		'req': req,
		'web': web,
		'db': db,
		'bj': bj,
		'current_name': current_vm.name_display,
		'apply': 0 })
   	return HttpResponse(template.render(context))

def cal_percent(pc, data):
	return (data * pc) / 100.00

def change_requirements(request):
	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection_model'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	if request.method == 'POST':
		id_vm 	= request.POST['name']
		name = VM.objects.get(pk=id_vm)
		req = Requirements.objects.get(pk=name.name)
		req_old = Requirements.objects.get(pk=name.name)
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
		cube_old = cube
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

		user = User.objects.get(id=request.session['user_id'])
		user_id = user.id
		vm = VM.objects.filter(owner=user_id)
		template = loader.get_template('apply.html')
		id_vm = request.POST['name']
		current_vm = VM.objects.get(id=id_vm)
		state = State.objects.get(vm_name=current_vm.name)
		storage = Storage.objects.get(vm_name=current_vm.name)
		if storage.appropiate_pool == 'HDD':
			appropiate_latency = state.latency_hdd
			appropiate_iops = state.iops_hdd
			cost = float(current_vm.size) * 0.050
		else:
			appropiate_latency = state.latency_ssd
			appropiate_iops = state.iops_ssd
			cost = float(current_vm.size) * 0.090
		if int(req.app_type) == 1:
			web = 1
			db = 0
			bj = 0
		elif int(req.app_type) == 2:
			web = 0
			db = 1
			bj = 0
		else:
			web = 0
			db = 0
			bj = 1
		if storage.current_pool == storage.appropiate_pool:
			change = 0
		else:
			change = 1
		context = RequestContext(request, {
			'id_vm': id_vm,
			'name': user.username,
			'id': user.id,
			'vm_list': vm,
			'req': req,
			'web': web,
			'db': db,
			'bj': bj,
			'current_name': current_vm.name,
			'apply': 1,
			'req_old': req_old,
			'appropiate_pool': storage.appropiate_pool,
			'appropiate_iops': appropiate_iops,
			'appropiate_latency': appropiate_latency,
			'cost': cost,
			'change': change, })
		return HttpResponse(template.render(context))
	else:
		return HttpResponseRedirect("/tiramisu/index")

def register(request):
    return render(request,'register.html')

def registersuccess(request):
	usr = request.POST['username']
	passwd = request.POST['password']
	user = User.objects.create_user(usr, '', passwd)
	user.save()
	return HttpResponseRedirect('/tiramisu/login/')

def showdetails(request):
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	template = loader.get_template('showdetails.html')
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	state = State.objects.get(vm_name=current_vm.name)
	storage = Storage.objects.get(vm_name=current_vm.name)
	if storage.current_pool == 'HDD':
		hdd = 1
	else:
		hdd = 0
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
		'turnoff': turnoff,
		'hdd': hdd,
		'rusure': 0 })
   	return HttpResponse(template.render(context))

def move(request):
	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection_move'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	command = 'ssh -t tuck@161.246.70.75 ./call_move ' + current_vm.name
	os.system(command)
	link = "../details/?id=" + id_vm
	return HttpResponseRedirect(link)

def turnoff(request):
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	storage = Storage.objects.get(vm_name=current_vm.name)
	storage.notice = 0
	storage.save()
	link = "../details/?id=" + id_vm
	return HttpResponseRedirect(link)

def turnon(request):
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	storage = Storage.objects.get(vm_name=current_vm.name)
	storage.notice = 1
	storage.save()
	link = "../details/?id=" + id_vm
	return HttpResponseRedirect(link)

def cancel(request):
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

		link = "../manage?id=" + id_vm
		return HttpResponseRedirect(link)

@csrf_exempt
def vmname_availability(request):
	if not request.session.is_empty() or request.user.is_anonymous():
		user = User.objects.get(id=request.session['user_id'])	
		if request.method == 'POST':
			vm_name = str(user.id)+request.POST.get('vm_name')
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
	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection_init'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	if not request.session.is_empty() or request.user.is_anonymous():
		user = User.objects.get(id=request.session['user_id'])	
		if request.method == 'GET':
			template = loader.get_template('createvm.html')	
			user = User.objects.get(id=request.session['user_id'])
			user_id = user.id
			vm = VM.objects.filter(owner=user_id)
			context = RequestContext(request, {
				'name': user.username,
				'id': user.id,
				'vm_list': vm,
			})
   			return HttpResponse(template.render(context))

		if request.method == 'POST':
			vm_name = str(user.id)+request.POST['name']
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

			state = State()
			state.vm_name		= vm_name
			state.latency 		= 8
			state.iops 			= 8
			state.latency_hdd	= 8
			state.iops_hdd		= 8
			state.latency_ssd	= 8
			state.iops_ssd		= 8
			state.save()

			command = 'ssh -t tuck@161.246.70.75 ./call_init ' + vm_name + " " + request.POST['name'] + " " + str(user.id)
			os.system(command)

			vm = VM.objects.get(name=vm_name)
			link = "/tiramisu/createvmsuccess/?id=" + str(vm.id)
			return HttpResponseRedirect(link)
	else:
		return HttpResponseRedirect('tiramisu/login')

def createvmsuccess(request):
	id_vm = request.GET['id']
	your_vm = VM.objects.get(id=id_vm)
	template = loader.get_template('createvmsuccess.html')
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	context = RequestContext(request, {
		'name': user.username,
		'id': user.id,
		'vm_list': vm,
		'ip': your_vm.ip,
	})
   	return HttpResponse(template.render(context))

def servererror(request):
	template = loader.get_template('500page.html')
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	context = RequestContext(request, {
		'name': user.username,
		'id': user.id,
		'vm_list': vm,
	})
	return HttpResponse(template.render(context))

def shutdown(request):
	id_vm = request.GET['id']
	your_vm = VM.objects.get(id=id_vm)

	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	command = 'ssh -t tuck@161.246.70.75 ./call_onoff shutdown ' + your_vm.name
	os.system(command)

	your_vm.status = 0
	your_vm.save()
	
	link = "/tiramisu/details/?id=" + id_vm
	return HttpResponseRedirect(link)

def start(request):
	id_vm = request.GET['id']
	your_vm = VM.objects.get(id=id_vm)

	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	command = 'ssh -t tuck@161.246.70.75 ./call_onoff start ' + your_vm.name
	os.system(command)

	your_vm.status = 1
	your_vm.save()
	
	link = "/tiramisu/details/?id=" + id_vm
	return HttpResponseRedirect(link)

def delete(request):
	id_vm = request.GET['id']
	your_vm = VM.objects.get(id=id_vm)

	try:
		subprocess.check_call(['ssh','tuck@161.246.70.75','./check_connection_delete'])
	except:
		return HttpResponseRedirect("/tiramisu/servererror")

	command = 'ssh -t tuck@161.246.70.75 ./call_delete ' + your_vm.name
	os.system(command)

	state = State.objects.get(vm_name=your_vm.name)
	state.delete()
	cube = Cube.objects.get(vm_name=your_vm.name)
	cube.delete()
	req = Requirements.objects.get(vm_name=your_vm.name)
	req.delete()
	storage = Storage.objects.get(vm_name=your_vm.name)
	storage.delete()
	your_vm.delete()

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

def rusure(request):
	user = User.objects.get(id=request.session['user_id'])
	user_id = user.id
	vm = VM.objects.filter(owner=user_id)
	template = loader.get_template('showdetails.html')
	id_vm = request.GET['id']
	current_vm = VM.objects.get(id=id_vm)
	state = State.objects.get(vm_name=current_vm.name)
	storage = Storage.objects.get(vm_name=current_vm.name)
	if storage.current_pool == 'HDD':
		hdd = 1
	else:
		hdd = 0
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
		'turnoff': turnoff,
		'hdd': hdd,
		'rusure': 1 })
   	return HttpResponse(template.render(context))