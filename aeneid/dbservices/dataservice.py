#Xinquan Wang -- xw2566


import pymysql.cursors
import json
import aeneid.utils.utils as ut
import aeneid.utils.dffutils as db
import aeneid.dbservices.DataExceptions
from aeneid.dbservices.RDBDataTable import RDBDataTable

db_schema = None                                # Schema containing accessed data
cnx = None                                      # DB connection to use for accessing the data.
key_delimiter = '_'                             # This should probably be a config option.

# Is a dictionary of {table_name : [primary_key_field_1, primary_key_field_2, ...]
# Used to convert a list of column values into a template of the form { col: value }
primary_keys = {}

# This dictionary contains columns mappings for nevigating from a source table to a destination table.
# The keys is of the form sourcename_destinationname. The entry is a list of the form
# [[sourcecolumn1, destinationcolumn1], ...
join_columns = {}

# Data structure contains RI constraints. The format is a dictionary with an entry for each schema.
# Within the schema entry, there is a dictionary containing the constraint name, source and target tables
# and key mappings.
ri_constraints = None

data_tables = {}


# TODO This is a bit of a hack and we should clean up.
# We should load information from database or configuration file.
people = RDBDataTable("HW1.people", key_columns=['playerID'])
data_tables["HW1.people"] = people
batting = RDBDataTable("HW1.batting", key_columns=['playerID', 'yearID', 'teamID', 'stint'])
data_tables["HW1.batting"] = batting
appearances = RDBDataTable("HW1.appearances", key_columns=['playerID', 'yearID', 'teamID'])
data_tables["HW1.appearances"] = appearances
offices = RDBDataTable("HW1.offices", key_columns=['officeCode'])
data_tables["Hw1.offices"] = offices
fantasy_manager = RDBDataTable("HW1.fantasy_manager", key_columns=['id'])
data_tables["Hw1.fantasy_manager"] = fantasy_manager


def get_data_table(table_name):

    result = data_tables.get(table_name, None)
    if result is None:
        result = RDBDataTable(table_name)
        data_tables[table_name] = result

    return result


def get_by_template(table_name, template, field_list=None, limit=None, offset=None, order_by=None, commit=True):

    dt = get_data_table(table_name)
    result = dt.find_by_template(template, field_list, limit, offset, order_by, commit)
    return result.get_rows()


def get_by_primary_key(table_name, key_fields, field_list=None, commit=True):

    dt = get_data_table(table_name)
    result = dt.find_by_primary_key(key_fields, field_list)
    return result


def create(table_name, new_value):
    dt = get_data_table(table_name)
    result = dt.insert(new_value)
    return result


def delete(table_name, key_cols):
    dt = get_data_table(table_name)
    result = dt.delete_by_key(key_cols)
    return result

















