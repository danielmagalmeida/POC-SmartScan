# SmartScan POC

Prova de conceito para integração com a API SmartScan da Visma.

## Estrutura do Projeto

- `visma_invoice_test/` - Contém o código principal para processamento de faturas
- `uploads/` - Coloque aqui seus arquivos PDF para processamento (ignorados pelo Git)
- `results/` - Os resultados do processamento serão salvos aqui (ignorados pelo Git)

## Configuração

### Ambiente Virtual

Recomenda-se usar um ambiente virtual para isolar as dependências do projeto:

```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r visma_invoice_test/requirements.txt
```

## Arquivos Ignorados pelo Git

Os seguintes arquivos e diretórios são ignorados pelo Git (adicionados ao `.gitignore`):

- `.venv/` e outros diretórios de ambiente virtual
- `results/` - Contém os resultados do processamento
- `uploads/` - Contém os arquivos a serem processados
- Arquivos de cache do Python (`.pyc`, `__pycache__/`, etc.)
- Arquivos específicos do sistema operacional (`.DS_Store`, `Thumbs.db`, etc.)
- Arquivos de configuração de IDE (`.vscode/`, `.idea/`, etc.)

## Uso

1. Coloque seus arquivos PDF na pasta `uploads/`
2. Execute o script principal:
   ```
   python visma_invoice_test/app.py
   ```
3. Os resultados serão salvos na pasta `results/`
