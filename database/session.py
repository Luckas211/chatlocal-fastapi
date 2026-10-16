from database.connection import sessaolocal

def obter_sessao():
    sessao = sessaolocal()
    try:
        yield sessao
    finally:
        sessao.close()
