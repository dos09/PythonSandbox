import pymongo

def run():
    client = pymongo.MongoClient()
    db = client['mytest']
    for doc in db.orcs.find():
        print(doc)
    
    input('press enter')
    client.close()

if __name__ == '__main__':
    run()