import pickle
with open("db backup.ass", "br") as f :
    u=pickle.load(f)
print(str(u))