importClass(com.sun.star.awt.XActionListener);
importClass(com.sun.star.awt.XKeyHandler);


/*
 * Valor inicial e também usado pelo botão Restaurar.
 */
var VALOR_INICIAL = "02 125XXXX XX";


function main() {

    var ctx = uno.getComponentContext();
    var smgr = ctx.ServiceManager;

    var desktop = smgr.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx
    );

    var doc = desktop.getCurrentComponent();

    if (!doc) {
        mostrarMensagem(
            ctx,
            "Nenhum documento está aberto."
        );
        return;
    }

    criarDialogo(ctx, doc);
}


/*
 * Cria o diálogo principal.
 */
function criarDialogo(ctx, doc) {

    var smgr = ctx.ServiceManager;

    var dialogModel = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel",
        ctx
    );

    dialogModel.Width = 220;
    dialogModel.Height = 120;

    dialogModel.Title =
        "Impressão de cargas semiautomático";


    /*
     * Título dentro do diálogo.
     */
    var titulo = dialogModel.createInstance(
        "com.sun.star.awt.UnoControlFixedTextModel"
    );

    titulo.PositionX = 10;
    titulo.PositionY = 8;
    titulo.Width = 200;
    titulo.Height = 12;

    titulo.Label = "box carga volumes";

    dialogModel.insertByName(
        "titulo",
        titulo
    );


    /*
     * Caixa de texto.
     *
     * Primeira execução:
     *
     * 02 125XXXX XX
     */
    var campo = dialogModel.createInstance(
        "com.sun.star.awt.UnoControlEditModel"
    );

    campo.PositionX = 10;
    campo.PositionY = 25;
    campo.Width = 200;
    campo.Height = 14;

    campo.Text = VALOR_INICIAL;

    dialogModel.insertByName(
        "campo",
        campo
    );


    /*
     * Botão Imprimir.
     */
    var botaoImprimir = dialogModel.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    );

    botaoImprimir.PositionX = 10;
    botaoImprimir.PositionY = 50;
    botaoImprimir.Width = 60;
    botaoImprimir.Height = 18;

    botaoImprimir.Label = "Imprimir";

    dialogModel.insertByName(
        "imprimir",
        botaoImprimir
    );


    /*
     * Botão Restaurar.
     */
    var botaoRestaurar = dialogModel.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    );

    botaoRestaurar.PositionX = 80;
    botaoRestaurar.PositionY = 50;
    botaoRestaurar.Width = 60;
    botaoRestaurar.Height = 18;

    botaoRestaurar.Label = "Restaurar";

    dialogModel.insertByName(
        "restaurar",
        botaoRestaurar
    );


    /*
     * Botão Fechar.
     */
    var botaoFechar = dialogModel.createInstance(
        "com.sun.star.awt.UnoControlButtonModel"
    );

    botaoFechar.PositionX = 150;
    botaoFechar.PositionY = 50;
    botaoFechar.Width = 60;
    botaoFechar.Height = 18;

    botaoFechar.Label = "Fechar";

    dialogModel.insertByName(
        "fechar",
        botaoFechar
    );


    /*
     * Cria o diálogo.
     */
    var dialog = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog",
        ctx
    );

    dialog.setModel(dialogModel);


    /*
     * Obtém os controles.
     */
    var campoControle =
        dialog.getControl("campo");

    var imprimirControle =
        dialog.getControl("imprimir");

    var restaurarControle =
        dialog.getControl("restaurar");

    var fecharControle =
        dialog.getControl("fechar");


    /*
     * Evento do botão Imprimir.
     */
    var listenerImprimir = new ActionListener(
        ctx,
        function () {

            processarImpressao(
                ctx,
                doc,
                campoControle
            );

        }
    );

    imprimirControle.addActionListener(
        listenerImprimir
    );


    /*
     * Evento do botão Restaurar.
     */
    var listenerRestaurar = new ActionListener(
        ctx,
        function () {

            campoControle.setText(
                VALOR_INICIAL
            );

            campoControle.setFocus();

        }
    );

    restaurarControle.addActionListener(
        listenerRestaurar
    );


    /*
     * Evento do botão Fechar.
     */
    var listenerFechar = new ActionListener(
        ctx,
        function () {

            dialog.endExecute();

        }
    );

    fecharControle.addActionListener(
        listenerFechar
    );


    /*
     * Permite pressionar Enter dentro da caixa
     * de texto para executar a impressão.
     */
    var keyHandler = new KeyHandler(
        ctx,
        function () {

            processarImpressao(
                ctx,
                doc,
                campoControle
            );

        }
    );

    campoControle.addKeyHandler(
        keyHandler
    );


    /*
     * Exibe o diálogo.
     */
    dialog.setVisible(true);

    campoControle.setFocus();
}


/*
 * Processa os valores digitados e imprime.
 */
function processarImpressao(
    ctx,
    doc,
    campo
) {

    var texto = campo.getText();

    /*
     * Divide os valores usando os espaços.
     *
     * Esperado:
     *
     * 02 1254567 10
     */
    var partes = texto.trim().split(/\s+/);


    if (partes.length !== 3) {

        mostrarMensagem(
            ctx,
            "Digite no formato:\n\n" +
            "02 1254567 10"
        );

        campo.setFocus();

        return;
    }


    var box = partes[0];
    var carga = partes[1];
    var volumes = partes[2];


    /*
     * BOX precisa ter exatamente 2 dígitos.
     */
    if (!/^\d{2}$/.test(box)) {

        mostrarMensagem(
            ctx,
            "O BOX deve ter exatamente 2 dígitos.\n\n" +
            "Exemplo: 02"
        );

        campo.setFocus();

        return;
    }


    /*
     * CARGA precisa ter exatamente 7 dígitos.
     */
    if (!/^\d{7}$/.test(carga)) {

        mostrarMensagem(
            ctx,
            "A carga deve ter exatamente 7 dígitos.\n\n" +
            "Exemplo: 1254567"
        );

        campo.setFocus();

        return;
    }


    /*
     * VOLUMES precisa ter exatamente 2 dígitos.
     */
    if (!/^\d{2}$/.test(volumes)) {

        mostrarMensagem(
            ctx,
            "Volumes deve ter exatamente 2 dígitos.\n\n" +
            "Exemplo: 10"
        );

        campo.setFocus();

        return;
    }


    /*
     * Monta os textos completos usados no documento.
     */
    var boxTexto = "BOX: " + box;

    var volumesTexto =
        "VOLUMES: " + volumes;


    /*
     * PRIMEIRA IMPRESSÃO
     *
     * O documento possui:
     *
     * BOX: {XX}
     * {CARGA}
     * VOLUMES: {XX}
     *
     * Nas próximas impressões, as variáveis abaixo
     * armazenam os valores anteriores.
     */
    if (
        typeof processarImpressao.boxAnterior ===
        "undefined"
    ) {

        /*
         * Primeiro uso.
         */
        substituir(
            doc,
            "BOX: {XX}",
            boxTexto
        );

        substituir(
            doc,
            "{CARGA}",
            carga
        );

        substituir(
            doc,
            "VOLUMES: {XX}",
            volumesTexto
        );

    } else {

        /*
         * Próximas impressões.
         *
         * Substituímos o texto completo anterior.
         *
         * Exemplo:
         *
         * BOX: 02 -> BOX: 03
         * 1254567 -> 1254568
         * VOLUMES: 10 -> VOLUMES: 05
         */
        substituir(
            doc,
            processarImpressao.boxAnterior,
            boxTexto
        );

        substituir(
            doc,
            processarImpressao.cargaAnterior,
            carga
        );

        substituir(
            doc,
            processarImpressao.volumesAnterior,
            volumesTexto
        );
    }


    /*
     * Imprime automaticamente.
     */
    imprimir(doc);


    /*
     * Guarda exatamente os valores inseridos.
     * Eles serão usados na próxima impressão.
     */
    processarImpressao.boxAnterior =
        boxTexto;

    processarImpressao.cargaAnterior =
        carga;

    processarImpressao.volumesAnterior =
        volumesTexto;


    /*
     * Prepara a próxima carga.
     *
     * Exemplo:
     *
     * 1254567
     *
     * vira:
     *
     * 125XXXX
     */
    var cargaProxima =
        carga.substring(0, 3) + "XXXX";


    /*
     * Volumes volta para XX.
     */
    var volumesProximo = "XX";


    /*
     * Mostra a próxima entrada.
     */
    campo.setText(
        box + " " +
        cargaProxima + " " +
        volumesProximo
    );


    campo.setFocus();
}


/*
 * Substitui texto no documento preservando
 * a formatação existente.
 */
function substituir(
    doc,
    procurar,
    substituirPor
) {

    var descriptor =
        doc.createReplaceDescriptor();

    descriptor.SearchString =
        procurar;

    descriptor.ReplaceString =
        substituirPor;

    doc.replaceAll(descriptor);
}


/*
 * Impressão automática.
 */
function imprimir(doc) {

    var propriedades = [];

    var prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    );

    prop.Name = "Wait";
    prop.Value = true;

    propriedades.push(prop);

    doc.print(propriedades);
}


/*
 * Listener dos botões.
 */
function ActionListener(ctx, callback) {

    this.ctx = ctx;
    this.callback = callback;

    this.actionPerformed = function(event) {

        this.callback();

    };

    this.disposing = function(event) {
    };
}


/*
 * Listener do teclado.
 *
 * Enter = imprimir.
 */
function KeyHandler(ctx, callback) {

    this.ctx = ctx;
    this.callback = callback;

    this.keyPressed = function(event) {

        /*
         * 1280 = Enter / Return
         */
        if (event.KeyCode === 1280) {

            this.callback();

        }
    };

    this.keyReleased = function(event) {
    };

    this.disposing = function(event) {
    };
}


/*
 * Exibe uma mensagem.
 */
function mostrarMensagem(ctx, texto) {

    var smgr = ctx.ServiceManager;

    var desktop =
        smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop",
            ctx
        );

    var doc = desktop.getCurrentComponent();

    var parent = null;

    if (doc) {

        try {

            parent =
                doc.CurrentController
                    .Frame
                    .ContainerWindow;

        } catch (e) {
        }
    }


    var toolkit =
        smgr.createInstanceWithContext(
            "com.sun.star.awt.Toolkit",
            ctx
        );


    var box = toolkit.createMessageBox(
        parent,
        1,
        1,
        "Impressão",
        texto
    );

    box.execute();
}