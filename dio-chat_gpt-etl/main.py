"""
Script desenvolvido para o desafio da DIO, Explorando IA Generativa em um
Pipeline de ETL com Python.
Objetivo Geral: Atribuir a funcionalidade da API Geocoding da GoogleMaps para
gerar um 'tradutor' de endereços para aumentar a veracidade de um DataFrame.

Estrutura do DataFrame(`.xlsx`):
    ____endereco____bairro______cidade______estado______pais____
    0   nomeRua     nomeBairro  nomeCidade  nomeEstado  nomePais

Estrutura do Dicionario(`.xlsx`)
nomeErrado1 nomeCorreto1
nomeErrado2 nomeCorreto2
nomeErrado3 nomeCorreto2

    BONUS.
        Qual é a graça de obter dados de geolocalização se não para
        representá-los em um mapa?
        Pensando nisso, desenvolvi duas funções(receber_poligono e 
        ponto_em_poligono) para calcular e retornar o polígono que compreende
        a coordenada passada.

        Para testes, estou disponibilizando dados em formato `.xlsx` de 
        endereços fictícios. Também incluirei a constante POLIGONOS, em 
        `polygons.py`, com certas regiões do município que resido e trabalho,
        para que o script também defina à qual região cada instancia pertence,
        só não poderei incluir os nomes das regiões pois, a pesar de terem 
        sido meticulosamente desenhadas por mim, as informações que elas 
        representam não são de minha autoria.
"""

__autor__ = 'TDPessoa'
__email__ = 'thiago.d.pessoa@gmail.com'
__github__ = 'https://github.com/tdpessoa'

import pandas as pd
import requests
import json
from polygons import POLIGONOS

# Esta variável precisa ser preenchida com uma chave da GoogleMaps que seja
# habilitada para requisições à plataforma de Geocoding
CHAVE_GMAPS = 'AIzaSyAGUvOl6Qdv0uMeVIHD4PMOCYgWdlrhjuA'

# Declarando uma variável global com o dicionário em um objeto dict
dicionario = pd.read_excel('dicionario.xlsx').to_dict(index=False)

def iniciar_script():
    """Controla o fluxo principal do script"""
    dados = pd.read_excel('dados.xlsx')  # Iniciando um DataFrame a partir do
    # arquivo `dados.xlsx`

    tarefas = criar_tarefas(dados)

    novos_dados = {'indice': [], 'endereco': [], 'bairro': [], 'cidade': [], 
                   'estado': [], 'pais': [], 'regiao': []}

    if CHAVE_GMAPS == '':
        print('A constante `CHAVE_GMAPS` está vazia, por favor, preencha-a.'
              '\nA mesma se encontra abaixo da sessão de imports.')
        
    for tarefa in tarefas:  # Iterando sobre as chaves de tarefas que fez uma
    # lista com os indices para cada tarefa unica no DataFrame
        pesquisa = receber_resposta(tarefa)  # Fazendo a requisição à API e 
        # extraindo as informações contidas no json de resposta
        for indice in tarefas[tarefa]:
            novos_dados['indice'].append(indice)  # Atribuindo o respectivo 
            # indice à linha atual do novo DataFrame

            # Resgatando cada pedaço de informação contido no json e inserindo
            # no DataFrame
            novos_dados['endereco'].append(pesquisa['endereco_certo'])
            novos_dados['bairro'].append(pesquisa['bairro_certo'])
            novos_dados['cidade'].append(pesquisa['cidade_certa'][indice])
            novos_dados['estado'].append(pesquisa['estado_certo'][indice])
            novos_dados['pais'].append(pesquisa['pais_certo'][indice])
            novos_dados['regiao'].append(
                receber_poligono(
                    pesquisa['coordenadas'][0],  # Longitude
                    pesquisa['coordenadas'][1]  # Latitude
                    )
                )
            
            # Definindo como seria a celula de endereço errado no dicionario
            endereco_errado = (f"{dados['endereco'][indice]}, "
                               f"{dados['bairro'][indice]}")
            
            if endereco_errado not in dicionario['errado']:
            # O endereço errado não consta no dicionario, portanto será 
            # adicionado, junto com seu valor correto
                dicionario['errado'].append(endereco_errado)
                dicionario['certo'].append(
                    f"{pesquisa['endereco_certo']}~{pesquisa['bairro_certo']}"
                    )

    # Ao fim do loop de tarefas, o script salvará os dados coletados
    salvar_xlsx(dicionario, 'dicionario.xlsx')
    salvar_xlsx(novos_dados, 'novos_dados.xlsx')
    

def ponto_em_poligono(ponto: tuple, poligono: list) -> bool:
    """Percorrerá as arestas do poligono, definidas por dois pontos na lista
    e sua próxima aresta, formando uma borda do polígono, se essa borda não 
    for horizontal ou não estiver ao lado do ponto, não é válida para o 
    algorítmo.    
    Utilizando a fórmula de direcionamento de raio (Ray Casting), definirá se 
    uma linha partindo do ponto horizontalmente, intercepta a borda atual, se 
    sim, a +1 para `num_intercecoes`, ao final do algorítimo, verifica-se se 
    a contágem é par ou impar. Irá repetir isto para todas as arestas do
    `poligono` e retornará se `ponto` está dentro ou fora da área"""

    longitude, latitude = ponto  # Dividindo a coordenada alvo em suas devidas 
    # partes
    num_intersecoes = 0  # Iniciando a contágem 
    for i in range(len(poligono)):
        # Dividindo a aresta atual do poligono
        longitude1, latitude1 = poligono[i]
        # Dividindo a próxima aresta `(i + 1)`,
        # `% len(poligono)` serve para que, quando i for o indice da ultima 
        # aresta, a próxima aresta seja a de indice 0
        longitude2, latitude2 = poligono[(i + 1) % len(poligono)]
        if latitude1 == latitude2:  
            # borda é horizontal, não é computável
            continue

        if (min(latitude1, latitude2) > latitude or
                max(latitude1, latitude2) < latitude):
            # borda está acima ou abaixo do ponto, não é computável
            continue
        
        # Calculando o ponto de interceção de uma linha horizontal que passa 
        # pelo ponto e pela borda
        longitude_intersecao = (
                longitude1
                + (latitude - latitude1)
                * (longitude2 - longitude1)
                / (latitude2 - latitude1)
        )

        if longitude_intersecao > longitude:
            # raio de intercecao da borda está á direita do ponto
            num_intersecoes += 1
    
    # Retorna True quando `num_intercecoes` é impar e False quando par
    return num_intersecoes % 2 == 1


def receber_poligono(lng: float, lat: float) -> str:
    """Itera sobre os poligonos e verifica se o ponto está dentro ou fora
    deste peligono"""
    ponto = (lng, lat)
    run = 0
    for poligono in POLIGONOS:
        if ponto_em_poligono(ponto, POLIGONOS[poligono]):
            # O poligono em questão compreende o ponto
            return poligono

        elif run == len(POLIGONOS):
            # Acabaram os polígonos para serem verificados
            return 'Fora da Área'

        run += 1


def salvar_xlsx(dados_xlsx: dict, file_xlsx: 'str') -> None:
    """Salvará os dados do dict no arquivo `.xlsx` passados nos parametros"""
    df = pd.DataFrame(dados_xlsx)  # Transformando o dict em um DataFrame
    with pd.ExcelWriter(file_xlsx) as xlsx_writer:
        df.to_excel(xlsx_writer, sheet_name='MAIN')


def receber_resposta(endereco: str) -> dict:
    """Faz um request.get para a API e converte a resposta json em dict e 
    retorna o produto de `extrair_resposta`"""
    # Envia o prompt para a API
    resposta_google_maps = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?'
        f'address={endereco}'
        f'&key={CHAVE_GMAPS}'
        '&language=pt-BR'
    )

    resposta_google_maps.encoding = 'utf-8'
    # converte a resposta em dict
    resposta_em_dict = resposta_google_maps.json()
    return extrair_resposta(resposta_em_dict)


def verificar_dicionario(parte_endereco: str) -> list:
    """Varre o dicionario procurando o nome da rua desejado na coluna errado,
    se encontrá-lo, retorna o valor que corresponde ao correto"""

    for index in range(len(dicionario['errado'])):
        # Definindo uma variável como o valor de 'errado' na linha atual
        errado = dicionario['errado'][index]
        if errado == parte_endereco:
            # O valor procurado corresponde a um valor errado do dicionario
            parte_endereco = dicionario['certo'][index]

    if '~' in parte_endereco:
        # O valor corresponde ao formato de um endereco correto
        return parte_endereco.split('~')
    
    else:
        # O valor permanece o mesmo que o passado nos parametros
        return parte_endereco.split(', ')


def criar_tarefas(base_dados: pd.DataFrame) -> dict:
    """Lê as colunas com um senso pré-definido do que contém no DataFrame,
    transformando cada linha em um prompt apropriado para a API, se o endereco
    não for encontrado no dicionário.
    O DataFrame está no formato:
        endereco    bairro  cidade  estado  pais    longitude   latitude
    0   str         str     str     str     str     float       float

    e cada tarefa fica no formato:
    indice: "endereco, bairro - cidade, estado, pais"
    
    sendo então tratada para ser enviada como parte de uma url, 
    substituindo os espaços por '%20', removendo acentos e cedilha.
    """
    lista_tarefas = {}
    # O formato de `lista_terafas` será a tarefa como chave e uma lista com
    # os indices nos quais esta tarefa se repete como valor

    for indice in range(len(base_dados['endereco'])):
        # Verificando se este endereço já consta no dicionario, permitindo uma 
        # busca atualizada
        endereco_correto = verificar_dicionario(
            f"{base_dados['endereco'][indice]}, {base_dados['bairro'][indice]}",
        )
        # Atualizando todas as aparições semelhantes no DataFrame pelo 
        # endereço corrigido
        base_dados.replace(base_dados['endereco'][indice],
                           endereco_correto[0],
                           inplace=True
                           )
        base_dados.replace(base_dados['bairro'][indice],
                           endereco_correto[1],
                           inplace=True
                           )

        # Formatando o prompt no modelo apresentado na documentação da função
        prompt = (f'{base_dados["endereco"][indice]}'
                  f', {base_dados["bairro"][indice]}'
                  f' - {base_dados["cidade"][indice]}'
                  f', {base_dados["estado"][indice]}'
                  f', {base_dados["pais"][indice]}'
                  )
        prompt = prompt.replace(' ', '%20')
        prompt = remover_acentos(prompt)

        try:
            # Tentando adicionar o indice à chave de `lista_tarefa` encontrada
            lista_tarefas[prompt].append(indice)

        except KeyError:
            # Criando a chave e atribuindo o indice á uma nova lista quando 
            # ainda não houver
            lista_tarefas[prompt] = [indice]

    return lista_tarefas


def remover_acentos(frase: str) -> str:
    """Lê um dicionário com caracteres não ideais para uma url e substitui
    pelo valor correto, remontando a frase somente com caracteres válidos"""
    caracteres_indesejados = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }

    nova_frase = ''
    for letra in frase:
        nova_letra = letra.lower()
        if nova_letra in caracteres_indesejados:
            nova_frase += caracteres_indesejados[nova_letra]
        else:
            nova_frase += nova_letra

    return nova_frase


def extrair_resposta(json_traduzido: dict) -> dict:
    """Recebe a informação do objeto json convertido para um dict e extrai as
    informações relevantes, distribuindo-as em um dict com chaves
    pre-definidas."""

    resposta = {'endereco_certo': '',
                'bairro_certo': '',
                'cidade_certa': '',
                'estado_certo': '',
                'pais_certo': '',
                'coordenadas': [0, 0],
                }
    if json_traduzido['status'] == "OK":  # A pesquisa foi bem sucedida.

        for parte in json_traduzido['results'][0]['address_components']:
            if 'route' in parte['types']:
                resposta['endereco_certo'] = parte['short_name']

            elif 'sublocality_level_1' in parte['types']:
                resposta['bairro_certo'] = parte['short_name']

            elif 'administrative_area_level_2' in parte['types']:
                resposta['cidade_certa'] = parte['short_name']

            elif 'administrative_area_level_1' in parte['types']:
                resposta['estado_certo'] = parte['short_name']

            elif 'country' in parte['types']:
                resposta['pais_certo'] = parte['short_name']

        # Para as coordenadas, no mesmo dict existe a chave 'geometry', onde 
        # pode-se encontrar o dict `location` que contém duas chaves `lng` e 
        # `lat` 
        resposta["coordenadas"][0] = (
            json_traduzido['results'][0]['geometry']['location']['lng']
            )
        resposta["coordenadas"][1] = (
            json_traduzido['results'][0]['geometry']['location']['lat']
            )

    else:
        # Erro é retornado e fará com que o endereco seja inválido para as
        # próximas operações.
        resposta["endereco_certo"] = "Error"

    return resposta


iniciar_script()
