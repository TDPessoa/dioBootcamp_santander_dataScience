# Explorando IA Generativa em um Pipeline de ETL com Python
Desafio de projeto proposto pela DIO para o **Santander Bootcamp 2023 - Ciência de Dados com Python**.  
Autor: TDPessoa | [Meu Github](https://github.com/TDPessoa) | 
[Meus READMES](https://tdpessoa.notion.site/READ-ME-s-0dbb921792dd4a6ab3e6266c1db02470?pvs=4) 
## Descrição do Desafio
Após apresentar uma solução utilizando a API da OpenAI para gerar mensagens personalizadas para clientes fictícios de 
um banco, o desafio lançado foi utilizar da mesma ferramenta, ou similar para algo parecido a meu critério.  
## A minha Ideia
### Contexto
No meu trabalho, tenho acesso a dados -- obtidos pelo preenchimento **manual** de formulários -- de chamadas telefonicas, 
os quais contém endereço, bairro etc, porém, por falhas na comunicação e/ou entendimento das partes, na maioria das 
vezes, estes dados são preenchidos incorretamente e acabam sendo utilizados da mesma forma que são obtidos por falta de 
recursos para tratá-los. O que diminui a confiabilidade da base de dados quando se precisar definir certas 
afirmativas sobre os dados como: "De qual bairro mais se recebe chamdados" ou "Qual é a incidencia na região A para o 
tipo de chamado Y".
### Ideia
**1. Utilizar** da [Geocoding API](https://developers.google.com/maps/documentation/geocoding) fornecida pelo GoogleMaps para tratar instancias de endereços contendo: [  
+ "nomeRua",  
+ "nomeBairro",  
+ "nomeCidade",  
+ "siglaEstado", e  
+ "nomePais"  
    ]

**2. Formatar** cada instancia da forma:  
"nomeRua, nomeBairro - nomeCidade, siglaEstado, nomePais"

**3. Requisitar e Coletar** a resposta da API, que vem em formato json, estrair os dados contidos nela e formar uma nova base com os dados: [  
+ "nomeRuaResposta",  
+ "nomeBairroResposta", 
+ "nomeCidadeResposta",  
+ "siglaEstadoResposta",
+ "nomePaisResposta", e
+ "coordenadasResposta"  
]
## Do Meu Projeto
Vou desenvolver cada parte como descrita no desafio onde o tutor caminha pela sigla ETL (Extraction; Transformation; 
Load). Vou:
+ Extrair do arquivo `dados.xlsx` para um `pd.DataFrame`;
+ Gerar *'tarefas'*, que seria um `dict` onde suas chaves são `str` das instancias de dado endereço (formatadas para o uso na API) e seus valores, `listas` com os indices do `DataFrame` onde essas chaves se repetem;  
+ Iterar sobre as *'tarefas'*, atribuindo-as à [url](https://maps.googleapis.com/maps/api/geocode/json?address={endereco}&key={CHAVE_GMAPS}&language=pt-BR), realizando um `request.get` e extraindo os dados da requisição;  
+ Formar um dicionário para os dados em um `dict`, que será salvo em `dicionario.xlsx`, contendo o endereco antigo (rua e bairro) e o endereco contido na resposta;  
+ (***Bonus:*** Irei inserir neste código e no diretório não só dados fictícios da minha cidade para realizar testes, mas também uma constante `POLIGONOS` em outro arquivo `.py` contendo as coordenadas das 17 subdivisões do municipio e funções para determinar em qual subdivisão a coordenada encontrada pela API se encontra)
+ Salvar de volta para o arquivo `dicionario.xlsx`, os dados da variável; e  
+ Salvar os dados das respostas em `novos_dados.xlsx.`
## Do README de Fato
Irei preparar a documentação após o término do Bootcamp, só fiz um breve resumo do desafio aqui, mas a documentação será escrita com olhos exculsivamente para o script, estará nesta [página do Notion](https://tdpessoa.notion.site/Utilizando-da-GoogleMaps-Geocoding-API-para-tratar-endere-os-f0ff8871eb1d4f8cbe4e5c154fae01c0?pvs=4).
