from app.classes import Member,Package
from app.database import mysql_config
import mysql.connector
from datetime import datetime, timedelta
import os
#----------------------------- Functions section ------------------------#

"""
this function will get the html content from any page 
and send it to browser
"""
def get_html(pagename):
    html_file = open("views/"+pagename+".html")
    content =html_file.read()
    html_file.close()
    return content
"""
this function will retrieve all members data from the database and create 
objects of member's class for each one of them
and will return array of members objects
"""
def get_all_members_data():
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
    for member in members:
        member_data = member
        member_obj = Member(member_data[1],(member_data[2]) , int(member_data[3]), int(member_data[4]), member_data[5], member_data[6], member_data[7],member_data[0])
        all_members.append(member_obj)
    
    return all_members

"""
this function will retrieve all pacages data from the database and create 
objects of package's class for each one of them
and will return array of packages objects
"""
def get_all_packages_data():
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
    for package in packages:
        package_obj = Package(package[1], int(package[3]),int(package[2]) , int(package[0]))
        all_packages.append(package_obj)
    return all_packages

"""
this function will delete the member from database based on it's ID
note the function is not created inside the class because it will be called using post 
method which will pass only member's ID
"""
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

        # Now delete the member
        cursor.execute(f"DELETE FROM members WHERE member_id = {member_id}")

        db.commit()
        print(f"Member with ID {member_id} deleted successfully")
    except mysql.connector.Error as error:
        print(f"Error deleting member: {error}")
    finally:
        cursor.close()

"""
this function will delete the package from database based on it's ID
note the function is not created inside the class because it will be called using post 
method which will pass only package's ID
"""
def delete_package_from_DB(package_id):
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()

        # Check if the package exist in subscription
        cursor.execute(f"SELECT * FROM subscription WHERE package_id = {package_id}")
        package = cursor.fetchall()

        if package:
            # If the package already exist in subscription table then delete it from this table first 
            cursor.execute(f"DELETE FROM subscription WHERE package_id = {package_id}")

        # Now delete the package from it's table
        cursor.execute(f"DELETE FROM package WHERE id = {package_id}")

        db.commit()
    except mysql.connector.Error as error:
        print(f"Error deleting package: {error}")
    finally:
        cursor.close()
"""
this function will take array of member's objects andd make them in shape of
members table to be placed in the homepage instead of placeholder
"""
def get_members_table_text(all_members):
    text = ""
    for member in all_members:
        text += "<tr>"
        text += "<td>" + str(member.id) + "</td>"
        text += "<td>" + member.name + "</td>"
        text += "<td>" + str(member.calculate_age()) + "</td>"
        #text += "<td>" + str(member.height) + "</td>"
        #text += "<td>" + str(member.weight) + "</td>"
        #text += "<td>" + member.gender + "</td>"
        text += "<td>" + member.phone + "</td>"
        #text += "<td>" + member.email + "</td>"
       # text += "<td>" + str(int(member.calculate_bmr()))+ "</td>"
        subscription_data = member.get_subscription()
        if subscription_data:
            text += "<td>" + subscription_data[0] + "</td>"
            text += "<td>" + str(subscription_data[1]) + "</td>"
            text += "<td>" + str(subscription_data[2]) + "</td>"
        else:
            text += "<td>" + "Not subscriped" + "</td>"
            text += "<td>"  + " " + "</td>"
            text += "<td>"  + " " + "</td>"
        text += "<td><a href='/deletemember?id=" + str(member.id) + "' class='delete'>Delete</a></td>"
        text += "<td><a href='/member_profile?id=" + str(member.id) + "' class='profile'>Profile</a></td>"
        text += "</tr>"
    return text

"""
this function will take array of package's objects and make them in shape of
packages table to be placed in the homepage instead of placeholder
"""
def get_packages_table_text(packages):
    text=""
    for package in packages:
        text += "<tr>"
        text += "<td>" + str(package.package_id) + "</td>"
        text += "<td>" + package.name + "</td>"
        text += "<td>" + str(package.value) + "</td>"
        text += "<td>" + str(package.duration) + "</td>"
        text += "<td><a href='/deletepackage?package_id=" + str(package.package_id) + "' class='delete'>Delete " + "</a></td>"
        text += "</tr>"
    return text

#this function subscribe the member in specific package
def subscribe_to_package(package_id,member_id):
    #first chack if memebr already subscriped
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM subscription WHERE memberId={member_id}")
        existing_subscription = cursor.fetchone()
        current_date = datetime.now().date()
#this condition if the member is not subscriped or if his subscriptin expired then let's subscripe
        if not existing_subscription or (existing_subscription)[2] < current_date:
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
            cursor.close()
            ret= True,0,0
#this section if the member have subscripe and still valid So confirm to him with the remaining duration
        else:
            existing_end_date=((existing_subscription)[2])
            remaining_days = (existing_end_date - current_date).days # total number of days remaining 
            remaining_months=remaining_days//30     # total number of Months remaining 
            remaining_days=remaining_days-remaining_months*30   #  number of days remaining after months
            cursor.close()
            ret= False,remaining_months,remaining_days

    except Exception as e:
        print(f"Error retrieving : {str(e)}")
        
    finally:
        cursor.close()
        return ret

#here if the member wants to subscribe even if his subscription still valid
def re_subscribe_to_package(package_id,member_id):
    try:
        db = mysql.connector.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(f"SELECT duration FROM package WHERE id={package_id}")
        duration = cursor.fetchone()[0]

        # Calculate start date (today) and end date (today + duration months)
        start_date = datetime.now().date()
        end_date = start_date + timedelta(30 * duration)   
      
        cursor.execute(" UPDATE subscription SET package_id = %s, startDate = %s, endDate = %s WHERE memberId = %s",
                    (package_id, start_date, end_date,member_id))
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"Error Updating : {str(e)}")
        
    finally:
        cursor.close()

def get_workout_nutrition(id):
    try:
        workout_file_path = f"members/{id}/workout_summary.txt"
        with open(workout_file_path, 'r') as file:
            workout_file_content = file.read()    
    except Exception as e:
        workout_file_content="Workout not Added Yet"
    try:
        nutrition_file_path = f"members/{id}/nutrition_plan.txt"
        with open(nutrition_file_path, 'r') as file:
            nutrition_file_content = file.read()    
    except Exception as e:
        nutrition_file_content="Nutrition not Added Yet"
    return workout_file_content,nutrition_file_content
