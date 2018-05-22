from django.core.management.base import BaseCommand
from fetch.models import Banks, Branches
from elasticsearch import Elasticsearch
import json
import requests

class Command(BaseCommand):
    help = 'ES indexes'

    def handle(self, *args, **options):
        print("start")
        self.wakeup()


    def wakeup(self):
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        branches = Branches.objects.filter()
        if branches.exists():
            for branch in branches:
                context = {}
                context["branch_name"] = branch.branch
                context["city"] = branch.city
                context["bank_id"] = branch.bank.id
                context["ifsc"] = branch.ifsc
                context["address"] = branch.address
                context["district"] = branch.district
                context["state"] = branch.state
                context["bank_name"] = branch.bank.name
                es.index(index='branch', doc_type='bank', id=branch.ifsc, body=json.dumps(context))
                print(es.get(index='branch', doc_type='bank', id=branch.ifsc))
        print("end")