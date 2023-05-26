from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

class CreateDeleteMixin:
    def create_delete(self, serializer, model, field):
        object = get_object_or_404(self.queryset, id=self.kwargs['pk'])
        context = {
            'request': self.request,
            'action': self.action,
        }
        data = {
            'user': self.request.user,
            field: object
        }

        if self.request.method == 'POST':
            serializer = serializer(object, data=self.request.data, context=context)
            serializer.is_valid(raise_exception=True)
            model.objects.create(**data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        model.objects.filter(**data).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
