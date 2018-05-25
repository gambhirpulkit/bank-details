from django.http import HttpResponse
from fetch.models import Banks, Branches
import json
import redis


def branch_details(request):
    rc = redis.StrictRedis(host='localhost', port=6379, db=0)

    if request.GET:
        ifsc = request.GET.get('ifsc')
        bank_name = request.GET.get('name')
        bank_city = request.GET.get('city')
        no_cache = request.GET.get('no-cache')

        if ifsc:
            key = "%s" % (ifsc.lower().strip())
            branch_detail = Branches.objects.filter(ifsc__iexact=ifsc)
            if branch_detail.exists():
                if not rc.hget("hash", key) or no_cache == '1':
                    context = {}
                    context["branch_name"] = branch_detail.first().branch
                    context["city"] = branch_detail.first().city
                    context["bank_id"] = branch_detail.first().bank_id
                    context["ifsc"] = branch_detail.first().ifsc
                    context["address"] = branch_detail.first().address
                    context["district"] = branch_detail.first().district
                    context["state"] = branch_detail.first().state
                    context["bank_name"] = branch_detail.first().bank.name

                    rc.hset("hash", key, json.dumps(context))
                    rc.expire("hash", 1000)

                    return HttpResponse(json.dumps(context), status=200)
                else:
                    cached_data = rc.hget("hash", key).decode('utf8')
                    return HttpResponse(cached_data, status=200)
            else:
                return HttpResponse('Not found', status=404)
        elif bank_name and bank_city:
            branch_detail = Branches.objects.filter(bank__name__iexact=bank_name, city__iexact=bank_city)
            key = "%s:%s" % (bank_name.lower().strip(), bank_city.lower().strip())

            if branch_detail.exists:
                if not rc.hget("hash", key) or no_cache == '1':
                    details = []
                    for i, branch in enumerate(branch_detail):
                        context = {}
                        context["branch_name"] = branch.branch
                        context["city"] = branch.city
                        context["bank_id"] = branch.bank_id
                        context["ifsc"] = branch.ifsc
                        context["address"] = branch.address
                        context["district"] = branch.district
                        context["state"] = branch.state
                        context["bank_name"] = branch.bank.name
                        details.append(context)

                    rc.hset("hash", key, json.dumps(details))
                    rc.expire("hash", 1000)

                    return HttpResponse(json.dumps(details), status=200)
                else:
                    cached_data = rc.hget("hash", key).decode('utf8')
                    return HttpResponse(cached_data, status=200)
            else:
                return HttpResponse('Not found', status=404)
        else:
            return HttpResponse('Validation error. Incorrect or missing parameters',status=400)

    else:
        return HttpResponse('Validation error. Incorrect or missing parameters', status=400)
