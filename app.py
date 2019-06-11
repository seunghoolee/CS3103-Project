#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import Resource, Api, reqparse
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql.cursors
import json

import cgitb
import cgi
import sys
cgitb.enable()

import settings # Our server and db settings, stored in settings.py

app = Flask(__name__, static_url_path='/static')
api = Api(app)

#####################################################################################
#Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

####################################################################################
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { "status": "Resource not found" } ), 404)

####################################################################################
# Static Endpoints for humans

class Root(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('index.html')

api.add_resource(Root,'/')

class Developer(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('developer.html')

api.add_resource(Developer,'/dev')
####################################################################################
#
# Routing: GET POST and DELETE for Flask-Session
#
class SignIn(Resource):
	#
	# Login, start a session and set/return a session cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Casper", "password": "cr*ap"}' -b cookie-jar http://info3103.cs.unb.ca:51327/signin
	#
	def post(self):
		if not request.json:
			abort(400) # bad request
		# Parse the json
		parser = reqparse.RequestParser()
		try:
			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request

		# Already logged in
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
			except (LDAPException, error_message):
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

			try:
				dbConnection = pymysql.connect(settings.DBHOST,
					settings.DBUSER,
					settings.DBPASSWD,
					settings.DBDATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)

				#checks if the user is there
				sql = 'checkIfUserIsThere'
				cursor = dbConnection.cursor()
				sqlArgs = (session['username'],) # Must be a collection
				cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
				row = cursor.fetchone()

				#Gets the user ID of the signing in user
				sql = 'getOneUser'
				cursor = dbConnection.cursor()
				sqlArgs = (session['username'],) # Must be a collection
				cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
				userid = cursor.fetchone()

				response = {'status': 'success', 'userid': userid}
				responseCode = 201
				#if they're not there, adds a new user
				if row is None:
					sql = 'addUser'
					cursor = dbConnection.cursor()
					sqlArgs = (session['username'],)
					cursor.callproc(sql,sqlArgs)
				dbConnection.commit() # database was modified, commit the changes
			except:
				abort(500)

		return make_response(jsonify(response), responseCode)

	# GET: Check for a login
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:51327/signin
	def get(self):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(settings.DBHOST,
					settings.DBUSER,
					settings.DBPASSWD,
					settings.DBDATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)

				#checks if the user is there
				sql = 'getOneUser'
				cursor = dbConnection.cursor()
				sqlArgs = (session['username'],) # Must be a collection
				cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
				userid = cursor.fetchone()

			except:
				abort(500)
			finally:
				dbConnection.commit() # database was modified, commit the changes

			response = {'status': 'success', 'userid': userid, 'username': session['username']}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

	# DELETE: Logout: remove session
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar http://info3103.cs.unb.ca:51327/signin
	def delete(self):
		if 'username' in session:
			session.clear()
			response = {'status': 'Success' }
			responseCode = 200
		else:
			response = {'status': 'Failure' }
			responseCode = 403

		return make_response(jsonify(response), responseCode)
####################################################################################
# GET ALL USERS
class Users(Resource):
    # GET: Return all users that are in the SQL
	# Example request: curl http://info3103.cs.unb.ca:51327/users
	def get(self):
		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUsers'
			cursor = dbConnection.cursor()
			cursor.callproc(sql) # stored procedure, no arguments
			rows = cursor.fetchall() # get all the results
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'users': rows}), 200) # turn set into json and return it

	def post(self):
        # curl -i -X POST -H "Content-Type: application/json" -d '{"userName":"Your dad"}' http://info3103.cs.unb.ca:51327/users
		if not request.json or not 'userName' in request.json:
			abort(400) # bad request

		if 'username' not in session:
			abort(403) #Checks for signed in

		name = request.json['userName'];

		try:
			dbConnection = pymysql.connect(settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addUser'
			cursor = dbConnection.cursor()
			sqlArgs = (name,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
		uri = uri+str(request.url_rule)
		return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation

#######################################################################################################
#GETS A SPECIFIC USER
class User(Resource):

    # GET: Will get user that belongs to a certain userID
	# Example request: curl http://info3103.cs.unb.ca:51327/users/1
	def get(self, userID):
		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByID'
			cursor = dbConnection.cursor()
			sqlArgs = (userID,) #, shows part of a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"User Information": row}), 200) #successful
	# Deleting a user / The below curl command would delete Fred
	# curl -X DELETE http://info3103.cs.unb.ca:51327/users/1
	def delete(self, userID):

		if 'username' not in session:
			abort(403) #Checks for signed in

		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'dropUser'
			cursor = dbConnection.cursor()
			sqlArgs = (userID,) #, shows part of a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
		uri = uri+str(request.url_rule)
		return make_response(jsonify( { "uri" : uri } ), 204)

####################################################################################

class toDoList(Resource):
    # GET: Get to See ALL the lists
	# Example request: curl http://info3103.cs.unb.ca:51327/users/toDoList
	def get(self):
		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getToDoItem'
			cursor = dbConnection.cursor()

			cursor.callproc(sql) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"ToDoListsofAllUsers": row}), 200) #successful

####################################################################################

class userList(Resource):
    # GET: Get to See ALL the lists
	# Example request: curl http://info3103.cs.unb.ca:51327/users/3/toDoList
	def get(self, userID):
		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getSpecificItem'
			cursor = dbConnection.cursor()
			sqlArgs = (userID, ) #, shows part of a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify({"ToDoListsofOneUsers": row}), 200) #successful

#######################################################################################
class Item(Resource):

    # GET: Will get user that belongs to a certain userID
	# Example request: curl http://info3103.cs.unb.ca:51327/users/1/toDoList/1
	def get(self, userID, toDoListID):
		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getSpecificItemFromUser'
			cursor = dbConnection.cursor()
			sqlArgs = (toDoListID, userID,) #, shows part of a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"User's specific Item": row}), 200) #successful

	def post(self, userID, toDoListID):
        # curl -i -X POST -H "Content-Type: application/json" -d '{"toDoItem":"Pay taxes"}' http://info3103.cs.unb.ca:51327/users/1/toDoList/69
		if not request.json:
			abort(400) # bad request

		if 'username' not in session:
			abort(403) #Checks for signed in


		# Parse the json
		parser = reqparse.RequestParser()
		try:
			# Check for required attributes in json document, create a dictionary
			parser.add_argument('toDoItem', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(407) # bad request

		toDoItem = request_params['toDoItem']
		print(toDoItem)

		try:
			dbConnection = pymysql.connect(settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addStuffToDo'
			cursor = dbConnection.cursor()
			sqlArgs = (toDoItem, userID,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()

		uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
		uri = uri+str(request.url_rule)+'/'#+str(row[userID])
		return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation

	#curl -X DELETE http://info3103.cs.unb.ca:51327/users/4/toDoList/10
	def delete(self, userID, toDoListID):

		if 'username' not in session:
			abort(403) #Checks for signed in

		try:
			dbConnection = pymysql.connect(
				settings.DBHOST,
				settings.DBUSER,
				settings.DBPASSWD,
				settings.DBDATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'dropStuffToDo'
			cursor = dbConnection.cursor()
			sqlArgs = (toDoListID,userID) #, shows part of a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
			row = cursor.fetchone()  # get the single result
			#if row is None:
			#	abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
		#uri = uri+str(request.url_rule)+'/'+str(row['LAST_INSERT_ID()'])
		return make_response(jsonify( { "uri" : row } ), 204) #successful delete

#######################################################################################
# Endpoints
api = Api(app)
#Users is the class name /
api.add_resource(Users, '/users') #/user ->should be able to see all users
api.add_resource(User, '/users/<int:userID>') #/users/1 -> should be able to see user1
api.add_resource(toDoList, '/users/toDoList') #/users/Lists -> should sees everyone's lists
api.add_resource(userList, '/users/<int:userID>/toDoList') #/users/3/Lists -> should sees user 3's list only
api.add_resource(Item, '/users/<int:userID>/toDoList/<int:toDoListID>')
#Enpoint for logging in
api.add_resource(SignIn, '/signin')

#############################################################################
if __name__ == "__main__":
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
