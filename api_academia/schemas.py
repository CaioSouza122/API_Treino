"""Marshmallow schemas for data validation and serialization.

Ensures strict validation of incoming requests and clean JSON output formatting.
"""

from marshmallow import Schema, fields, validate


class TreinoRequestSchema(Schema):
    """Schema for validating POST /api/v1/treino payload."""

    objetivo = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255, error="O objetivo deve ter entre 3 e 255 caracteres.")
    )
    nivel = fields.Str(
        load_default="iniciante",
        validate=validate.OneOf(
            ["iniciante", "intermediario", "avancado"],
            error="O nível deve ser 'iniciante', 'intermediario' ou 'avancado'."
        )
    )

    # Optional user profile sent by the HIPERTROF.IA backend to personalize the workout
    altura = fields.Float(validate=validate.Range(min=1, max=250, error="A altura deve estar entre 1 e 250."))
    peso = fields.Float(validate=validate.Range(min=20, max=400, error="O peso deve estar entre 20 e 400 kg."))
    idade = fields.Int(validate=validate.Range(min=10, max=100, error="A idade deve estar entre 10 e 100 anos."))
    vezes_por_semana = fields.Int(
        validate=validate.Range(min=1, max=7, error="A frequência deve estar entre 1 e 7 vezes por semana.")
    )
    tempo = fields.Int(validate=validate.Range(min=10, max=300, error="O tempo deve estar entre 10 e 300 minutos."))


PERFIL_FIELDS = ("altura", "peso", "idade", "vezes_por_semana", "tempo")


class TreinoResponseSchema(Schema):
    """Schema for serializing Treino model instances to JSON responses."""

    id = fields.Int(dump_only=True)
    objetivo = fields.Str(dump_only=True)
    nivel = fields.Str(dump_only=True)
    treino_gerado = fields.Str(dump_only=True)
    criado_em = fields.DateTime(dump_only=True, format="%Y-%m-%dT%H:%M:%SZ")
