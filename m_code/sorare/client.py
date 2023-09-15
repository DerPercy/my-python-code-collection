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

    def request(self,body:str, variables = {},options = {}):
        int_result = self.__request(body,variables,options)
        result = int_result.get("result")
        
        # pagination
        if options.get("pagination") != None:
            p_options = options.get("pagination")
            while len(result) < p_options.get("targetNumber"):
                cursor = json_selector(int_result.get("full_result"),p_options.get("cursorSelector"))
                #print(cursor)
                variables[p_options.get("paginationVariable")] = cursor
                int_result = self.__request(body,variables,options)
                result.extend(int_result.get("result"))
        #print(json.dumps(r.json(),indent=2))
        return result

    def __request(self,body:str, variables = {},options = {}):
        """ Returns an object with the following keys
        - result: the result
        - full_result: the complete result (in case f.e. options.resultSelector was set)
        """
        headers = {
            'content-type': 'application/json', 
            'Accept-Charset': 'UTF-8',
            'Authorization': 'Bearer '+ self.jwt,
            'JWT-AUD': 'myPrivateApp'
        }
        payloadJSON = {
			"query": body,
			"variables": variables
		}
        r = requests.post("https://api.sorare.com/graphql", json=payloadJSON, headers=headers)
        print(r.status_code)

        result = r.json()
        

        # preselect result
        if options.get("resultSelector") != None:
            result = json_selector(result,options.get("resultSelector"))
        return {
            "result": result,
            "full_result": r.json()
        }
            

def json_selector(json_obj, selector_array):
    for selector in selector_array:
        #print(selector)
        json_obj = json_obj.get(selector)
    return json_obj