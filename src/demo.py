import requests


try:
    response = requests.head("https://www.tickerreport.com/banking-finance/12581930/mdex-achieves-market-cap-of-14-25-million-mdx.html", timeout=10, allow_redirects=True)
    print(response.headers)
    print(response.status_code)
except Exception as error:
    print(error)
