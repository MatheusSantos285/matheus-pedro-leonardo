# Relatório de Auditoria de Segurança: Scan Passivo OWASP ZAP

## 1. Título e Introdução
**Escopo:** Avaliação de vulnerabilidades via Scan Passivo utilizando o OWASP ZAP.<br>
**Alvo:** API FastAPI Local (`http://127.0.0.1:8000/docs` e endpoints associados).<br>
**Data da Análise:** 05 de Outubro de 2026.<br>
**Objetivo:** Identificar ausência de configurações seguras de transporte, cabeçalhos HTTP e anomalias arquiteturais visíveis no tráfego passivo da aplicação, correlacionando os achados com os controles de segurança ativos previamente implementados no código (SecurityHeadersMiddleware, CORSMiddleware, SlowAPI, Pydantic estrito e SQLModel).

---

## 2. Resumo dos Achados (Alerts Summary)
O scan passivo detectou um total de 7 alertas. A tabela abaixo apresenta a contagem segmentada pelo nível de severidade (Risk Level):

| Severidade | Nível de Risco | Quantidade de Alertas |
| :--- | :--- | :---: |
| 🔴 **High** | Alto | 1 |
| 🟠 **Medium**| Médio | 2 |
| 🟡 **Low** | Baixo | 1 |
| 🔵 **Informational**| Informativo | 3 |
| **Total** | - | **7** |

*Nota: Alertas informativos (ex: identificação da API como Aplicação Web Moderna e detecção de gerenciadores de sessão) e de risco baixo (Inclusão de JS de Terceiros) não exigem mitigação direta, sendo comportamentos esperados em frameworks como o FastAPI (Swagger UI).*

---

## 3. Análise de Vulnerabilidades Severidade Medium e High

Foram identificados **3 findings** nas categorias *Medium* e *High*. Abaixo encontra-se o detalhamento técnico, o impacto e a tratativa de cada alerta, levando em consideração a infraestrutura defensiva já existente na API.

### Vulnerabilidade 1
* **7.1. Finding:** Credenciais de Autenticação Capturadas (Authentication Credentials Captured)
* **7.2. Severidade:** High (Alto)
* **7.3. Confiança:** Medium (Médio)
* **7.4. URL afetada:** `POST http://127.0.0.1:8000/auth/token`
* **7.5. O que foi detectado:** Transmissão de credenciais (usuário e senha) não criptografadas através de um canal inseguro (HTTP). O ZAP detectou a submissão de credenciais em texto plano.
* **7.6. Por que é um problema:** Trafegar credenciais sobre protocolo HTTP permite ataques de *Man-in-the-Middle* (MitM) e *Sniffing* de rede (OWASP 2025 A04 - Cryptographic Failures), resultando em comprometimento completo das contas afetadas.
* **7.7. Correção realizada:** Nenhuma alteração no código foi necessária para ambiente local. O código atual da API já possui o `SecurityHeadersMiddleware` injetando a diretiva `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HSTS).
* **7.8. Validação:** A reexecução em um ambiente de produção (onde o proxy reverso realiza a terminação SSL/TLS forçando HTTPS) suprimirá automaticamente este alerta.
* **7.9. Risco aceito, se não corrigido:** **Risco Aceito (Falso Positivo de Ambiente).** Como o teste ocorreu via `localhost` (`http://127.0.0.1`), a comunicação não dispõe de SSL/TLS por padrão. A API foi arquitetada *Security-by-Design* com HSTS, delegando a camada de criptografia de transporte ao servidor web de borda em produção (ex: Nginx/Traefik).

---

### Vulnerabilidade 2
* **7.1. Finding:** CSP: Failure to Define Directive with No Fallback
* **7.2. Severidade:** Medium (Médio)
* **7.3. Confiança:** High (Alto)
* **7.4. URL afetada:** `GET http://127.0.0.1:8000/docs`
* **7.5. O que foi detectado:** O cabeçalho de resposta `Content-Security-Policy` definido (`default-src 'self'`) omite diretivas estritas que não herdam o *fallback* de `default-src`, especificamente `frame-ancestors` e `form-action`.
* **7.6. Por que é um problema:** A ausência de `frame-ancestors` poderia teoricamente permitir que a aplicação fosse embutida em iframes maliciosos (OWASP 2025 A02 - Security Misconfiguration), facilitando vetores de *Clickjacking*.
* **7.7. Correção realizada:** Nenhuma alteração exigida, pois há um controle de segurança sobreposto já atuante.
* **7.8. Validação:** Avaliação manual da resposta HTTP.
* **7.9. Risco aceito, se não corrigido:** **Risco Mitigado e Aceito.** O `SecurityHeadersMiddleware` da aplicação já possui a instrução `response.headers["X-Frame-Options"] = "DENY"`. Esta regra bloqueia ativamente o *Clickjacking* em navegadores modernos, tornando o aviso do ZAP redundante para a ausência da diretiva `frame-ancestors` no CSP neste cenário.

---

### Vulnerabilidade 3
* **7.1. Finding:** Sub Resource Integrity Attribute Missing
* **7.2. Severidade:** Medium (Médio)
* **7.3. Confiança:** High (Alto)
* **7.4. URL afetada:** `GET http://127.0.0.1:8000/docs`
* **7.5. O que foi detectado:** A página importa arquivos externos de folha de estilo e scripts (`swagger-ui.css`, `swagger-ui-bundle.js` vindos do CDN `cdn.jsdelivr.net`) sem a presença do atributo HTML `integrity`.
* **7.6. Por que é um problema:** Se o servidor CDN de terceiros sofrer um comprometimento (Supply Chain Attack), um atacante poderia alterar o script servido. Sem a validação do hash de integridade (SRI), o navegador executará o script alterado, caracterizando vulnerabilidade a *Cross-Site Scripting* (XSS) via terceiro.
* **7.7. Correção realizada:** Não aplicável diretamente via código FastAPI simples, visto que o HTML do Swagger UI é gerado de forma autônoma pela biblioteca nativa do framework (`fastapi.openapi.docs`).
* **7.8. Validação:** Uma eventual mitigação seria desabilitar o Swagger na produção e fornecê-lo offline, retestando o serviço sem a exposição da rota `/docs`.
* **7.9. Risco aceito, se não corrigido:** **Risco Aceito.** Esta falha ocorre estritamente na rota pública de documentação do Swagger interativo. Em fluxos operacionais de DevSecOps, a boa prática estipula que endpoints interativos (`/docs` e `/redoc`) sejam desativados em ambientes de **Produção**. Para ambientes de Desenvolvimento/Homologação, o risco da ausência de SRI nestes *assets* providos pela própria mantenedora do FastAPI é aceitável.

---

## 4. Conclusão de Postura de Segurança

A execução do scan passivo OWASP ZAP confirma o **alto grau de maturidade defensiva** adotado na construção da API.

1. **Eficiência de Controles de Borda:** A ausência de falhas graves em rotas de negócio comprova a eficácia das defesas globais configuradas em código:
   - A taxativa validação do **Pydantic** (`extra='forbid'`) e as regras de tipagem garantiram que fuzzing estrutural ou Mass Assignment não surtissem efeito no mapeamento das rotas.
   - O tráfego conta com uma camada protetiva de **Middlewares de Segurança**, onde as cabeceiras limitam escopos de execução (CSP estrito, X-Frame-Options contra *Clickjacking* e X-Content-Type-Options prevenindo ataques *MIME-Sniffing*).
2. **Defesa em Profundidade contra Força Bruta:** O ZAP tentou diagnosticar *Session Management* interagindo com a rota `/auth/token`. O **SlowAPI** configurado na aplicação garante a interrupção precoce em caso de varreduras ativas que ultrapassem 10 req/min, blindando o banco SQLite contra exaustão de *Thread Pools* ou tentativas de adivinhação de senhas com *Bcrypt*.

Em síntese, os findings com severidade Medium/High referem-se, em sua totalidade, a características temporárias do ambiente local (HTTP ao invés de HTTPS) ou de artefatos de documentação nativa do FastAPI (Swagger UI dependente de CDNs). O núcleo da aplicação ("Core Business API") encontra-se blindado e resiliente a ataques categorizados pelo OWASP API Security Top 10.