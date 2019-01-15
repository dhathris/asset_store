from django.http import Http404
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework.views import APIView, status
from rest_framework.response import Response
import re
from .models import Asset, TYPES, SAT_CLASSES, ANT_CLASSES
from .serializers import AssetSerializer

# Create your views here.


class ListAssetsView(generics.ListAPIView):
    """
    Provides GET method handler
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def get(self, request, *args, **kwargs):
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        response = {"assets": serializer.data}
        return Response(response, status=200)


class ListAssetView(generics.ListAPIView):
    """
    Provides GET method handler
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def get_object(self, pk):
        try:
            return Asset.objects.get(asset_name=pk)
        except Asset.DoesNotExist:
            raise Http404

    def get(self, request, name, format=None):
        asset = self.get_object(name)
        serializer = AssetSerializer(asset)
        return Response(serializer.data, status=200)


class CreateAssetsView(generics.CreateAPIView):
    """
    Provides POST method handler
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    @staticmethod
    def validate_asset(asset):
        match = re.search(r'^([\w\-]{4,64})$', asset['asset_name'])

        errors = []
        if match is None:
            errors.append("asset_name is not formatted correctly")
        if asset['asset_type'] == TYPES[0]:
            if asset['asset_class'] not in SAT_CLASSES:
                errors.append("asset_class is not valid")
        elif asset['asset_class'] not in ANT_CLASSES:
            return errors.append("asset_class is not valid")
        try:
            asset = Asset.objects.get(asset_name=asset['asset_name'])
            if asset is not None:
                errors.append("Asset already exists in the asset store, it cannot be updated using a POST request")
        except Asset.DoesNotExist:
            # Ignore the exception
            print("")
        return errors

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)

        assets = data['assets']
        messages = []
        error_flag = False
        for asset in assets:
            message = {}
            message['asset_name'] = asset['asset_name']
            message['errors'] = []
            serializer = AssetSerializer(data=asset)
            if not serializer.is_valid():
                for key, value in serializer.errors.items():
                    message['errors'].append(value[0]+" for "+key)
                error_flag = True
            result = self.validate_asset(asset)
            if result is not None and len(result) != 0:
                [message['errors'].append(x) for x in result]
                error_flag = True
            elif len(message['errors']) == 0:
                message['errors'].append("Asset is valid and does not yet exist in the asset store")
            messages.append(message)
        if error_flag:
            return Response(data={"assets": messages}, status=status.HTTP_400_BAD_REQUEST)
        """
        Perform a bulk update here
        """
        Asset.objects.bulk_create([Asset.convert_dict_to_asset(x) for x in assets])
        return Response(status=201)


class CreateAssetView(generics.CreateAPIView):
    """
    Provides a handler for single asset creation using POST
    """
    def post(self, request, *args, **kwargs):
        return Response(status=405)


class UpdateAssetsView(generics.UpdateAPIView):
    """
    Provides PUT method handler
    """
    def put(self, request, *args, **kwargs):
        return Response(status=405)


class DeleteAssetsView(generics.DestroyAPIView):
    """
    This is a DELETE method handler for bulk asset delete
    """
    def delete(self, request, *args, **kwargs):
        return Response(status=405)


class DeleteAssetView(generics.DestroyAPIView):
    """
    This is a DELETE method handler for a single asset delete
    """
    def delete(self, request, *args, **kwargs):
        return Response(status=405)


class BaseView(APIView):
    """
    Base view class for routing requests to different view classes based on HTTP Methods for the same url
    """
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'VIEWS_BY_METHOD'):
            raise Exception('VIEWS_BY_METHOD static dictionary variable must be defined on a BaseView class!')
        if request.method in self.VIEWS_BY_METHOD:
            return self.VIEWS_BY_METHOD[request.method]()(request, *args, **kwargs)

        return Response(status=405)


class AssetsViewRouter(BaseView):
    VIEWS_BY_METHOD = {
        'GET': ListAssetsView.as_view,
        'POST': CreateAssetsView.as_view,
        'PUT': UpdateAssetsView.as_view,
        'DELETE': DeleteAssetsView.as_view
    }


class AssetViewRouter(BaseView):
    VIEWS_BY_METHOD = {
        'GET': ListAssetView.as_view,
        'POST': CreateAssetView.as_view,
        'PUT': UpdateAssetsView.as_view,
        'DELETE': DeleteAssetView.as_view
    }
