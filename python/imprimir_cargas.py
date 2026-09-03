import uno
import json


def main():
    # Obtém o contexto atual do LibreOffice
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    # Obtém o Desktop do LibreOffice
    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

    # Documento Writer atualmente aberto
    doc = desktop.getCurrentComponent()

    if not doc:
        mostrar_mensagem("Nenhum documento está aberto.")
        return

    # Abre o seletor para escolher o arquivo JSON
    json_path = selecionar_arquivo(ctx)

    if not json_path:
        return

    # Carrega o JSON
    try:
        with open(json_path, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

    except Exception as e:
        mostrar_mensagem(
            "Erro ao abrir o JSON:\n\n" + str(e)
        )
        return

    # O JSON precisa ser uma lista
    if not isinstance(dados, list):
        mostrar_mensagem(
            "O JSON precisa ser uma lista."
        )
        return

    # Prefixos usados no documento.
    # Guardamos em variáveis para não repetir os textos.
    prefixo_box = "BOX: "
    prefixo_volumes = "VOLUMES: "

    # Essas variáveis guardarão exatamente o que foi
    # inserido na última substituição.
    box_anterior = None
    carga_anterior = None
    cxs_anterior = None

    # Indica se estamos processando o primeiro item
    primeira_carga = True

    for item in dados:

        # Ignora itens que não possuem os campos necessários
        if "box" not in item:
            continue

        if "carga" not in item:
            continue

        if "cxs" not in item:
            continue

        # Tudo é convertido para string para preservar
        # valores como "01", "05", etc.
        box = str(item["box"])
        carga = str(item["carga"])
        cxs = str(item["cxs"])

        # Montamos os textos completos que serão inseridos.
        # Exemplo:
        # "BOX: " + "01" = "BOX: 01"
        # "VOLUMES: " + "05" = "VOLUMES: 05"
        box_atual = prefixo_box + box
        cxs_atual = prefixo_volumes + cxs

        if primeira_carga:

            # Na primeira carga ainda existem os placeholders.
            #
            # Procuramos o texto completo "BOX: {XX}"
            # e não apenas "{XX}".
            substituir(
                doc,
                prefixo_box + "{XX}",
                box_atual
            )

            # A carga continua usando seu placeholder normal.
            substituir(
                doc,
                "{CARGA}",
                carga
            )

            # Da mesma forma, procuramos "VOLUMES: {XX}"
            # e não apenas "{XX}".
            substituir(
                doc,
                prefixo_volumes + "{XX}",
                cxs_atual
            )

            # A partir daqui, já não é mais a primeira carga.
            primeira_carga = False

        else:

            # Nas próximas cargas, substituímos exatamente
            # o texto que foi inserido anteriormente.
            #
            # Exemplo:
            # "BOX: 01" -> "BOX: 02"
            substituir(
                doc,
                box_anterior,
                box_atual
            )

            # A carga é substituída pelo valor anterior completo.
            #
            # Exemplo:
            # "1234567" -> "1234568"
            substituir(
                doc,
                carga_anterior,
                carga
            )

            # Para volumes, usamos o texto completo.
            #
            # Exemplo:
            # "VOLUMES: 05" -> "VOLUMES: 01"
            substituir(
                doc,
                cxs_anterior,
                cxs_atual
            )

        # Imprime o documento com os valores atuais
        imprimir(doc)

        # Guardamos os valores que acabamos de inserir.
        # Eles serão usados como alvo na próxima substituição.
        box_anterior = box_atual
        carga_anterior = carga
        cxs_anterior = cxs_atual

    mostrar_mensagem(
        "Impressão concluída.\n\n"
        "Total de itens: " + str(len(dados))
    )


def selecionar_arquivo(ctx):
    smgr = ctx.ServiceManager

    # Cria o seletor de arquivos do LibreOffice
    file_picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker",
        ctx
    )

    file_picker.setTitle("Selecione o arquivo JSON")

    # Mostra somente arquivos JSON
    file_picker.appendFilter(
        "Arquivos JSON",
        "*.json"
    )

    file_picker.setMultiSelectionMode(False)

    resultado = file_picker.execute()

    # 1 = usuário confirmou a seleção
    if resultado != 1:
        return None

    arquivos = file_picker.getFiles()

    if not arquivos:
        return None

    # Converte a URL do LibreOffice para um caminho
    # normal do Windows.
    return uno.fileUrlToSystemPath(arquivos[0])


def substituir(doc, procurar, substituir_por):
    # Cria um descritor de substituição do Writer
    descriptor = doc.createReplaceDescriptor()

    descriptor.SearchString = procurar
    descriptor.ReplaceString = substituir_por

    # Faz a substituição mantendo a formatação do documento.
    doc.replaceAll(descriptor)


def imprimir(doc):
    # Mantemos a configuração de impressão automática
    # que já estava funcionando corretamente.
    propriedades = []

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = "Wait"
    prop.Value = True

    propriedades.append(prop)

    doc.print(tuple(propriedades))


def mostrar_mensagem(texto):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

    doc = desktop.getCurrentComponent()

    parent = None

    if doc:
        try:
            parent = doc.CurrentController.Frame.ContainerWindow
        except Exception:
            pass

    toolkit = smgr.createInstanceWithContext(
        "com.sun.star.awt.Toolkit",
        ctx
    )

    box = toolkit.createMessageBox(
        parent,
        1,
        1,
        "Impressão",
        texto
    )

    box.execute()