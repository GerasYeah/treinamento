#include <stdio.h>

// Tabuleiro 10x10
int tabuleiro[10][10] = {0};
char tabela[] = "  A  B  C  D  E  F  G  H  I  J";

// Navios 1, 2 e 3
int navioA[3] = {5, 15, 25}; // Navio na vertical
int navioB[3] = {91, 92, 93}; // Navio na horizontal
int navioC[3] = {54, 65, 76}; // Navio na diagonal

// Função para verificar se possui uma parte do navio na posição
int temNavio(int navio[], int coordenadas) {
    for (int i = 0; i < 3; i++) {
        if (navio[i] == coordenadas) {
            return 1;
        }
    }
    return 0;
}

// Função para adicionar navios ao tabuleiro
void posicionarNavio(int navio[]) {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            int coordenadas = i * 10 + j;  // Obtém o número da posição no tabuleiro (0 - 99)
            if (temNavio(navio, coordenadas)) {
                tabuleiro[i][j] = 3;  // Valor 3 para indicar uma parte do navio
            }
        }
    }
}

// Função para exibir o tabuleiro com ou sem os navios
void exibirTabuleiro(int comNavios) {
    printf("%s\n", tabela); // Imprime as colunas
    for (int i = 0; i < 10; i++) {
        printf("%d ", i); // Imprime as linhas
        for (int j = 0; j < 10; j++) {
            int elemento;
            if (comNavios) {
                elemento = tabuleiro[i][j];  // Obtém o elemento no tabuleiro
            } else {
                elemento = 0;  // Valor 0 para indicar água
            }
            printf("%ds ", elemento);  // Exibe o elemento
        }
        printf("\n");
    }
}

int main() {
    posicionarNavio(navioA);
    posicionarNavio(navioB);
    posicionarNavio(navioC);

    exibirTabuleiro(1);  // 1 para exibir os navios, 0 para não exibir

    return 0;
}
