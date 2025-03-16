#include <stdio.h>

// Função recursiva para mover qualquer peça
void moverPeca(int casas, char sentido[]) {
    if (casas > 0) {
        printf("%s\n", sentido);
        moverPeca(casas - 1, sentido);
    }
}

// Função específica para mover o cavalo
void moverCavalo() {
    int casas = 0;

    // Loop aninhado para fazer o movimento "duplo" do cavalo
    // Apenas para fins educacionais, existem maneiras melhores, obviamente.
    while (casas < 3) {
        if (casas < 2) {
            printf("Baixo\n");
        } else {
            for (int i = 0; i < 1; i++) {
                printf("Esquerda\n");
            }
        }
        casas++;
    }
}

int main() {
    // Movimentando as peças uma por uma
    printf("Movimentação de Peças de Xadrez!\n");

    printf("\nMovimentação da Torre:\n");
    moverPeca(5, "Direita");

    printf("\nMovimentação da Rainha:\n");
    moverPeca(8, "Esquerda");

    printf("\nMovimentação do Bispo:\n");
    moverPeca(5, "Cima, Direita");

    printf("\nMovimentação do Cavalo:\n");
    moverCavalo();

    return 0;
}
