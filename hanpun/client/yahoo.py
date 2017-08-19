import requests

from hanpun.common.memorycache import MWT


class YahooClient:
    @classmethod
    @MWT(timeout=3600)
    def usd_krw_exchange_rate(cls):
        url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchang" \
              "e%20where%20pair%20in%20(%22USDKRW%22)&format=json&env=store://datatables.org/alltabl" \
              "eswithkeys&callback="
        r = requests.get(url)
        res_json = r.json()
        return float(res_json['query']['results']['rate']['Rate'])
