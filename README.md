# Breweries-Case
Breweries Case - BEES

## Setting up the Python Virtual Environment

1. Create the virtual environment:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    - **Linux/Mac**:
      ```bash
      source venv/bin/activate
      ```
    - **Windows**:
      ```bash
      .\venv\Scripts\activate
      ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Code Quality

This project uses [pre-commit](https://pre-commit.com/) and [flake8](https://flake8.pycqa.org/en/latest/) to enforce code standards.

# Infra - Buckets S3 do Projeto Breweries

Dentro da pasta Infra existe o Terraform que define os buckets S3 utilizados para o pipeline de dados do projeto.


## Requisitos

- Terraform >= 1.3
- AWS CLI configurado (com acesso à conta que conterá os buckets)

## Como usar

1. Inicialize o Terraform:
   ```bash
   terraform init
   terraform plan
   terraform apply

## Instruções para rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu_usuario/seu_projeto.git
cd seu_projeto
```
### 2. Suba o docker
```
docker-compose build
docker-compose up
```
