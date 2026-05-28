from marshmallow import Schema, fields, validate

class TreinoRequestSchema(Schema):
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

class TreinoResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    objetivo = fields.Str(dump_only=True)
    nivel = fields.Str(dump_only=True)
    treino_gerado = fields.Str(dump_only=True)
    criado_em = fields.DateTime(dump_only=True, format="%Y-%m-%dT%H:%M:%SZ")
