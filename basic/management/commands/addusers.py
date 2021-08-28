from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
import json
import codecs

from basic.models import User, Role, BimeShavanadeGharardad, Gharardad


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        data1 = json.load(codecs.open(BASE_DIR/'media/data.json', 'r', 'utf-8-sig'))
        data2 = json.dumps(data1)
        print(data1["NewDataSet"][0])
        for json_user in data1["NewDataSet"]:
            user = User.objects.create_user(json_user["melli_code"], '', json_user["melli_code"][-6:])
            user.melli_code = json_user["melli_code"]
            user.first_name = json_user["fisrt_name"]
            user.last_name = json_user["last_name"]
            user.age = int(json_user["age"])
            user.roles.add(Role.objects.get(pk=1))
            user.save()
            BimeShavanadeGharardad.objects.create(bimeshavande=user, gharardad=Gharardad.objects.last())
        self.stdout.write(self.style.SUCCESS('Successfully closed poll'))
