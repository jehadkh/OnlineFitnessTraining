#(Online Fit trainer) APP
from datetime import datetime, timedelta
import mysql.connector
import flask
from flask_mysqldb import MySQL
from flask import Flask, render_template

app =flask.Flask(__name__)
app = Flask(__name__, template_folder="views")
if __name__=='__main__':
    app.run(debug=True)

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'K1d02370@2024',
    'database': 'fittrackdb'
}
# Connect to MySQL
#db = mysql.connector.connect(**mysql_config)
#cursor = db.cursor()


"""
this class will contain the main info about each member
"""
class Member:
    id=None
    def __init__(self, name, birthdate,height,weight,gender,phone,email,member_id=None):
        #self.id = generate_new_id() if not member_id else  member_id
        try:
            self.name = name
            self.gender = gender.lower()
            if isinstance(birthdate, str):
                self.birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
            else:
                self.birthdate = birthdate  
            self.height=height
            self.weight=weight
            self.phone=phone
            self.email=email
        except Exception as e:
            print(f"Error adding member: {str(e)}")
            return get_html("errorPage").replace("$$MSG$$", "Enter Valid Data")
        if member_id == None:
            self.add_to_DB()    
        else:
            self.id=member_id

    def add_to_DB(self):
        query = """ INSERT INTO members (name, birthdate, height, weight, gender, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (self.name, self.birthdate, self.height, self.weight, self.gender, self.phone, self.email)
        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(query, values)
            db.commit()
            self.id=cursor.lastrowid
            print("member id =" + str(self.id))
        except Exception as e:
            print(f"Error adding member to the database: {str(e)}")
    
    def get_package(self):
        package_name=""

        query = f"SELECT package.name FROM subscription JOIN package ON subscription.package_id = package.id WHERE subscription.memberId = {self.id}"
        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(query)
            #this must return tuple contains every subscriped backage and every name
            # so here we will have only one row and will take the only value in it
            package_name = str(cursor.fetchall()[0][0])
        except Exception as e:
            print(f"Error getting package: {str(e)}")
        finally:
            cursor.close()
        return package_name
        
    #this function will return true if the member object created successfully and added to the database
    def member_added_successfully(self):
        if self.id == None:
            return False   
        else:
            return True

    """
        this function used to calculate the age of the member based on his birthdate
    """
    def calculate_age(self):
         today = datetime.now().date()
         age = today.year - self.birthdate.year
         return age
    
    """
    this function calculate the member's bmr
    """
    def calculate_bmr(self):
        if self.gender == "male":
            bmr = 88.362 + (13.397 * self.weight)+(4.799 * self.height)-(5.677 * self.calculate_age())
        elif self.gender == "female":
            bmr = 447.593 + (9.247 * self.weight)+(3.098 * self.height)-(4.330 * self.calculate_age())
        return bmr

    def deletemember(self):
        deleteMemberFromDB(self.id)
        del self

class Package:
    def __init__(self, name, value,duration,package_id=None):
        self.package_id = generate_new_id() if not package_id else  package_id
        self.name = name
        self.value=value
        self.duration=duration

    def add_to_DB(self):
        print("execute query")
        query = """INSERT INTO Package ( name, duration, value)
                   VALUES ( %s, %s, %s)"""
        values = ( self.name, self.duration,self.value)
        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(query, values)
            db.commit()
            self.package_id=cursor.lastrowid
            print(f"Package added to the database with ID = {str(self.package_id)}")
        except Exception as e:
            print(f"Error adding Package to the database: {str(e)}")
        finally:
            cursor.close()


class VitaDetails:
    def __init__(self, allergy,disease,bodyFatPercentage, fitnessGoals,medications,member_id=None):
        self.member_id =  member_id
        self.fitnessGoals = fitnessGoals
        self.medications = medications
        self.allergy=allergy
        self.disease=disease
        self.bodyFatPercentage=bodyFatPercentage

        
    def add_to_DB(self):
        print("=-------------inserting------------")
        query = """INSERT INTO VitalDetails (memberId, allergy, disease, bodyFatPercentage, fitnessGoals, medications)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (self.member_id, self.allergy, self.disease, self.bodyFatPercentage, self.fitnessGoals, self.medications)

        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(query, values)
            db.commit()
            print("VitaDetails added to the database for member ID =", str(self.member_id))
        except Exception as e:
            print(f"Error adding VitaDetails to the database: {str(e)}")




def getAllMembersData():

    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving members: {str(e)}")
        members=[]
    finally:
        cursor.close()
    all_members = []
    #if members=='':
    for member in members:
        member_data = member
        member_obj = Member(member_data[1],(member_data[2]) , int(member_data[3]), int(member_data[4]), member_data[5], member_data[6], member_data[7],member_data[0])
        all_members.append(member_obj)
    
    return all_members

def getAllPackagesData():
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM package;")
        packages = cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving package: {str(e)}")
        packages=[]
    finally:
        cursor.close()
    all_packages = []
    #if members=='':
    for package in packages:
        package_obj = Package(package[1], int(package[3]),int(package[2]) , int(package[0]))
        all_packages.append(package_obj)
    return all_packages


def deleteMemberFromDB(member_id):
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()

        # Check if the member has vital details
        cursor.execute(f"SELECT * FROM vitaldetails WHERE memberId = {member_id}")
        vital_details = cursor.fetchall()

        if vital_details:
            # If the member has vital details, delete them first
            cursor.execute(f"DELETE FROM vitaldetails WHERE memberId = {member_id}")

        # Check if the member has subscriptions
        cursor.execute(f"SELECT * FROM subscription WHERE memberId = {member_id}")
        subscriptions = cursor.fetchall()

        if subscriptions:
            # If the member has subscriptions, delete them first
            cursor.execute(f"DELETE FROM subscription WHERE memberId = {member_id}")

        # Now you can delete the member
        cursor.execute(f"DELETE FROM members WHERE member_id = {member_id}")

        db.commit()
        print(f"Member with ID {member_id} deleted successfully")
    except mysql.connector.Error as error:
        print(f"Error deleting member: {error}")
    finally:
        cursor.close()




def generate_new_id():
    file = open("latestID.txt")
    id = int(file.read().strip())
    file.close()
    file = open("latestID.txt",'w')
    file.write(str(id+1))
    file.close()
    return id
class User:
    name=""



@app.route("/") 
def homepage():
    members = getAllMembersData()
    text = get_members_table_text(members)
        
    packages=getAllPackagesData()
    text2=get_packages_table_text(packages)
    return get_html("index").replace("$$MEMBERS$$", text).replace("$$PACKAGES$$",text2)


@app.route ("/newmember") 
def newmemberpage():
    return get_html("add_member")

@app.route ("/addnewmember") 
def addnewmember():
    name= flask.request.args.get("name")
    height= flask.request.args.get("height")
    email= flask.request.args.get("email")
    weight= flask.request.args.get("weight")
    phone= flask.request.args.get("phone")
    birthdate= flask.request.args.get("birthdate")
    gender= flask.request.args.get("gender")
    member=Member(name,birthdate,height,weight,gender,phone,email)

    return flask.redirect(f"/newVital?id={member.id}")

@app.route ("/newVital") 
def newVitalpage():
    id= flask.request.args.get("id")
    return get_html("add_vital_details").replace("&&ID&&",id)
   
@app.route ("/addVitalDetails") 
def addVitalDetails():
    member_id= flask.request.args.get("id")
    bodyFatPercentage= flask.request.args.get("bodyFatPercentage")
    disease= flask.request.args.get("disease")
    medications= flask.request.args.get("medications")
    allergy= flask.request.args.get("allergy")
    fitnessGoals= flask.request.args.get("fitnessGoals")

    vitaDetails=VitaDetails(allergy, disease,bodyFatPercentage,fitnessGoals,medications,member_id)
    vitaDetails.add_to_DB()
    return flask.redirect("/")



@app.route ("/delete") 
def deletemember():
    id= flask.request.args.get("id")
    deleteMemberFromDB(id)
    return flask.redirect("/") 

@app.route ("/search") #the next function will be called once user entered the name of contact he wanted to search for
def search():
    result=[]
    nameOrId= flask.request.args.get("search") 
    print("nameOrId = "+str(nameOrId))
    if nameOrId.isdigit():
        id=nameOrId
        #search by id
        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM members where member_id={id}")
            members = cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving members: {str(e)}")
            return flask.redirect("/") 
            
        finally:
            cursor.close()
            ######################
    else:
        name=nameOrId
        try:
            db = mysql.connector.connect(**mysql_config)
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM members where name='{name}'")
            members = cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving members: {str(e)}")
            return flask.redirect("/")
         
    all_members = []
    for member in members:
        member_data = member
        member_obj = Member(member_data[1],(member_data[2]) , int(member_data[3]), int(member_data[4]), member_data[5], member_data[6], member_data[7], (member_data[0]))
        all_members.append(member_obj)
    
    text = get_members_table_text(all_members)

    packages=getAllPackagesData()
    text2=get_packages_table_text(packages)
    return get_html("index").replace("$$MEMBERS$$", text).replace("$$PACKAGES$$",text2)

def get_members_table_text(all_members):
    text = ""
    for member in all_members:
        text += "<tr>"
        text += "<td>" + str(member.id) + "</td>"
        text += "<td>" + member.name + "</td>"
        text += "<td>" + str(member.calculate_age()) + "</td>"
        #text += "<td>" + str(member.height) + "</td>"
        #text += "<td>" + str(member.weight) + "</td>"
        text += "<td>" + member.gender + "</td>"
        text += "<td>" + member.phone + "</td>"
        text += "<td>" + member.email + "</td>"
       # text += "<td>" + str(int(member.calculate_bmr()))+ "</td>"
        text += "<td>" + member.get_package() + "</td>"
        text += "<td><a href='/delete?id=" + str(member.id) + "' class='delete'>Delete</a></td>"
        text += "<td><a href='/member_profile?id=" + str(member.id) + "' class='delete'>Profile</a></td>"
        text += "</tr>"
    return text

def get_packages_table_text(packages):
    text=""
    for package in packages:
        text += "<tr>"
        text += "<td>" + str(package.package_id) + "</td>"
        text += "<td>" + package.name + "</td>"
        text += "<td>" + str(package.value) + "</td>"
        text += "<td>" + str(package.duration) + "</td>"
        text += "</tr>"
    return text

@app.route("/member_profile")
def member_profile():
    result = []
    id = flask.request.args.get("id")
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM members WHERE member_id={id}")
        member_data = cursor.fetchone()
    except Exception as e:
        print(f"Error retrieving members: {str(e)}")
        return flask.redirect("/")
    finally:
        cursor.close()
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM Vitaldetails WHERE memberId={id}")
        member_vital_data = cursor.fetchone()
    except Exception as e:
        print(f"Error retrieving vital: {str(e)}")
        return flask.redirect("/")
    finally:
        cursor.close()
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM package")
        packages_data = cursor.fetchone()
    except Exception as e:
        print(f"Error retrieving vital: {str(e)}")
        cursor.close()
        return flask.redirect("/")
    
    if member_vital_data and member_data is not None:
        member = Member(
            member_data[1],
            (member_data[2]),
            int(member_data[3]),
            int(member_data[4]),
            member_data[5],
            member_data[6],
            member_data[7],
            int(member_data[0]),
        )

        vitaDetails = VitaDetails(
            member_vital_data[1],
            member_vital_data[2],
            member_vital_data[3],
            member_vital_data[4],
            member_vital_data[5],
            int(member_data[0])
        )
        packages=getAllPackagesData()
        

        return render_template("member_profile.html", member=member, vitaDetails=vitaDetails,packages=packages)
    else:
        return "No vital details found for this member."




"""
this function will get the html content from any page 
and send it to browser
"""
def get_html(pagename):
    html_file = open("views/"+pagename+".html")
    content =html_file.read()
    html_file.close()
    return content

@app.route ("/newpacakge") 
def newpackage():
    return get_html("add_package")

@app.route ("/addnewpackage") 
def addnewpackage():
    name= flask.request.args.get("name")
    value= flask.request.args.get("value")
    duration= flask.request.args.get("duration")

    package=Package(name, value,duration)
    print(package.name)
    print(package.value)
    print(package.duration)
    package.add_to_DB()
    return flask.redirect("/")



# New route to handle subscription form submission
@app.route("/subscribe", methods=["POST"])
def subscribe():
    package_id = flask.request.form.get("package_id")
    member_id = flask.request.form.get("member_id")
    print("member_id is =" + str(member_id))
    print("package_id is =" + str(package_id))
    
    subscribe_to_package(package_id,member_id)
        # Redirect to member profile or wherever you want to go after subscription
    return flask.redirect("/")


def subscribe_to_package(package_id,member_id):
    #first chack if memebr already subscriped
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        print("let's check")
        cursor.execute(f"SELECT * FROM subscription WHERE memberId={member_id}")
        existing_subscription = cursor.fetchone()
        if existing_subscription:
            # Member is already subscribed, handle accordingly (e.g., show a message)
            print("Member is already subscribed to a package")
        else:
            print("let's sub")
            # Get package duration from the package table
            cursor.execute(f"SELECT duration FROM package WHERE id={package_id}")
            duration = cursor.fetchone()[0]

            # Calculate start date (today) and end date (today + duration months)
            start_date = datetime.now().date()
            end_date = start_date + timedelta(30 * duration)

            # Subscribe the member to the selected package with start and end dates
            cursor.execute("INSERT INTO subscription (memberId, package_id, startDate, endDate) VALUES (%s, %s, %s, %s)",
                           (member_id, package_id, start_date, end_date))
            db.commit()
            print("Member subscribed successfully")
    except Exception as e:
        print(f"Error retrieving vital: {str(e)}")
        return flask.redirect("/")
    finally:
        cursor.close()