from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_framework.renderers import JSONRenderer
from .models import Asset
from .serializers import AssetSerializer

# Create your tests here.


class BaseTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_asset(name="", type="", aclass=""):
        if name != "" and type != "" and aclass != "":
            Asset.objects.create(asset_name=name, asset_type=type, asset_class=aclass)

    def setUp(self):
        # add the test data
        self.create_asset("Dove1", "satellite", "dove")
        self.create_asset("SkySat1", "satellite", "skysat")
        self.create_asset("RapidEye1", "satellite", "rapideye")
        self.create_asset("Dish1", "antenna", "dish")
        self.create_asset("Yagi1", "antenna", "yagi")


class GetAllAssetsTest(BaseTest):

    def test_get_all_assets(self):
        """
        This test makes sure all Assets from database are returned in
        the GET ALL API response
        """
        # hit the API endpoint
        response = self.client.get(reverse("assets"))

        # fetch the data from db
        expected = Asset.objects.all()
        serialized = AssetSerializer(expected, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["assets"], serialized.data)


class GetAnAssetTest(BaseTest):

    def verify_get_an_asset(self, name):
        """
        This method makes sure a single asset referenced in the path of the GET
        request is returned correctly, when it exists in the database
        """
        response = self.client.get(reverse("asset", args=[name]))
        expected = Asset.objects.get(asset_name=name)
        serialized = AssetSerializer(expected)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.data['asset_name'], serialized.data['asset_name'])

    def test_get_an_asset_all(self):
        self.verify_get_an_asset("Dove1")
        self.verify_get_an_asset("SkySat1")
        self.verify_get_an_asset("RapidEye1")
        self.verify_get_an_asset("Dish1")
        self.verify_get_an_asset("Yagi1")

    def test_get_an_asset_negative_cases(self):
        negative_cases = ["Sky130", "()123abc", "(^abc123)", "Do", "Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove"]

        for asset in negative_cases:
            response = self.client.get("/api/v1/assets/"+asset)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateAssetsTest(BaseTest):

    def test_post_an_asset(self):
        single_asset = {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "skysat"}
        payload = {"assets": [single_asset]}

        response = self.client.post(reverse("assets"), JSONRenderer().render(payload) , format=None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = Asset.objects.get(asset_name=single_asset['asset_name'])
        serialized = AssetSerializer(expected)

        self.assertEqual(single_asset['asset_name'], serialized.data['asset_name'])
        self.assertEqual(single_asset['asset_type'], serialized.data['asset_type'])
        self.assertEqual(single_asset['asset_class'], serialized.data['asset_class'])

    def verify_post_an_asset_with_errors(self, payload, name, messages):
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload) , format=None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_message = response.data['assets'][0]
        self.assertEqual(name, error_message['asset_name'])
        self.assertEqual(messages, error_message['errors'])

    def test_post_an_asset_negative_cases(self):
        assets = {"name_error": {"asset_name": "(^abc123)", "asset_type": "satellite", "asset_class": "skysat"},
                  "type_error": {"asset_name": "SkySat123", "asset_type": "abcd1234", "asset_class": "skysat"},
                  "class_error": {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "dish"},
                  "exists_error": {"asset_name": "SkySat1", "asset_type": "satellite", "asset_class": "skysat"}}
        error_messages = {"name_error": ["asset_name is not formatted correctly"],
                          "type_error": ['"abcd1234" is not a valid choice. for asset_type'],
                          "class_error": ["asset_class is not valid"],
                          "exists_error": ["Asset already exists in the asset store, it cannot be updated using a POST request"]}
        for key, value in assets.items():
            payload = {"assets": [value]}
            self.verify_post_an_asset_with_errors(payload, value['asset_name'], error_messages[key])
            
    def test_post_multiple_assets(self):
        assets = []
        assets.append({"asset_name": "SkySat678", "asset_type": "satellite", "asset_class": "skysat"})
        assets.append({"asset_name": "Dove678", "asset_type": "satellite", "asset_class": "dove"})
        assets.append({"asset_name": "RapidEye678", "asset_type": "satellite", "asset_class": "rapideye"})
        assets.append({"asset_name": "Dish678", "asset_type": "antenna", "asset_class": "dish"})
        assets.append({"asset_name": "Yagi678", "asset_type": "antenna", "asset_class": "yagi"})

        payload = {"assets": assets}
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload) , format=None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate that the assets exist in the database
        for asset in assets:
            try:
                Asset.objects.get(asset_name=asset['asset_name'])
            except Asset.DoesNotExist:
                self.assertFalse(True, asset['asset_name'] + " is not stored in asset store")

    def test_post_multiple_assets_errors(self):
        assets = [{"asset_name": "(^abc123)", "asset_type": "satellite", "asset_class": "skysat"},
                  {"asset_name": "SkySat123", "asset_type": "abcd1234", "asset_class": "skysat"},
                  {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "dish"},
                  {"asset_name": "SkySat1", "asset_type": "satellite", "asset_class": "skysat"},
                  {"asset_name": "SkySat1765", "asset_type": "satellite", "asset_class": "skysat"}]
        error_messages = [["asset_name is not formatted correctly"],
                          ['"abcd1234" is not a valid choice. for asset_type'],
                          ["asset_class is not valid"],
                          ["Asset already exists in the asset store, it cannot be updated using a POST request"],
                          ["Asset is valid and does not yet exist in the asset store"]]
        payload = {"assets": assets}
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload) , format=None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['assets']
        index = 0
        for asset in assets:
            self.assertEqual(asset['asset_name'], errors[index]['asset_name'])
            self.assertEqual(error_messages[index], errors[index]['errors'])
            index = index + 1
