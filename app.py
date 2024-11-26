from flask import Flask, jsonify, request, render_template_string
import uuid
from lrs.KeyPair import KeyPair 
from lrs.CryptographicSystem import CryptographicSystem
from lrs.Signature import Signature

from model.models import *
from database import db, Config
import smtplib
from sqlalchemy import text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from decimal import Decimal

tokens = {}

q = 17125458317614137930196041979257577826408832324037508573393292981642667139747621778802438775238728592968344613589379932348475613503476932163166973813218698343816463289144185362912602522540494983090531497232965829536524507269848825658311420299335922295709743267508322525966773950394919257576842038771632742044142471053509850123605883815857162666917775193496157372656195558305727009891276006514000409365877218171388319923896309377791762590614311849642961380224851940460421710449368927252974870395873936387909672274883295377481008150475878590270591798350563488168080923804611822387520198054002990623911454389104774092183
g = 8041367327046189302693984665026706374844608289874374425728797669509435881459140662650215832833471328470334064628508692231999401840332046192569287351991689963279656892562484773278584208040987631569628520464069532361274047374444344996651832979378318849943741662110395995778429270819222431610927356005913836932462099770076239554042855287138026806960470277326229482818003962004453764400995790974042663675692120758726145869061236443893509136147942414445551848162391468541444355707785697825741856849161233887307017428371823608125699892904960841221593344499088996021883972185241854777608212592397013510086894908468466292313

def create_app():
    app = Flask(__name__)

    # Carrega as configurações da aplicação
    app.config.from_object(Config)

    # Inicializa o SQLAlchemy com o app
    db.init_app(app)
    
    @app.route('/generate_key', methods=['GET'])
    def generate_key():
        config_keypair = KeyPair(q,g)
        private_key, public_key = config_keypair.generate_key_pair()
        return jsonify({'private_key': private_key, 'public_key': public_key}), 201

        
    @app.route('/generate-link', methods=['GET'])
    def generate_link(participante_id):
        token = str(uuid.uuid4())  
        tokens[token] = False  
        link = f'http://localhost:5000/use-link/{token}/{participante_id}'
        return f'Link gerado: <a href="{link}">{link}</a>'

    @app.route('/use-link/<token>/<participante_id>', methods=['GET'])
    def use_link(token, participante_id):
        
        if token in tokens:
            if tokens[token]:  
                expired_html = '''
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Link Expirado</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                        h1 { color: red; }
                        p { color: #333; }
                    </style>
                </head>
                <body>
                    <h1>Este link já foi utilizado!</h1>
                    <p>Por favor, gere um novo link para acessar a chave.</p>
                </body>
                </html>
                '''
                return render_template_string(expired_html)
            else:
                
                tokens[token] = True
                q = 17125458317614137930196041979257577826408832324037508573393292981642667139747621778802438775238728592968344613589379932348475613503476932163166973813218698343816463289144185362912602522540494983090531497232965829536524507269848825658311420299335922295709743267508322525966773950394919257576842038771632742044142471053509850123605883815857162666917775193496157372656195558305727009891276006514000409365877218171388319923896309377791762590614311849642961380224851940460421710449368927252974870395873936387909672274883295377481008150475878590270591798350563488168080923804611822387520198054002990623911454389104774092183
                g = 8041367327046189302693984665026706374844608289874374425728797669509435881459140662650215832833471328470334064628508692231999401840332046192569287351991689963279656892562484773278584208040987631569628520464069532361274047374444344996651832979378318849943741662110395995778429270819222431610927356005913836932462099770076239554042855287138026806960470277326229482818003962004453764400995790974042663675692120758726145869061236443893509136147942414445551848162391468541444355707785697825741856849161233887307017428371823608125699892904960841221593344499088996021883972185241854777608212592397013510086894908468466292313
                config_keypair = KeyPair(q,g)
                private_key, public_key = config_keypair.generate_key_pair()
                print("aqui 👌",atualizar_chave_publica(participante_id=participante_id, nova_chave_publica=public_key))
                success_html = f'''
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Chaves Geradas</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                        h1 {{ color: green; }}
                        .key {{ 
                            max-width: 600px; 
                            margin: auto; 
                            word-wrap: break-word; 
                            white-space: pre-wrap; 
                            overflow-wrap: break-word; 
                            border: 1px solid #ccc; 
                            padding: 10px; 
                            background-color: #f9f9f9; 
                        }}
                    </style>
                </head>
                <body>
                    <h1>Chaves geradas com sucesso!</h1>
                    <p>Chave pública:</p>
                    <div class="key">{public_key}</div>
                    <p>Chave privada:</p>
                    <div class="key">{private_key}</div>
                    <p>Obrigado por acessar o link.</p>
                </body>
                </html>
                '''
                return render_template_string(success_html)
        else:
            return 'Link inválido ou expirado.', 404
    @app.route('/create-pesquisa', methods=['POST'])
    def create_pesquisa():
        data = request.json

        if not data or 'titulo' not in data or 'descricao' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400

        titulo = data['titulo']
        descricao = data['descricao']

        
        nova_pesquisa = Pesquisa(titulo=titulo, descricao=descricao)
        db.session.add(nova_pesquisa)
        db.session.commit()

        return jsonify({'message': 'Pesquisa criada com sucesso!', 'pesquisa_id': nova_pesquisa.id}), 201

    #cria uma pergunta e associa a uma pesquisa
    @app.route('/create-pergunta', methods=['POST'])
    def create_pergunta():
        data = request.json
        if not data or 'texto' not in data or 'tipo' not in data or 'pesquisa_id' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400
        
        texto = data['texto']
        tipo = data['tipo']
        pesquisa_id = data['pesquisa_id']


        nova_pergunta = Pergunta(texto=texto, tipo=tipo, pesquisa_id=pesquisa_id)
        db.session.add(nova_pergunta)
        db.session.commit()

        return jsonify({'message': 'Pergunta criada com sucesso', 'pergunta_id': nova_pergunta.id}), 201

    @app.route('/create-participante', methods=['POST'])
    def create_participante():
        data = request.json
        print(data)
        if not data or 'nome' not in data or 'email' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400
        
        nome = data['nome']
        chave_publica = 'null'
        email = data['email']
        novo_participante = Participante(nome=nome, chave_publica=chave_publica, email=email)
        db.session.add(novo_participante)
        db.session.commit()
        return jsonify({'message': 'Participante criado com sucesso!', 'pesquisa_id': novo_participante.id}), 201

    @app.route('/create-grupo', methods=['POST'])
    def create_grupo():
        data = request.json
        if not data or 'nome' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400

        nome = data['nome']
        descricao = data.get('descricao', '')

        novo_grupo = Grupo(nome=nome, descricao=descricao)
        db.session.add(novo_grupo)
        db.session.commit()

        return jsonify({'message': 'Grupo criado com sucesso!', 'grupo_id': novo_grupo.id}), 201
    @app.route('/add-participante-grupo/<int:grupo_id>/<int:participante_id>', methods=['POST'])
    def add_participante(grupo_id, participante_id):
        grupo = Grupo.query.get(grupo_id)
        participante = Participante.query.get(participante_id)
        if not participante:
            return jsonify({'error': 'Participante não encontrado.'}), 404
        if not grupo:
            return jsonify({'error': 'Grupo  não encontrado.'}), 404

        grupo.participantes.append(participante)
        db.session.commit()

        return jsonify({'message': 'Participante adicionado ao grupo com sucesso!'}), 200
    
    @app.route('/responder', methods=['POST'])
    def responder():
        data = request.json
        if not data or 'conteudo' not in data or 'pergunta_id' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400
        
        
        conteudo = data['conteudo']
        pergunta_id = data['pergunta_id']
        pergunta = Pergunta.query.get(pergunta_id)
        if not pergunta:
            return jsonify({'error': 'Pergunta não encontradada.'}), 404
        resposta = Resposta(conteudo=conteudo, pergunta_id=pergunta_id)
        db.session.add(resposta)
        db.session.commit()
        return jsonify({'message': 'Resposta adicionada com sucesso!', 'grupo_id': resposta.id}), 201

    @app.route('/assinar', methods=['POST'])
    def assinar():
        q = 17125458317614137930196041979257577826408832324037508573393292981642667139747621778802438775238728592968344613589379932348475613503476932163166973813218698343816463289144185362912602522540494983090531497232965829536524507269848825658311420299335922295709743267508322525966773950394919257576842038771632742044142471053509850123605883815857162666917775193496157372656195558305727009891276006514000409365877218171388319923896309377791762590614311849642961380224851940460421710449368927252974870395873936387909672274883295377481008150475878590270591798350563488168080923804611822387520198054002990623911454389104774092183
        g = 8041367327046189302693984665026706374844608289874374425728797669509435881459140662650215832833471328470334064628508692231999401840332046192569287351991689963279656892562484773278584208040987631569628520464069532361274047374444344996651832979378318849943741662110395995778429270819222431610927356005913836932462099770076239554042855287138026806960470277326229482818003962004453764400995790974042663675692120758726145869061236443893509136147942414445551848162391468541444355707785697825741856849161233887307017428371823608125699892904960841221593344499088996021883972185241854777608212592397013510086894908468466292313

        data = request.json
        message = ''
        contador_perguntas = 1
        if 'grupo_id' not in data:
            return jsonify({'error': 'faltou o id do grupo'}), 400
        grupo_id = data['grupo_id']
        if 'pesquisa_id' not in data:
            return jsonify({'error': 'faltou o id da pesquisa'}), 400
        pesquisa_id = data['pesquisa_id']

        existe_pesquisa = Pesquisa.query.get(pesquisa_id)
        print(existe_pesquisa)
        if not existe_pesquisa:
            return jsonify({'error': 'a pesquisa informada não existe!'}), 404

        if 'private_key' not in data:
            return jsonify({'error': 'faltou o id da pesquisa'}), 400
        private_key = data['private_key']

        listas_chaves_publicas = obter_chaves_publicas(grupo_id)
        listas_chaves_publicas = [int(key) for key in listas_chaves_publicas]
        private_key = int(private_key)
        

        if not obter_chaves_publicas :
            return jsonify({'error': 'id de grupo inválido'}), 400

        for resposta in data['respostas']:
            
            if not resposta or 'conteudo' not in resposta or 'pergunta_id' not in resposta:
                return jsonify({'error': 'Dados inválidos ou incompletos'}), 400
            message += str(contador_perguntas) + ": " + resposta['conteudo']

            contador_perguntas += 1
        crypto_sys = CryptographicSystem(q, g)  # Certifique-se de que q e g estejam definidos no escopo.
        assinatura = crypto_sys.generate_signature(public_keys=listas_chaves_publicas, message=message, private_key=private_key)
        assinatura[0].s_values = str(assinatura[0].s_values)
        assinatura[0].c_values = str(assinatura[0].c_values)
     
        #if verificar_se_ja_respondeu(str(assinatura[0].y0), pesquisa_id):
            #return jsonify({'error': 'Esta pesquisa já foi respondida por este usuário'}), 401
        

        assinatura_model = Assinatura(y0=assinatura[0].y0, s_values=assinatura[0].s_values,c_values=assinatura[0].c_values, r=assinatura[1])
        db.session.add(assinatura_model)
        db.session.commit()
        resposta_pesquisa = RespostaPesquisa(assinatura_id=assinatura_model.id, grupo_id=grupo_id, pesquisa_id=pesquisa_id)
        db.session.add(resposta_pesquisa)
        
        for dado in data['respostas']:
            pergunta_id = dado['pergunta_id']
            conteudo = dado['conteudo']
            
            pergunta = Pergunta.query.get(pergunta_id)
            if not pergunta:
                return jsonify({'error': 'Pergunta não encontradada.'}), 404
            resposta = Resposta(conteudo=conteudo, pergunta_id=pergunta_id, resposta_pesquisa_id=resposta_pesquisa.id)
            db.session.add(resposta)
        db.session.commit()

        return jsonify({'message': 'Assinatura realizada com sucesso!', 'grupo_id': data}), 201

    @app.route("/verificar-assinatura", methods=['POST'])
    def verificar_assinatura():
        data = request.json
        if not data or 'grupo_id' not in data or 'assinatura_id' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400

        assinatura_id = data['assinatura_id']
        grupo_id = data['grupo_id']
        assinatura = Assinatura.query.get(assinatura_id)
        print(assinatura)
        if not assinatura:
            return jsonify({'error': 'Não existe assinatura cadastrada com este id'}), 400
        
        resposta_pesquisa = RespostaPesquisa.query.filter(RespostaPesquisa.assinatura_id ==assinatura_id).first()
        


        if not resposta_pesquisa:
            return jsonify({'error': 'RespostaPesqusia não encontrado'}), 400
        
        respostas = Resposta.query.filter(Resposta.resposta_pesquisa_id == resposta_pesquisa.id).all()
        print("aqui",respostas)
        message = ''
        contador_perguntas = 1
        for resposta in respostas:
            
            if not resposta.conteudo  or not resposta.pergunta_id:
                return jsonify({'error': 'Dados inválidos ou incompletos'}), 400
            message += str(contador_perguntas) + ": " + resposta.conteudo
            contador_perguntas +=1
        
        listas_chaves_publicas = obter_chaves_publicas(grupo_id)
        listas_chaves_publicas = [int(key) for key in listas_chaves_publicas]
        crypto_sys =CryptographicSystem(q,g)

        assinatura.s_values = str(assinatura.s_values)
        print(f"Tipo de assinatura.s_values: {type(assinatura.s_values)}")
        print(f"Conteúdo de assinatura.s_values: {assinatura.s_values}")

        assinatura.s_values = assinatura.s_values.strip('[]')
        assinatura.s_values = assinatura.s_values.split(',')
        assinatura.s_values = [int(key) for key in assinatura.s_values]

        assinatura.c_values = assinatura.c_values.strip('[]')
        assinatura.c_values = assinatura.c_values.split(',')
        assinatura.c_values = [int(key) for key in assinatura.c_values]

        assinatura.y0 = int(assinatura.y0)
        

        resultado = crypto_sys.verify_signature(listas_chaves_publicas, message, assinatura, int(assinatura.r))
        print(resultado)
        if resultado == True:

            return jsonify({'message': 'A assinatura é válida', 'resultado': resultado}), 201
        else: 
            return jsonify({'message': 'A assinatura é inválida', 'resultado': resultado}), 201

    @app.route('/enviar-link', methods=['POST'])
    def enviar_link():
        data = request.json

        if not data or 'grupo_id' not in data or 'pesquisa_id' not in data:
            return jsonify({'error': 'Dados inválidos ou incompletos'}), 400

        grupo_id = data['grupo_id']
        pesquisa_id = data['pesquisa_id']
        participantes = obter_participantes(grupo_id=grupo_id)

        FROMADDR = "fd912735@gmail.com"
        LOGIN    = FROMADDR
        PASSWORD = "yrvz ttwz bfyl vyuk"
        SUBJECT  = "Link para a Pesquisa (to do)"
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(LOGIN, PASSWORD)
        print("aqui",participantes)
        for participante in participantes:
            email = participante[1]
            id = participante[0]
            # Gerar um link único para cada participante
            link_unico = generate_link(id)  # Você deve garantir que essa função gere links únicos
            msg = MIMEMultipart()
            msg['From'] = FROMADDR
            msg['To'] = email
            msg['Subject'] = SUBJECT

            # Corpo do e-mail com o link único (usando UTF-8 para suportar caracteres especiais)
            body = f"Aqui está o link para gerar seu par de chaves: {link_unico}\r\n"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Enviar o e-mail
            server.sendmail(FROMADDR, email, msg.as_string())

        server.quit()
        
        return jsonify({'message': 'Links enviados com sucesso!'}), 200
    return app




# Função para buscar os emails dos participantes de um grupo com SQL nativo
def obter_participantes(grupo_id):
    result = db.session.execute(
        text('''
            SELECT participantes.id, participantes.email
            FROM participantes
            JOIN grupo_participante ON participantes.id = grupo_participante.participante_id
            WHERE grupo_participante.grupo_id = :grupo_id
        '''), {'grupo_id': grupo_id}
    )
    
    participantes = [(row[0], row[1]) for row in result]
    return participantes


def atualizar_chave_publica(participante_id, nova_chave_publica):
    try:
        # Buscar o participante pelo ID
        participante = Participante.query.filter_by(id=participante_id).first()

        if participante is None:
            return 'Participante não encontrado'

        # Atualizar a chave pública
        participante.chave_publica = nova_chave_publica
        
        # Confirmar a alteração no banco de dados
        db.session.commit()

        return 'Chave pública atualizada com sucesso!'

    except Exception as e:
        db.session.rollback()  # Reverter alterações em caso de erro
        return 'error', str(e)


def obter_chaves_publicas(grupo_id):
    # Executa uma consulta SQL para obter as chaves públicas dos participantes de um grupo específico
    result = db.session.execute(
        text('''
            SELECT participantes.chave_publica
            FROM participantes
            JOIN grupo_participante ON participantes.id = grupo_participante.participante_id
            WHERE grupo_participante.grupo_id = :grupo_id
        '''), {'grupo_id': grupo_id}
    )
    
    # Cria uma lista contendo apenas as chaves públicas
    chaves_publicas = [row[0] for row in result]
    return chaves_publicas


def verificar_se_ja_respondeu(y0, pesquisa_id):
    
    result = db.session.execute(
        text('''
           select * from resposta_pesquisa r 
            join assinaturas a on r.assinatura_id = a.id where a.y0 = :y0 and r.pesquisa_id = :pesquisa_id;
        '''), {'y0': y0, 'pesquisa_id': pesquisa_id}
    )
    

    data = [row[0] for row in result]
    return data

if __name__ == '__main__':
    
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
