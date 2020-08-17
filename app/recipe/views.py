from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe.serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Create a new user in the system"""
    serializer_class = TagSerializer
    authentication_classes = (
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
    )
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Limit qs to user's own tags"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Override to make sure a new tag belongs to its user"""
        serializer.save(user=self.request.user)
