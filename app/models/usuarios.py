from errno import EROFS
from sqlalchemy import ForeignKey
from app import db
from werkzeug.security import generate_password_hash
from flask import request, jsonify
from .enderecos import Endereco

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema':'api_flask'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    cpf = db.Column(db.String(20), unique=True)
    pis = db.Column(db.String(20), unique=True)
    status = db.Column(db.Boolean)
    endereco_id = db.Column(db.Integer, ForeignKey('api_flask.enderecos.id'))
    endereco = db.relationship("Endereco")

    def __init__(self, nome, senha, email, cpf, pis, endereco):
        self.nome = nome
        self.senha = senha
        self.email = email
        self.cpf = cpf
        self.pis = pis
        self.endereco = endereco
        self.status = True

    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "pis": self.pis,
            "endereco": self.endereco.to_json()
        }


def select_usuarios():
    usuarios = Usuario.query.all()
    list_usuarios = list()
    if usuarios:
        for usuario in usuarios:
            list_usuarios.append(usuario.to_json())

        return jsonify({'data': list_usuarios})

    return jsonify({'mensagem': 'Dados não encontrados'})

def insert_usuario():
    nome = request.json['nome']
    email = request.json['email']
    cpf = request.json['cpf']
    pis = request.json['pis']
    senha = request.json['senha']
    senha_hash = generate_password_hash(senha)
    endereco = request.json['endereco']
    endereco = Endereco(
        endereco.get('pais'),
        endereco.get('estado'),
        endereco.get('municipio'),
        endereco.get('cep'),
        endereco.get('rua'),
        endereco.get('numero'),
        endereco.get('complemento')
        )

    usuario = Usuario(nome, senha_hash, email, cpf, pis, endereco)

    try:
        db.session.add(usuario)
        db.session.commit()
        return jsonify({'mensagem': 'Cadastro Realizado!'}), 201
    except:
        return jsonify({'mensagem': 'Erro no cadastro!'}), 500


def update_usuario(usuario):
    nome = request.json['nome']
    endereco = request.json['endereco']

    try:
        usuario.nome = nome
        usuario.endereco.pais = endereco.get("pais")
        usuario.endereco.estado = endereco.get("estado")
        usuario.endereco.municipio = endereco.get("municipio")
        usuario.endereco.cep = endereco.get("cep")
        usuario.endereco.rua = endereco.get("rua")
        usuario.endereco.numero = endereco.get("numero")
        usuario.endereco.complemento = endereco.get("complemento")
        db.session.commit()

        return jsonify({'mensagem': 'Usuário editado!'}), 201
    except:
        return jsonify({'mensagem': 'Erro ao atualizar dados!'}), 500


def delete_usuario(usuario):
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'mensagem': 'Usuário deletado!'})
    except:
        return jsonify({'mensagem': 'Erro ao deletar usuário!'}), 500

def realiza_login(login):
    try:
        return Usuario.query.filter(Usuario.cpf == login).one()
    except:
        try:
            return Usuario.query.filter(Usuario.email == login).one()
        except:
            try:
                return Usuario.query.filter(Usuario.pis == login).one()
            except:
                return None