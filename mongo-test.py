from pymongo import MongoClient
import pymongo

print "\n## Establish the connection and aim at a specific database"
client = MongoClient('127.0.0.1:27017')
db = client.myDB
print db

#####################################
#### INSERTING DOCUMENTS
#### Insert a single document
db.countries.insert_one({"name" : "Australia", "capital" : "Canberra", "population" : 30000})

print "\n## This tells you the uid of the inserted document"
res = db.countries.insert_one({"name" : "New Zealand", "capital" : "Auckland", "population" : 50000})
print (res.inserted_id)

print "\n## Insert many at once. Using a list of documents"
db.countries.insert_many([
    {"name" : "Italy", "capital" : "Rome" , "population" : 100000 },
    {"name" : "France", "capital" : "Paris" , "population" : 100000 }
    ])

print "\n## Schema is not rigid. I can introduce new fields or not populate existing ones"
db.countries.insert_one({"name" : "Spain", "capital" : "Madrid", "cities" : ["Madrid", "Bilbao"]})

print "\n## Amount of records in the database"
print db.countries.count()

print "\n## You could also import a JSON file like this"
print "## wget https://raw.githubusercontent.com/mongodb/docs-assets/primer-dataset/primer-dataset.json"
print "## mongoimport --db test --collection restaurants --drop --file primer-dataset.json"

#####################################
#### RETRIEVING DOCUMENTS
print "\n## This will return a single document"
print db.countries.find_one()

print "\n## Show all documents"
cursor = db.countries.find()
for each_country in cursor:
    print each_country

print "\n## Find all entries matching a criteria"
cursor = db.countries.find({"capital": "Rome", "population" : 100000})
#print "The amount of records manthcin " + str(db.countries.find({"population" : {"$gt" : 35000}}).count())
for each_country in cursor:
    print each_country['name']

print "\n## Let's sort them by a specific field, display only some fields"
cursor = db.countries.find().sort("name", pymongo.ASCENDING)
for each_country in cursor:
    print each_country['name'] + " , " + each_country['capital']
print " - Population field doesn't exist in one document"
print " - so I can't use ['population'] without checking whether it exists"

raw_input("\n -- Press ENTER to continue --")

print "\n## We can match numeric criteria too, ex: population $gt 35000"
cursor = db.countries.find({"population" : {"$gt" : 35000}})
for each_country in cursor:
    print each_country['name'] + " has " + str(each_country['population']) + " people"
print " - Population field exists in all selected documents so we can use it without error"

print "\n## We can make searches like that more efficient by using an index"
print "## By default Mongo creates only the _id index to ensure no record is duplicated"
print "## But it does support many other index types, ex: compound, multi-key, geospatial ..."
print "## 1 = ascending, -1 = descending order. You can also use pymongo.ASCENDING / DESCENDING"
res = db.countries.create_index([("population", 1)])
print"This is the new index we created : " + res
cursor = db.countries.find({"population" : {"$gt" : 35000}}).sort("population" , 1)
for each_country in cursor:
    print each_country['name'] + " has " + str(each_country['population']) + " people"

#####################################
#### UPDATING DOCUMENTS
print "\n## Let's update a record and see the result"
db.countries.update_one({"name" : "Spain"} ,
                        {"$set" : {"population" : 80000, "capital" : "Toledo"}}
                        )
cursor = db.countries.find()
for each_country in cursor:
    print each_country['name'] + " , " + each_country['capital'] + " , " + str(each_country['population'])

print "\n## Let's update multiple records"
res = db.countries.update_many({"population" : 100000} ,
                        {"$set" : {"population" : 110000, "capital" : "Monaco"}}
                        )
print "The amount of records changed : " + str(res.modified_count)
cursor = db.countries.find()
for each_country in cursor:
    print each_country['name'] + " , " + each_country['capital'] + " , " + str(each_country['population'])

raw_input("\n -- Press ENTER to continue --")

print "\n## Let's count the amount of countries with the same capital"
cursor = db.countries.aggregate([{"$group":
                                  {"_id": "$capital", "count": {"$sum": 1}}
                                  }])
for item in cursor:
    print item["_id"] + " = " + str(item["count"])

print "\n## Or even their aggregated populations"
cursor = db.countries.aggregate([{"$group":
                                  {"_id": "$capital", "count": {"$sum": "$population"}}
                                  }])
for item in cursor:
    print item["_id"] + " = " + str(item["count"])
    
#####################################
#### DELETING DOCUMENTS
print "\n## Let's drop records whose population is 100000"
res = db.countries.delete_many({"capital" : "Monaco"})
print str(res.deleted_count) + " countries deleted"

print "\n## Capitals of all countries"
cursor = db.countries.find().sort("name", pymongo.ASCENDING)
for each_country in cursor:
    print each_country['name'] + " , " + each_country['capital']

#####################################
#### DELETING THE WHOLE LOT
print "\n## Let's drop a collection" 
db.countries.drop()
print "\n## Let's drop the database. Bye for now"
client.drop_database('myDB')
