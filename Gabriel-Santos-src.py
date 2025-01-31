import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import mysql.connector

# Foi utilizado o tkinter para criação da interface gráfica, site da biblioteca https://docs.python.org/pt-br/3.13/library/tk.html

# Função para conectar ao banco de dados
def connect_to_database():
    try:
        conn = mysql.connector.connect( # Função da biblioteca fornecida
            host="localhost",
            user="root",
            password="Password123!",
            database="imobiliaria"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para executar consultas no banco de dados
def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro na consulta: {err}")
        return []

# Função para exibir resultados de consultas
def show_results(results):
    if results:
        result_str = "\n\n".join([str(result) for result in results])
        messagebox.showinfo("Resultados", result_str)
    else:
        messagebox.showinfo("Resultados", "Nenhum resultado encontrado.")

# Funções para cada consulta específica
def query_cliente_proposta(): # 1.4.1 - Todos os clientes cadastrados e que já fizeram alguma proposta
    conn = connect_to_database()
    if conn:
        query = "SELECT distinct CPF, Nome_cliente FROM Cliente, Proposta WHERE CPF = CPF_inquilino"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()# Função da biblioteca fornecida

def query_imovel(): # 1.4.2 - Todos os imóveis cadastrados (alugados ou não)
    conn = connect_to_database()
    if conn:
        query = "SELECT num_registro, Endereco_cidade, Endereco_rua, Endereco_num FROM Imovel"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_proposta_imovel(): # 1.4.3 - Listar as ofertas feitas para um determinado imóvel
    conn = connect_to_database()
    if conn:
        query = "SELECT num_registro, valor_proposta FROM Proposta WHERE num_registro = 2"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_comissao_2022(): # 1.4.4 - Informar o corretor que obteve maior rendimento no ano de 2022.
    conn = connect_to_database()
    if conn:
        query = "SELECT c.Nome_corretor, SUM(p.valor_proposta * c.comissao / 100) as total_comissao FROM Corretor as c JOIN Visita as v ON c.CRECI = v.CRECI JOIN Proposta as p ON v.num_registro = p.num_registro WHERE YEAR(p.dt_proposta) = 2022 GROUP BY c.CRECI ORDER BY total_comissao DESC LIMIT 1"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_imoveis_caros(): # 1.4.5 - Listar os 3 imóveis mais caros
    conn = connect_to_database()
    if conn:
        query = "SELECT Endereco_cidade, Endereco_rua, Valor_imovel FROM Imovel ORDER BY Valor_imovel DESC LIMIT 3"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_imoveis_com_vagas(): # Imóveis com mais de 2 vagas de garagem
    conn = connect_to_database()
    if conn:
        query = "SELECT Endereco_cidade, Endereco_rua, Vagas, Valor_imovel FROM Imovel WHERE Vagas > 2 ORDER BY Vagas DESC"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_imoveis_acima_600k(): # Imóveis com valor superior a 700 mil
    conn = connect_to_database()
    if conn:
        query = "SELECT Endereco_cidade, Endereco_rua, Vagas, Valor_imovel FROM Imovel WHERE Valor_imovel > 600000"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_cidades_imoveis(): # Cidades com maior número de imóveis cadastrados
    conn = connect_to_database()
    if conn:
        query = "SELECT Endereco_cidade, COUNT(*) as num_imoveis FROM Imovel GROUP BY Endereco_cidade"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_imoveis_com_4_comodos(): # Imóveis com mais de 4 cômodos
    conn = connect_to_database()
    if conn:
        query = "SELECT Endereco_cidade, Endereco_rua, num_comodos, Valor_imovel FROM Imovel WHERE num_comodos > 4 ORDER BY num_comodos DESC"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

def query_imoveis_sem_visitas(): # Imóveis que não receberam nenhuma proposta
    conn = connect_to_database()
    if conn:
        query = "SELECT i.Endereco_cidade, i.Endereco_rua FROM Imovel as i LEFT JOIN Visita as v ON i.num_registro = v.num_registro WHERE v.num_registro is NULL"
        results = execute_query(conn, query)
        show_results(results)
        conn.close()

# Funções de atualização, remoção e inserção

def insert_corretor(): # Insere um corretor no banco de dados
    conn = connect_to_database()
    if conn: # Coleta as informações referentes ao Corretor
        creci = simpledialog.askstring("Inserir Corretor", "Digite o número do CRECI do corretor:")
        nome = simpledialog.askstring("Inserir Corretor", "Digite o nome do corretor:")
        comissao = simpledialog.askfloat("Inserir Corretor", "Digite a comissão do corretor (%):")
        dt_inicio = simpledialog.askstring("Inserir Corretor", "Digite a data de início (AAAA-MM-DD):")
        if creci and nome and comissao and dt_inicio:
            query = f"INSERT INTO Corretor (CRECI, Nome_corretor, dt_inicio, comissao) VALUES ('{creci}', '{nome}', '{dt_inicio}', {comissao})"
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                messagebox.showinfo("Sucesso", "Corretor inserido com sucesso!")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao inserir corretor: {err}")
        conn.close()

def insert_imovel(): # Insere um imóvel no banco de dados
    conn = connect_to_database()
    if conn: # Coleta as informações referentes ao Imóvel
        num_registro = simpledialog.askstring("Inserir Imóvel", "Digite o número de registro do imóvel:")
        cidade = simpledialog.askstring("Inserir Imóvel", "Digite a cidade do imóvel:")
        rua = simpledialog.askstring("Inserir Imóvel", "Digite a rua do imóvel:")
        num = simpledialog.askinteger("Inserir Imóvel", "Digite o número do imóvel:")
        valor = simpledialog.askfloat("Inserir Imóvel", "Digite o valor do imóvel:")
        vagas = simpledialog.askinteger("Inserir Imóvel", "Digite o número de vagas do imóvel:")
        area = simpledialog.askfloat("Inserir Imóvel", "Digite a área do imóvel (m²):")
        num_comodos = simpledialog.askinteger("Inserir Imóvel", "Digite o número de cômodos do imóvel:")
        dt_registro = simpledialog.askstring("Inserir Imóvel", "Digite a data de registro (AAAA-MM-DD):")
        
        if num_registro and cidade and rua and num and valor and vagas and area and num_comodos and dt_registro:
            query = f"INSERT INTO Imovel (num_registro, Endereco_cidade, Endereco_rua, Endereco_num, Area, num_comodos, Vagas, Valor_imovel, dt_registro) VALUES ({num_registro}, '{cidade}', '{rua}', {num}, {area}, {num_comodos}, {vagas}, {valor}, '{dt_registro}')"
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                messagebox.showinfo("Sucesso", "Imóvel inserido com sucesso!")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao inserir imóvel: {err}")
        conn.close()

def update_record(): # Atualiza quaisquer registro dad três tabelas principais
    conn = connect_to_database()
    if conn: # Recebe do usário qual tabela será modificada
        table_option = simpledialog.askinteger("Atualizar Registro", 
                                               "Selecione a tabela:\n[1] Corretor\n[2] Imóvel\n[3] Cliente\n[0] Cancelar")
        # Guarda a resposta na variável
        if table_option == 1:
            table_name = "Corretor"
        elif table_option == 2:
            table_name = "Imovel"
        elif table_option == 3:
            table_name = "Cliente"
        else:
            messagebox.showinfo("Operação cancelada", "Operação cancelada.")
            return
        # Coleta algumas informações adicionais
        column_name = simpledialog.askstring("Atualizar Registro", "Digite o nome da coluna que deseja atualizar:")
        new_value = simpledialog.askstring("Atualizar Registro", f"Digite o novo valor para a coluna {column_name}:")
        condition_column = simpledialog.askstring("Atualizar Registro", "Digite o nome da coluna para critério de atualização:")
        condition_value = simpledialog.askstring("Atualizar Registro", f"Digite o valor do critério para a coluna {condition_column}:")
        
        if column_name and new_value and condition_column and condition_value: # Se válido, executa a query
            query = f"UPDATE {table_name} SET {column_name} = '{new_value}' WHERE {condition_column} = '{condition_value}'"
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                messagebox.showinfo("Sucesso", f"Registro atualizado com sucesso na tabela {table_name}!")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar registro: {err}")
        conn.close()

def delete_record(): # Exclui quaisquer registro dad três tabelas principais
    conn = connect_to_database()
    if conn: # Recebe do usário qual tabela será modificada
        table_option = simpledialog.askinteger("Remover Registro", 
                                               "Selecione a tabela:\n[1] Corretor\n[2] Imóvel\n[3] Cliente\n[0] Cancelar")
        # Guarda a resposta na variável
        if table_option == 1:
            table_name = "Corretor"
        elif table_option == 2:
            table_name = "Imovel"
        elif table_option == 3:
            table_name = "Cliente"
        else:
            messagebox.showinfo("Operação cancelada", "Operação cancelada.")
            return
        
        column_name = simpledialog.askstring("Remover Registro", "Digite o nome da coluna usada como critério:")
        value = simpledialog.askstring("Remover Registro", f"Digite o valor do critério para a coluna {column_name}:")
        
        if column_name and value: # Se válido, executa a query
            query = f"DELETE FROM {table_name} WHERE {column_name} = '{value}'"
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                messagebox.showinfo("Sucesso", f"Registro removido com sucesso da tabela {table_name}!")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao remover registro: {err}")
        conn.close()

# Função para carregar clientes cadastrados
def load_clientes(tree):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CPF, Nome_cliente, Estado_Civil FROM Cliente")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

# Função para carregar corretores cadastrados
def load_corretores(tree):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CRECI, Nome_corretor, dt_inicio, comissao FROM Corretor")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()
# Função para pesquisar clientes
def search_clientes(tree, search_term):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = f"SELECT CPF, Nome_cliente, Estado_Civil FROM Cliente WHERE Nome_cliente LIKE '%{search_term}%' OR CPF LIKE '%{search_term}%'"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Limpa a Treeview antes de inserir os novos resultados
        for row in tree.get_children():
            tree.delete(row)
        # Insere os resultados da pesquisa
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

# Função para pesquisar corretores
def search_corretores(tree, search_term):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = f"SELECT CRECI, Nome_corretor, dt_inicio, comissao FROM Corretor WHERE Nome_corretor LIKE '%{search_term}%' OR CRECI LIKE '%{search_term}%'"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Limpa a Treeview antes de inserir os novos resultados
        for row in tree.get_children():
            tree.delete(row)
        # Insere os resultados da pesquisa
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

# Função para criar a interface principal
def create_main_interface(root):
    # Frame para a aba lateral
    sidebar = tk.Frame(root, bg="#2E4053")
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    # Frame para o conteúdo dinâmico
    content_frame = tk.Frame(root, bg="#F4F6F7")
    content_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    # Função para mostrar o conteúdo de uma opção
    def show_content(frame):
        # Oculta todos os frames de conteúdo
        for widget in content_frame.winfo_children():
            widget.pack_forget()
        # Mostra o frame correspondente
        frame.pack(expand=True, fill="both")

    # Cria os frames de conteúdo para cada opção
    clientes_frame = tk.Frame(content_frame, bg="#F4F6F7")
    corretores_frame = tk.Frame(content_frame, bg="#F4F6F7")
    consultas_frame = tk.Frame(content_frame, bg="#F4F6F7")
    insert_frame = tk.Frame(content_frame, bg="#F4F6F7")
    update_delete_frame = tk.Frame(content_frame, bg="#F4F6F7")

    # Adiciona conteúdo ao frame de Clientes
    search_clientes_frame = tk.Frame(clientes_frame, bg="#F4F6F7")
    search_clientes_frame.pack(fill="x", pady=10)

    search_clientes_entry = tk.Entry(search_clientes_frame, font=("Arial", 12), width=30)
    search_clientes_entry.pack(side="left", padx=10)

    search_clientes_button = tk.Button(search_clientes_frame, text="Pesquisar", font=("Arial", 12),
                                       command=lambda: search_clientes(clientes_tree, search_clientes_entry.get()))
    search_clientes_button.pack(side="left")

    clientes_tree = ttk.Treeview(clientes_frame, columns=("CPF", "Nome", "Estado Civil"), show="headings")
    clientes_tree.heading("CPF", text="CPF")
    clientes_tree.heading("Nome", text="Nome")
    clientes_tree.heading("Estado Civil", text="Estado Civil")
    clientes_tree.pack(expand=True, fill="both", padx=10, pady=10)
    load_clientes(clientes_tree)

    # Adiciona conteúdo ao frame de Corretores
    search_corretores_frame = tk.Frame(corretores_frame, bg="#F4F6F7")
    search_corretores_frame.pack(fill="x", pady=10)

    search_corretores_entry = tk.Entry(search_corretores_frame, font=("Arial", 12), width=30)
    search_corretores_entry.pack(side="left", padx=10)

    search_corretores_button = tk.Button(search_corretores_frame, text="Pesquisar", font=("Arial", 12),
                                         command=lambda: search_corretores(corretores_tree, search_corretores_entry.get()))
    search_corretores_button.pack(side="left")

    corretores_tree = ttk.Treeview(corretores_frame, columns=("CRECI", "Nome", "Data Início", "Comissão"), show="headings")
    corretores_tree.heading("CRECI", text="CRECI")
    corretores_tree.heading("Nome", text="Nome")
    corretores_tree.heading("Data Início", text="Data Início")
    corretores_tree.heading("Comissão", text="Comissão")
    corretores_tree.pack(expand=True, fill="both", padx=10, pady=10)
    load_corretores(corretores_tree)

    # Adiciona conteúdo ao frame de Consultas
    consultas = [
        ("Clientes e Propostas", query_cliente_proposta),
        ("Imóveis Cadastrados", query_imovel),
        ("Propostas para Imóvel", query_proposta_imovel),
        ("Comissões dos Corretores (2022)", query_comissao_2022),
        ("Top 3 Imóveis Mais Caros", query_imoveis_caros),
        ("Imóveis com Mais de 2 Vagas", query_imoveis_com_vagas),
        ("Imóveis Acima de 600k", query_imoveis_acima_600k),
        ("Cidades com Mais Imóveis", query_cidades_imoveis),
        ("Imóveis com Mais de 4 Cômodos", query_imoveis_com_4_comodos),
        ("Imóveis Sem Visitas", query_imoveis_sem_visitas)
    ]

    for i, (text, command) in enumerate(consultas):
        row = i // 2
        column = i % 2
        tk.Button(consultas_frame, text=text, command=command, font=("Arial", 12), width=30, height=2).grid(row=row, column=column, padx=10, pady=10)

    # Adiciona conteúdo ao frame de Inserção
    tk.Button(insert_frame, text="Inserir Corretor", command=insert_corretor, font=("Arial", 12), width=20, height=2).pack(pady=10)
    tk.Button(insert_frame, text="Inserir Imóvel", command=insert_imovel, font=("Arial", 12), width=20, height=2).pack(pady=10)

    # Adiciona conteúdo ao frame de Atualização/Remoção
    tk.Button(update_delete_frame, text="Atualizar Registro", command=update_record, font=("Arial", 12), width=20, height=2).pack(pady=10)
    tk.Button(update_delete_frame, text="Remover Registro", command=delete_record, font=("Arial", 12), width=20, height=2).pack(pady=10)

    # Botões para as opções na aba lateral
    tk.Button(sidebar, text="Clientes", font=("Arial", 14), bg="#2E4053", fg="white", bd=0,
              command=lambda: show_content(clientes_frame)).pack(fill="x", pady=5, padx=10)
    tk.Button(sidebar, text="Corretores", font=("Arial", 14), bg="#2E4053", fg="white", bd=0,
              command=lambda: show_content(corretores_frame)).pack(fill="x", pady=5, padx=10)
    tk.Button(sidebar, text="Consultas", font=("Arial", 14), bg="#2E4053", fg="white", bd=0,
              command=lambda: show_content(consultas_frame)).pack(fill="x", pady=5, padx=10)
    tk.Button(sidebar, text="Inserção", font=("Arial", 14), bg="#2E4053", fg="white", bd=0,
              command=lambda: show_content(insert_frame)).pack(fill="x", pady=5, padx=10)
    tk.Button(sidebar, text="Atualização/Remoção", font=("Arial", 14), bg="#2E4053", fg="white", bd=0,
              command=lambda: show_content(update_delete_frame)).pack(fill="x", pady=5, padx=10)
              
def create_initial_menu():
    root = tk.Tk()
    root.title("Banco de Dados - Imobiliária")
    root.geometry("900x600")

    # Frame para o conteúdo da tela inicial
    initial_frame = tk.Frame(root, bg="#F4F6F7")
    initial_frame.pack(expand=True, fill="both")

    # Mensagem de boas-vindas (centralizada)
    welcome_label = tk.Label(initial_frame, text="Bem-vindo\nImobiliária - CEFET", font=("Arial", 24), bg="#F4F6F7")
    welcome_label.pack(expand=True, pady=(0, 20))  # Centraliza verticalmente e adiciona espaço abaixo

    # Botão para acessar o sistema (centralizado)
    access_button = tk.Button(initial_frame, text="Acessar Sistema", font=("Arial", 16), bg="#2E4053", fg="white", bd=0,
                              command=lambda: [initial_frame.destroy(), create_main_interface(root)])
    access_button.pack(expand=True, pady=(0, 50))  # Centraliza verticalmente e adiciona espaço abaixo

    root.mainloop()

# Executa a tela de menu inicial
create_initial_menu()