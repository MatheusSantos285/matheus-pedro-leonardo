## 1. Modelo(s) Candidato(s) para Classificação de Intenções

Para a tarefa principal do projeto — a classificação supervisionada multiclasse da intenção do chamado de suporte (variável alvo categórica `Ticket Type`, composta pelas classes *Technical issue*, *Billing inquiry*, *Cancellation request*, *Product inquiry* e *Refund request*) a partir do texto livre da coluna `Ticket Description` —, selecionam-se os seguintes algoritmos candidatos:

### 1.1. Candidato Principal: Regressão Logística Multinomial (*Multinomial Logistic Regression*)

* **Descrição:** Modelo linear generalizado que utiliza a função *Softmax* para estender a classificação binária a cenários com múltiplas classes ($K = 5$), atribuindo uma distribuição de probabilidades sobre as classes possíveis:
  $$P(Y = k \mid \mathbf{x}) = \frac{e^{\mathbf{w}_k^T \mathbf{x} + b_k}}{\sum_{j=1}^{K} e^{\mathbf{w}_j^T \mathbf{x} + b_j}}$$
* **Adequação ao Problema:**
  1. **Excelente Desempenho em Espaços Esparsos de Alta Dimensionalidade:** Em processamento de linguagem natural (NLP), matrizes de contagem de palavras (*Bag-of-Words*) geram milhares de colunas, com esparsidade superior a 95%. Modelos lineares baseados em gradiente convergem rapidamente e mantêm estabilidade numérica sob essas condições.
  2. **Interpretabilidade dos Pesos ($\mathbf{w}$):** Permite inspecionar diretamente os coeficientes associados a cada palavra do vocabulário, viabilizando a auditoria das decisões do modelo e a identificação de termos com maior peso preditivo para cada intenção.
  3. **Calibração de Incerteza:** Produz escores de probabilidade calibrados, fundamentais para estabelecer limiares de confiança (*confidence thresholds*) antes de despachar o chamado para atendimento automático ou humano.
  4. **Controle de Sobreajuste (*Overfitting*):** A inclusão de termos de regularização $L_2$ (Ridge) ou $L_1$ (Lasso) previne a supervalorização de termos espúrios ou ruídos do corpus.

### 1.2. Candidato Secundário: Máquina de Vetores de Suporte com Kernel Linear (*Linear Support Vector Machine - LinearSVC*)

* **Descrição:** Algoritmo que busca encontrar o hiperplano de separação ótimo que maximiza a margem geométrica entre as classes no espaço vetorial de características.
* **Adequação ao Problema:**
  1. **Princípio da Margem Máxima:** Proporciona capacidade de generalização elevada em conjuntos de dados textuais onde o número de variáveis ($p$) é comparável ou superior ao número de observações ($n$).
  2. **Robustez a Outliers e Textos com Variação de Estilo:** Como a fronteira de decisão é delimitada exclusivamente pelos vetores de suporte mais críticos, o modelo é resiliente a variações de extensão ou pontuação presentes nas mensagens dos usuários.
  3. **Baixo Custo Computacional de Inferência:** O produto interno entre o vetor de entrada e os vetores de suporte lineares possui complexidade $\mathcal{O}(d)$, garantindo tempos de resposta na escala de milissegundos na API em produção.

---

## 2. Estratégia de Representação Textual: `CountVectorizer`

Para converter os textos brutos das solicitações (`Ticket Description` combinado ou não ao `Ticket Subject`) em representações numéricas computáveis pelos algoritmos de aprendizado supervisionado, adota-se a técnica **`CountVectorizer`** (modelo *Bag-of-Words*).

### 2.1. Definição da Técnica

O `CountVectorizer` realiza a tokenização do corpus, constrói um vocabulário de termos únicos $V$ e converte cada documento $d_i$ em um vetor esparso $\mathbf{x}_i \in \mathbb{R}^{|V|}$, onde cada dimensão representa a frequência absoluta de ocorrência do token correspondente:
$$\mathbf{x}_{i,j} = \text{contagem do termo } j \text{ no documento } i$$

### 2.2. Justificativa da Escolha

1. **Alinhamento com as Evidências da Análise Exploratória (EDA):** A análise univariada e os testes formais de hipótese (Mann-Whitney U com $p > 0.05$) comprovaram que métricas estruturais (como a extensão do texto em caracteres ou palavras) não diferenciam as intenções dos tickets. A discriminação reside estritamente na presença de termos-chave temáticos (ex.: *refund*, *billing*, *error*, *hardware*, *cancel*). O `CountVectorizer` captura diretamente essa frequência de unigramas e bigramas.
2. **Linha de Base Sólida (*Strong Baseline*):** Em problemas de classificação de intenções com vocabulário de domínio fechado (suporte técnico e transacional), representações de contagem aliadas a regressores lineares frequentemente atingem desempenho equivalente a arquiteturas neurais mais complexas, com fração do custo computacional.
3. **Simplicidade de Pipeline e Menor Latência:** A geração de matrizes de contagem dispensa o cálculo de inversão de frequências de documentos (*IDF*) ou inferências de redes de embeddings, minimizando o tempo de pré-processamento nos endpoints síncronos da API.
4. **Configuração Otimizada de Parâmetros:**
   * **`ngram_range=(1, 2)`:** Permite capturar unigramas e pares de termos contíguos (bigramas como *refund request*, *system crash*, *credit card*).
   * **`stop_words='english'`:** Remove termos gramaticais de alta frequência sem conteúdo semântico específico.
   * **`min_df=3` e `max_df=0.85`:** Elimina ruídos de digitação pontuais e remove palavras excessivamente genéricas presentes em quase todos os chamados.

---

## 3. Alvo Autorizado para Testes Adversariais (TP4 / TP5)

Para a condução das atividades de testes de robustez, ataques adversariais de evasão e testes de intrusão (*pentest*) dinâmico planejados para as etapas subsequentes, delimita-se o ambiente alvo e o escopo de autorização:

### 3.1. Identificação do Alvo

* **Ambiente de Homologação / Staging Local:**
  * **URL Base Autorizada:** `http://127.0.0.1:8000` (ou `http://localhost:8000`)
  * **Endereço de Rede para Testes em Contêiner:** `http://host.docker.internal:8000`
* **Especificação OpenAPI / Swagger:** `http://127.0.0.1:8000/openapi.json`
* **Documentação Interativa:** `http://127.0.0.1:8000/docs`

### 3.2. Endpoints no Escopo de Ataque

| Endpoint | Método | Descrição | Vetores de Teste Planejados |
| :--- | :---: | :--- | :--- |
| `/api/v1/predict` | `POST` | Inferência e classificação de intenções via modelo ML | Evasão adversarial (perturbação de texto por sinônimos, inserção de ruído/typos, caracteres homóglifos), injeção de payload extenso (DoS de memória) e *prompt injection* |
| `/api/v1/tickets/search` | `POST` | Busca filtrada e consulta ao banco de chamados | Validação de resistência a SQL Injection (CWE-89) e bypass de filtros de parâmetros |
| `/api/v1/auth/login` | `POST` | Emissão de tokens de acesso JWT | Testes de força bruta, auditoria de expiração de token e resistência a algoritmos fracos de assinatura (`none`) |

### 3.3. Parâmetros de Autorização e Salvaguardas

* Os testes devem ser realizados estritamente na base de dados de homologação ou réplica de testes, sem conexão com ambientes produtivos ou serviços externos pagos.
* Fica autorizada a execução de scanners dinâmicos (OWASP ZAP), frameworks de ataques adversariais para texto (ex.: TextAttack / Adversarial Robustness Toolbox) e ferramentas de injeção de carga controlada (cURL / Postman / Locust).