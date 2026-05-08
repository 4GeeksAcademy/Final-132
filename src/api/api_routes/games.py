from api.routes import api


#CRUD games y game tier, users game tier , user game list

@api.route("/games") 
def get_games () :

    return "lista de games"
