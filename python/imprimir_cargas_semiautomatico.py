import uno
import unohelper
import re

from com.sun.star.awt import XActionListener
from com.sun.star.awt import XKeyListener


# Valor inicial do campo e também usado pelo botão Restaurar
VALOR_INICIAL = "02 125XXXX XX"


def main():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager

    desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    )

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


    # Cabeçalho
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
    botao_imprimir.DefaultButton = True

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


    # Mantemos os listeners em variáveis para que
    # eles continuem existindo enquanto o diálogo estiver aberto.
    listener_imprimir = BotaoListener(
        lambda event: processar_impressao(
            ctx,
            doc,
            campo_controle,
            estado
        )
    )

    listener_restaurar = BotaoListener(
        lambda event: restaurar(
            campo_controle
        )
    )

    listener_fechar = BotaoListener(
        lambda event: dialog.endExecute()
    )

    listener_teclado = TecladoListener(
        lambda event: processar_impressao(
            ctx,
            doc,
            campo_controle,
            estado
        )
    )


    # Registra os listeners
    imprimir_controle.addActionListener(
        listener_imprimir
    )

    restaurar_controle.addActionListener(
        listener_restaurar
    )

    fechar_controle.addActionListener(
        listener_fechar
    )

    campo_controle.addKeyListener(
        listener_teclado
    )


    # Exibe o diálogo
    dialog.setVisible(True)

    campo_controle.setFocus()


def processar_impressao(
    ctx,
    doc,
    campo,
    estado
):

    texto = campo.getText().strip()

    # Divide os três valores pelos espaços
    partes = texto.split()

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


    # Carga precisa ter exatamente 7 dígitos
    if not re.fullmatch(r"\d{7}", carga):

        mostrar_mensagem(
            ctx,
            "A carga deve ter exatamente 7 dígitos.\n\n"
            "Exemplo: 1254567"
        )

        campo.setFocus()
        return


    # Volumes precisa ter exatamente 2 dígitos
    if not re.fullmatch(r"\d{2}", volumes):

        mostrar_mensagem(
            ctx,
            "Volumes deve ter exatamente 2 dígitos.\n\n"
            "Exemplo: 10"
        )

        campo.setFocus()
        return


    # Textos completos usados na substituição
    box_texto = "BOX: " + box
    volumes_texto = "VOLUMES: " + volumes


    if estado["box_anterior"] is None:

        # Primeira impressão:
        #
        # BOX: {XX}
        # {CARGA}
        # VOLUMES: {XX}

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

        # Próximas impressões:
        #
        # BOX: 02 -> BOX: 03
        # 1254567 -> 1254568
        # VOLUMES: 10 -> VOLUMES: 05
        #
        # Nunca procuramos apenas "02", "10", etc.

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


    # Guarda os valores completos que acabaram
    # de ser inseridos.
    estado["box_anterior"] = box_texto
    estado["carga_anterior"] = carga
    estado["volumes_anterior"] = volumes_texto


    # Mantém os três primeiros dígitos da carga
    # e apaga os quatro últimos.
    #
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

    # Restaura somente o conteúdo da caixa de texto
    campo.setText(VALOR_INICIAL)
    campo.setFocus()


def substituir(doc, procurar, substituir_por):

    descriptor = doc.createReplaceDescriptor()

    descriptor.SearchString = procurar
    descriptor.ReplaceString = substituir_por

    # Mantém a formatação existente do documento
    doc.replaceAll(descriptor)


def imprimir(doc):

    # Mantemos exatamente a configuração
    # de impressão automática.
    propriedades = []

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = "Wait"
    prop.Value = True

    propriedades.append(prop)

    doc.print(tuple(propriedades))


class BotaoListener(
    unohelper.Base,
    XActionListener
):

    def __init__(self, callback):
        self.callback = callback

    def actionPerformed(self, event):
        self.callback(event)

    def disposing(self, event):
        pass


class TecladoListener(
    unohelper.Base,
    XKeyListener
):

    def __init__(self, callback):
        self.callback = callback

    def keyPressed(self, event):

        # Enter
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