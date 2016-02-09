from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from tiramisu.models import Requirements, VM, Cube
import os
# Create your views here.
def index(request):
	return render(request,'index.html')

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

def listvm(request):
	