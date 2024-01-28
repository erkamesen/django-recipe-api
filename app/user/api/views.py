"""
Views for the User API
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.api.serializers import (
    UserSerializer,
    AuthTokenSerializer
)

# Use for Create not Read - Update or Delete


class CreateUserView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new Auth Token for User"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  #  For browsable API


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
