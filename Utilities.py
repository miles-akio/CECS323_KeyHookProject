from pymongo import MongoClient


class Utilities:
    @staticmethod
    def startup():
        print("Prompting for the password.")
        cluster = "mongodb+srv://bonniellhwhite:UwaTQ6VSYHZ0Y84O@dbhw.t5dzjis.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(cluster)
        # I could also have said "db = client.demo_database" to do the same thing.
        db = client.MongoDBHW
        return db

    @staticmethod
    def get_section(db, courseName):
        result = db.sections.find_one({"courseName": courseName})['_id']

        return result
