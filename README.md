# **Sistema de Gerenciamento de Alunos**

Este é um sistema de gerenciamento de alunos desenvolvido com **Flask** e **SQLAlchemy**, com suporte para manipulação de dados e visualizações gráficas.

---

## **Recursos**

- Gerenciamento de alunos, turmas, e presenças.
- Banco de dados relacional gerenciado com **SQLAlchemy**.
- Manipulação de dados com **Pandas** e suporte a arquivos **Excel**.
- Visualizações e relatórios com **Matplotlib** e **Seaborn**.

---

## **Pré-requisitos**

- Python 3.8 ou superior
- Virtualenv (recomendado)
- SQLite ou PostgreSQL (caso opte por outro banco de dados)

---

## **Instalação**

### **1. Clone o repositório**

Faça o clone do repositório localmente:

```bash
git clone git@github.com:seu-usuario/seu-repositorio.git
cd seu-repositorio
```
---

### **2. Configure o ambiente virtual**

Crie e ative um ambiente virtual para gerenciar as dependências do projeto:

```bash
python -m venv venv
# Ativar no Linux/Mac
source venv/bin/activate
# Ativar no Windows
venv\Scripts\activate
```
---

### **3. Instale as dependências**

Use o arquivo requirements.txt para instalar todas as dependências necessárias:

```bash
pip install -r requirements.txt
```
---

### **4. Configure o banco de dados**

Por padrão, o banco de dados será criado automaticamente no arquivo db ao rodar o aplicativo pela primeira vez. Se preferir, edite a classe DataBaseConnection no código para personalizar o nome ou localização do banco de dados.

---

### **5. Execute o servidor**

Inicie o servidor Flask com o comando:

```bash
python Projeto/app.py
```
---

## **Estrutura do Projeto**

```plaintext
Projeto/
│
├── .gitignore                  # Arquivos ignorados pelo Git
├── db.db                       # Banco de dados SQLite
├── app.py                      # Arquivo principal da aplicação Flask
├── models/                     # Diretório dos modelos e repositórios
│   ├── configs/                # Configurações e conexão com o banco
│   │   ├── base.py
│   │   └── connection.py
│   ├── entities/               # Entidades do sistema
│   │   ├── aspirante.py
│   │   ├── atividade.py
│   │   ├── encontro.py
│   │   ├── eventos.py
│   │   ├── professor.py
│   │   └── turma.py
│   └── repository/             # Repositórios para acesso aos dados
│       ├── aspirante_repository.py
│       ├── atividade_repository.py
│       ├── encontro_repository.py
│       ├── evento_repository.py
│       ├── professor_repository.py
│       ├── repository.py
│       └── turma_repository.py
├── static/                     # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/
│   │   ├── styles.css
├── templates/                  # Arquivos HTML (Jinja2)
│   ├── base.html
│   ├── alunos.html
│   ├── aspirantes_lista.html
│   ├── aspirantes_adicionar.html
│   ├── aspirantes_detalhes.html
│   └── trilha.html
└── requirements.txt            # Lista de dependências do projeto
```

## **Dúvidas?**
Entre em contato comigo: jmariosjunior2000@gmail.com
