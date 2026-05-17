
import click
from api.models import db, User

"""
In this file, you can add as many commands as you want using the @app.cli.command decorator
Flask commands are usefull to run cronjobs or tasks outside of the API but sill in integration 
with youy database, for example: Import the price of bitcoin every night as 12am
"""
def setup_commands(app):
    
    """ 
    This is an example command "insert-test-users" that you can run from the command line
    by typing: $ flask insert-test-users 5
    Note: 5 is the number of users to add
    """
    @app.cli.command("insert-test-users") # name of our command
    @click.argument("count") # argument of out command
    def insert_test_users(count):
        print("Creating test users")
        for x in range(1, int(count) + 1):
            user = User()
            user.email = "test_user" + str(x) + "@test.com"
            user.password = "123456"
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            print("User: ", user.email, " created.")

        print("All test users created")

    @app.cli.command("insert-test-data")
    def insert_test_data():
        from datetime import date
        from extensions import bcrypt
        from api.models import Game, GameTier, User, Profile, UserGameList

        games_data = [
            {
                "title": "The Legend of Zelda: Breath of the Wild",
                "description": "Explora el vasto reino de Hyrule en una aventura épica. Despierta de un sueño de cien años para derrotar a Calamity Ganon y salvar el reino. Con mecánicas de exploración, combate y resolución de puzzles que redefinieron el género de mundo abierto.",
                "release_date": date(2017, 3, 3),
                "developer": "Nintendo EPD",
                "publisher": "Nintendo",
                "cover_img_url": "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=400",
                "genres": ["Acción", "Aventura", "Mundo Abierto"],
                "platforms": ["Nintendo Switch", "Wii U"]
            },
            {
                "title": "Elden Ring",
                "description": "Álzate, Sinluz, y adéntrate en las Tierras Intermedias. Un vasto mundo abierto con una narrativa profunda creada por Hidetaka Miyazaki y George R.R. Martin. Combate desafiante, magia y exploración en un mundo de fantasía oscura.",
                "release_date": date(2022, 2, 25),
                "developer": "FromSoftware",
                "publisher": "Bandai Namco",
                "cover_img_url": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=400",
                "genres": ["RPG", "Acción", "Fantasía Oscura"],
                "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X|S"]
            },
            {
                "title": "God of War Ragnarök",
                "description": "Kratos y Atreus se embarcan en un viaje épico a través de los nueve reinos nórdicos. Enfrenta a dioses y monstruos mientras te preparas para la batalla profetizada del Ragnarök. Una historia emocional con combate visceral y puzzles ingeniosos.",
                "release_date": date(2022, 11, 9),
                "developer": "Santa Monica Studio",
                "publisher": "Sony Interactive Entertainment",
                "cover_img_url": "https://images.unsplash.com/photo-1552820728-8b83bb6b2f2f?w=400",
                "genres": ["Acción", "Aventura", "Hack and Slash"],
                "platforms": ["PlayStation 4", "PlayStation 5", "PC"]
            },
            {
                "title": "Red Dead Redemption 2",
                "description": "Vive la historia de Arthur Morgan y la banda Van der Linde en los últimos días del Salvaje Oeste. Un mundo abierto masivo con una narrativa cautivadora, caza, pesca, y decisiones que afectan tu honor y el destino de la banda.",
                "release_date": date(2018, 10, 26),
                "developer": "Rockstar Studios",
                "publisher": "Rockstar Games",
                "cover_img_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400",
                "genres": ["Acción", "Aventura", "Mundo Abierto"],
                "platforms": ["PC", "PlayStation 4", "Xbox One"]
            },
            {
                "title": "The Witcher 3: Wild Hunt",
                "description": "Conviértete en Geralt de Rivia, cazador de monstruos profesional, en un mundo de fantasía moralmente ambiguo. Una narrativa ramificada, misiones secundarias profundas y un mundo abierto masivo que estableció el estándar de los RPG modernos.",
                "release_date": date(2015, 5, 19),
                "developer": "CD Projekt Red",
                "publisher": "CD Projekt",
                "cover_img_url": "https://images.unsplash.com/photo-1643134902338-3c7850e27799?w=400",
                "genres": ["RPG", "Fantasía", "Mundo Abierto"],
                "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X|S", "Nintendo Switch"]
            },
            {
                "title": "Cyberpunk 2077",
                "description": "Sumérgete en Night City, un futuro distópico donde la tecnología y la humanidad colisionan. Personaliza a tu personaje, elige tu camino y descubre los secretos de un implante robado que podría darte la clave de la inmortalidad.",
                "release_date": date(2020, 12, 10),
                "developer": "CD Projekt Red",
                "publisher": "CD Projekt",
                "cover_img_url": "https://images.unsplash.com/photo-1614728263952-84ea256f9679?w=400",
                "genres": ["RPG", "Acción", "Ciencia Ficción"],
                "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X|S"]
            },
            {
                "title": "Minecraft",
                "description": "El fenómeno sandbox que revolucionó la industria. Construye, explora, sobrevive y crea en un mundo infinito de bloques. Desde enormes castillos hasta circuitos de redstone, las únicas limitaciones son tu imaginación y creatividad.",
                "release_date": date(2011, 11, 18),
                "developer": "Mojang",
                "publisher": "Mojang",
                "cover_img_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400",
                "genres": ["Sandbox", "Supervivencia", "Aventura"],
                "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X|S", "Nintendo Switch", "iOS", "Android"]
            },
            {
                "title": "Hollow Knight",
                "description": "Adéntrate en las profundidades de Hallownest, un reino de insectos en ruinas. Un metroidvania bellamente dibujado a mano con combate preciso, exploración no lineal y una atmósfera melancólica que te atrapará desde el primer momento.",
                "release_date": date(2017, 2, 24),
                "developer": "Team Cherry",
                "publisher": "Team Cherry",
                "cover_img_url": "https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=400",
                "genres": ["Metroidvania", "Acción", "Plataformas"],
                "platforms": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]
            },
        ]

        print("🗑️  Limpiando datos existentes...")
        db.session.execute(db.text("DELETE FROM user_glg"))
        db.session.execute(db.text("DELETE FROM user_game_list"))
        db.session.execute(db.text("DELETE FROM user_game_tier"))
        db.session.execute(db.text("DELETE FROM game_tier"))
        db.session.execute(db.text("DELETE FROM user_survey"))
        db.session.execute(db.text("DELETE FROM comment"))
        db.session.execute(db.text("DELETE FROM add_game"))
        db.session.execute(db.text("DELETE FROM ban"))
        db.session.execute(db.text("DELETE FROM profile"))
        db.session.execute(db.text("DELETE FROM game"))
        db.session.execute(db.text("DELETE FROM \"user\""))
        db.session.commit()

        print("🎮 Creando juegos...")
        for g in games_data:
            game = Game(
                title=g["title"],
                description=g["description"],
                release_date=g["release_date"],
                developer=g["developer"],
                publisher=g["publisher"],
                cover_img_url=g["cover_img_url"],
                genres=g["genres"],
                platforms=g["platforms"]
            )
            db.session.add(game)
            db.session.flush()
            tier = GameTier(game_id=game.id)
            db.session.add(tier)
            print(f"  ✅ {game.title}")

        print("👤 Creando usuario de prueba...")
        from extensions import bcrypt
        password_hash = bcrypt.generate_password_hash("123456").decode('utf-8')
        user = User(
            username="testuser",
            email="test@game-side.com",
            password_hash=password_hash,
            is_active=True,
            is_admin=True
        )
        db.session.add(user)
        db.session.flush()

        profile = Profile(
            user_id=user.id,
            description="Usuario de prueba para Game-Side",
        )
        db.session.add(profile)
        db.session.flush()

        ugl = UserGameList(user_id=user.id)
        db.session.add(ugl)

        db.session.commit()
        print("✅ Seed data completa!")
        print(f"   🎮 {len(games_data)} juegos creados")
        print(f"   👤 Usuario: test@game-side.com / 123456")