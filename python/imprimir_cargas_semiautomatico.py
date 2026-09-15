import uno
import re


# Valor usado na primeira execução e pelo botão Restaurar
VALOR_INICIAL = "02 125XXXX XX"


def main():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    # Obtém o Desktop do LibreOffice
    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

    # Obtém o documento Writer atualmente aberto
    doc = desktop.getCurrentComponent()

    if not doc:
        mostrar_mensagem(
            ctx,
            "Nenhum documento está aberto."
        )
        return

    criar_dialogo(ctx, doc)


def criar_dialogo(ctx, doc):
    smgr = ctx.ServiceManager

    # Modelo do diálogo
    dialog_model = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel",
        ctx
    )

    dialog_model.Width = 220
    dialog_model.Height = 120
    dialog_model.Title = "Impressão de cargas semiautomático"


    # Texto de cabeçalho
    titulo = dialog_model.createInstance(
        "com.sun.star.awt.UnoControlFixedTextModel"
    )

    titulo.PositionX = 10
    titulo.PositionY = 8
    titulo.Width = 200
    titulo.Height = 12
    titulo.Label = "box carga volumes"

    dialog_model.insertByName(
        "titulo",
        titulo
    )


    # Caixa de texto
    campo = dialog_model.createInstance(
        "com.sun.star.awt.UnoControlEditModel"
    )

    campo.PositionX = 10
    campo.PositionY = 25
    campo.Width = 200
    campo.Height = 14

    # Valor inicial
    campo.Text = VALOR_INICIAL

    dialog_model.insertByName(
        "campo",
        campo
    )


    # Botão Imprimir
    botao_imprimir = dialog_model.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    botao_imprimir.PositionX = 10
    botao_imprimir.PositionY = 50
    botao_imprimir.Width = 60
    botao_imprimir.Height = 18

    botao_imprimir.Label = "Imprimir"

    dialog_model.insertByName(
        "imprimir",
        botao_imprimir
    )


    # Botão Restaurar
    botao_restaurar = dialog_model.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    botao_restaurar.PositionX = 80
    botao_restaurar.PositionY = 50
    botao_restaurar.Width = 60
    botao_restaurar.Height = 18

    botao_restaurar.Label = "Restaurar"

    dialog_model.insertByName(
        "restaurar",
        botao_restaurar
    )


    # Botão Fechar
    botao_fechar = dialog_model.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    botao_fechar.PositionX = 150
    botao_fechar.PositionY = 50
    botao_fechar.Width = 60
    botao_fechar.Height = 18

    botao_fechar.Label = "Fechar"

    dialog_model.insertByName(
        "fechar",
        botao_fechar
    )


    # Cria o diálogo
    dialog = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog",
        ctx
    )

    dialog.setModel(dialog_model)


    # Obtém os controles
    campo_controle = dialog.getControl("campo")
    imprimir_controle = dialog.getControl("imprimir")
    restaurar_controle = dialog.getControl("restaurar")
    fechar_controle = dialog.getControl("fechar")


    # Guarda os valores usados na última impressão
    estado = {
        "box_anterior": None,
        "carga_anterior": None,
        "volumes_anterior": None
    }


    # Listener do botão Imprimir
    imprimir_controle.addActionListener(
        ActionListener(
            lambda event: processar_impressao(
                ctx,
                doc,
                campo_controle,
                estado
            )
        )
    )


    # Listener do botão Restaurar
    restaurar_controle.addActionListener(
        ActionListener(
            lambda event: restaurar(
                campo_controle
            )
        )
    )


    # Listener do botão Fechar
    fechar_controle.addActionListener(
        ActionListener(
            lambda event: dialog.endExecute()
        )
    )


    # Listener do Enter
    campo_controle.addKeyListener(
        KeyListener(
            lambda event: processar_impressao(
                ctx,
                doc,
                campo_controle,
                estado
            )
        )
    )


    # Mostra o diálogo
    dialog.setVisible(True)

    campo_controle.setFocus()


def processar_impressao(
    ctx,
    doc,
    campo,
    estado
):

    texto = campo.getText()

    # Divide o texto pelos espaços
    partes = texto.strip().split()

    if len(partes) != 3:
        mostrar_mensagem(
            ctx,
            "Digite no formato:\n\n"
            "02 1254567 10"
        )

        campo.setFocus()
        return


    box = partes[0]
    carga = partes[1]
    volumes = partes[2]


    # BOX precisa ter exatamente 2 dígitos
    if not re.fullmatch(r"\d{2}", box):

        mostrar_mensagem(
            ctx,
            "O BOX deve ter exatamente 2 dígitos.\n\n"
            "Exemplo: 02"
        )

        campo.setFocus()
        return


    # CARGA precisa ter exatamente 7 dígitos
    if not re.fullmatch(r"\d{7}", carga):

        mostrar_mensagem(
            ctx,
            "A carga deve ter exatamente 7 dígitos.\n\n"
            "Exemplo: 1254567"
        )

        campo.setFocus()
        return


    # VOLUMES precisa ter exatamente 2 dígitos
    if not re.fullmatch(r"\d{2}", volumes):

        mostrar_mensagem(
            ctx,
            "Volumes deve ter exatamente 2 dígitos.\n\n"
            "Exemplo: 10"
        )

        campo.setFocus()
        return


    # Monta os textos completos usados no documento
    box_texto = "BOX: " + box
    volumes_texto = "VOLUMES: " + volumes


    # Primeira impressão
    if estado["box_anterior"] is None:

        substituir(
            doc,
            "BOX: {XX}",
            box_texto
        )

        substituir(
            doc,
            "{CARGA}",
            carga
        )

        substituir(
            doc,
            "VOLUMES: {XX}",
            volumes_texto
        )

    else:

        # Próximas impressões.
        #
        # Substituímos os textos completos anteriores,
        # evitando substituir números isoladamente.

        substituir(
            doc,
            estado["box_anterior"],
            box_texto
        )

        substituir(
            doc,
            estado["carga_anterior"],
            carga
        )

        substituir(
            doc,
            estado["volumes_anterior"],
            volumes_texto
        )


    # Imprime automaticamente
    imprimir(doc)


    # Guarda os valores usados nesta impressão
    estado["box_anterior"] = box_texto
    estado["carga_anterior"] = carga
    estado["volumes_anterior"] = volumes_texto


    # Mantém somente os 3 primeiros dígitos da carga
    # e substitui os 4 últimos por X.
    #
    # Exemplo:
    # 1254567 -> 125XXXX
    carga_proxima = carga[:3] + "XXXX"


    # Volumes volta para XX
    volumes_proximo = "XX"


    # Prepara a próxima entrada
    campo.setText(
        box + " " +
        carga_proxima + " " +
        volumes_proximo
    )

    campo.setFocus()


def restaurar(campo):
    # Volta para o valor inicial
    campo.setText(VALOR_INICIAL)
    campo.setFocus()


def substituir(doc, procurar, substituir_por):
    # Cria o descritor de substituição
    descriptor = doc.createReplaceDescriptor()

    descriptor.SearchString = procurar
    descriptor.ReplaceString = substituir_por

    # Substitui preservando a formatação do documento
    doc.replaceAll(descriptor)


def imprimir(doc):
    # Configuração da impressão automática
    propriedades = []

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = "Wait"
    prop.Value = True

    propriedades.append(prop)

    doc.print(tuple(propriedades))


class ActionListener:
    """
    Listener utilizado pelos botões do diálogo.
    """

    def __init__(self, callback):
        self.callback = callback

    def actionPerformed(self, event):
        self.callback(event)

    def disposing(self, event):
        pass


class KeyListener:
    """
    Listener utilizado para detectar o Enter
    dentro da caixa de texto.
    """

    def __init__(self, callback):
        self.callback = callback

    def keyPressed(self, event):

        # 1280 = Enter
        if event.KeyCode == 1280:
            self.callback(event)

    def keyReleased(self, event):
        pass

    def disposing(self, event):
        pass


def mostrar_mensagem(ctx, texto):
    smgr = ctx.ServiceManager

    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

    doc = desktop.getCurrentComponent()

    parent = None

    if doc:
        try:
            parent = (
                doc.CurrentController
                .Frame
                .ContainerWindow
            )
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