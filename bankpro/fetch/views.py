from django.http import HttpResponse
from fetch.models import Banks, Branches
import json
from elasticsearch import Elasticsearch


def branch_details(request):

    if request.GET:
        ifsc = request.GET.get('ifsc')
        bank_name = request.GET.get('name')
        bank_city = request.GET.get('city')
        es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'size': 1000}])
        if ifsc:
            # branch_detail = es.search(index="branch", body={"query": {"match": {'ifsc': ifsc}}})
            branch_detail = es.search(index="branch", body={
                "query": {"bool": {"must": [{"term": {"ifsc": ifsc.lower()}}]}}
            })

            branch_detail = branch_detail['hits']['hits']
            # branch_detail = Branches.objects.filter(ifsc__iexact=ifsc)
            if branch_detail:
                branch_detail = branch_detail[0]['_source']
                context = {}
                context["branch_name"] = branch_detail['branch_name']
                context["city"] = branch_detail['city']
                context["bank_id"] = branch_detail['bank_id']
                context["ifsc"] = branch_detail['ifsc']
                context["address"] = branch_detail['address']
                context["district"] = branch_detail['district']
                context["state"] = branch_detail['state']
                context["bank_name"] = branch_detail['bank_name']
                return HttpResponse(json.dumps(context), status=200)
            else:
                return HttpResponse('Not found', status=404)
        elif bank_name and bank_city:
            # branch_detail = Branches.objects.filter(bank__name__iexact=bank_name, city__iexact=bank_city)

            branch_detail = es.search(index="branch", doc_type='bank',  body={
                "size" : 10000, "query": {"bool": {"must": [{"match_phrase": {"bank_name": bank_name}},{"match_phrase": {"city": bank_city}}]}}
            })
            branch_detail = branch_detail['hits']['hits']
            if branch_detail:
                details = []
                for i, branch in enumerate(branch_detail):
                    branch = branch_detail[i]['_source']
                    context = {}
                    context["branch_name"] = branch['branch_name']
                    context["city"] = branch['city']
                    context["bank_id"] = branch['bank_id']
                    context["ifsc"] = branch['ifsc']
                    context["address"] = branch['address']
                    context["district"] = branch['district']
                    context["state"] = branch['state']
                    context["bank_name"] = branch['bank_name']
                    details.append(context)
                return HttpResponse(json.dumps(details), status=200)
            else:
                return HttpResponse('Not found', status=404)
        else:
            return HttpResponse('Validation error. Incorrect or missing parameters',status=400)

    else:
        return HttpResponse('Validation error. Incorrect or missing parameters', status=400)