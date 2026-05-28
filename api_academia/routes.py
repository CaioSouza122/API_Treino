from flask import Blueprint, request, jsonify, current_app
from flask_limiter.errors import RateLimitExceeded
from .database import db
from .models import Treino
from .schemas import TreinoRequestSchema, TreinoResponseSchema
from .auth import require_api_key
from .services import generate_treino
from .limiter import limiter

api_blueprint = Blueprint('api', __name__)

@api_blueprint.errorhandler(RateLimitExceeded)
def handle_rate_limit_error(e):
    """Graceful JSON error response when API consumer hits rate limit."""
    return jsonify({
        'erro': 'Muitas requisições!',
        'mensagem': 'Você excedeu o limite de uso permitido para esta rota. Tente novamente mais tarde.',
        'detalhe': str(e.description)
    }), 429

@api_blueprint.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'operante',
        'mensagem': 'API de Treinos com IA rodando com sucesso!'
    }), 200

@api_blueprint.route('/treino', methods=['POST'])
@limiter.limit("5 per minute", error_message="Limite de 5 treinos por minuto atingido.")
@require_api_key
def criar_treino():
    """Validates parameters, calls Gemini AI to generate a workout, and saves to database."""
    dados_requisicao = request.get_json() or {}
    
    # 1. Validate payload
    schema_req = TreinoRequestSchema()
    errors = schema_req.validate(dados_requisicao)
    if errors:
        return jsonify({'erros_validacao': errors}), 400
        
    dados_validados = schema_req.load(dados_requisicao)
    objetivo = dados_validados.get('objetivo')
    nivel = dados_validados.get('nivel')
    
    try:
        # 2. Call Gemini AI via Service
        treino_gerado_texto = generate_treino(objetivo, nivel)
        
        # 3. Create Model instance and persist to DB
        novo_treino = Treino(
            objetivo=objetivo,
            nivel=nivel,
            treino_gerado=treino_gerado_texto
        )
        db.session.add(novo_treino)
        db.session.commit()
        
        # 4. Serialize response
        schema_resp = TreinoResponseSchema()
        response_data = schema_resp.dump(novo_treino)
        return jsonify(response_data), 201
        
    except ValueError as ve:
        # Configuration or content error
        return jsonify({'erro': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar treino: {str(e)}")
        return jsonify({'erro': f'Falha no servidor ou na IA: {str(e)}'}), 500

@api_blueprint.route('/treinos', methods=['GET'])
@require_api_key
def listar_treinos():
    """Lists all workout routines stored in the database."""
    try:
        treinos = Treino.query.order_by(Treino.criado_em.desc()).all()
        schema_resp = TreinoResponseSchema(many=True)
        return jsonify(schema_resp.dump(treinos)), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao listar treinos: {str(e)}")
        return jsonify({'erro': f'Erro ao acessar banco de dados: {str(e)}'}), 500

@api_blueprint.route('/treino/<int:id>', methods=['GET'])
@require_api_key
def obter_treino(id):
    """Retrieves a specific workout routine by ID."""
    try:
        treino = Treino.query.get(id)
        if not treino:
            return jsonify({'erro': f'Treino com ID {id} não encontrado.'}), 404
            
        schema_resp = TreinoResponseSchema()
        return jsonify(schema_resp.dump(treino)), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao obter treino {id}: {str(e)}")
        return jsonify({'erro': f'Erro ao carregar registro: {str(e)}'}), 500

@api_blueprint.route('/treino/<int:id>', methods=['DELETE'])
@require_api_key
def deletar_treino(id):
    """Deletes a specific workout routine by ID."""
    try:
        treino = Treino.query.get(id)
        if not treino:
            return jsonify({'erro': f'Treino com ID {id} não encontrado.'}), 404
            
        db.session.delete(treino)
        db.session.commit()
        return jsonify({'mensagem': f'Treino {id} deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao deletar treino {id}: {str(e)}")
        return jsonify({'erro': f'Erro ao deletar registro: {str(e)}'}), 500
