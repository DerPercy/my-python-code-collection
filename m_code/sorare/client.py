import requests
import json
import bcrypt
import time
import logging
from socket import error as SocketError
import errno

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
                    jwtToken(aud: "myPrivateApp") { 
                            token expiredAt 
                        } 
                    currentUser { 
                        slug 
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
        print(r.text)
        jwtData = json.loads(r.text)
        self.jwt = jwtData["data"]["signIn"]["jwtToken"]["token"]
        #print(self.jwt)
        pass

    def request(self,body:str, variables = {},options = {}):
        int_result = self.__request(body,variables,options)
        result = int_result.get("result")
        
        # pagination
        if options.get("pagination") != None:
            p_options = options.get("pagination")
            if p_options.get("resultFilter",None) != None:
                result = list(filter(p_options.get("resultFilter"), result))

            while len(result) < p_options.get("targetNumber",0) or p_options.get("resultFilter",None) != None:
                cursor = json_selector(int_result.get("full_result"),p_options.get("cursorSelector"))
                #print(cursor)
                variables[p_options.get("paginationVariable")] = cursor
                int_result = self.__request(body,variables,options)
                sub_result = int_result.get("result")

                if p_options.get("resultFilter",None) != None:
                    sub_result = list(filter(p_options.get("resultFilter"), sub_result))

                if len( sub_result) == 0:
                    #print("No furter results")
                    break
                result.extend(sub_result)
                print(str(len(result)),end='\r')
                if cursor == "" or cursor == None:
                    logging.info("No end Cursor: exit")
                    break
        #print(json.dumps(r.json(),indent=2))
        return result

    def __request(self,body:str, variables = {},options = {}, num_retries:int = 3):
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
        try:
            r = requests.post("https://api.sorare.com/graphql", json=payloadJSON, headers=headers)
        except SocketError as e:
            logging.error("SocketError occured "+str(e.errno))
            logging.info(e)
            time.sleep(300)
            return self.__request(body,variables,options)
            #if e.errno != errno.ECONNRESET:
            #    raise # Not error we are looking for

        if r.status_code == 429:
            to_wait = int(r.headers.get("Retry-After",30))
            logging.info("Rate limit ("+str(to_wait)+")" )
            time.sleep(to_wait)
            return self.__request(body,variables,options)
        
        elif r.status_code != 200:
            logging.warn(r.status_code)
            logging.warn("Invalid status code")
            if num_retries > 0:
                logging.warn("Waiting 30 seconds and retry")
                time.sleep(30)
                return self.__request(body,variables,options, (num_retries - 1))
            

        try:
            result = r.json()
            #print(result)
        except Exception as error:
            logging.error("Could not render response to json")
            logging.error(r.content)
            raise error

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