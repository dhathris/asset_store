from django.db import models

# Create your models here.

class Asset(models.Model):
    # asset name
    asset_name = models.CharField(max_length=64, null=False)
    # asset type
    asset_type = models.CharField(max_length=64, null=False)
    # asset class
    asset_class = models.CharField(max_length=64, null=False)

    def __str__(self):
        return "Asset(asset_name={}, asset_type={}, asset_class={})".format(self.name, self.type, self.asset_class)

    @staticmethod
    def convert_dict_to_asset(indict):
        return Asset(asset_name=indict['asset_name'], asset_type=indict['asset_type'], asset_class=indict['asset_class'])


TYPES = ["satellite", "antenna"]
CLASSES = ["dove", "skysat", "rapideye", "dish", "yagi"]
SAT_CLASSES = CLASSES[0:3]
ANT_CLASSES = CLASSES[3:5]
