aggregation = [
    {
        "$sort": {
            "_id": -1
        }
    },
    {
        "$match": {
            "S14": {
                "$exists": true
            }
        },
        "$match": {
            "S14.s": {
                "$gte": 2e5,
                "$lte": 5e5
            },
            "T1.t": {
                "$lte": 60
            }
        }
    },
    {
        "$project": {
            "S14": 1,
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
        "$limit": 20000
    }
]
;

use('prod');
// Search for documents in the current collection.
db.getCollection('PRJ-16').aggregate(aggregation);
