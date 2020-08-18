from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers \
    import \
    TagSerializer, IngredientSerializer, RecipeSerializer, \
    RecipeDetailSerializer, RecipeImageSerializer


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    authentication_classes = (
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        """Limit qs to user's own attribute"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Override to make sure a new attribute belongs to its user"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Create a new tag in the system"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Create a new ingredient in the system"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the DB"""
    authentication_classes = (
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
    )
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def _params_to_ints(self, qs):
        """Turn a comma delimited list of ints into a list of int"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Get the authenticated user's recipes"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            # Magic string indicates a filter on a foreign id link:
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingred_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingred_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return different serializer for our detail view"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Override to make sure a new attribute belongs to its user"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # And if not...
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
