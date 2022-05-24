# ** ATTENTION **
Please do not publicly fork this repository.

# Task

- Parse `request-data.json` into the query similar to `result.sql`. 

Inside `request-data.json` you have two properties `nodes` and `edges`, `nodes` contains all the required information to apply the transformation into Table/Query and `edges` represents how they are linked together. In each node there is a property `transformObject` which is different for each `type`
There are 5 different types of nodes used in this request

	- INPUT		-> it contains information about table and which fields to select from original table. 
	- FILTER	-> contains SQL "where" settings 
	- SORT		-> contains SQL "order by" settings 
	- TEXT_TRANSFORMATION	    -> contains information about applying some text SQL function on any column. For example UPPER, LOWER (see the digram for actual use case)
	- OUTPUT	-> contains SQL "limit" settings

Graphical representation of actual use-case:
![graphical representation](https://github.com/goes-funky/modeling-test/blob/master/graphical-representation.png?raw=true)

Use your imagination to fill in the missing information however you like to achieve the result.

# Bonus Points
 - Optimize `request-data.json` json structure/schema: a sample request-data-v1.json is added and the json is optimized.
 - Extendable structure which allows to add more types easily in the future. Factory design pattern is used to support the extendable sturucture. 
 - Suggestion on how to validate the columns used inside the nodes.We can validate the current node columns with the first node columns in input parameter by including _validate_column methods in every Node class. 


## RUN
`pip install -r requirements.txt`

`cd parse`

`python main.py`

## Explaination

The query generated in file `result_withclause.sql`
Pypika query builder is used to generate the query dynamically.
The with clause with comman seperated is supported using pypika but not with the alias name,
Result will consist of the complete query instead of Alias names. 

Example:
`WITH A AS (SELECT "id","name","age" FROM "users") ,
B AS (SELECT "A"."id","A"."name","A"."age" FROM (SELECT "id","name","age" FROM "users") "A" WHERE "A"."age">'18') ,
C AS (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "A"."id","A"."name","A"."age" FROM (SELECT "id","name","age" FROM "users") "A" WHERE "A"."age">'18') "sq0" ORDER BY "sq0"."age",'ASC',"sq0"."name",'ASC') ,
D AS (SELECT "sq1"."id",UPPER("sq1"."name") "name","sq1"."age" FROM (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "A"."id","A"."name","A"."age" FROM (SELECT "id","name","age" FROM "users") "A" WHERE "A"."age">'18') "sq0" ORDER BY "sq0"."age",'ASC',"sq0"."name",'ASC') "sq1") ,
E AS (SELECT * FROM (SELECT "sq1"."id",UPPER("sq1"."name") "name","sq1"."age" FROM (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "A"."id","A"."name","A"."age" FROM (SELECT "id","name","age" FROM "users") "A" WHERE "A"."age">'18') "sq0" ORDER BY "sq0"."age",'ASC',"sq0"."name",'ASC') "sq1") "sq2" LIMIT 100)
SELECT * FROM E`

## Note
Where clause in the filter type can take multiple conditions.
Sorting can be made on multiple columns

