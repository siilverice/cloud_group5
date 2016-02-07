from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
def index(request):
	return render(request,'starter.html')

def manage(request):

	template = loader.get_template('requirements.html')
	id = request.GET['id']	
	context = RequestContext(request, {
		'id': id })
   	return HttpResponse(template.render(context))

def test(request):
	return HttpResponseRedirect("/tiramisu/index")