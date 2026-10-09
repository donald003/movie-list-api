from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email()

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class LoginResponseSchema(Schema):
    access_token = fields.Str()

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    director = fields.Str()
    year = fields.Int()
    rating = fields.Int(allow_none=True)
    watched = fields.Bool()

class MovieCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    director = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(required=True)
    rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=10))
    watched = fields.Bool(load_default=False)

class MovieUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1))
    director = fields.Str(validate=validate.Length(min=1))
    year = fields.Int()
    rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=10))
    watched = fields.Bool()
