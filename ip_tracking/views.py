from django.shortcuts import render
from rest_framework.views import APIView
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator


def get_rate_key(group, request):
    """
    Determine key used for rate limiting
    """
    if request.user.is_authenticated:
        return str(request.user.pk)
    return request.META.get("REMOTE_ADDR")


def ratelimit_view(group=None, rate=None, method="POST"):
    """
    Rate limit decorator with a dynamic key.
    """

    def decorator(view_func):
        return ratelimit(key=get_rate_key, rate=rate, method=method, block=True)(
            view_func
        )

    return decorator


@method_decorator(ratelimit_view(rate="5/m"), name="dispatch")
class CustomLoginView(LoginView):
    """
    Custom login view with rate limiting
    """

    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            decorator = ratelimit_view(rate="10/m")
            decorated_dispatch = decorator(super().dispatch)
            return decorated_dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def handle_ratelimited(self, request, exception):
        """
        Handle ratelimited exception
        """
        return HttpResponse("Rate limit exceeded. Try again later.", status=429)


# class CustomLoginView(LoginView):
#     @ratelimit()
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         return response


# # Create your views here.


# @ratelimit(key="user_or_ip", rate="10/m", block=True)
# def my_view_authenticated(request):
#     if request.user.is_authenticated:
#         return HttpResponse("Authenticated user view. Rate limited to 10 per minute.")
#     else:
#         return HttpResponse(
#             "Not authenticated. Please log in to access this view.", status=403
#         )


# @ratelimit(key="ip", rate="5/m", block=True)
# def my_view_anonymous(request):
#     if not request.user.is_authenticated:
#         return HttpResponse("Anonymous user view. Rate limited to 5 per minute.")
#     else:
#         return HttpResponse(
#             "Authenticated user. Please use the authenticated view.", status=403
#         )
