
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

    # Define o tipo da caixa de mensagem usando valores numéricos.
    tipo = 3 if erro else 1
    botoes = 1

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

    # Diferencia maiúsculas de minúsculas.
    descritor.SearchCaseSensitive = True

    # Executa a substituição no documento.
    doc.replaceAll(descritor)


def imprimir_documento(doc):
    """Envia o documento atual para a impressora padrão."""

    propriedades = []

    # Aguarda a conclusão do trabalho de impressão.
    wait = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )
    wait.Name = "Wait"
    wait.Value = True

    propriedades.append(wait)

    # Envia o documento para impressão.
    doc.print(tuple(propriedades))


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

    # Converte a URL retornada para um caminho local.
    return uno.fileUrlToSystemPath(picker.getFiles()[0])


def ImprimirDocumentos(*args):
    """
    Macro principal.

    1. Seleciona o arquivo JSON/TXT.
    2. Lê e valida o array.
    3. Remove objetos com box inválido.
    4. Ordena os objetos pelo número do box.
    5. Ignora objetos com cxs inválido ou proibido.
    6. Formata cxs com zero à esquerda quando necessário.
    7. Substitui os marcadores sequencialmente.
    8. Imprime cada objeto válido.
    9. Soma os volumes e contabiliza cargas por box.
    10. Exibe o resumo completo ao final.
    11. Restaura os marcadores originais.
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

    # Variáveis que armazenam os textos atuais.
    box_atual = MARCADOR_BOX
    carga_atual = MARCADOR_CARGA
    cxs_atual = MARCADOR_CXS

    # Controla a restauração dos marcadores.
    iniciou_substituicoes = False

    # Quantidade de documentos efetivamente impressos.
    total_impressos = 0

    # Soma dos volumes de todos os objetos impressos.
    total_cxs = 0

    # Armazena a quantidade de cargas e caixas por box.
    # Exemplo: {2: {"cargas": 5, "caixas": 25}}
    resumo_boxes = {}

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

        # ---------------------------------------------------------
        # VALIDAÇÃO E ORDENAÇÃO DOS BOXES
        # ---------------------------------------------------------

        dados_validos = []

        # Verifica cada objeto antes de ordenar.
        for item in dados:

            # Cada elemento precisa ser um objeto JSON.
            if not isinstance(item, dict):
                continue

            # Obtém o box e converte para texto.
            box = item.get("box")
            box = "" if box is None else str(box).strip()

            # Ignora boxes vazios ou não numéricos.
            if not box.isdigit():
                continue

            # Converte o box para número inteiro.
            box_numero = int(box)

            # Ignora o box zero, incluindo "00", "000" etc.
            if box_numero <= 0:
                continue

            # Guarda o objeto e seu valor numérico para ordenar.
            dados_validos.append((box_numero, item))

        # Ordena os objetos pelo número do box, em ordem crescente.
        dados_validos.sort(key=lambda elemento: elemento[0])

        # Recupera os objetos na ordem correta.
        dados = [elemento[1] for elemento in dados_validos]

        try:
            # Percorre os objetos na ordem crescente dos boxes.
            for item in dados:

                # Obtém os valores dos campos.
                box = item.get("box")
                carga = item.get("carga")
                cxs = item.get("cxs")

                # Converte os valores para texto e trata null.
                box = "" if box is None else str(box).strip()
                carga = "" if carga is None else str(carga)
                cxs = "" if cxs is None else str(cxs)

                # Remove espaços externos para validação.
                cxs_validacao = cxs.strip()

                # Ignora cxs vazio ou não numérico.
                if not cxs_validacao.isdigit():
                    continue

                # Ignora os valores expressamente proibidos.
                if cxs_validacao in ("0", "00", "99"):
                    continue

                # Converte cxs para número inteiro.
                cxs_numero = int(cxs_validacao)

                # Formata com dois dígitos quando menor que 10.
                cxs = (
                    "{:02d}".format(cxs_numero)
                    if cxs_numero < 10
                    else cxs_validacao
                )

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

                # Procura o marcador original na primeira iteração.
                # Nas próximas, procura o texto anterior.
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

                # Atualiza os totais gerais.
                total_impressos += 1
                total_cxs += cxs_numero

                # -------------------------------------------------
                # CONTAGEM POR BOX
                # -------------------------------------------------

                # Utiliza o número inteiro como chave para agrupar
                # boxes equivalentes, como "2" e "02".
                box_numero = int(box)

                # Inicializa o registro caso seja o primeiro
                # objeto impresso deste box.
                if box_numero not in resumo_boxes:
                    resumo_boxes[box_numero] = {
                        "cargas": 0,
                        "caixas": 0
                    }

                # Conta uma carga impressa neste box.
                resumo_boxes[box_numero]["cargas"] += 1

                # Soma as caixas deste objeto ao box correspondente.
                resumo_boxes[box_numero]["caixas"] += cxs_numero

        finally:
            # -----------------------------------------------------
            # RESTAURAÇÃO DOS MARCADORES ORIGINAIS
            # -----------------------------------------------------

            # Executada após o processamento do laço.
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

        # ---------------------------------------------------------
        # RESUMO FINAL
        # ---------------------------------------------------------

        if total_impressos == 0:
            mostrar_mensagem(
                doc,
                "Nenhuma impressão",
                "Nenhum objeto válido foi encontrado no arquivo."
            )

        else:
            # Monta o resumo com os boxes em ordem crescente.
            linhas_resumo = []

            for box_numero in sorted(resumo_boxes.keys()):

                cargas_box = resumo_boxes[box_numero]["cargas"]
                caixas_box = resumo_boxes[box_numero]["caixas"]

                # Formata box, cargas e caixas com zero à esquerda
                # quando os respectivos valores são menores que 10.
                linhas_resumo.append(
                    "BOX {:02d}: {:02d} CARGAS | {:02d} CAIXAS".format(
                        box_numero,
                        cargas_box,
                        caixas_box
                    )
                )

            # Adiciona uma linha em branco antes dos totais.
            linhas_resumo.append("")

            # Adiciona os totais gerais.
            linhas_resumo.append(
                "TOTAL: {:02d} CARGAS | {:02d} CAIXAS".format(
                    total_impressos,
                    total_cxs
                )
            )

            # Exibe o resumo completo em uma única mensagem.
            mostrar_mensagem(
                doc,
                "Processo concluído",
                "\n".join(linhas_resumo)
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
