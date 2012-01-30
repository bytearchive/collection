from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

def browse(request):
    return render(request, 'bundle/browse.html', {'create_class': 'active'})
   
def create(request):
    text = request.POST['bundle_text']
    print text
    return HttpResponseRedirect(reverse('bundle:browse'), )
   
