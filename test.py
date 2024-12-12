import requests


headers = {
    "content-type": "application/json",
    "origin": "https://mevx.io",
    "referer": "https://mevx.io/",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
url = "https://api-fe.mevx.io/api/token/hot-pairs"
params = {
    "chain": "sol",
    "liquidFrom": "10000",
    "liquidTo": "2000000000",
    "volumeFrom": "50000",
    "volumeTo": "2000000000",
    "mktCapFrom": "20000",
    "mktCapTo": "2000000000",
    "txnFrom": "50",
    "txnTo": "2000000000",
    "offset": "0",
    "limit": "50",
    "maker": "50",
    "mintAuth": "true",
    "freezeAble": "true",
    "lpBurnded": "true",
    "topHolder": "true",
    "interval": "1440",
    "price": "inc",
    "orderBy": "price"
}
response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response)
