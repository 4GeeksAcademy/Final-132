from api.routes import api


#CRUD users y profile, user survey, addgame(crear)

@api.route("/users") 
def get_users () :

    return "lista de users"
