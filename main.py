import getpass
from datetime import datetime
from pprint import pprint

import pymongo
from bson import DBRef, ObjectId
from pymongo import MongoClient
from pprint import pprint

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # MODIFY the first and third line below to match your DB info (modify "cluster=..." and "db=..."
    cluster = "mongodb+srv://bonnie:VAkBWuxdiqsLCEdn@cluster0.69jvesy.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(cluster)
    db = client.cluster0

    # ----------SEED DATA----------#

    # University Employees Collection
    university_employees = db.university_employees
    university_employees.delete_many({})
    university_employees.create_index([("id_number", pymongo.ASCENDING)], unique=True)
    university_employees.create_index([("last_name", pymongo.ASCENDING)])
    university_employees.create_index([("first_name", pymongo.ASCENDING)])

    university_employees_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Employee that works for the University",
                'required': ["id_number"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'id_number': {
                        'bsonType': "int",
                        "description": "The ID number that uniquely identifies each employee"
                    },
                    'last_name': {
                        'bsonType': "string",
                        "description": "The last name of an employee"
                    },
                    'first_name': {
                        'bsonType': "string",
                        "description": "The first name of an employee"
                    }
                }
            }
        }
    }
    db.command('collMod', 'university_employees', **university_employees_validator)

    university_employees_results = university_employees.insert_many([
        {"id_number": 1, "last_name": "Jackson", "first_name": "Michael"},
        {"id_number": 2, "last_name": "Prime", "first_name": "Optimus"},
        {"id_number": 3, "last_name": "Kamado", "first_name": "Tanjiro"},
        {"id_number": 4, "last_name": "Chan", "first_name": "Jackie"},
        {"id_number": 5, "last_name": "Tucker", "first_name": "Chris"},
        {"id_number": 6, "last_name": "Brown", "first_name": "David"}
    ])

    print("Added university employees")

    # Buildings Collection
    buildings = db.buildings
    buildings.delete_many({})
    buildings.create_index([("name", pymongo.ASCENDING)], unique=True)

    buildings_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "A structure that contains many rooms where different classes meet",
                'required': ["name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'name': {
                        'bsonType': "string",
                        "description": "The name the structure is referred to as"
                    }
                }
            }
        }
    }
    db.command('collMod', 'buildings', **buildings_validator)

    buildings_results = buildings.insert_many([
        {"name": "CECS"},
        {"name": "ECS"},
        {"name": "VEC"},
        {"name": "HC"},
        {"name": "COB"},
        {"name": "CLA"}
    ])

    print("Added buildings")

    # Rooms Collection
    rooms = db.rooms
    rooms.delete_many({})
    rooms.create_index([("room_number", pymongo.ASCENDING)], unique=True)

    rooms_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Space inside of a building that can be identified by a number",
                'required': ["room_number", "building_name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'room_number': {
                        'bsonType': "int",
                        "description": "Number that identifies a certain room"
                    },
                    'building_name': {
                        'bsonType': "object",
                        "description": "Name of the building the room is in"
                    }
                }
            }
        }
    }
    db.command('collMod', 'rooms', **rooms_validator)

    rooms_results = rooms.insert_many([
        {"room_number": 100, "building_name": DBRef("buildings", db.buildings.find_one({"name": "CECS"})['_id'])},
        {"room_number": 200, "building_name": DBRef("buildings", db.buildings.find_one({"name": "ECS"})['_id'])},
        {"room_number": 300, "building_name": DBRef("buildings", db.buildings.find_one({"name": "VEC"})['_id'])},
        {"room_number": 101, "building_name": DBRef("buildings", db.buildings.find_one({"name": "HC"})['_id'])},
        {"room_number": 201, "building_name": DBRef("buildings", db.buildings.find_one({"name": "COB"})['_id'])},
        {"room_number": 301, "building_name": DBRef("buildings", db.buildings.find_one({"name": "CLA"})['_id'])}
    ])
    print("Added rooms")

    # Requests Collection (Junction Table)
    requests = db.requests
    requests.delete_many({})
    requests.create_index([("request_id", pymongo.ASCENDING)], unique=True)
    requests.create_index([("date_of_request", pymongo.ASCENDING)])

    requests_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "A notice made by an employee specifying that they would like access to a certain room in a building.",
                'required': ["university_employee_id_number", "room_number", "building_name", "request_id",
                             "date_of_request"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'university_employee_id_number': {
                        'bsonType': "object",
                        "description": "Number that identifies a certain employee"
                    },
                    'room_number': {
                        'bsonType': "object",
                        "description": "Number that identifies the requested room"
                    },
                    'building_name': {
                        'bsonType': "object",
                        "description": "Name of the building the requested room is in"
                    },
                    'request_id': {
                        'bsonType': "int",
                        "description": "Number that uniquely identifies the request"
                    },
                    'date_of_request': {
                        'bsonType': "string",
                        "description": "Date the request was made by the employee"
                    }
                }
            }
        }
    }
    db.command('collMod', 'requests', **requests_validator)

    requests_results = requests.insert_many([
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 1})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 100})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CECS"})['_id']),
         "request_id": 1,
         "date_of_request": "12-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 2})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 200})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "ECS"})['_id']),
         "request_id": 2,
         "date_of_request": "11-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 3})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 300})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "VEC"})['_id']),
         "request_id": 3,
         "date_of_request": "10-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 4})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 101})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "HC"})['_id']),
         "request_id": 4,
         "date_of_request": "09-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 5})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 201})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "COB"})['_id']),
         "request_id": 5,
         "date_of_request": "08-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 6})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 301})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CLA"})['_id']),
         "request_id": 6,
         "date_of_request": "07-04-2022"},
        {"university_employee_id_number": DBRef("university_employees",
                                                db.university_employees.find_one({"id_number": 2})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 100})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CECS"})['_id']),
         "request_id": 7,
         "date_of_request": "04-04-2022"}
    ])
    print("Added requests")

    # Door Names Collection (Lookup Table)
    door_names = db.door_names
    door_names.delete_many({})
    door_names.create_index([("name", pymongo.ASCENDING)], unique=True)

    door_names_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Name of an object located within a room or building that grants access inside based on location",
                'required': ["name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'name': {
                        'bsonType': "string",
                        "description": "Name of the door based on location in room"
                    }
                }
            }
        }
    }
    db.command('collMod', 'door_names', **door_names_validator)

    door_names_results = door_names.insert_many([
        {"name": "Front"},
        {"name": "Back"},
        {"name": "North"},
        {"name": "South"},
        {"name": "West"},
        {"name": "East"}
    ])
    print("Added door names")

    # Doors Collection
    doors = db.doors
    doors.delete_many({})

    doors_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Objected located within a room or building that grants access inside",
                'required': ["door_name", "room_number", "building_name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'door_name': {
                        'bsonType': "object",
                        "description": "Name of the door based on its location"
                    },
                    'room_number': {
                        'bsonType': "object",
                        "description": "Number that identifies a certain room"
                    },
                    'building_name': {
                        'bsonType': "object",
                        "description": "Name that identifies a certain building"
                    }
                }
            }
        }
    }
    db.command('collMod', 'doors', **doors_validator)

    doors_results = doors.insert_many([
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "Front"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 100})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CECS"})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "Back"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 200})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "ECS"})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "North"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 300})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "VEC"})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "South"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 101})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "HC"})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "West"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 201})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "COB"})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "East"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 301})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CLA"})['_id'])}
    ])
    print("Added doors")

    # Hooks Collection
    hooks = db.hooks
    hooks.delete_many({})
    hooks.create_index([("hook_id", pymongo.ASCENDING)], unique=True)

    hooks_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Master key that is copied to provide employees access to a certain room or building",
                'required': ["hook_id"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'hook_id': {
                        'bsonType': "int",
                        "description": "Number that uniquely identifies the master key"
                    }
                }
            }
        }
    }
    db.command('collMod', 'hooks', **hooks_validator)

    hooks_results = hooks.insert_many([
        {"hook_id": 1},
        {"hook_id": 2},
        {"hook_id": 3},
        {"hook_id": 4},
        {"hook_id": 5},
        {"hook_id": 6}
    ])
    print("Added hooks")

    # Accesses Collection (Junction Table)
    accesses = db.accesses
    accesses.delete_many({})

    accesses_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Records of what hooks can be used to access a certain room or building",
                'required': ["door_name", "room_number", "building_name", "hook_id"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'door_name': {
                        'bsonType': "object",
                        "description": "Name of the door based on its location"
                    },
                    'room_number': {
                        'bsonType': "object",
                        "description": "Number that identifies a certain room"
                    },
                    'building_name': {
                        'bsonType': "object",
                        "description": "Name that identifies a certain building"
                    },
                    'hook_id': {
                        'bsonType': "object",
                        "description": "Number that uniquely identifies a hook"
                    }
                }
            }
        }
    }
    db.command('collMod', 'accesses', **accesses_validator)

    accesses_results = accesses.insert_many([
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "Front"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 100})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CECS"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 1})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "Back"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 200})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "ECS"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 2})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "North"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 300})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "VEC"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 3})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "South"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 101})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "HC"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 4})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "West"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 201})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "COB"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 5})['_id'])},
        {"door_name": DBRef("door_names", db.door_names.find_one({"name": "East"})['_id']),
         "room_number": DBRef("rooms", db.rooms.find_one({"room_number": 301})['_id']),
         "building_name": DBRef("buildings", db.buildings.find_one({"name": "CLA"})['_id']),
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 6})['_id'])}
    ])
    print("Added accesses")

    # Distributing Departments Collection
    distributing_depts = db.distributing_depts
    distributing_depts.delete_many({})
    distributing_depts.create_index([("name", pymongo.ASCENDING)], unique=True)

    distributing_depts_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Name of a department that distributes keys",
                'required': ["name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'name': {
                        'bsonType': "string",
                        "description": "Name of the distributing department"
                    }
                }
            }
        }
    }
    db.command('collMod', 'distributing_depts', **distributing_depts_validator)

    distributing_depts_results = distributing_depts.insert_many([
        {"name": "Department1"},
        {"name": "Department2"},
        {"name": "Department3"},
        {"name": "Department4"},
        {"name": "Department5"},
        {"name": "Department6"}
    ])
    print("Added distributing departments")

    # Keys Collection
    keys = db.keys
    keys.delete_many({})
    keys.create_index([("key_id", pymongo.ASCENDING)], unique=True)
    keys.create_index([("loaned_out", pymongo.ASCENDING)])

    keys_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Object that is used to access a certain room or building",
                'required': ["key_id", "loaned_out", "hook_id", "distributing_dept_name"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'key_id': {
                        'bsonType': "int",
                        "description": "Number that uniquely identifies a key"
                    },
                    'loaned_out': {
                        'bsonType': "bool",
                        "description": "True if key is loaned out, False if key is not loaned out"
                    },
                    'hook_id': {
                        'bsonType': "object",
                        "description": "Number that uniquely identifies the master key that the key is a copy of"
                    },
                    'distributing_dept_name': {
                        'bsonType': "object",
                        "description": "Name of the department that distributes the key"
                    }
                }
            }
        }
    }
    db.command('collMod', 'keys', **keys_validator)

    keys_results = keys.insert_many([
        {"key_id": 1,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 1})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department1"})['_id'])},
        {"key_id": 2,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 2})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department2"})['_id'])},
        {"key_id": 3,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 3})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department3"})['_id'])},
        {"key_id": 4,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 4})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department4"})['_id'])},
        {"key_id": 5,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 5})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department5"})['_id'])},
        {"key_id": 6,
         "loaned_out": False,
         "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": 6})['_id']),
         "distributing_dept_name": DBRef("distributing_depts",
                                         db.distributing_depts.find_one({"name": "Department6"})['_id'])}
    ])
    print("Added keys")

    # Issued Dates Collection
    issued_dates = db.issued_dates
    issued_dates.delete_many({})
    issued_dates.create_index([("date", pymongo.ASCENDING)])

    issued_dates_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Date that a request is approved",
                'required': ["date", "keys_id", "request_id"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'date': {
                        'bsonType': "string",
                        "description": "Date that a request is approved and a key is loaned out"
                    },
                    'keys_id': {
                        'bsonType': "object",
                        "description": "ID number of the key loaned out"
                    },
                    'request_id': {
                        'bsonType': "object",
                        "description": "ID of the employee request that was approved"
                    }
                }
            }
        }
    }
    db.command('collMod', 'issued_dates', **issued_dates_validator)

    issued_dates_results = issued_dates.insert_many([
        {"date": "12-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 1})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 1})['_id'])},
        {"date": "11-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 2})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 2})['_id'])},
        {"date": "10-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 3})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 3})['_id'])},
        {"date": "09-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 4})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 4})['_id'])},
        {"date": "08-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 5})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 5})['_id'])},
        {"date": "07-05-2022",
         "keys_id": DBRef("keys", db.keys.find_one({"key_id": 6})['_id']),
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 6})['_id'])}
    ])
    print("Added issued dates")

    # Returns Collection
    returns = db.returns
    returns.delete_many({})
    returns.create_index([("date_of_return", pymongo.ASCENDING)])

    returns_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Records of when a loaned out key is successfully returned",
                'required': ["date_of_return", "request_id"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'date_of_return': {
                        'bsonType': "string",
                        "description": "Date that a previously loaned out key is returned"
                    },
                    'request_id': {
                        'bsonType': "object",
                        "description": "ID of the employee request that was previously approved to loan out key"
                    }
                }
            }
        }
    }
    db.command('collMod', 'returns', **returns_validator)

    returns_results = returns.insert_many([
        {"date_of_return": "12-06-2022",
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 1})['_id'])},
        {"date_of_return": "10-06-2022",
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 3})['_id'])},
        {"date_of_return": "08-06-2022",
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 5})['_id'])}
    ])
    print("Added returns")

    #Reports Collection
    reports = db.reports
    reports.delete_many({})
    reports.create_index([("date_of_report", pymongo.ASCENDING)])
    reports.create_index([("charge", pymongo.ASCENDING)])

    reports_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "Records of when a loaned out key is not successfully returned, employee is charged $25",
                'required': ["date_of_report", "charge", "request_id"],
                'additionalProperties': False,
                'properties': {
                    '_id': {'bsonType': "objectId"},
                    'date_of_report': {
                        'bsonType': "string",
                        "description": "Date that a report is made for a missing key"
                    },
                    'charge': {
                        'bsonType': "int",
                        "description": "Amount of money an employee is charged for losing a key"
                    },
                    'request_id': {
                        'bsonType': "object",
                        "description": "ID of the employee request that was previously approved to loan out missing key"
                    }
                }
            }
        }
    }
    db.command('collMod', 'reports', **reports_validator)

    reports_results = reports.insert_many([
        {"date_of_report": "11-06-2022",
         "charge": 25,
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 2})['_id'])},
        {"date_of_report": "09-06-2022",
         "charge": 25,
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 4})['_id'])},
        {"date_of_report": "07-06-2022",
         "charge": 25,
         "request_id": DBRef("requests", db.requests.find_one({"request_id": 6})['_id'])}
    ])
    print("Added reports")

    print("Inserted Seed Data Successfully")


    # ----------MENU AND MENU FUNCTIONS----------#

    def createNewKey():
        print("a: Create a New Key")
        print("Available hook IDs:")
        all_hooks = db.hooks.find({}, {"_id": 0})
        hook_list = []
        for h in all_hooks:
            print(h.get("hook_id"), "", end='')
            hook_list.append(int(h.get("hook_id")))
        last_key_id = 0
        hook_id = input("Please select a hook ID from the list above:")
        if int(hook_id) in hook_list:
            all_keys = db.keys.find({}, {"_id": 0})
            for k in all_keys:
                last_key_id = (int)(k.get("key_id"))
            newKey = {"key_id": last_key_id + 1,
                      "loaned_out": False,
                      "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": (int)(hook_id)})['_id']),
                      "distributing_dept_name": DBRef("distributing_depts", db.distributing_depts.find_one({"name": "Department1"})['_id'])}
            try:
                db.keys.insert_one(newKey)
            except:
                print("There was an error creating a new key")
                return

        elif int(hook_id) not in hook_list:
            print("Invalid hook, please try again")
            return
        print("Key ID:", last_key_id + 1, " successfully added!")

    def requestAccess():
        print("b: Request access to a given room by a given employee")

        ue_list = db.university_employees.find({}, {"_id": 0})
        for h in ue_list:
            id_number = h.get("id_number")
            last = h.get('last_name')
            first = h.get('first_name')
            print(id_number, ") ", first, " ", last)
        employee = input("Please enter employee ID:")

        blist = db.buildings.find({}, {"_id": 0})
        for h in blist:
            print(h.get('name'))
        building = input("Please enter requested building name:")

        rlist = db.rooms.find({}, {"_id": 0})
        for h in rlist:
            print(h.get('room_number'))
        room = input("Please enter requested room number:")

        date = input("Please enter the date of request in date format (MM-DD-YYYY):")
        # Find the last value for request id
        all_requests = db.requests.find({}, {"_id": 0})
        last_request_id = 0
        for r in all_requests:
            last_request_id = (int)(r.get("request_id"))
            search_employee = db.university_employees.find_one({"id_number": int(employee)})['_id']
            check_employee = db.requests.find_one({"university_employee_id_number.$id": search_employee})['_id']
            search_room = db.rooms.find_one({"room_number": int(room)})['_id']
            check_room = db.requests.find_one({"room_number.$id": search_room})['_id']
            search_building = db.buildings.find_one({"name": building})['_id']
            check_building = db.requests.find_one({"building_name.$id": search_building})['_id']

        if check_employee == check_room and check_building == check_room:
            try:
                #If there is an entry for this room with this employee in issued date, do not make a new request
                search_issued = db.issued_dates.find_one({"request_id.$id": check_building})['_id']
                print("Employee already has access, exiting...")
                return
            except:
                print("Error")

        thisRequest = ({"university_employee_id_number": DBRef("university_employees",
                                                           db.university_employees.find_one({"id_number": int(employee)})[
                                                               '_id']),
                    "room_number": DBRef("rooms", db.rooms.find_one({"room_number": int(room)})['_id']),
                    "building_name": DBRef("buildings", db.buildings.find_one({"name": building})['_id']),
                    "request_id": last_request_id + 1,
                    "date_of_request": date})
        db.requests.insert_one(thisRequest)
        print("Request for ", building, " building, room ", room, " under employee number ", employee,
                  " successfully submitted! New Request ID:", last_request_id + 1)

    def issueKey():
        print("c: Capture the issue of a key to an employee")
        employeeIdNumber = input("Please enter your ID number:")
        roomNumer = input("Please enter the room number you would like the enter:")
        buildingName = input("Please enter the building name you would like to enter:")
        currentDate = input("Please enter today's date in the format MM-DD-YYYY:")
        # Find the room number in rooms collection, then find the building name in rooms collection using referenced id from search in buildings collection
        try:
            this_room = db.rooms.find_one({"room_number": (int)(roomNumer)})['_id']
            building_find = db.buildings.find_one({"name": buildingName})['_id']
            this_building = db.rooms.find_one({'building_name.$id': building_find})['_id']
                # If request room/building combination is invalid, rerun the program
            if this_room != this_building:
                print("Room does not exist")
                return
            # Find an access with the room number and building name
            accesses_find = db.accesses.find_one({"building_name.$id": building_find, "room_number.$id": this_room})
            # Find the hook id that has access to desired room
            valid_hook_in_access = accesses_find.get("hook_id").id
            # Find a key with the valid hook id
            keys_find = db.keys.find_one({"hook_id.$id": valid_hook_in_access})
            #The key id value
            valid_key_id = keys_find.get("key_id")

            #Find the last value for request id
            all_requests = db.requests.find({}, {"_id": 0})
            last_request_id = 0
            for r in all_requests:
                last_request_id = (int)(r.get("request_id"))

            #Create a new request for the employee
            newRequest = {"university_employee_id_number": DBRef("university_employees", db.university_employees.find_one({"id_number": int(employeeIdNumber)})['_id']),
                          "room_number": DBRef("rooms", db.rooms.find_one({"room_number": int(roomNumer)})['_id']),
                          "building_name": DBRef("buildings", db.buildings.find_one({"name": buildingName})['_id']),
                          "request_id": last_request_id + 1,
                          "date_of_request": currentDate}
            db.requests.insert_one(newRequest)

            #Create a new issued date for the request
            newIssued = {"date": currentDate,
                         "keys_id": DBRef("keys", db.keys.find_one({"key_id": int(valid_key_id)})['_id']),
                         "request_id": DBRef("requests", db.requests.find_one({"request_id": last_request_id + 1})['_id'])}
            db.issued_dates.insert_one(newIssued)

            print("Key ID", valid_key_id, "has been issued")

        except:
            print("Error while issuing new key")

    def lostKey():
        print("d: Capture losing a key")
        date = input("Please enter the date of report in MM-DD-YYYY format:")
        requestID = input("Please enter the requestID: ")
        newRequest = {"date_of_report": date,
                      "charge": 25,
                      "request_id": DBRef("requests", db.requests.find_one({"request_id": (int)(requestID)})['_id'])}
        try:
            db.reports.insert_one(newRequest)
        except:
            print("Invalid request ID, please enter a valid request ID:")
            lostKey()
            return
        print("Report has been successfully recorded!")


    def employeeRoomKeyReport():
        print("e: Report out all the rooms that an employee can enter, given the keys that he/she already has")
        employeeID = input("Please Employee ID:")
        print("All rooms employee ID:", employeeID, " can enter are:")
        print("-------------------------------------------------------------")
        try:
            found_list = []
            requested_id = db.requests.find({"request_id": (int)(employeeID)})
            for r in requested_id:
                employee_requested_id = r["request_id"]
                requested_id = db.requests.find_one({"request_id": employee_requested_id})['_id']
                try:
                    entry_in_issued = db.issued_dates.find_one({"request_id.$id": requested_id})['_id']
                    access_building_id = r.get('building_name').id
                    access_room_id = r.get('room_number').id
                    building_name_search = db.buildings.find_one({"_id": ObjectId(access_building_id)})
                    building_name = building_name_search.get('name')
                    room_number_search = db.rooms.find_one({"_id": ObjectId(access_room_id)})
                    room_number = room_number_search.get('room_number')
                    if building_name + (str)(room_number) not in found_list:
                        print(building_name, room_number)
                        found_list.append(building_name + (str)(room_number))
                except:
                    print("Employee does not have access to any rooms")
                    print("-------------------------------------------------------------")
                    print("End of report")
                    return
        except:
            print("There was an error while reporting all rooms the employee can enter")
            return
        print("-------------------------------------------------------------")
        print("End of report")


def deleteKey():
    print("f: Delete a key")
    keysID = input("Please enter the key ID you wish to delete:")
    keyID = int(keysID)
    try:
        keys.delete_one({"key_id": keyID})
        print("Key ID:", keyID, " deleted successfully.")
    except:
        print("An error occured when deleting the key")


def deleteEmployee():
    print("g: Delete an employee")
    employeeID = input("Please enter the employee ID you wish to delete:")
    try:
        university_employees.delete_one({"id_number": employeeID})
        print("Employee ", employeeID, " deleted!")
    except:
        print("Something went wrong")


def addDoor():
    print("h: Add a new door that can be opened by an existing hook")
    roomNum = input("Please enter the new door's room number:")
    dlist = db.door_names.find({}, {"_id": 0})
    for h in dlist:
        print(h.get('name'))
    doorName = input("Please enter the new door's name:")
    building = input("Please enter the new door's building name:")
    hookid = input("Enter the hook ID for this door:")
    hook = int(hookid)
    newDoor = {
        "door_name": DBRef("door_names", db.door_names.find_one({"name": doorName})['_id']),
        "room_number": DBRef("rooms", db.rooms.find_one({"room_number": int(roomNum)})['_id']),
        "building_name": DBRef("buildings", db.buildings.find_one({"name": building})['_id'])}
    try:
        doors.insert_one(newDoor)
        relationship = {
            "door_name": DBRef("door_names", db.door_names.find_one({"name": doorName})['_id']),
            "room_number": DBRef("rooms", db.rooms.find_one({"room_number": int(roomNum)})['_id']),
            "building_name":DBRef("buildings", db.buildings.find_one({"name": building})['_id']),
            "hook_id": DBRef("hooks", db.hooks.find_one({"hook_id": int(hook)})['_id'])}
        accesses.insert_one(relationship)
        print("Door Successfully Added!")
    except:
        print("There was an error adding a new door")


def updateRequest():
    print("i: Update an access request to move it to a new employee")
    oldEmployee = input("Please enter the old employee ID:")
    roomNum = input("Please enter the room you want to update your request for:")
    newEmployee = input("Please enter the new employee ID:")
    try:
        this_old_employee = db.university_employees.find_one({"id_number": int(oldEmployee)})['_id']
        this_room_number = db.rooms.find_one({"room_number": (int(roomNum))})['_id']
        this_request = db.requests.find_one({"room_number.$id": this_room_number, "university_employee_id_number.$id": this_old_employee})

        requests.update_one({
            "request_id": int(this_request.get("request_id")),

        }, {"$set" : { "university_employee_id_number": DBRef("university_employees", db.university_employees.find_one({"id_number": int(newEmployee)})['_id'])}})
        print("Request Successfully updated!")
    except:
        print("There was an error updating the request")


def reportAll():
    print("j: Report out all the employees who can get into a room")
    roomNumer = input("Please enter the room number for the report:")
    buildingName = input("Please enter the building name of the room number you'd like to report:")
    print("_____________________________________________________________________________________________")

    # Find the room number in rooms collection, then find the building name in rooms collection using referenced id from search in buildings collection
    try:
        this_room = db.rooms.find_one({"room_number": (int)(roomNumer)})['_id']
        building_find = db.buildings.find_one({"name": buildingName})['_id']
        this_building = db.rooms.find_one({'building_name.$id': building_find})['_id']
        # If request room/building combination is invalid, rerun the program
        if this_room != this_building:
            print("Invalid room, please enter a valid room number and building name:")
            reportAll()
            return

        # Find all the requests that include this room number
        room_requests = db.requests.find({"building_name.$id": building_find, "room_number.$id": this_room})
        # Find each person that requested this room
        for r in room_requests:
            employee_requested = r["request_id"]
            requested_id = db.requests.find_one({"request_id": employee_requested})['_id']
            try:
                entry_in_issued = db.issued_dates.find_one({"request_id.$id": requested_id})['_id']
                # Find the employee in the employees collection using the id number from requests collection
                access_employee_id = r.get('university_employee_id_number').id
                employee_id_search = db.university_employees.find_one({"_id": ObjectId(access_employee_id)})
                employee_id_last_name = employee_id_search.get('last_name')
                employee_id_first_name = employee_id_search.get('first_name')
                print("Employee ID with access to room: ", employee_id_first_name, "", employee_id_last_name)
            # If the request has not been issued, do not include
            except:
                break
    except:
        print("Invalid room, please enter a valid room number and building name:")
        reportAll()
        return

    print("_____________________________________________________________________________________________")
    print("End of report")


if __name__ == '__main__':
    cont = True
    while cont:
        print("""
        OPTIONS
        -------------------------------------------------------------------------------------------------
        a. Create a new Key.
        b. Request access to a given room by a given employee.
        c. Capture the issue of a key to an employee
        d. Capture losing a key
        e. Report out all the rooms that an employee can enter, given the keys that he/she already 
        has.
        f. Delete a key.
        g. Delete an employee.
        h. Add a new door that can be opened by an existing hook.
        i. Update an access request to move it to a new employee.
        j. Report out all the employees who can get into a room.
        -------------------------------------------------------------------------------------------------
        """)
        answer = input("Hello, please enter a letter from the options above:")

        menuDictionary = {
            "a": createNewKey,
            "b": requestAccess,
            "c": issueKey,
            "d": lostKey,
            "e": employeeRoomKeyReport,
            "f": deleteKey,
            "g": deleteEmployee,
            "h": addDoor,
            "i": updateRequest,
            "j": reportAll

        }
        menuDictionary[answer]()
        again = input("Would you like do perform another action?(y/n):")
        if again != "y":
            cont = False
            print("Exiting...")
