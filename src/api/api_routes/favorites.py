from api.routes import api


#CRUD favorite

@api.route("/favorites") 
def get_favorites () :

    return "lista de games"
