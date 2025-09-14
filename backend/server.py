from flask import Flask, request, render_template, jsonify
from database.mongodb import connect
from pymongo import MongoClient, errors
from bson import ObjectId
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = connect()
db = client['VerticalParts']

# Collections
visitors_collection = db['visitors']
cards_collection = db['cards']
users_collection = db['users']
returns_collection = db['returns']

# Inicializar dados padrão se não existirem
def initialize_default_data():
    # Verificar se já existem usuários
    if users_collection.count_documents({}) == 0:
        default_users = [
            {
                'username': 'admin',
                'email': 'admin@verticalparts.com.br',
                'password': '12345678',  # Em produção, usar hash
                'name': 'Administrador',
                'userType': 'admin',
                'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            {
                'username': 'recepcao',
                'email': 'recepcao@verticalparts.com.br',
                'password': 'recepcao123',
                'name': 'Recepção',
                'userType': 'common',
                'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            {
                'username': 'seguranca',
                'email': 'seguranca@verticalparts.com.br',
                'password': 'seguranca123',
                'name': 'Segurança',
                'userType': 'common',
                'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            {
                'username': 'giovanna',
                'email': 'giovanna@verticalparts.com.br',
                'password': '123456',
                'name': 'Giovanna',
                'userType': 'common',
                'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            {
                'username': 'geovane.silva',
                'email': 'geovane.silva@verticalparts.com.br',
                'password': '123456',
                'name': 'Geovane Silva',
                'userType': 'admin',
                'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        ]
        users_collection.insert_many(default_users)
        print("✅ Usuários padrão criados com sucesso!")

    # Verificar se já existem cartões
    if cards_collection.count_documents({}) == 0:
        default_cards = [
            {'number': 'VISITANTE 001', 'status': 'available', 'visitor': None},
            {'number': 'VISITANTE 002', 'status': 'available', 'visitor': None},
            {'number': 'VISITANTE 003', 'status': 'available', 'visitor': None},
            {'number': 'VISITANTE 004', 'status': 'available', 'visitor': None},
            {'number': 'VISITANTE 005', 'status': 'available', 'visitor': None},
            {'number': 'PRESTADOR DE SERVIÇO 001', 'status': 'available', 'visitor': None},
            {'number': 'PRESTADOR DE SERVIÇO 002', 'status': 'available', 'visitor': None},
            {'number': 'PRESTADOR DE SERVIÇO 003', 'status': 'available', 'visitor': None},
            {'number': 'PROVISÓRIO 001', 'status': 'available', 'visitor': None},
            {'number': 'PROVISÓRIO 002', 'status': 'available', 'visitor': None},
            {'number': 'PROVISÓRIO 003', 'status': 'available', 'visitor': None}
        ]
        cards_collection.insert_many(default_cards)
        print("✅ Cartões padrão criados com sucesso!")

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/login', methods=['POST'])
def login():
    """Rota para autenticar usuário"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'E-mail e senha são obrigatórios'}), 400
        
        # Buscar usuário no banco
        user = users_collection.find_one({'email': email})
        
        if user and user['password'] == password:  # Em produção, usar bcrypt
            # Atualizar último login
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'lastLogin': datetime.now().strftime('%d/%m/%Y %H:%M:%S')}}
            )
            
            # Remover senha do retorno
            user.pop('password', None)
            user['_id'] = str(user['_id'])
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso',
                'user': user
            }), 200
        else:
            return jsonify({'success': False, 'message': 'E-mail ou senha incorretos'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Rota para alterar senha do usuário"""
    try:
        data = request.get_json()
        user_email = data.get('userEmail')
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        changed_by = data.get('changedBy')
        
        if not all([user_email, current_password, new_password, changed_by]):
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Verificar usuário e senha atual
        user = users_collection.find_one({'email': user_email})
        if not user or user['password'] != current_password:
            return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 401
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Atualizar senha
        update_data = {
            'password': new_password,
            'lastPasswordChange': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Adicionar ao histórico
        if 'passwordHistory' not in user:
            user['passwordHistory'] = []
        
        user['passwordHistory'].append({
            'oldPassword': current_password,
            'changedAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'changedBy': changed_by
        })
        update_data['passwordHistory'] = user['passwordHistory']
        
        users_collection.update_one({'email': user_email}, {'$set': update_data})
        
        return jsonify({
            'success': True,
            'message': 'Senha alterada com sucesso',
            'changedAt': update_data['lastPasswordChange']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE VISITANTES ====================

@app.route('/api/visitors', methods=['GET'])
def get_visitors():
    """Obter todos os visitantes"""
    try:
        visitors = list(visitors_collection.find())
        for visitor in visitors:
            visitor['_id'] = str(visitor['_id'])
        
        return jsonify({
            'success': True,
            'visitors': visitors
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/visitors', methods=['POST'])
def create_visitor():
    """Cadastrar novo visitante"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'document', 'phone', 'visitReason', 'visitResponsible']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
        
        visitor_data = {
            'name': data['name'],
            'document': data['document'],
            'phone': data['phone'],
            'visitReason': data['visitReason'],
            'visitResponsible': data['visitResponsible'],
            'observations': data.get('observations', ''),
            'photo': data.get('photo'),
            'entryTime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'status': 'pending',
            'cardNumber': None,
            'registeredBy': data.get('registeredBy', 'Sistema'),
            'createdAt': datetime.now()
        }
        
        result = visitors_collection.insert_one(visitor_data)
        visitor_data['_id'] = str(result.inserted_id)
        visitor_data['id'] = int(datetime.now().timestamp() * 1000)  # Para compatibilidade com frontend
        
        # Atualizar com o ID para compatibilidade
        visitors_collection.update_one(
            {'_id': result.inserted_id},
            {'$set': {'id': visitor_data['id']}}
        )
        
        return jsonify({
            'success': True,
            'message': 'Visitante cadastrado com sucesso',
            'visitor': visitor_data
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/visitors/<visitor_id>', methods=['PUT'])
def update_visitor(visitor_id):
    """Atualizar dados do visitante"""
    try:
        data = request.get_json()
        
        # Buscar visitante
        if ObjectId.is_valid(visitor_id):
            visitor = visitors_collection.find_one({'_id': ObjectId(visitor_id)})
        else:
            visitor = visitors_collection.find_one({'id': int(visitor_id)})
        
        if not visitor:
            return jsonify({'success': False, 'message': 'Visitante não encontrado'}), 404
        
        # Atualizar dados
        update_data = {}
        updatable_fields = ['status', 'cardNumber', 'exitTime', 'cardAssignedAt', 'cardAssignedBy']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            if ObjectId.is_valid(visitor_id):
                visitors_collection.update_one({'_id': ObjectId(visitor_id)}, {'$set': update_data})
            else:
                visitors_collection.update_one({'id': int(visitor_id)}, {'$set': update_data})
        
        return jsonify({
            'success': True,
            'message': 'Visitante atualizado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/visitors/<visitor_id>', methods=['DELETE'])
def delete_visitor(visitor_id):
    """Deletar visitante (apenas admin)"""
    try:
        deleted_by = request.args.get('deletedBy', 'Sistema')
        
        # Buscar visitante
        if ObjectId.is_valid(visitor_id):
            visitor = visitors_collection.find_one({'_id': ObjectId(visitor_id)})
        else:
            visitor = visitors_collection.find_one({'id': int(visitor_id)})
        
        if not visitor:
            return jsonify({'success': False, 'message': 'Visitante não encontrado'}), 404
        
        # Se visitante está ativo, liberar cartão
        if visitor.get('status') == 'active' and visitor.get('cardNumber'):
            cards_collection.update_one(
                {'number': visitor['cardNumber']},
                {'$set': {'status': 'available', 'visitor': None}}
            )
        
        # Registrar no histórico de devoluções para auditoria
        returns_collection.insert_one({
            'visitorName': f"[DELETADO] {visitor['name']}",
            'cardNumber': visitor.get('cardNumber'),
            'phone': visitor.get('phone'),
            'responsible': visitor.get('visitResponsible'),
            'returnTime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'action': 'DELETADO',
            'deletedBy': deleted_by
        })
        
        # Deletar visitante
        if ObjectId.is_valid(visitor_id):
            visitors_collection.delete_one({'_id': ObjectId(visitor_id)})
        else:
            visitors_collection.delete_one({'id': int(visitor_id)})
        
        return jsonify({
            'success': True,
            'message': 'Visitante deletado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE CARTÕES ====================

@app.route('/api/cards', methods=['GET'])
def get_cards():
    """Obter todos os cartões"""
    try:
        cards = list(cards_collection.find())
        for card in cards:
            card['_id'] = str(card['_id'])
        
        return jsonify({
            'success': True,
            'cards': cards
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/cards/assign', methods=['POST'])
def assign_card():
    """Atribuir cartão a visitante"""
    try:
        data = request.get_json()
        visitor_id = data.get('visitorId')
        card_number = data.get('cardNumber')
        assigned_by = data.get('assignedBy')
        
        if not all([visitor_id, card_number, assigned_by]):
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Verificar se cartão está disponível
        card = cards_collection.find_one({'number': card_number, 'status': 'available'})
        if not card:
            return jsonify({'success': False, 'message': 'Cartão não está disponível'}), 400
        
        # Buscar visitante
        if ObjectId.is_valid(visitor_id):
            visitor = visitors_collection.find_one({'_id': ObjectId(visitor_id)})
        else:
            visitor = visitors_collection.find_one({'id': int(visitor_id)})
        
        if not visitor:
            return jsonify({'success': False, 'message': 'Visitante não encontrado'}), 404
        
        # Atribuir cartão
        cards_collection.update_one(
            {'number': card_number},
            {'$set': {'status': 'in-use', 'visitor': visitor['name']}}
        )
        
        # Atualizar visitante
        visitor_update = {
            'cardNumber': card_number,
            'status': 'active',
            'cardAssignedAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'cardAssignedBy': assigned_by
        }
        
        if ObjectId.is_valid(visitor_id):
            visitors_collection.update_one({'_id': ObjectId(visitor_id)}, {'$set': visitor_update})
        else:
            visitors_collection.update_one({'id': int(visitor_id)}, {'$set': visitor_update})
        
        return jsonify({
            'success': True,
            'message': 'Cartão atribuído com sucesso',
            'assignedAt': visitor_update['cardAssignedAt']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/cards/return', methods=['POST'])
def return_card():
    """Devolver cartão"""
    try:
        data = request.get_json()
        search_term = data.get('searchTerm', '').strip()
        
        if not search_term:
            return jsonify({'success': False, 'message': 'Termo de busca é obrigatório'}), 400
        
        # Buscar visitante por nome ou número do cartão
        visitor = visitors_collection.find_one({
            '$and': [
                {'status': 'active'},
                {'$or': [
                    {'name': {'$regex': search_term, '$options': 'i'}},
                    {'cardNumber': search_term}
                ]}
            ]
        })
        
        if not visitor:
            return jsonify({'success': False, 'message': 'Visitante ativo não encontrado'}), 404
        
        # Liberar cartão
        if visitor.get('cardNumber'):
            cards_collection.update_one(
                {'number': visitor['cardNumber']},
                {'$set': {'status': 'available', 'visitor': None}}
            )
        
        # Atualizar visitante
        exit_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        visitors_collection.update_one(
            {'_id': visitor['_id']},
            {'$set': {'status': 'left', 'exitTime': exit_time}}
        )
        
        # Registrar devolução
        returns_collection.insert_one({
            'visitorName': visitor['name'],
            'cardNumber': visitor.get('cardNumber'),
            'phone': visitor.get('phone'),
            'responsible': visitor.get('visitResponsible'),
            'returnTime': exit_time
        })
        
        return jsonify({
            'success': True,
            'message': 'Cartão devolvido com sucesso',
            'visitor': {
                'name': visitor['name'],
                'cardNumber': visitor.get('cardNumber'),
                'exitTime': exit_time
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE USUÁRIOS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Obter todos os usuários (apenas admin)"""
    try:
        users = list(users_collection.find())
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password', None)  # Não retornar senhas
        
        return jsonify({
            'success': True,
            'users': users
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Criar novo usuário (apenas admin)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password', 'userType']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
        
        email = data['email'].lower().strip()
        
        # Verificar se e-mail já existe
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'success': False, 'message': 'E-mail já está cadastrado'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        user_data = {
            'username': email.split('@')[0],
            'email': email,
            'password': data['password'],  # Em produção, usar hash
            'name': data['name'],
            'userType': data['userType'],
            'createdAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'createdBy': data.get('createdBy', 'Sistema')
        }
        
        result = users_collection.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        user_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'message': 'Usuário criado com sucesso',
            'user': user_data
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/users/<user_email>/toggle-type', methods=['PUT'])
def toggle_user_type(user_email):
    """Alternar tipo de usuário (admin/common)"""
    try:
        data = request.get_json()
        changed_by = data.get('changedBy', 'Sistema')
        
        user = users_collection.find_one({'email': user_email})
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        new_type = 'common' if user['userType'] == 'admin' else 'admin'
        
        # Verificar se não é o último admin
        if user['userType'] == 'admin':
            admin_count = users_collection.count_documents({'userType': 'admin'})
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Não é possível remover o último administrador'}), 400
        
        update_data = {
            'userType': new_type,
            'typeChangedAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'typeChangedBy': changed_by
        }
        
        users_collection.update_one({'email': user_email}, {'$set': update_data})
        
        return jsonify({
            'success': True,
            'message': 'Tipo de usuário alterado com sucesso',
            'newType': new_type,
            'changedAt': update_data['typeChangedAt']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/users/<user_email>/reset-password', methods=['PUT'])
def reset_user_password(user_email):
    """Resetar senha de usuário"""
    try:
        data = request.get_json()
        new_password = data.get('newPassword')
        reset_by = data.get('resetBy', 'Sistema')
        
        if not new_password or len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        user = users_collection.find_one({'email': user_email})
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        update_data = {
            'password': new_password,
            'passwordResetAt': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'passwordResetBy': reset_by
        }
        
        users_collection.update_one({'email': user_email}, {'$set': update_data})
        
        return jsonify({
            'success': True,
            'message': 'Senha resetada com sucesso',
            'resetAt': update_data['passwordResetAt']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/users/<user_email>', methods=['DELETE'])
def delete_user(user_email):
    """Deletar usuário"""
    try:
        user = users_collection.find_one({'email': user_email})
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        # Verificar se não é o último admin
        if user['userType'] == 'admin':
            admin_count = users_collection.count_documents({'userType': 'admin'})
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Não é possível deletar o último administrador'}), 400
        
        users_collection.delete_one({'email': user_email})
        
        return jsonify({
            'success': True,
            'message': 'Usuário deletado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE RELATÓRIOS E ESTATÍSTICAS ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas do sistema"""
    try:
        # Estatísticas de visitantes
        total_visitors = visitors_collection.count_documents({})
        active_visitors = visitors_collection.count_documents({'status': 'active'})
        pending_visitors = visitors_collection.count_documents({'status': 'pending'})
        
        # Estatísticas de cartões
        total_cards = cards_collection.count_documents({})
        available_cards = cards_collection.count_documents({'status': 'available'})
        used_cards = cards_collection.count_documents({'status': 'in-use'})
        
        # Estatísticas de usuários
        total_users = users_collection.count_documents({})
        admin_users = users_collection.count_documents({'userType': 'admin'})
        common_users = users_collection.count_documents({'userType': 'common'})
        
        return jsonify({
            'success': True,
            'stats': {
                'visitors': {
                    'total': total_visitors,
                    'active': active_visitors,
                    'pending': pending_visitors
                },
                'cards': {
                    'total': total_cards,
                    'available': available_cards,
                    'inUse': used_cards
                },
                'users': {
                    'total': total_users,
                    'admin': admin_users,
                    'common': common_users
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/recent-returns', methods=['GET'])
def get_recent_returns():
    """Obter devoluções recentes"""
    try:
        limit = int(request.args.get('limit', 5))
        returns = list(returns_collection.find().sort('_id', -1).limit(limit))
        
        for return_item in returns:
            return_item['_id'] = str(return_item['_id'])
        
        return jsonify({
            'success': True,
            'returns': returns
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/search/visitors', methods=['GET'])
def search_visitors():
    """Buscar visitantes por termo"""
    try:
        search_term = request.args.get('term', '').strip()
        
        if not search_term:
            return jsonify({'success': False, 'message': 'Termo de busca é obrigatório'}), 400
        
        # Busca por nome, documento ou telefone
        visitors = list(visitors_collection.find({
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'document': {'$regex': search_term, '$options': 'i'}},
                {'phone': {'$regex': search_term, '$options': 'i'}}
            ]
        }))
        
        for visitor in visitors:
            visitor['_id'] = str(visitor['_id'])
        
        return jsonify({
            'success': True,
            'visitors': visitors
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/')
def hello():
    return "🏢 API VerticalParts - Sistema de Controle de Acesso"

# Inicializar dados padrão na primeira execução
initialize_default_data()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
