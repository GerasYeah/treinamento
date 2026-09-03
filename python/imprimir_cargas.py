import uno
import json


def main():
    """
    Macro principal.
    Solicita ao usuário o arquivo JSON e inicia a impressão.
    """

    # Documento atualmente aberto
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

    doc = desktop.getCurrentComponent()

    if not doc:
        mostrar_mensagem("Nenhum documento está aberto.")
        return

    # Solicita o arquivo JSON
    json_path = selecionar_arquivo(ctx)

    if not json_path:
        return

    try:
        # Lê o JSON
        with open(json_path, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

    except Exception as e:
        mostrar_mensagem(
            "Erro ao abrir o JSON:\n\n" + str(e)
        )
        return

    # O JSON deve ser diretamente uma lista
    if not isinstance(dados, list):
        mostrar_mensagem(
            "O JSON precisa ser uma lista."
        )
        return

    # Processa cada item
    for item in dados:

        if "box" not in item:
            continue

        if "carga" not in item:
            continue

        if "cxs" not in item:
            continue

        # Converte tudo para string
        box = str(item["box"])
        carga = str(item["carga"])
        cxs = str(item["cxs"])

        # Substitui os placeholders
        substituir(doc, "{BOX}", box)
        substituir(doc, "{CARGA}", carga)
        substituir(doc, "{CXS}", cxs)

        # Imprime
        imprimir(doc)

        # Volta os placeholders para o próximo item
        substituir(doc, box, "{BOX}")
        substituir(doc, carga, "{CARGA}")
        substituir(doc, cxs, "{CXS}")

    mostrar_mensagem(
        "Impressão concluída.\n\n"
        "Total de itens: " + str(len(dados))
    )


def selecionar_arquivo(ctx):
    """
    Abre o seletor de arquivos do LibreOffice
    e retorna o caminho do JSON selecionado.
    """

    smgr = ctx.ServiceManager

    file_picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker",
        ctx
    )

    file_picker.setTitle("Selecione o arquivo JSON")

    file_picker.appendFilter(
        "Arquivos JSON",
        "*.json"
    )

    file_picker.setMultiSelectionMode(False)

    resultado = file_picker.execute()

    if resultado != 1:
        return None

    arquivos = file_picker.getFiles()

    if not arquivos:
        return None

    return uno.fileUrlToSystemPath(arquivos[0])


def substituir(doc, procurar, substituir_por):
    """
    Substitui todas as ocorrências de um texto
    no documento atual.
    """

    descriptor = doc.createReplaceDescriptor()

    descriptor.SearchString = procurar
    descriptor.ReplaceString = substituir_por

    doc.replaceAll(descriptor)


def imprimir(doc):
    """
    Imprime o documento sem abrir a caixa
    de diálogo de impressão.
    """

    propriedades = []

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = "Wait"
    prop.Value = True

    propriedades.append(prop)

    doc.print(tuple(propriedades))


def mostrar_mensagem(texto):
    """
    Mostra uma mensagem para o usuário.
    """

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