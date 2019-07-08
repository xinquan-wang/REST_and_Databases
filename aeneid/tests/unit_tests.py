#Xinquan Wang -- xw2566


from aeneid.dbservices.RDBDataTable import RDBDataTable
import logging
logging.basicConfig(level=logging.DEBUG)
from aeneid.dbservices import dataservice as ds
import pymysql
import json


cnx = pymysql.connect(
    host="localhost",
    database="HW1",
    user="dbuser",
    password="dbuser",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)


def create_rdb_test():

    tbl = RDBDataTable("people")
    print("create_rdb_test:", tbl)


def create_fantasy_manager():
    result = ds.create("HW1.fantasy_manager",
                       {"id": "9", "last_name": "Ferguson", "first_name": "Douglas", "email": "dff9@columbia.edu"}
                       )

    print("create_fantasy_manager: ", result)


def get_join_column_mapping(schema1, table1, schema2, table2):
    q = """
        SELECT
          TABLE_NAME,
          COLUMN_NAME,
          CONSTRAINT_NAME,
          REFERENCED_TABLE_NAME,
          REFERENCED_COLUMN_NAME
        FROM
          INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE
         (REFERENCED_TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME = %s
           AND TABLE_SCHEMA = %s AND TABLE_NAME = %s)
         OR
         (REFERENCED_TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME = %s
           AND TABLE_SCHEMA = %s AND TABLE_NAME = %s)

    """

    params = (schema1, table1, schema2, table2, schema2, table2, schema1, table1)

    cursor = cnx.cursor()
    final_q = cursor.mogrify(q, params)
    # print(final_q)
    r = cursor.execute(q, params)
    constraints = cursor.fetchall()

    result = {}

    for c in constraints:

        n = c['CONSTRAINT_NAME']
        e = result.get(n, None)

        if e is None:
            e = {}
            e['CONSTRAINT_NAME'] = n
            e['MAP'] = []
            result[n] = e

        this_m = {k: c[k] for k in ['TABLE_NAME', 'COLUMN_NAME',
                                    'REFERENCED_TABLE_NAME', 'REFERENCED_COLUMN_NAME']}
        e['MAP'].append(this_m)

    return result


# join_paths = get_join_column_mapping("HW1", "people", "HW1", "batting")
# print("JOIN paths = \n", json.dumps(join_paths, indent=2, default=str))

print("create_rdb_test()")
create_rdb_test()

print("create_fantasy_manager()")
create_fantasy_manager()


