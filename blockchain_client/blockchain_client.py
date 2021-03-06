from flask import Flask, request, jsonify, render_template
import binascii
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
from collections import OrderedDict
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5


class Transaction:
    # para qualquer transação no Blockchain, seus 4 itens necessários são sua chave pública e privada e a chave pública do destinatário e o valor
    def __init__(self, sender_public_key, sender_private_key, recipient_public_key, amount):
        self.sender_public_key = sender_public_key
        self.sender_private_key = sender_private_key
        self.recipient_public_key = recipient_public_key
        self.amount = amount

    def to_dict(self):
        return OrderedDict({
            'sender_public_key': self.sender_public_key,
            'recipient_public_key': self.recipient_public_key,
            'amount': self.amount,
        })

    def sign_transaction(self):
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


# Flask é uma estrutura leve de aplicativo da web WSGI. Ele foi projetado para tornar os primeiros passos rápidos e fáceis, com a capacidade de escalar para aplicativos complexos.
app = Flask(__name__)


@app.route('/')
def index():
    # Our main menu page
    return render_template('index.html')


@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
    sender_public_key = request.form['sender_public_key']
    sender_private_key = request.form['sender_private_key']
    recipient_public_key = request.form['recipient_public_key']
    amount = request.form['amount']

    transaction = Transaction(sender_public_key, sender_private_key, recipient_public_key, amount)

    response = {'transaction': transaction.to_dict(),
                'signature': transaction.sign_transaction()}

    return jsonify(response), 200


@app.route('/make/transaction')
def make_transaction():
    return render_template('make_transaction.html')


@app.route('/view/transactions')
def view_transactions():
    return render_template('view_transactions.html')


@app.route('/wallet/new')
def new_wallet():
    # para gerar uma chave pública e privada aleatória, usamos RSA de Crypto.PublicKey
    # saiba mais aqui: https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html
    random_gen = Crypto.Random.new().read
    # It must be at least 1024, but you can also use 2048 and 3072
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()

    response = {
        # Retorna a representação hexadecimal dos dados binários. e então decodificar para ASCII
        'private_key': binascii.hexlify(private_key.export_key(format('DER'))).decode('ascii'),
        'public_key': binascii.hexlify(public_key.export_key(format('DER'))).decode('ascii')
    }

    # A função jsonify() em flask retorna um objeto flask.Response() que já possui o cabeçalho de tipo de conteúdo apropriado 'application/json' para uso com respostas json.
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6060, type=int, help="port to listen to")
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)
