from graphql_meta import GraphQLMetaData

gq_meta = GraphQLMetaData()

gq_meta.fill_from_url("https://api.sorare.com/federation/graphql")

query = gq_meta.get_query_schema()