from api.routes import api


#CRUD ban y addgame(aceptar o rechazar)

@api.route("/admins") 
def get_admin () :

    return "lista de games"
