#(Online Fit trainer) APP
from datetime import datetime
import mysql.connector
import flask
from flask_mysqldb import MySQL
app =flask.Flask("server")

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'K1d02370@2024',
    'database': 'fittrackdb'
}
# Connect to MySQL
db = mysql.connector.connect(**mysql_config)
cursor = db.cursor()

"""
this class will contain the main info about each member
"""
class Member:
    def __init__(self, name, birthdate,height,weight,gender,phone,email,member_id=None):
        self.id = generate_new_id() if not member_id else  member_id
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
    """
    this function will add the member into the file
    """
    def addmembertodb(self):
        query = """ INSERT INTO members (name, birthdate, height, weight, gender, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (self.name, self.birthdate, self.height, self.weight, self.gender, self.phone, self.email)
        try:
            cursor.execute(query, values)
            db.commit()
            print("Member added successfully to the database!")
            return True
        except Exception as e:
            print(f"Error adding member to the database: {str(e)}")
            return False

    def deletemember(self):
        deleteMemberFromDB(self.id)

   
    
def getAllMembersData():
    try:
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving members: {str(e)}")
        members=[]
    all_members = []
    #if members=='':
    for member in members:
        member_data = member
        member_obj = Member(member_data[1],(member_data[2]) , int(member_data[3]), int(member_data[4]), member_data[5], member_data[6], member_data[7], (member_data[0]))
        all_members.append(member_obj)
    return all_members

def deleteMemberFromDB(member_id):
    try:
        sqlQuery = f"DELETE FROM members WHERE member_id = {member_id}"
        cursor.execute(sqlQuery)
        db.commit()
        print(f"Member with ID {member_id} deleted successfully")
    except mysql.connector.Error as error:
        print(f"Error deleting member: {error}")



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
    text = ""
    for member in members:
        text += "<tr>"
        text += "<td>" + str(member.id) + "</td>"
        text += "<td>" + member.name + "</td>"
        text += "<td>" + str(member.calculate_age()) + "</td>"
        text += "<td>" + str(member.height) + "</td>"
        text += "<td>" + str(member.weight) + "</td>"
        text += "<td>" + member.gender + "</td>"
        text += "<td>" + member.phone + "</td>"
        text += "<td>" + member.email + "</td>"
        text += "<td>" + str(int(member.calculate_bmr()))+ "</td>"
        text += "<td><a href='/delete?id=" + str(member.id) + "' class='delete'>Delete</a></td>"
        text += "<td><a href='/member_profile?id=" + str(member.id) + "' class='delete'>Profile</a></td>"
        text += "</tr>"
    return get_html("index").replace("$$MEMBERS$$", text)


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
    if(member.addmembertodb()):
        return flask.redirect("/")
    else:
        return flask.redirect("/newmember")
     

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
            cursor.execute(f"SELECT * FROM members where member_id={id}")
            members = cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving members: {str(e)}")
            return flask.redirect("/") 
            ######################
    else:
        name=nameOrId
        try:
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
    #return all_members
    text = ""
    for member in all_members:
        text += "<tr>"
        text += "<td>" + str(member.id) + "</td>"
        text += "<td>" + member.name + "</td>"
        text += "<td>" + str(member.calculate_age()) + "</td>"
        text += "<td>" + str(member.height) + "</td>"
        text += "<td>" + str(member.weight) + "</td>"
        text += "<td>" + member.gender + "</td>"
        text += "<td>" + member.phone + "</td>"
        text += "<td>" + member.email + "</td>"
        text += "<td>" + str(int(member.calculate_bmr()))+ "</td>"
        text += "<td><a href='/delete?id=" + str(member.id) + "' class='delete'>Delete</a></td>"
        text += "<td><a href='/member_profile?id=" + str(member.id) + "' class='delete'>Profile</a></td>"
        text += "</tr>"
    return get_html("index").replace("$$MEMBERS$$", text)





@app.route ("/member_profile") #the next function will be called once user entered the name of contact he wanted to search for
def member_profile():
    result=[]
    id= flask.request.args.get("id") 
    try:
        cursor.execute(f"SELECT * FROM members where member_id={id}")
        member_data = cursor.fetchone() 
    except Exception as e:
        print(f"Error retrieving members: {str(e)}")
        return flask.redirect("/") 
    print(member_data)
    member = Member(member_data[1],(member_data[2]) , int(member_data[3]), int(member_data[4]), member_data[5], member_data[6], member_data[7], int(member_data[0]))
    #return all_members
    text = ""
    text += "<p class='member_info'>ID: " + str(member.id) + "</p>"
    text += "<p class='member_info'>Name: " + str(member.name) + "</p>"
    text += "<p class='member_info'>Age: " + str(member.calculate_age()) + "</p>"
    text += "<p class='member_info'>Height: " + str(member.height) + "</p>"
    text += "<p class='member_info'>Weight: " + str(member.weight) + "</p>"
    text += "<p class='member_info'>Gender: " + member.gender + "</p>"
    text += "<p class='member_info'>Phone: " + member.phone + "</p>"
    text += "<p class='member_info'>Email: " + member.email + "</p>"
    text += "<a href='/delete?id=" + str(member.id) + "' class='delete'>Delete</a>"
    vital_derails=""
    vital_derails+="<p class='member_info'>BMR: " + str(int(member.calculate_bmr())) + "</p>"
    return get_html("member_profile").replace("$$MEMBER_INFO$$", text).replace("$$MEMBER_VITAL_DETAILS$$",vital_derails)




"""
this function will get the html content from any page 
and send it to browser
"""
def get_html(pagename):
    html_file = open(pagename+".html")
    content =html_file.read()
    html_file.close()
    return content
