#Xinquan Wang -- xw2566


from aeneid.dbservices.BaseDataTable import BaseDataTable
from aeneid.dbservices.DerivedDataTable import DerivedDataTable
import pandas as pd
import logging
import pymysql


class RDBDataTable(BaseDataTable):
    """
    RDBDataTable is relation DB implementation of the BaseDataTable.
    """

    # Default connection information in case the code does not pass an object
    # specific connection on object creation.
    #
    # You must replace with your own schema, user id and password.
    #
    _default_connect_info = {
        'host': 'localhost',
        'user': 'dbuser',
        'password': 'dbuser',
        'db': 'HW1',
        'port': 3306
    }


    def __init__(self, table_name, key_columns=None, connect_info=None, debug=True):
        """

        :param table_name: The name of the RDB table.
        :param connect_info: Dictionary of parameters necessary to connect to the data.
        :param key_columns: List, in order, of the columns (fields) that comprise the primary key.
        """

        # Initialize and store information in the parent class.
        super().__init__(table_name, connect_info, key_columns, debug)

        # If there is not explicit connect information, use the defaults.
        if connect_info is None:
            self._connect_info = RDBDataTable._default_connect_info

        # Create a connection to use inside this object. In general, this is not the right approach.
        # There would be a connection pool shared across many classes and applications.
        self._cnx = pymysql.connect(
            host=self._connect_info['host'],
            user=self._connect_info['user'],
            password=self._connect_info['password'],
            db=self._connect_info['db'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)

        self._key_columns = self._get_primary_key_columns()


    def debug_message(self, *m):
        """
        Prints some debug information if self._debug is True
        :param m: List of things to print.
        :return: None
        """
        if self._debug:
            print(" *** DEBUG:", *m)


    def __str__(self):
        """

        :return: String representation of the data table.
        """
        result = "RDBDataTable: table_name = " + self._table_name
        result += "\nTable type = " + str(type(self))
        result += "\nKey fields: " + str(self._key_columns)

        # Find out how many rows are in the table.
        q1 = "SELECT count(*) as count from " + self._table_name
        r1 = self._run_q(q1, fetch=True, commit=True)
        result += "\nNo. of rows = " + str(r1[0]['count'])

        # Get the first five rows and print to show sample data.
        # Query to get data.
        q = "select * from " + self._table_name + " limit 5"

        # Read into a data frame to make pretty print easier.
        df = pd.read_sql(q, self._cnx)
        result += "\nFirst five rows:\n"
        result += df.to_string()

        return result


    def _run_q(self, q, args=None, fields=None, fetch=True, cnx=None, commit=True):
        """

        :param q: An SQL query string that may have %s slots for argument insertion. The string
            may also have {} after select for columns to choose.
        :param args: A tuple of values to insert in the %s slots.
        :param fetch: If true, return the result.
        :param cnx: A database connection. May be None
        :param commit: Do not worry about this for now. This is more wizard stuff.
        :return: A result set or None.
        """
        try:
            # Use the connection in the object if no connection provided.
            if cnx is None:
                cnx = self._cnx

            # Convert the list of columns into the form "col1, col2, ..." for following SELECT.
            if fields:
                q = q.format(",".join(fields))

            cursor = cnx.cursor()  # Just ignore this for now.

            # If debugging is turned on, will print the query sent to the database.
            self.debug_message("Query = ", cursor.mogrify(q, args))

            r = cursor.execute(q, args)  # Execute the query.

            # Technically, INSERT, UPDATE and DELETE do not return results.
            # Sometimes the connector libraries return the number of created/deleted rows.
            if fetch:
                r = cursor.fetchall()  # Return all elements of the result.
            else:
                # r = None
                pass

            if commit:  # Do not worry about this for now.
                cnx.commit()

        except Exception as e:
            cnx.rollback()
            logging.exception("RDBDataTable._run_q: error = ", exc_info=True)
            raise e

        return r


    def _run_insert(self, table_name, column_list, values_list, cnx=None, commit=False):
        """

        :param table_name: Name of the table to insert data. Probably should just get from the object data.
        :param column_list: List of columns for insert.
        :param values_list: List of column values.
        :param cnx: Ignore this for now.
        :param commit: Ignore this for now.
        :return:
        """
        try:
            q = "insert into " + table_name + " "

            # If the column list is not None, form the (col1, col2, ...) part of the statement.
            if column_list is not None:
                q += "(" + ",".join(column_list) + ") "

            # We will use query parameters. For a term of the form values(%s, %s, ...) with one slot for
            # each value to insert.
            values = ["%s"] * len(values_list)

            # Form the values(%s, %s, ...) part of the statement.
            values = " ( " + ",".join(values) + ") "
            values = "values" + values

            # Put all together.
            q += values

            result = self._run_q(q, args=values_list, fields=None, fetch=False, cnx=cnx, commit=True)
            return result

        except Exception as e:
            logging.error("RDBDataTable._run_insert exception", exc_info=True)
            raise e


    def _get_primary_key(self):

        q = "SHOW KEYS FROM " + self._table_name + " WHERE Key_name = 'PRIMARY'"
        rows = self._run_q(q=q, args=None)

        keys = [r["Column_name"] for r in rows]

        return keys


    def _get_primary_key_columns(self):
        """

        :return: The names of the primary key columns in the form ['col1', ..., 'coln']

        The current implementation just returns the list of keys passed in the constructor.
        An extended implementation would/should query database data/metadata to get the information.
        """
        result = self._get_primary_key()
        return result


    def find_by_primary_key(self, key_fields, field_list=None):
        """

        :param key_fields: The values for the key_columns, in order, to use to find a record.
        :param field_list: A subset of the fields of the record to return.
        :return: None, or a dictionary containing the request fields for the record identified
            by the key.
        """
        try:
            # Get the key_columns specified on table create.
            key_columns = self._get_primary_key_columns()

            # Zipping together key_columns and passed fields produces a valid template
            tmp = dict(zip(key_columns, key_fields))

            # Call find_by_template. This returns a DerivedDataTable.
            result = self.find_by_template(tmp, field_list)

            # For various reasons, we do not return a DerivedDataTable for find_by_primary_key().
            # We return the single row. This follows REST semantics.
            if result is not None:
                result = result.get_rows()

                if result is not None and len(result) > 0:
                    result = result[0]
                else:
                    result = None

        except Exception as e:
            logging.error("RDBDataTable.find_by_primary_key exception", exc_info=True)
            raise e

        return result


    def _template_to_where_clause(self, t):
        """
        Convert a query template into a WHERE clause.
        :param t: Query template.
        :return: (WHERE clause, arg values for %s in clause)
        """
        terms = []
        args = []
        w_clause = ""

        # The where clause will be of the for col1=%s, col2=%s, ...
        # Build a list containing the individual col1=%s
        # The args passed to +run_q will be the values in the template in the same order.
        for k, v in t.items():
            temp_s = k + "=%s "
            terms.append(temp_s)
            args.append(v)

        if len(terms) > 0:
            w_clause = "WHERE " + " AND ".join(terms)
        else:
            w_clause = ""
            args = None

        return w_clause, args


    def _get_extras(self, limit=None, offset=None, order_by=None):

        result = ' '
        if order_by:
            result += ' order by ' + order_by + ' '
        if limit:
            result += ' limit ' + str(limit)
        if offset:
            result += ' offset ' + str(offset)


        return result


    def _project(self, rows, field_list):
        return rows

        pass

        """

        result = []

        if field_list is None:
            result = rows
        else:
            for r in rows:
                new_r = {f: r[f] for f in field_list}
                result.append(new_r)

        return result

        """


    def find_by_template(self, template, field_list=None, limit=None,
                         offset=None, order_by=None, follow_paths=False,
                         commit=True):
        """

        :param template: A dictionary of the form { "field1" : value1, "field2": value2, ...}
        :param field_list: A list of request fields of the form, ['fielda', 'fieldb', ...]
        :param limit: Do not worry about this for now.
        :param offset: Do not worry about this for now.
        :param order_by: Do not worry about this for now.
        :return: A list containing dictionaries. A dictionary is in the list representing each record
            that matches the template. The dictionary only contains the requested fields.
        """

        result = None

        try:
            # Compute the where clause.
            w_clause = self._template_to_where_clause(template)

            if field_list is None:
                # If there is not field list, we are doing 'select *'
                f_select = ['*']
            else:
                f_select = field_list

            # Query template.
            # _run_q will use args for %s terms and will format the field selection into {}
            q = "select {} from " + self._table_name + " " + w_clause[0]

            if limit:
                q += " limit " + str(limit)
            if offset:
                q += " offset " + str(offset)

            result = self._run_q(q, args=w_clause[1], fields=f_select, fetch=True, commit=commit)

            # SELECT queries always produce tables.
            result = DerivedDataTable("SELECT(" + self._table_name + ")", result)

        except Exception as e:
            logging.error("RDBDataTable.find_by_template exception", exc_info=True)
            raise e

        return result


    def delete_by_template(self, template):
        """

        Deletes all records that match the template.

        :param template: A template.
        :return: A count of the rows deleted.
        """
        try:
            wc = self._template_to_where_clause(template)
            q = "delete from " + self._table_name + " " + wc[0]
            result = self._run_q(q=q, args=wc[1], fields=None, fetch=False, cnx=None, commit=True)

        except Exception as e:
            logging.error("RDBDataTable.delete_by_templete exception", exc_info=True)
            raise e

        return result


    def delete_by_key(self, key_fields):

        try:
            k = dict(zip(self._key_columns, key_fields))
            return self.delete_by_template(k)

        except Exception as e:
            logging.error("RDBDataTable.delete_by_key exception", exc_info=True)
            raise e


    def insert(self, new_record):
        """

        :param new_record: A dictionary representing a row to add to the set of records.
        :return: None
        """
        result = None

        try:
            # Get the list of columns.
            column_list = list(new_record.keys())

            # Get corresponding list of values.
            value_list = list(new_record.values())

            # Name of table.
            t_name = self._table_name

            # Perform insert.
            result = self._run_insert(t_name, column_list, value_list)
            return result

        except Exception as e:
            print("Insert Exception = ", e)
            raise e


    def update_by_template(self, template, new_values):
        """

        :param template: A template that defines which matching rows to update.
        :param new_values: A dictionary containing fields and the values to set for the corresponding fields
            in the records.
        :return: The number of rows updates.
        """
        terms = []
        set_args = []

        for k, v in new_values.items():
            terms.append(k + "=%s")
            set_args.append(v)

        terms = ",".join(terms)

        wc = self._template_to_where_clause(template)

        set_args.extend(wc[1])

        q = "update " + self._table_name + " set " + str(terms) + " " + wc[0]

        result = self._run_q(q, set_args, fetch=False)
        return result


    def update_by_key(self, key_fields, new_values):

        tmp = dict(zip(self._key_columns, key_fields))
        return self.update_by_template(tmp, new_values)

