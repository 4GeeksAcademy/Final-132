from api.routes import api


#CRUD(create,read one,read all,update,delete) commets

@api.route("/comments") 
def get_comments () :

    return "lista de games"
