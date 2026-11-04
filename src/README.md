# API de Atividades da Mergington High School

Uma aplicação FastAPI simples que permite que estudantes visualizem, se inscrevam e sejam removidos de atividades extracurriculares.

## Funcionalidades

- Visualizar todas as atividades extracurriculares disponíveis
- Inscrever-se em atividades
- Cancelar a inscrição de estudantes

## Primeiros Passos

1. Instale as dependências:

   ```
   pip install fastapi uvicorn
   ```

2. Execute a aplicação:

   ```
   python app.py
   ```

3. Abra seu navegador e acesse:
   - Documentação da API: http://localhost:8000/docs
   - Documentação alternativa: http://localhost:8000/redoc

## Endpoints da API

| Método | Endpoint                                                          | Descrição                                                                   |
| ------ | ----------------------------------------------------------------- | --------------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Obtém todas as atividades com seus detalhes e contagem atual de participantes |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Inscreve-se em uma atividade                                                   |
| DELETE | `/activities/{activity_name}/participants?email=student@mergington.edu` | Remove a inscrição de um estudante da atividade |

O endpoint DELETE exige autenticação HTTP Basic. Configure `UNREGISTER_CREDENTIALS` como um objeto JSON de usuários autorizados, com uma senha e o email verificado para cada estudante; para autorizar uma equipe, configure `"role": "staff"` para a conta. Por exemplo:

```json
{"student":{"password":"<senha>","email":"student@mergington.edu"},"staff":{"password":"<senha>","role":"staff"}}
```

Envie o usuário e a senha configurados como credenciais HTTP Basic. Sem credenciais válidas, a solicitação é rejeitada; estudantes só podem remover a própria inscrição e a equipe pode remover qualquer participante. Use HTTPS e mantenha as senhas de configuração em segredo.

## Modelo de Dados

A aplicação usa um modelo de dados simples com identificadores significativos:

1. **Activities** - Usa o nome da atividade como identificador:

   - Descrição
   - Horário
   - Número máximo de participantes permitidos
   - Lista de emails dos estudantes inscritos

2. **Students** - Usa email como identificador:
   - Nome
   - Série/Ano escolar

Todos os dados são armazenados em memória, o que significa que os dados serão resetados quando o servidor reiniciar.
