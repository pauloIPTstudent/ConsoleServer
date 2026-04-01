from flask import Flask
import enum
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. Enumeração para as Tags de Estilo
class GameTag(enum.Enum):
    ARCADE = "Arcade"
    PUZZLE = "Puzzle"
    ADVENTURE = "Aventura"
    ACTION = "Ação"
    STRATEGY = "Estratégia"

# 2. Modelo da Tabela de Jogos
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    # Tamanho em MB ou KB (ex: "45.2 MB")
    size = db.Column(db.String(50), nullable=True) 
    
    # Armazena o valor da Enum como String no banco
    tag = db.Column(db.Enum(GameTag), nullable=False, default=GameTag.ARCADE)
    
    author_name = db.Column(db.String(100), nullable=False)
    institution_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Avaliação estática de 0 a 5
    rating = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Game {self.title}>'

    @staticmethod
    def add_game(title, url, tag, author, description, size=None, institution=None, rating=0,img=""):
        """Método auxiliar para adicionar um novo jogo"""
        # Garante que o rating não passe do limite de 0-5
        safe_rating = max(0, min(5, rating))
        
        new_game = Game(
            title=title,
            url=url,
            img_url=img,
            tag=tag,
            size=size,
            author_name=author,
            institution_name=institution,
            description=description,
            rating=safe_rating
        )
        db.session.add(new_game)
        db.session.commit()
        return new_game
    
class ControllerButton(enum.Enum):
    UP = "ArrowUp"
    DOWN = "ArrowDown"
    LEFT = "ArrowLeft"
    RIGHT = "ArrowRight"
    A = "A"
    B = "B"
    X = "X"
    Y = "Y"

class KeyMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciona com o jogo
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    # Identifica se é Jogador 1, 2, etc. (0, 1, 2...)
    player_index = db.Column(db.Integer, default=0, nullable=False)
    
    # O botão do controle (Enum)
    button = db.Column(db.Enum(ControllerButton), nullable=False)
    
    # A tecla do computador (ex: "W", "Space", "ArrowUp")
    key = db.Column(db.String(50), nullable=False)
    
    # Descrição da ação (ex: "Pular", "Atirar")
    description = db.Column(db.String(200), nullable=True)

    # Relacionamento para facilitar a busca (Opcional)
    game = db.relationship('Game', backref=db.backref('mappings', lazy=True))

    def __repr__(self):
        return f'<Mapping P{self.player_index+1} {self.button.value} -> {self.key}>'
    
# Criando o banco e as tabelas
with app.app_context():
    db.create_all()