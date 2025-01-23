#include <mysql/mysql.h>
#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>

MYSQL *conn;
MYSQL_RES *res;
GtkWidget *window, *button_box, *button[10];

// Função para conectar ao banco de dados
MYSQL *connect_to_database(const char *server, const char *user, const char *password, const char *database) {
    MYSQL *conn = mysql_init(NULL);
    if (conn == NULL) {
        fprintf(stderr, "mysql_init() falhou\n");
        exit(EXIT_FAILURE);
    }

    if (mysql_real_connect(conn, server, user, password, database, 0, NULL, 0) == NULL) {
        fprintf(stderr, "Erro ao conectar: %s\n", mysql_error(conn));
        mysql_close(conn);
        exit(EXIT_FAILURE);
    }

    return conn;
}

// Função para executar uma consulta
MYSQL_RES *execute_query(MYSQL *conn, const char *query) {
    if (mysql_query(conn, query)) {
        fprintf(stderr, "Erro na consulta: %s\n", mysql_error(conn));
        mysql_close(conn);
        exit(EXIT_FAILURE);
    }

    MYSQL_RES *res = mysql_store_result(conn);
    if (res == NULL) {
        fprintf(stderr, "Erro ao obter resultado: %s\n", mysql_error(conn));
        mysql_close(conn);
        exit(EXIT_FAILURE);
    }

    return res;
}

// Função para exibir os resultados da consulta em um dialog GTK
void show_query_results(GtkWidget *widget, gpointer data) {
    int option = GPOINTER_TO_INT(data);
    const char *queries[] = {
        "SELECT distinct CPF, Nome_cliente FROM Cliente, Proposta WHERE CPF = CPF_inquilino", // Consulta 1.4.1
        "SELECT num_registro, Endereco_cidade, Endereco_rua, Endereco_num FROM Imovel", // Consulta 1.4.2
        "SELECT num_registro, valor_proposta FROM Proposta WHERE num_registro = 2", // Consulta 1.4.3
        "SELECT c.Nome_corretor, SUM(p.valor_proposta * c.comissao / 100) as total_comissao FROM Corretor as c JOIN Visita as v ON c.CRECI = v.CRECI JOIN Proposta as p ON v.num_registro = p.num_registro WHERE YEAR(p.dt_proposta) = 2022 GROUP BY c.CRECI ORDER BY total_comissao DESC LIMIT 1", // Consulta 1.4.4
        "SELECT Endereco_cidade, Endereco_rua, Endereco_num, Valor_imovel FROM Imovel ORDER BY Valor_imovel DESC LIMIT 3", // Consulta 1.4.5
        "SELECT Endereco_cidade, Endereco_rua, Vagas, Valor_imovel FROM Imovel WHERE Vagas > 2 ORDER BY Vagas DESC", // Consulta 1.4.6
        "SELECT i.Endereco_cidade, i.Endereco_rua, i.Valor_imovel FROM Imovel as i WHERE i.Valor_imovel > 600000", // Consulta 1.4.7
        "SELECT Endereco_cidade, COUNT(*) as num_imoveis FROM Imovel GROUP BY Endereco_cidade", // Consulta 1.4.8
        "SELECT Endereco_cidade, Endereco_rua, num_comodos, Valor_imovel FROM Imovel WHERE num_comodos > 4 ORDER BY num_comodos DESC", // Consulta 1.4.9
        "SELECT i.Endereco_cidade, i.Endereco_rua FROM Imovel as i LEFT JOIN Visita as v ON i.num_registro = v.num_registro WHERE v.num_registro is NULL" // Consulta 1.4.10
    };

    const char *descriptions[] = {
        "Todos os clientes cadastrados e que já fizeram alguma proposta.",
        "Todos os imóveis cadastrados (alugados ou não).",
        "Listar as ofertas feitas para um determinado imóvel.",
        "Informar o corretor que obteve maior rendimento no ano de 2022.",
        "Listar os 3 imóveis mais caros.",
        "Imóveis com mais de 2 vagas de garagem.",
        "Imóveis com valor superior a 600 mil.",
        "Cidades com maior número de imóveis cadastrados.",
        "Imóveis com mais de 4 cômodos.",
        "Imóveis que não receberam nenhuma proposta."
    };

    // Executa a consulta SQL
    res = execute_query(conn, queries[option - 1]);
    
    // Criar um novo dialog para exibir os resultados
    GtkWidget *dialog = gtk_dialog_new_with_buttons("Resultados da Consulta", GTK_WINDOW(window), GTK_DIALOG_MODAL, "Fechar", GTK_RESPONSE_CLOSE, NULL);
    GtkWidget *text_view = gtk_text_view_new();
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(text_view));
    
    unsigned int num_fields = mysql_num_fields(res);
    MYSQL_ROW row;
    char result[1024] = "";
    
    // Concatenar os resultados no buffer
    while ((row = mysql_fetch_row(res)) != NULL) {
        for (unsigned int i = 0; i < num_fields; i++) {
            sprintf(result + strlen(result), "%s\t", row[i] ? row[i] : "NULL");
        }
        strcat(result, "\n");
    }

    // Adicionar a descrição ao resultado
    strcat(result, "\nDescrição da consulta: ");
    strcat(result, descriptions[option - 1]);
    
    gtk_text_buffer_set_text(buffer, result, -1);

    // Acessar o conteúdo do dialog corretamente
    GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(dialog));
    gtk_box_pack_start(GTK_BOX(content_area), text_view, TRUE, TRUE, 0);
    gtk_widget_show_all(dialog);

    // Conectar o botão "Fechar" ao fechamento do dialog
    g_signal_connect(dialog, "response", G_CALLBACK(gtk_widget_destroy), NULL);

    mysql_free_result(res);
}

// Função para inicializar a interface gráfica
void init_gui(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Sistema Imobiliária");
    gtk_window_set_default_size(GTK_WINDOW(window), 1000, 800);
    
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    button_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(window), button_box);

    const char *labels[] = {
        "Consulta 1.4.1 - Todos os clientes cadastrados e que já fizeram alguma proposta.",
        "Consulta 1.4.2 - Todos os imóveis cadastrados (alugados ou não).",
        "Consulta 1.4.3 - Listar as ofertas feitas para um determinado imóvel.",
        "Consulta 1.4.4 - Informar o corretor que obteve maior rendimento no ano de 2022.",
        "Consulta 1.4.5 - Listar os 3 imóveis mais caros.",
        "Consulta 1.4.6 - Imóveis com mais de 2 vagas de garagem.",
        "Consulta 1.4.7 - Imóveis com valor superior a 700 mil.",
        "Consulta 1.4.8 - Cidades com maior número de imóveis cadastrados.",
        "Consulta 1.4.9 - Imóveis com mais de 4 cômodos.",
        "Consulta 1.4.10 - Imóveis que não receberam nenhuma proposta."
    };

    // Criar os botões e associar com cada consulta
    for (int i = 0; i < 10; i++) {
        button[i] = gtk_button_new_with_label(labels[i]);
        g_signal_connect(button[i], "clicked", G_CALLBACK(show_query_results), GINT_TO_POINTER(i + 1));
        gtk_box_pack_start(GTK_BOX(button_box), button[i], TRUE, TRUE, 0);
    }
    gtk_widget_show_all(window);
}

int main(int argc, char *argv[]) {
    const char *server = "localhost";
    const char *user = "root";
    const char *password = "Password123!";
    const char *database = "imobiliaria";

    conn = connect_to_database(server, user, password, database);
    
    init_gui(argc, argv);

    gtk_main();

    mysql_close(conn);
    return EXIT_SUCCESS;
}
