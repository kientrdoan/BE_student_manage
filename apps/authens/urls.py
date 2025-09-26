from django.urls import path


from .views.token import MyTokenObtainPairView, MyTokenRefreshView
from .views.user import UserView, UserProfile

urlpatterns = [
    path('login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path('signup', UserView.as_view(), name='signup'),
]

urlpatterns += [
    path('users', UserProfile.as_view(), name='profile'),
]
