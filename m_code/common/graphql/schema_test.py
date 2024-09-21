import schema
import requests
import json
import bcrypt

#nodes = schema.Query().football().allCards().nodes()
#nodes.slug()
#nodes.age()
#nodes.allSo5Scores().nodes().anyPlayer()

# Define payload

hashpw = bcrypt.hashpw("dummy".encode(), "$2a$11$qOjOV6OV1b.sKajI2C3oT.".encode())

mutation = schema.Mutation()
signIn = mutation.signIn(input=schema.signInInput(email="my@mail.de", password=hashpw.decode()))
token = signIn.jwtToken(aud="myPrivateApp")
token.token()
token.expiredAt()
signIn.currentUser().slug()
signIn.errors(_param_name="my_errors").message()
signIn.errors().message()

#schema.Query().football().rivals().pastSeasons(after=None,before=None,first=50,last=None).nodes().slug()
#schema.Query().value_football.value_rivals.value_pastSeasons.value_nodes[0].value_slug
req =  signIn._create_query_code()
print(req)

#schema.Query().football().rivals().upcomingGames()
# Request
query = "mutation SignInMutation { "+req+" }"
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payloadJSON = {
	"query": query
}
r = requests.post("https://api.sorare.com/graphql", json=payloadJSON, headers=headers)
print(json.loads(r.text))

mutation._fill_response(json.loads(r.text)["data"])

#print(mutation.value_signIn.value_errors[0].value_message)
print(mutation.value_signIn.value_my_errors[0].value_message)
print(mutation.value_signIn.value_errors[0].value_message)
#
#print(signIn)
        

 #query = """
 #           mutation SignInMutation($input: signInInput!) { 
 #               signIn(input: $input) { 
 #                   jwtToken(aud: "myPrivateApp") { 
 #                           token expiredAt 
 #                       } 
 #                   currentUser { 
 #                       slug 
 #                   } errors { 
 #                       message 
 #                   } 
 #               } 
 #           }
 #       """
 #       headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
 #       payloadJSON = {
#			"query": query,
#			"variables": {
 #               "input": {
 #                   "email": email,
 #                   "password": hashpw.decode()
 #               }
 #           }
#		}

# Get Data
