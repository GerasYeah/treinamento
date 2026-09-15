import uno
import unohelper
import re

from com.sun.star.awt import XActionListener
from com.sun.star.awt import XKeyListener


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

    abrir_dialogo(ctx, doc)


def abrir_dialogo(ctx, doc):

    smgr = ctx.ServiceManager

    # -------------------------------------------------
    # MODELO DO DIÁLOGO
    # -------------------------------------------------

    modelo = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel",
        ctx
    )

    modelo.Width = 220
    modelo.Height = 85

    modelo.Title = "Impressão de cargas semiautomático"


    # -------------------------------------------------
    # CABEÇALHO
    # -------------------------------------------------

    titulo = modelo.createInstance(
        "com.sun.star.awt.UnoControlFixedTextModel"
    )

    titulo.PositionX = 10
    titulo.PositionY = 8
    titulo.Width = 200
    titulo.Height = 12

    titulo.Label = "box carga volumes"

    modelo.insertByName(
        "titulo",
        titulo
    )


    # -------------------------------------------------
    # CAMPO
    # -------------------------------------------------

    campo_modelo = modelo.createInstance(
        "com.sun.star.awt.UnoControlEditModel"
    )

    campo_modelo.PositionX = 10
    campo_modelo.PositionY = 24
    campo_modelo.Width = 200
    campo_modelo.Height = 14

    campo_modelo.Text = VALOR_INICIAL

    modelo.insertByName(
        "campo",
        campo_modelo
    )


    # -------------------------------------------------
    # BOTÃO IMPRIMIR
    # -------------------------------------------------

    imprimir_modelo = modelo.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    imprimir_modelo.PositionX = 10
    imprimir_modelo.PositionY = 48
    imprimir_modelo.Width = 60
    imprimir_modelo.Height = 18

    imprimir_modelo.Label = "Imprimir"

    modelo.insertByName(
        "imprimir",
        imprimir_modelo
    )


    # -------------------------------------------------
    # BOTÃO RESTAURAR
    # -------------------------------------------------

    restaurar_modelo = modelo.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    restaurar_modelo.PositionX = 80
    restaurar_modelo.PositionY = 48
    restaurar_modelo.Width = 60
    restaurar_modelo.Height = 18

    restaurar_modelo.Label = "Restaurar"

    modelo.insertByName(
        "restaurar",
        restaurar_modelo
    )


    # -------------------------------------------------
    # BOTÃO FECHAR
    # -------------------------------------------------

    fechar_modelo = modelo.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    )

    fechar_modelo.PositionX = 150
    fechar_modelo.PositionY = 48
    fechar_modelo.Width = 60
    fechar_modelo.Height = 18

    fechar_modelo.Label = "Fechar"

    modelo.insertByName(
        "fechar",
        fechar_modelo
    )


    # -------------------------------------------------
    # CONTROLE DO DIÁLOGO
    # -------------------------------------------------

    dialogo = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog",
        ctx
    )

    dialogo.setModel(modelo)


    # -------------------------------------------------
    # CONTROLES
    # -------------------------------------------------

    campo = dialogo.getControl("campo")
    botao_imprimir = dialogo.getControl("imprimir")
    botao_restaurar = dialogo.getControl("restaurar")
    botao_fechar = dialogo.getControl("fechar")


    # -------------------------------------------------
    # ESTADO
    # -------------------------------------------------

    estado = {
        "box_anterior": None,
        "carga_anterior": None,
        "volumes_anterior": None
    }


    # -------------------------------------------------
    # CALLBACKS
    # -------------------------------------------------

    def executar_impressao():

        processar_impressao(
            ctx,
            doc,
            campo,
            estado
        )


    def executar_restauracao():

        campo.setText(
            VALOR_INICIAL
        )

        campo.setFocus()


    def executar_fechamento():

        dialogo.endExecute()


    # -------------------------------------------------
    # LISTENERS
    # -------------------------------------------------

    listener_imprimir = ActionListener(
        executar_impressao
    )

    listener_restaurar = ActionListener(
        executar_restauracao
    )

    listener_fechar = ActionListener(
        executar_fechamento
    )

    listener_teclado = KeyListener(
        executar_impressao
    )


    # -------------------------------------------------
    # REGISTRA LISTENERS
    # -------------------------------------------------

    botao_imprimir.addActionListener(
        listener_imprimir
    )

    botao_restaurar.addActionListener(
        listener_restaurar
    )

    botao_fechar.addActionListener(
        listener_fechar
    )

    campo.addKeyListener(
        listener_teclado
    )


    # -------------------------------------------------
    # EXECUTA O DIÁLOGO
    # -------------------------------------------------

    try:

        campo.setFocus()

        dialogo.execute()

    finally:

        dialogo.dispose()


# =====================================================
# IMPRESSÃO
# =====================================================

def processar_impressao(
    ctx,
    doc,
    campo,
    estado
):

    texto = campo.getText().strip()

    partes = texto.split()


    # -------------------------------------------------
    # FORMATO
    # -------------------------------------------------

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


    # -------------------------------------------------
    # VALIDA BOX
    # -------------------------------------------------

    if not re.fullmatch(
        r"\d{2}",
        box
    ):

        mostrar_mensagem(
            ctx,
            "O BOX deve ter exatamente 2 dígitos.\n\n"
            "Exemplo: 02"
        )

        campo.setFocus()

        return


    # -------------------------------------------------
    # VALIDA CARGA
    # -------------------------------------------------

    if not re.fullmatch(
        r"\d{7}",
        carga
    ):

        mostrar_mensagem(
            ctx,
            "A carga deve ter exatamente 7 dígitos.\n\n"
            "Exemplo: 1254567"
        )

        campo.setFocus()

        return


    # -------------------------------------------------
    # VALIDA VOLUMES
    # -------------------------------------------------

    if not re.fullmatch(
        r"\d{2}",
        volumes
    ):

        mostrar_mensagem(
            ctx,
            "Volumes deve ter exatamente 2 dígitos.\n\n"
            "Exemplo: 10"
        )

        campo.setFocus()

        return


    box_texto = "BOX: " + box
    volumes_texto = "VOLUMES: " + volumes


    # -------------------------------------------------
    # PRIMEIRA IMPRESSÃO
    # -------------------------------------------------

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


    # -------------------------------------------------
    # IMPRESSÕES SEGUINTES
    # -------------------------------------------------

    else:

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


    # -------------------------------------------------
    # IMPRIME
    # -------------------------------------------------

    imprimir(doc)


    # -------------------------------------------------
    # GUARDA OS VALORES ATUAIS
    # -------------------------------------------------

    estado["box_anterior"] = box_texto
    estado["carga_anterior"] = carga
    estado["volumes_anterior"] = volumes_texto


    # -------------------------------------------------
    # PREPARA PRÓXIMA ENTRADA
    # -------------------------------------------------

    carga_proxima = (
        carga[:3] +
        "XXXX"
    )

    campo.setText(
        box +
        " " +
        carga_proxima +
        " XX"
    )

    campo.setFocus()


# =====================================================
# SUBSTITUIÇÃO
# =====================================================

def substituir(
    doc,
    procurar,
    substituir_por
):

    descriptor = doc.createReplaceDescriptor()

    descriptor.SearchString = procurar
    descriptor.ReplaceString = substituir_por

    doc.replaceAll(descriptor)


# =====================================================
# IMPRESSÃO
# =====================================================

def imprimir(doc):

    propriedades = []

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = "Wait"
    prop.Value = True

    propriedades.append(prop)

    doc.print(
        tuple(propriedades)
    )


# =====================================================
# LISTENER DOS BOTÕES
# =====================================================

class ActionListener(
    unohelper.Base,
    XActionListener
):

    def __init__(self, callback):

        self.callback = callback

    def actionPerformed(
        self,
        event
    ):

        self.callback()

    def disposing(
        self,
        event
    ):

        pass


# =====================================================
# LISTENER DO TECLADO
# =====================================================

class KeyListener(
    unohelper.Base,
    XKeyListener
):

    def __init__(self, callback):

        self.callback = callback

    def keyPressed(
        self,
        event
    ):

        if event.KeyCode == 1280:

            self.callback()

    def keyReleased(
        self,
        event
    ):

        pass

    def disposing(
        self,
        event
    ):

        pass


# =====================================================
# MENSAGEM
# =====================================================

def mostrar_mensagem(
    ctx,
    texto
):

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