#(Online Fit trainer) APP
#----------------------------- Imports section ------------------------#
import mysql.connector
import flask
from flask import Flask, render_template, send_from_directory
import os
from app.classes import Member,Package,VitaDetails
from app.database import mysql_config
from app.functions import get_html,get_all_members_data,get_all_packages_data,delete_member_from_DB,get_vital_info
from app.functions import delete_package_from_DB,subscribe_to_package,re_subscribe_to_package,search_by_id,search_by_name
from app.html_hanlding import get_members_table_text,get_packages_table_text
from app.files_handling import get_workout_nutrition
#----------------------------- Initialize the coed section ------------------------#
#init flask
app =flask.Flask(__name__)
app = Flask(__name__, template_folder="views")
if __name__=='__main__':
    app.run(debug=True)

#----------------------------- Routes section ------------------------#
#this route used for the icon of the website
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

#the first route in the website whech is welcome page
@app.route ("/") 
def login():
    return get_html("login")

#the home page route which will view member's, packages, subscriptions main info
@app.route("/home") 
def homepage():
    members = get_all_members_data()
    text = get_members_table_text(members)
        
    packages=get_all_packages_data()
    text2=get_packages_table_text(packages)
    return get_html("index").replace("$$MEMBERS$$", text).replace("$$PACKAGES$$",text2)


#this route will return the page where trainer will insert the main info of the member
@app.route ("/newmember") 
def newmemberpage():
    return get_html("add_member")
"""
this route will be called after inserting the main info to create object
for the member and then will go to page where  trainer insert member's vital details
"""
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

#this route will return the page where trainer will insert the vital details of the member
@app.route ("/newVital") 
def newVitalpage():
    id= flask.request.args.get("id")
    return get_html("add_vital_details").replace("&&ID&&",id)
   
"""
this route will be called after inserting the Vital Details to create object
for the Vital Details and then will go to the home page
"""
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
    return flask.redirect("/home")


#this route will used to pass id for member to the delete from database function
@app.route ("/deletemember") 
def deletemember():  
    id= flask.request.args.get("id")
    delete_member_from_DB(id)
    return flask.redirect("/home") 

#this route will used to pass id for package to the delete from database function
@app.route ("/deletepackage") 
def deletepackage():
    id= flask.request.args.get("package_id")
    delete_package_from_DB(id)
    print ("delete package with id = " + str(id))
    return flask.redirect("/home") 

#this route will be called once user entered the name or id of the member he wanted to search for
@app.route ("/search") 
def search():
    nameOrId= flask.request.args.get("search") 
#check iff trainer entered an ID
    if nameOrId.isdigit():
        id=nameOrId
        members=search_by_id(id)   
#if it is not by id so search by member's name    
    else:
        name=nameOrId
        members=search_by_name(name)   
         
    all_members = []
    for member in members:
        member_data = member
        member_obj = Member(member_data[1],(member_data[2]) , int(member_data[3]),
                            int(member_data[4]), member_data[5], member_data[6], member_data[7], (member_data[0]))
        all_members.append(member_obj)
#now get the data (the html element of the member's table) which will be replaced with the placeholder in the home page(index.html)
    members_table = get_members_table_text(all_members)

#this section will be called any way to view packages table in the home page
    packages=get_all_packages_data()
    packages_table=get_packages_table_text(packages)
    return get_html("index").replace("$$MEMBERS$$", members_table).replace("$$PACKAGES$$",packages_table)


"""
this route responsible for viewing all the details of the member in his profile page
so it will render the profile page with all member's data (info, vital info, sunscription info, workout info)
"""
@app.route("/member_profile")
def member_profile():
    id = flask.request.args.get("id")
#this will get main info of the member
    member_data=search_by_id(id)[0]
    
#this section will get Vitaldetails of the member
    member_vital_data=get_vital_info(id)
    

#if the member already exist and has vital data then get his subscription data if he has previous one
#then pass all of them to the template of member profile
    if member_vital_data and member_data is not None:
        member = Member(member_data[1],(member_data[2]),int(member_data[3]),int(member_data[4])
            ,member_data[5],member_data[6],member_data[7],int(member_data[0]),
        )

        vitaDetails = VitaDetails(member_vital_data[1],member_vital_data[2],member_vital_data[3],member_vital_data[4],
                                  member_vital_data[5],int(member_data[0])
        )
#get all packages data for the trainer if he want to subscribe or resubscripe for the memebr in package
        packages=get_all_packages_data()

#this line to get workout info and nutrition plan for the member
        workout_file_content,nutrition_file_content=get_workout_nutrition(id)
        
        subscription=member.get_subscription()
        if subscription:
            subscription_data = {'name':subscription[0],'startDate': subscription[1] ,'endDate':subscription[2]}
        else:
            subscription_data = {'name':'Subscribe first','startDate': '' ,'endDate':''}
        return render_template("member_profile.html", member=member, vitaDetails=vitaDetails, packages=packages, subscription_data=subscription_data,workout_file_content=workout_file_content,nutrition_file_content=nutrition_file_content)
#this condition will be valid if the member already exist but does not has vital data   
    elif member_data is not None:
        return flask.redirect("/newVital?id="+str(id))
    else:
        return flask.redirect("/home"+str(id))

#this route send the new package page
@app.route ("/newpacakge") 
def newpackage():
    return get_html("add_package")

#this route recieve the new package data and create instance of it's class then add to database
@app.route ("/addnewpackage") 
def addnewpackage():
    name= flask.request.args.get("name")
    value= flask.request.args.get("value")
    duration= flask.request.args.get("duration")

    package=Package(name, value,duration)
    package.add_to_DB()
    return flask.redirect("/home")



# New route to handle subscription form submission
@app.route("/subscribe", methods=["POST"])
def subscribe():
    package_id = flask.request.form.get("package_id")
    member_id = flask.request.form.get("member_id")
   
    flag,remaining_months,remaining_days=subscribe_to_package(package_id,member_id)
    if not flag:
        return flask.redirect("/member_profile?id="+str(member_id)+"&remaining_months="+str(remaining_months)+"&remaining_days="+str(remaining_days))
    else:
        return flask.redirect("/member_profile?id="+str(member_id))
    
# New route to handle subscription form submission
@app.route("/resubscribe", methods=["POST"])
def resubscribe():
    package_id = flask.request.form.get("package_id")
    member_id = flask.request.form.get("member_id")
   
    re_subscribe_to_package(package_id,member_id)
    return flask.redirect("/member_profile?id="+str(member_id))
    
# this route to handle add workout to member
@app.route("/add_workout", methods=["POST"])
def add_workout():
    # Get member_id from the form data
    member_id = flask.request.form.get("member_id")

    # Create a directory if it doesn't exist for the member
    member_directory = f"members/{member_id}"
    os.makedirs(member_directory, exist_ok=True)

    # Create a single file for all workout data
    file_path = os.path.join(member_directory, "workout_summary.txt")
    
    with open(file_path, 'w') as workout_file:
        workout_file.write(f"Member ID: {member_id}\n\n")
        for day in range(1, 6):
            #check if there is at least one exercise existed for each day
            if flask.request.form.get(f"exercise_day{day}_{1}"): 
                workout_file.write(f"{'Day':<4}{day:<10}\n{'Exercise:':<40}{'Sets:':<20}{'Reps:':<20}{'Video Link:':<40}")
                for j in range(1, 4):
                    # Get exercise, sets, reps, and video_link for each day and exercise
                    exercise = flask.request.form.get(f"exercise_day{day}_{j}")
                    sets = flask.request.form.get(f"sets_day{day}_{j}")
                    reps = flask.request.form.get(f"reps_day{day}_{j}")
                    video_link = flask.request.form.get(f"video_link_day{day}_{j}")
                    workout_file.write(f"\n{exercise:<40}{sets:<20}{reps:<20}{video_link:<40}")
                workout_file.write("\n\n\n")   
            
                
    # Redirect to the member profile or another destination after subscription
    return flask.redirect(f"/member_profile?id=" + str(member_id))


# this route to handle add nutrition_plan to member
@app.route("/add_nutrition_plan", methods=["POST"])
def add_nutrition_plan():
    # Get member_id from the form data
    member_id = flask.request.form.get("member_id")

    # Create a directory if it doesn't exist for the member
    member_directory = f"members/{member_id}"
    os.makedirs(member_directory, exist_ok=True)

    # Create a single file for all workout data
    file_path = os.path.join(member_directory, "nutrition_plan.txt")
    
    with open(file_path, 'w') as nutrition_plan_file:
        nutrition_plan_file.write(f"Member ID: {member_id}\n\n")
        for day in range(1, 6):
            #check if there is at least one exercise existed for each day
            if flask.request.form.get(f"meal{day}_{1}"): 
                nutrition_plan_file.write(f"{'Day':<4}{day:<10}\n{'Meal:':<40}{'Quantity:':<20}")
                for j in range(1, 4):
                    # Get exercise, sets, reps, and video_link for each day and exercise
                    meal = flask.request.form.get(f"meal{day}_{j}")
                    quantity = flask.request.form.get(f"quantity{day}_{j}")
                    nutrition_plan_file.write(f"\n{meal:<40}{quantity:<20}")
                nutrition_plan_file.write("\n\n\n")  
            
                
    # Redirect to the member profile or another destination after subscription
    return flask.redirect(f"/member_profile?id=" + str(member_id))
