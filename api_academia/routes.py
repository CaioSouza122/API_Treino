"""API routes and HTTP endpoint definitions for api_academia.

Exposes RESTful endpoints for health status checking and workout routine CRUD operations.
"""

from typing import Tuple
from flask import Blueprint, request, jsonify, current_app, Response
from flask_limiter.errors import RateLimitExceeded

from .database import db
from .models import Treino
from .schemas import TreinoRequestSchema, TreinoResponseSchema
from .auth import require_api_key
from .services import generate_treino
from .limiter import limiter

api_blueprint = Blueprint('api', __name__)


@api_blueprint.errorhandler(RateLimitExceeded)
def handle_rate_limit_error(e: RateLimitExceeded) -> Tuple[Response, int]:
    """Handles rate-limiting violations gracefully with a JSON payload."""
    return jsonify({
        'erro': 'Limite de requisições excedido',
        'mensagem': 'Você atingiu o limite de uso permitido para esta rota. Tente novamente em breve.',
        'detalhe': str(e.description)
    }), 429


@api_blueprint.route('/health', methods=['GET'])
def health() -> Tuple[Response, int]:
    """Health check endpoint to verify backend operational readiness."""
    return jsonify({
        'status': 'operante',
        'mensagem': 'API de Treinos com IA rodando com sucesso!'
    }), 200


@api_blueprint.route('/treino', methods=['POST'])
@limiter.limit("5 per minute", error_message="Limite de 5 requisições de treinos por minuto atingido.")
@require_api_key
def criar_treino() -> Tuple[Response, int]:
    """Generates a new workout plan via Gemini AI and persists it in the database.

    Expected JSON Payload:
        {
            "objetivo": "Ganho de massa muscular",
            "nivel": "intermediario"  # Opções: iniciante, intermediario, avancado (padrão: iniciante)
        }
    """
    dados_requisicao = request.get_json(silent=True) or {}

    # Validate payload against Marshmallow schema
    schema_req = TreinoRequestSchema()
    errors = schema_req.validate(dados_requisicao)
    if errors:
        return jsonify({'erros_validacao': errors}), 400

    dados_validados = schema_req.load(dados_requisicao)
    objetivo = dados_validados.get('objetivo')
    nivel = dados_validados.get('nivel', 'iniciante')

    try:
        # Call Gemini AI Service
        treino_gerado_texto = generate_treino(objetivo=objetivo, nivel=nivel)

        # Persist to database
        novo_treino = Treino(
            objetivo=objetivo,
            nivel=nivel,
            treino_gerado=treino_gerado_texto
        )
        db.session.add(novo_treino)
        db.session.commit()

        # Serialize and return response
        schema_resp = TreinoResponseSchema()
        return jsonify(schema_resp.dump(novo_treino)), 201

    except ValueError as ve:
        db.session.rollback()
        return jsonify({'erro': str(ve)}), 400
    except RuntimeError as re:
        db.session.rollback()
        return jsonify({'erro': str(re)}), 502
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro inesperado ao criar treino: {str(e)}")
        return jsonify({'erro': f'Falha no servidor ao processar treino: {str(e)}'}), 500


@api_blueprint.route('/treinos', methods=['GET'])
@require_api_key
def listar_treinos() -> Tuple[Response, int]:
    """Retrieves all workouts stored in database ordered by creation date desc."""
    try:
        treinos = Treino.query.order_by(Treino.criado_em.desc()).all()
        schema_resp = TreinoResponseSchema(many=True)
        return jsonify(schema_resp.dump(treinos)), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao listar treinos: {str(e)}")
        return jsonify({'erro': f'Erro ao acessar banco de dados: {str(e)}'}), 500


@api_blueprint.route('/treino/<int:id>', methods=['GET'])
@require_api_key
def obter_treino(id: int) -> Tuple[Response, int]:
    """Retrieves a specific workout routine by unique ID."""
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
def deletar_treino(id: int) -> Tuple[Response, int]:
    """Deletes a specific workout routine from database by unique ID."""
    try:
        treino = Treino.query.get(id)
        if not treino:
            return jsonify({'erro': f'Treino com ID {id} não encontrado.'}), 404

        db.session.delete(treino)
        db.session.commit()
        return jsonify({'mensagem': f'Treino com ID {id} deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao deletar treino {id}: {str(e)}")
        return jsonify({'erro': f'Erro ao deletar registro: {str(e)}'}), 500
