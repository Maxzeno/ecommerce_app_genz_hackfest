from django.shortcuts import render

# Create your views here.


def error_404(request, exception):
	return render(request, 'main/404.html', context={'msg': "requested page not found"}, status=404)

# def error_500(request):
    # return render(request, 'main/500.html', status=500)