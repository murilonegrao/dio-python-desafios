import PyPDF2

def extrairPagina(caminho_entrada, pagina):
    pdf_file = open(caminho_entrada, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    page = pdf_reader.pages[pagina - 1]

    pdf_writer = PyPDF2.PdfWriter()
    pdf_writer.add_page(page)

    with open(f'página_extraida_{pagina}.pdf', 'wb') as output:
        pdf_writer.write(output)

    return f'pagina_extraida_{pagina}.pdf'

caminho_arquivo = input('Digite o caminho do arquivo: ')
pagina = int(input('Digite o número da página que você precisa extrair: '))

caminho_saida = extrairPagina(caminho_arquivo, pagina)

print('O arquivo pdf foi extraído e salvo em :', caminho_saida)
