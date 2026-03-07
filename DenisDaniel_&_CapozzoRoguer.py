import requests 

r = requests.get("https://github.com/FernandoSapient/BPTSP05_2526-2.git", 
                auth =("user", "pass"))

print(r.status_code)