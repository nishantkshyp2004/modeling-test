if __name__=='__main__':

    from pypika import Table, Query, Order, AliasedQuery
    from pypika.functions import Upper

    users_table = Table('users')

    query_a = Query.from_(users_table).select(users_table.id, users_table.name, users_table.age)
    query_b = Query.from_(query_a).select(query_a.id, query_a.name, query_a.age).where(query_a.age > 18)
    query_c = Query.from_(query_b).select(query_b.id, query_b.name, query_b.age).orderby(query_b.age, query_b.name,
                                                                                         order=Order.desc)
    query_d = Query.from_(query_c).select(query_c.id, Upper(query_c.name), query_c.age)
    query_e = Query.from_(query_d).select("*").limit(100).offset(0)

    query = Query \
        .with_(query_a, "A") \
        .with_(query_b, "B") \
        .with_(query_c, "C") \
        .with_(query_d, "D") \
        .with_(query_e, "E") \
        .from_(AliasedQuery("E")) \
        .select(query_e.star)

    print(query)

    """WITH A AS 
    (SELECT "id","name","age" FROM "users") ,
    B AS (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "id","name","age" FROM "users") "sq0" WHERE "sq0"."age">18) ,
    C AS (SELECT "sq1"."id","sq1"."name","sq1"."age" FROM (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "id","name","age" FROM "users") "sq0" WHERE "sq0"."age">18) "sq1" ORDER BY "sq1"."age" DESC,"sq1"."name" DESC) ,
    D AS (SELECT "sq2"."id",UPPER("sq2"."name") FROM (SELECT "sq1"."id","sq1"."name","sq1"."age" FROM (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "id","name","age" FROM "users") "sq0" WHERE "sq0"."age">18) "sq1" ORDER BY "sq1"."age" DESC,"sq1"."name" DESC) "sq2") ,E AS (SELECT * FROM (SELECT "sq2"."id",UPPER("sq2"."name") FROM (SELECT "sq1"."id","sq1"."name","sq1"."age" FROM (SELECT "sq0"."id","sq0"."name","sq0"."age" FROM (SELECT "id","name","age" FROM "users") "sq0" WHERE "sq0"."age">18) "sq1" ORDER BY "sq1"."age" DESC,"sq1"."name" DESC) "sq2") "sq3" LIMIT 100) SELECT *"""