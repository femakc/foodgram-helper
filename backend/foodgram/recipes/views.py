from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from .models import Tag, Recipe
from .serializers import TagSerializer, RecipeSerialzer
from api.permissions import IsAuthorOrReadOnly


class TagsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeVievSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerialzer
    permission_classes = [IsAuthorOrReadOnly,]

    def retrieve(self, request, pk=None):
        queryset = Recipe.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = RecipeSerialzer(user)
        return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    