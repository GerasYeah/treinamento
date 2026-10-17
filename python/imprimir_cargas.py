
# -*- coding: utf-8 -*-

import uno
import json
import os


def mostrar_mensagem(doc, titulo, mensagem, erro=False):
    """Exibe uma mensagem na tela do LibreOffice."""

    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    toolkit = smgr.createInstanceWithContext(
        "com.sun.star.awt.Toolkit", ctx
    )

    parent = doc.CurrentController.Frame.ContainerWindow

    tipo = uno.getConstantByName(
        "com.sun.star.awt.MessageBoxType.ERRORBOX"
        if erro else
        "com.sun.star.awt.MessageBoxType.INFOBOX"
    )

    botoes = uno.getConstantByName(
        "com.sun.star.awt.MessageBoxButtons.BUTTONS_OK"
    )

    caixa = toolkit.createMessageBox(
        parent, tipo, botoes, titulo, mensagem
    )

    caixa.execute()


def substituir_texto(doc, texto_antigo, texto_novo):
    """
    Substitui todas as ocorrências do texto informado
    no documento Writer atualmente aberto.
    """

    # Cria um descritor de substituição do Writer.
    descritor = doc.createReplaceDescriptor()

    # Define o texto que será procurado.
    descritor.SearchString = texto_antigo

    # Define o texto que será inserido.
    descritor.ReplaceString = texto_novo

    # Evita diferenciar maiúsculas de minúsculas.
    descritor.SearchCaseSensitive = True

    # Executa a substituição no documento.
    doc.replaceAll(descritor)


def imprimir_documento(doc):
    """
    Envia o documento atual para a impressora padrão.
    Aguarda a conclusão do trabalho de impressão.
    """

    propriedades = []

    # Cria a propriedade Wait, utilizada para aguardar
    # a conclusão da impressão antes de continuar.
    wait = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )
    wait.Name = "Wait"
    wait.Value = True

    propriedades.append(wait)

    # Envia o documento para impressão.
    doc.print_(tuple(propriedades))


def selecionar_arquivo(ctx):
    """
    Abre a janela de seleção de arquivo.
    Aceita arquivos JSON e TXT.
    Retorna o caminho local ou None se cancelar.
    """

    picker = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker", ctx
    )

    # Inicializa a janela no modo de abertura de arquivo.
    picker.initialize((
        uno.getConstantByName(
            "com.sun.star.ui.dialogs.TemplateDescription.FILEOPEN_SIMPLE"
        ),
    ))

    # Adiciona os filtros disponíveis.
    picker.appendFilter("Arquivos JSON", "*.json")
    picker.appendFilter("Arquivos de texto", "*.txt")

    picker.setCurrentFilter("Arquivos JSON")

    # Abre a janela e verifica se o usuário confirmou.
    if picker.execute() != 1:
        return None

    # Converte a URL retornada pelo LibreOffice
    # para um caminho de arquivo do sistema operacional.
    return uno.fileUrlToSystemPath(picker.getFiles()[0])


def ImprimirDocumentos(*args):
    """
    Macro principal.

    1. Seleciona o arquivo JSON/TXT.
    2. Lê e valida o array.
    3. Ignora objetos com cxs inválido ou proibido.
    4. Substitui os marcadores sequencialmente.
    5. Imprime cada objeto válido.
    6. Restaura os marcadores originais ao final.
    """

    # Obtém o documento atualmente aberto no LibreOffice.
    ctx = uno.getComponentContext()

    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )

    doc = desktop.getCurrentComponent()

    # Verifica se existe um documento Writer aberto.
    if doc is None or not doc.supportsService(
        "com.sun.star.text.TextDocument"
    ):
        return

    # Textos originais presentes no modelo.
    MARCADOR_BOX = "BOX: XX"
    MARCADOR_CARGA = "XXXXXXX"
    MARCADOR_CXS = "VOLUMES: XX"

    # Variáveis que armazenam os textos atualmente
    # presentes no documento.
    box_atual = MARCADOR_BOX
    carga_atual = MARCADOR_CARGA
    cxs_atual = MARCADOR_CXS

    # Controla a restauração dos marcadores.
    iniciou_substituicoes = False

    # Quantidade de documentos efetivamente processados.
    total_impressos = 0

    try:
        # Solicita ao usuário o arquivo de entrada.
        caminho = selecionar_arquivo(ctx)

        # Encerra se o usuário cancelar a seleção.
        if caminho is None:
            return

        # Abre o arquivo aceitando UTF-8 com ou sem BOM.
        with open(caminho, "r", encoding="utf-8-sig") as arquivo:
            dados = json.load(arquivo)

        # O conteúdo precisa ser um array JSON.
        if not isinstance(dados, list):
            raise ValueError(
                "O arquivo JSON deve conter um array de objetos."
            )

        try:
            # Percorre todos os objetos na ordem original.
            for item in dados:

                # Cada elemento precisa ser um objeto JSON.
                if not isinstance(item, dict):
                    continue

                # Obtém os valores dos campos.
                # Converte os valores para texto e trata null.
                box = item.get("box")
                carga = item.get("carga")
                cxs = item.get("cxs")

                box = "" if box is None else str(box)
                carga = "" if carga is None else str(carga)
                cxs = "" if cxs is None else str(cxs)

                # Remove espaços externos do campo cxs
                # para realizar a validação.
                cxs_validacao = cxs.strip()

                # Ignora cxs vazio ou que não seja numérico.
                if not cxs_validacao.isdigit():
                    continue

                # Ignora os valores expressamente proibidos.
                if cxs_validacao in ("0", "00", "99"):
                    continue

                # A partir daqui, o objeto é válido.
                # Marca que o documento pode precisar ser restaurado.
                iniciou_substituicoes = True

                # -------------------------------------------------
                # SUBSTITUIÇÃO DO BOX
                # -------------------------------------------------

                # Na primeira iteração válida, procura o marcador
                # original. Nas próximas, procura o valor anterior.
                substituir_texto(
                    doc,
                    box_atual,
                    "BOX: " + box
                )

                # Guarda o novo texto para a próxima iteração.
                box_atual = "BOX: " + box

                # -------------------------------------------------
                # SUBSTITUIÇÃO DA CARGA
                # -------------------------------------------------

                # Procura XXXXXXX somente na primeira iteração.
                # Depois, procura a carga da iteração anterior.
                substituir_texto(
                    doc,
                    carga_atual,
                    carga
                )

                # Atualiza a referência da carga atual.
                carga_atual = carga

                # -------------------------------------------------
                # SUBSTITUIÇÃO DOS VOLUMES
                # -------------------------------------------------

                # Procura VOLUMES: XX somente na primeira iteração.
                # Depois, procura o texto de volumes anterior.
                substituir_texto(
                    doc,
                    cxs_atual,
                    "VOLUMES: " + cxs
                )

                # Atualiza a referência dos volumes atuais.
                cxs_atual = "VOLUMES: " + cxs

                # -------------------------------------------------
                # IMPRESSÃO
                # -------------------------------------------------

                # Imprime o documento com os valores deste objeto.
                imprimir_documento(doc)

                # Incrementa o contador após a impressão.
                total_impressos += 1

        finally:
            # -----------------------------------------------------
            # RESTAURAÇÃO DOS MARCADORES ORIGINAIS
            # -----------------------------------------------------

            # Esta etapa acontece após o processamento, inclusive
            # se ocorrer uma exceção durante o laço.
            #
            # Cada busca utiliza o último valor registrado,
            # evitando procurar os marcadores originais novamente.

            if iniciou_substituicoes:

                substituir_texto(
                    doc,
                    box_atual,
                    MARCADOR_BOX
                )

                substituir_texto(
                    doc,
                    carga_atual,
                    MARCADOR_CARGA
                )

                substituir_texto(
                    doc,
                    cxs_atual,
                    MARCADOR_CXS
                )

        # Informa o resultado após a restauração.
        if total_impressos == 0:
            mostrar_mensagem(
                doc,
                "Nenhuma impressão",
                "Nenhum objeto válido foi encontrado no arquivo."
            )
        else:
            mostrar_mensagem(
                doc,
                "Processo concluído",
                "Impressões realizadas: "
                + str(total_impressos)
                + "\n\nOs marcadores originais foram restaurados."
            )

    except Exception as e:
        # Exibe erros de leitura, processamento ou impressão.
        mostrar_mensagem(
            doc,
            "Erro na macro",
            str(e),
            True
        )
