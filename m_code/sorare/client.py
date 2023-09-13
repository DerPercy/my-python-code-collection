import requests
import json
import bcrypt


class Client:

    
    def __init__(self, options=None):

        email = options.get("email")
        password = options.get("password")
        r_salt = requests.get("https://api.sorare.com/api/v1/users/"+email)
        salt = json.loads(r_salt.text).get("salt")
        #print(salt)

        hashpw = bcrypt.hashpw(password.encode(), salt.encode())
    

        query = """
            mutation SignInMutation($input: signInInput!) { 
                signIn(input: $input) { 
                    currentUser { 
                        slug jwtToken(aud: "myPrivateApp") { 
                            token expiredAt 
                        } 
                    } errors { 
                        message 
                    } 
                } 
            }
        """
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        payloadJSON = {
			"query": query,
			"variables": {
                "input": {
                    "email": email,
                    "password": hashpw.decode()
                }
            }
		}

        
        r = requests.post("https://api.sorare.com/graphql", json=payloadJSON, headers=headers)
        #print(r.text)
        jwtData = json.loads(r.text)
        self.jwt = jwtData["data"]["signIn"]["currentUser"]["jwtToken"]["token"]
        print(self.jwt)
        pass

    def request(self,body:str):
        headers = {
            'content-type': 'application/json', 
            'Accept-Charset': 'UTF-8',
            'Authorization': 'Bearer '+ self.jwt,
            'JWT-AUD': 'myPrivateApp'
        }
        payloadJSON = {
			"query": body,
			"variables": {}
		}
        r = requests.post("https://api.sorare.com/graphql", json=payloadJSON, headers=headers)
        print(json.dumps(r.json(),indent=2))
        pass