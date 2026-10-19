"""API routes and HTTP endpoint definitions for api_academia.

Exposes RESTful endpoints for health status checking and workout routine CRUD operations.
"""

from typing import Tuple
from flask import Blueprint, request, jsonify, current_app, Response
from flask_limiter.errors import RateLimitExceeded

from .database import db
from .models import Treino
from .schemas import PERFIL_FIELDS, TreinoRequestSchema, TreinoResponseSchema
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
@limiter.exempt
def health() -> Tuple[Response, int]:
    """Health check endpoint to verify backend operational readiness."""
    return jsonify({
        'status': 'operante',
        'mensagem': 'API de Treinos com IA rodando com sucesso!'
    }), 200


@api_blueprint.route('/treino', methods=['POST'])
@limiter.limit("30 per minute", error_message="Limite de 30 requisições de treinos por minuto atingido.")
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
    perfil = {campo: dados_validados[campo] for campo in PERFIL_FIELDS if campo in dados_validados}

    try:
        # Call Gemini AI Service
        treino_gerado_texto = generate_treino(objetivo=objetivo, nivel=nivel, perfil=perfil)

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

    # Details go to the log only: exception text can expose hosts, tables or queries
    except ValueError as ve:
        db.session.rollback()
        current_app.logger.warning(f"Treino não gerado: {ve}")
        return jsonify({'erro': 'Não foi possível gerar o treino com os dados enviados.'}), 400
    except RuntimeError as re:
        db.session.rollback()
        current_app.logger.error(f"Falha no serviço de IA: {re}")
        return jsonify({'erro': 'O serviço de IA está indisponível no momento.'}), 502
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro inesperado ao criar treino")
        return jsonify({'erro': 'Falha no servidor ao processar treino.'}), 500


@api_blueprint.route('/treinos', methods=['GET'])
@require_api_key
def listar_treinos() -> Tuple[Response, int]:
    """Retrieves the most recent workouts (?limit=, default 50, max 200) ordered by creation date desc."""
    limite = min(max(request.args.get('limit', 50, type=int), 1), 200)
    try:
        treinos = Treino.query.order_by(Treino.criado_em.desc()).limit(limite).all()
        schema_resp = TreinoResponseSchema(many=True)
        return jsonify(schema_resp.dump(treinos)), 200
    except Exception:
        current_app.logger.exception("Erro ao listar treinos")
        return jsonify({'erro': 'Erro ao acessar o banco de dados.'}), 500


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
    except Exception:
        current_app.logger.exception(f"Erro ao obter treino {id}")
        return jsonify({'erro': 'Erro ao carregar registro.'}), 500


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
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Erro ao deletar treino {id}")
        return jsonify({'erro': 'Erro ao deletar registro.'}), 500
