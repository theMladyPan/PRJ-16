aggregation = [
    {
        "$sort": {
            "_id": -1
        }
    },
    {
        "$match": {
            "S12": {
                "$exists": true
            }
        },
        "$match": {
            "S12.s": {
                "$gte": 6e5,
                "$lte": 7e5
            },
            "T1.t": {
                "$lte": 60
            }
        }
    },
    {
        "$project": {
            "S12": 1,
            "T1": 1,
            "time": 1
        }
    },
    {
        "$addFields": {
            "hour": {
                "$hour": "$_id"
            },
            "temp": {
                "$round": ["$T1.t", 3]
            },
            "S": {
                "$multiply": ["$S14.s", 3.11e-9, 210e3]
            }
        }
        
    },
    {
        "$match": {
            "temp": {
                "$gte": 25,
                "$lte": 30
            }
        }
    },
    {
        "$limit": 10000
    }
]
;

use('prod');
// Search for documents in the current collection.
db.getCollection('PRJ-16').aggregate(aggregation);
