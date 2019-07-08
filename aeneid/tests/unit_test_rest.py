## Xinquan Wang -- xw2566


import requests
import json
from aeneid.dbservices.RDBDataTable import RDBDataTable
from tabulate import tabulate

import pymysql
pymysql.install_as_MySQLdb()


data_tables = {}

cnx = pymysql.connect(
    host="localhost",
    database="HW1",
    user="dbuser",
    password="dbuser",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)


fantasy_manager = RDBDataTable("HW1.fantasy_manager", key_columns=['id'])
data_tables["Hw1.fantasy_manager"] = fantasy_manager


def test_api_1():

    r = requests.get("http://127.0.0.1:5000")
    result = r.text

    print("First REST API returned", r.text)


## Get
def test_json():

    params = {"id": "ok1", "fields": "last_name, first_name, email"}
    url = 'http://127.0.0.1:5000/api/HW1/fantasy_manager'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(url, headers=headers, params=params)
    print("Result = ")
    print(r.text)
    print(json.dumps(r.json(), indent=2, default=str))
    display_response(r)

    print("\ntest_create_manager: test 2 retrieving created manager.")
    link = r.headers.get('Location', None)
    if link is None:
        print("No link header returned.")
    else:
        url = link
        headers = None
        result = requests.get(url)
        print("\ntest_create_manager: Get returned: ")
        display_response(result)


## Post
def test_json2():

    url = 'http://127.0.0.1:5000/explain/body'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = {"p": "cool"}
    r = requests.post(url, headers=headers, json=data)
    print("Result = ")
    print(json.dumps(r.json(), indent=2, default=str))


def display_response(rsp):

    try:
        print("Printing a response.")
        print("HTTP status code: ", rsp.status_code)
        h = dict(rsp.headers)
        print("Response headers: \n", json.dumps(h, indent=2, default=str))

        try:
            body = rsp.json()
            print("JSON body: \n", json.dumps(body, indent=2, default=str))
        except Exception as e:
            body = rsp.text
            print("Text body: \n", body)

    except Exception as e:
        print("display_response got exception e = ", e)


def test_create_related():


    try:

        playerid = 'ls1'
        sub_resource = "fantasy_team"

        print("\ntest_create_related: test 1")
        path_url = "http://127.0.0.1:5000/api/moneyball/fantasy_manager/ls1/fantasy_team"
        print("Path = ", path_url)
        body = {"team_name": "Braves"}
        print("Body = \n", json.dumps(body, indent=2))
        result = requests.post(path_url, json=body, headers={"Content-Type" : "application/json"})
        print("test_create_related response = ")
        display_response(result)

        l = result.headers.get("Location", None)
        if l is not None:
            print("Got location = ", l)
            print("test_create_related, getting new resource")
            result = requests.get(l)
            display_response(result)
        else:
            print("No location?")


    except Exception as e:
        print("POST got exception = ", e)


def test_create_manager():

    try:
        body = {
            "id": "ok1",
            "last_name": "Obiwan",
            "first_name": "Kenobi",
            "email": "ow@jedi.org"
        }
        print("\ntest_create_manager: test 1, manager = \,", json.dumps(body, indent=2, default=str))
        url = "http://127.0.0.1:5000/api/HW1/fantasy_manager"
        headers = {"content-type": "application/json"}
        result = requests.post(url, headers=headers, json=body)
        display_response(result)

        print("\ntest_create_manager: test 2 retrieving created manager.")
        link = result.headers.get('Location', None)
        if link is None:
            print("No link header returned.")
        else:
            url = link
            headers = None
            result = requests.get(url)
            print("\ntest_create_manager: Get returned: ")
            display_response(result)

    except Exception as e:
        print("POST got exception = ", e)


def retrieve_manager():
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM fantasy_manager")
    result = cursor.fetchall()
    print(tabulate(result))


def test_delete_manager():
    print("\ntest_delete_manager: manager = \,")
    url = "http://127.0.0.1:5000/api/HW1/fantasy_manager/ok1"
    headers = {"content-type": "application/json"}
    result = requests.delete(url, headers=headers)
    display_response(result)





test_api_1()
test_json2()
test_create_manager()
test_delete_manager()
print("After deleting manager with id 'ok1'")
retrieve_manager()
