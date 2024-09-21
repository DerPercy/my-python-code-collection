import requests
import json


body = {
    "operationName":"IntrospectionQuery",
    "variables":{},
    "query":"query IntrospectionQuery {\n  __schema {\n    queryType {\n      name\n      __typename\n    }\n    mutationType {\n      name\n      __typename\n    }\n    subscriptionType {\n      name\n      __typename\n    }\n    types {\n      ...FullType\n      __typename\n    }\n    directives {\n      name\n      description\n      locations\n      args {\n        ...InputValue\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment FullType on __Type {\n  kind\n  name\n  description\n  fields(includeDeprecated: true) {\n    name\n    description\n    args {\n      ...InputValue\n      __typename\n    }\n    type {\n      ...TypeRef\n      __typename\n    }\n    isDeprecated\n    deprecationReason\n    __typename\n  }\n  inputFields {\n    ...InputValue\n    __typename\n  }\n  interfaces {\n    ...TypeRef\n    __typename\n  }\n  enumValues(includeDeprecated: true) {\n    name\n    description\n    isDeprecated\n    deprecationReason\n    __typename\n  }\n  possibleTypes {\n    ...TypeRef\n    __typename\n  }\n  __typename\n}\n\nfragment InputValue on __InputValue {\n  name\n  description\n  type {\n    ...TypeRef\n    __typename\n  }\n  defaultValue\n  __typename\n}\n\nfragment TypeRef on __Type {\n  kind\n  name\n  ofType {\n    kind\n    name\n    ofType {\n      kind\n      name\n      ofType {\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {\n            kind\n            name\n            ofType {\n              kind\n              name\n              ofType {\n                kind\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}


resp = requests.post("https://api.sorare.com/federation/graphql",json=body)

print(resp.status_code)
print(resp.json())

with open('schema.json', 'w') as f:
    json.dump(resp.json(), f, indent=2)