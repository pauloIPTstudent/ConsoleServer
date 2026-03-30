from flask import render_template, request, redirect, url_for, jsonify

import os
from db.tables import app, db, Game, GameTag
from db.tables import KeyMapping, ControllerButton

@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        # Capturando o novo campo img_url
        Game.add_game(
            title=request.form['title'],
            url=request.form['url'],
            img=request.form['img_url'], # Novo
            tag=GameTag[request.form['tag']],
            author=request.form['author'],
            institution=request.form['institution'],
            size=request.form['size'],
            rating=int(request.form['rating']),
            description=request.form['description']
        )
        return redirect(url_for('index'))
    
    return render_template('add.html', tags=GameTag)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_game(id):
    game = Game.query.get_or_404(id)
    if request.method == 'POST':
        game.title = request.form['title']
        game.url = request.form['url']
        game.img_url = request.form['img_url'] # Novo
        game.tag = GameTag[request.form['tag']]
        game.author_name = request.form['author']
        game.institution_name = request.form['institution']
        game.size = request.form['size']
        game.rating = int(request.form['rating'])
        game.description = request.form['description']
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit.html', game=game, tags=GameTag)

@app.route('/game_all/', methods=['GET'])
def get_all_games():
    games = Game.query.all()
    
    # Criamos uma lista de dicionários
    output = []
    for game in games:
        game_data = {
            "id": game.id,
            "title": game.title,
            "url": game.url,
            "img_url": game.img_url,
            "tag": game.tag.value,
            "author": game.author_name,
            "institution": game.institution_name,
            "size": game.size,
            "rating": game.rating,
            "description": game.description
        }
        output.append(game_data)
        
    return jsonify(output)

@app.route('/game/<int:id>', methods=['GET'])
def get_game_by_id(id):
    game = Game.query.get_or_404(id)
    
    # Transformando o objeto do banco em um dicionário/JSON
    return jsonify({
        "id": game.id,
        "title": game.title,
        "url": game.url,
        "img_url": game.img_url,
        "tag": game.tag.value,  # Retorna o nome amigável (ex: "Aventura")
        "author": game.author_name,
        "institution": game.institution_name,
        "size": game.size,
        "rating": game.rating,
        "description": game.description
    })

# Rota para listar e adicionar mapeamentos de um jogo específico
@app.route('/game/<int:game_id>/mappings', methods=['GET', 'POST'])
def game_mappings(game_id):
    game = Game.query.get_or_404(game_id)
    
    if request.method == 'POST':
        new_mapping = KeyMapping(
            game_id=game.id,
            player_index=int(request.form['player_index']),
            button=ControllerButton[request.form['button']],
            key=request.form['key'],
            description=request.form['description']
        )
        db.session.add(new_game_mapping) # Correção: use o objeto criado
        db.session.add(new_mapping)
        db.session.commit()
        return redirect(url_for('game_mappings', game_id=game.id))

    # Busca os mapeamentos existentes ordenados por jogador
    mappings = KeyMapping.query.filter_by(game_id=game_id).order_by(KeyMapping.player_index).all()
    return render_template('mappings.html', game=game, mappings=mappings, buttons=ControllerButton)

# Rota para deletar um mapeamento (útil para correções)
@app.route('/mapping/delete/<int:id>')
def delete_mapping(id):
    mapping = KeyMapping.query.get_or_404(id)
    game_id = mapping.game_id
    db.session.delete(mapping)
    db.session.commit()
    return redirect(url_for('game_mappings', game_id=game_id))


if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host='0.0.0.0', port=port)