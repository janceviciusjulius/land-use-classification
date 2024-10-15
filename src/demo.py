# DB ROW
country = "lithuania"
request = "32kddsa-213"


pattern = "https://prophet-databricks-bronze.s3.amazonaws.com/anewstip/countries/{country}/{request}/outlet-{request}.json"

x = pattern.format(country=country, request=request)
print(x)