import urllib.request, json
url = "http://localhost:8069/report/download"
data = json.dumps({"data": "[\"/report/pdf/sadaya_rutin.report_ba_negotiation_template/1\", \"qweb-pdf\"]"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    res = urllib.request.urlopen(req)
    content = res.read()
    print("CODE:", res.getcode())
    print("LENGTH:", len(content))
    if len(content) < 100:
        print("CONTENT:", content)
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read())
