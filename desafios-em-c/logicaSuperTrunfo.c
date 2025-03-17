#include <stdio.h>

// Variáveis para armazenar as propriedades das cartas
char codigoA[3], estadoA[2], cidadeA[21];
char codigoB[3], estadoB[2], cidadeB[21];

unsigned long int populacaoA, populacaoB;
int pontosTuristicosA, pontosTuristicosB;

float pibA, pibB;
float areaA, areaB;

float densidadePopulacionalA, densidadePopulacionalB;
float pibPerCapitaA, pibPerCapitaB;
float superPoderA, superPoderB;

// Declarações de metódos
void exibirMenuDeComparacao();

// Função que solicita uma entrada de dados
int solicitarOpcao() {
    int opcao;

    printf("\nSelecione uma opção: ");
    scanf("%d", &opcao);

    return opcao;
}

// Funções para cálculos
float calcularPibPerCapita(float pib, int populacao) {
    float pibPerCapita = pib / populacao;
    return pibPerCapita;
}

float calcularDensidadePopulacional(float populacao, int area) {
    float densidadePopulacional = populacao / area;
    return densidadePopulacional;
}

float calcularSuperPoder(unsigned long int populacao, int pontosTuristicos, float area, float pib, float pibPerCapita, float densidadePopulacional) {
    // Inverter o valor da densidade populacional
    float densidadePopulacionalInvertida = 0;
    if (densidadePopulacional > 0) {
        densidadePopulacionalInvertida = 1.0 / densidadePopulacional;
    }
    // Somar todos os valores e retornar
    float superPoder = populacao + pontosTuristicos + area + pib + pibPerCapita + densidadePopulacionalInvertida;
    return superPoder;
}

// Menu após a comparação de um atributo escolhido
void exibirMenuPosComparacao() {
    printf("\n\nCOMPARAÇÃO FINALIZADA!\n");
    printf("1. Voltar ao Menu de Comparação\n");
    printf("2. Recomeçar o jogo\n");
    printf("0. Sair do programa\n");

    // Solicitar uma opção ao usuário
    int opcao = solicitarOpcao();

    int main();

    switch (opcao) {
        case 1:
            exibirMenuDeComparacao();
            break;
        case 2:
            main();
            break;
        default:
            printf("Saindo...");
            break;
    }
}

// Funções para comparação de cartas
void imprimirComparacao(char propriedade[], int resultado) {
    // Exibir a comparação de um atributo específico
    int cartaVencedora = resultado == 1 ? 1 : 2;
    printf("%s: A carta %d venceu! (%d)\n", propriedade, cartaVencedora, resultado);
}

void compararAtributosInt(char propriedade[], float atr1, float atr2) {
    if (atr1 == atr2) {
        printf("%s: Houve um empate!", propriedade);
    } else if (atr1 > atr2) {
        printf("%s: A carta 1 venceu!", propriedade);
    } else {
        printf("%s: A carta 2 venceu!", propriedade);
    }

    exibirMenuPosComparacao();
}

void compararAtributosFloat(char propriedade[], float atr1, float atr2) {
    if (atr1 == atr2) {
        printf("%s: Houve um empate!", propriedade);
    } else if (atr1 > atr2) {
        printf("%s: A carta 1 venceu!", propriedade);
    } else {
        printf("%s: A carta 2 venceu!", propriedade);
    }

    exibirMenuPosComparacao();
}

void compararCartas() {
    // Comparar e exibir atributos um por um
    // Para fins didáticos, os métodos a seguir não tratam empates
    printf("\nCOMPARAÇÃO DE TODOS OS ATRIBUTOS!\n");
    imprimirComparacao("População", populacaoA > populacaoB);
    imprimirComparacao("Área", areaA > areaB);
    imprimirComparacao("PIB", pibA > pibB);
    imprimirComparacao("Pontos turísticos", pontosTuristicosA > pontosTuristicosB);
    imprimirComparacao("Densidade populacional", densidadePopulacionalA < densidadePopulacionalB);
    imprimirComparacao("PIB per Capita", pibPerCapitaA > pibPerCapitaB);
    imprimirComparacao("Super Poder", superPoderA > superPoderB);

    exibirMenuPosComparacao();
}

// Menu com todas as opções de comparação disponíveis
void exibirMenuDeComparacao() {
    // Exibir um menu de opções
    printf("COMPARAÇÃO DE CARTAS!\n");
    printf("1. Todos os atributos\n");
    printf("2. Comparar Super Poder\n");
    printf("3. Comparar População\n");
    printf("4. Comparar Área\n");
    printf("5. Comparar PIB\n");
    printf("6. Comparar PIB Per Capita\n");
    printf("7. Comparar Pontos Turísticos\n");
    printf("8. Comparar Densidade Populacional\n");
    printf("9. Recomeçar o jogo\n");
    printf("0. Sair do programa\n");

    // Solicitar uma opção ao usuário
    int opcao = solicitarOpcao();

    int main();
    void compararCartas();

    switch (opcao) {
        case 1:
            compararCartas();
            break;
        case 2:
            compararAtributosInt("Super Poder", superPoderA, superPoderB);
            break;
        case 3:
            compararAtributosInt("População", populacaoA, populacaoB);
            break;
        case 4:
            compararAtributosFloat("Área", areaA, areaB);
            break;
        case 5:
            compararAtributosFloat("PIB", pibA, pibB);
            break;
        case 6:
            compararAtributosFloat("PIB per Capita", pibPerCapitaA, pibPerCapitaB);
            break;
        case 7:
            compararAtributosInt("Pontos Turísticos", pontosTuristicosA, pontosTuristicosB);
            break;
        case 8:
            char propriedade[] = "Densidade populacional";

            if (densidadePopulacionalA == densidadePopulacionalB) {
                printf("%s: Houve um empate!", propriedade);
            } else if (densidadePopulacionalA < densidadePopulacionalB) {
                printf("%s: A carta 1 venceu!", propriedade);
            } else {
                printf("%s: A carta 2 venceu!", propriedade);
            }

            exibirMenuPosComparacao();
            break;
        case 9:
            main();
            break;
        default:
            printf("Saindo...");
            break;
    }
}

int main() {
    printf("Boas vindas ao Super Trunfo: Países!\n\n");

    // Cadastrar carta 1
    printf("CADASTRE A PRIMEIRA CARTA!\n");

    printf("Digite a letra do Estado (de A a H): ");
    scanf("%1s", estadoA);

    printf("Digite o código da carta 2 (de 01 a 04): ");
    scanf("%2s", codigoA);

    printf("Digite o nome da cidade: ");
    scanf("%20s", cidadeA);

    printf("Digite o total de habitantes: ");
    scanf("%ld", &populacaoA);

    printf("Digite o PIB: ");
    scanf("%f", &pibA);

    printf("Digite a área territorial: ");
    scanf("%f", &areaA);

    printf("Digite o total de pontos turísticos: ");
    scanf("%d", &pontosTuristicosA);

    // Calcular PIB per Capita, densidade populacional e super poder da carta 1
    pibPerCapitaA = calcularPibPerCapita(pibA, populacaoA);
    densidadePopulacionalA = calcularDensidadePopulacional(populacaoA, areaA);
    superPoderA = calcularSuperPoder(populacaoA, pontosTuristicosA, areaA, pibA, pibPerCapitaA, densidadePopulacionalA);

    // Exibir as propriedades da carta 1
    printf("\nINFORMAÇÕES DA CARTA 1:\n");
    printf("Estado: %s\n", estadoA);
    printf("Código: %s%s\n", estadoA, codigoA);
    printf("Cidade: %s\n", cidadeA);
    printf("População: %ld\n", populacaoA);
    printf("Área: %.2f km²\n", areaA);
    printf("PIB: %.2f bilhões de reais\n", pibA);
    printf("Pontos turísticos: %d\n", pontosTuristicosA);
    printf("PIB per Capita: %.2f reais\n", pibPerCapitaA);
    printf("Densidade populacional: %.2f habitantes/km²\n\n", densidadePopulacionalA);

    // Cadastrar carta 2
    printf("CADASTRE A SEGUNDA CARTA!\n");
    printf("Digite a letra do Estado (de A a H): ");
    scanf("%1s", estadoB);

    printf("Digite o código da carta 2 (de 01 a 04): ");
    scanf("%2s", codigoB);

    printf("Digite o nome da cidade: ");
    scanf("%20s", cidadeB);

    printf("Digite a população: ");
    scanf("%ld", &populacaoB);

    printf("Digite o PIB: ");
    scanf("%f", &pibB);

    printf("Digite a área territorial: ");
    scanf("%f", &areaB);

    printf("Digite o total de pontos turísticos: ");
    scanf("%d", &pontosTuristicosB);

    // Calcular PIB per Capita, densidade populacional e super poder da carta 2
    pibPerCapitaB = calcularPibPerCapita(pibB, populacaoB);
    densidadePopulacionalB = calcularDensidadePopulacional(populacaoB, areaB);
    superPoderB = calcularSuperPoder(populacaoB, pontosTuristicosB, areaB, pibB, pibPerCapitaB, densidadePopulacionalB);

    // Exibir as propriedades da carta 2
    printf("\nINFORMAÇÕES DA CARTA 2:\n");
    printf("Estado: %s\n", estadoB);
    printf("Código: %s%s\n", estadoB, codigoB);
    printf("Cidade: %s\n", cidadeB);
    printf("População: %ld\n", populacaoB);
    printf("Área: %.2f km² \n", areaB);
    printf("PIB: %.2f bilhões de reais\n", pibB);
    printf("Pontos turísticos: %d\n", pontosTuristicosB);
    printf("PIB per Capita: %.2f reais \n", pibPerCapitaB);
    printf("Densidade populacional: %.2f habitantes/km²\n\n", densidadePopulacionalB);

    // Solicitar a comparação após o fim do registro das cartas
    exibirMenuDeComparacao();
}
