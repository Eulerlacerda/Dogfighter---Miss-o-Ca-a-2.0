# Dogfighter_Missao_Caca_2.0
Jogo de Caça
Dogfighter - Missão Caça 2.0
Um emocionante jogo de avião 2D de tiro vertical (shoot 'em up) desenvolvido em Python com a biblioteca Pygame. Pilote um caça moderno, enfrente hordas de inimigos aéreos e terrestres, desvie de projéteis, colete power-ups e derrote chefes desafiadores para completar sua missão.
Índice
Visão Geral
Funcionalidades
Como Jogar
Controles
Objetivo
Estrutura do Projeto
Requisitos
Instalação
Estrutura de Arquivos
Análise do Código
Módulos Utilizados
Classes Principais
Lógica do Jogo
Como Contribuir
Visão Geral
Dogfighter - Missão Caça 2.0 é um jogo de arcade dinâmico onde o jogador controla um avião de caça. O objetivo é sobreviver o maior tempo possível, destruindo inimigos, subindo de nível e acumulando a maior pontuação. O jogo apresenta uma dificuldade progressiva, introduzindo novos tipos de inimigos e desafios à medida que o jogador avança.
Funcionalidades
Movimentação Livre: Controle total do caça na tela.
Sistema de Níveis: A dificuldade aumenta progressivamente, com 20 níveis para conquistar.
Variedade de Inimigos: Enfrente caças aéreos, tanques terrestres e caçadores teleguiados.
Batalhas com Chefes (Bosses): A cada 5 níveis, um chefe poderoso surge para um confronto épico.
Armas e Habilidades:
Tiro Padrão: Munição que se regenera com o tempo.
Mísseis Teleguiados: Armamento poderoso com munição limitada.
Turbo: Aumente sua velocidade temporariamente para manobras evasivas.
Power-ups: Colete itens para recuperar vidas, ativar um escudo temporário ou ganhar mais mísseis.
HUD Completo: Interface que exibe vidas, pontuação, nível, munição, mísseis, energia do turbo e progresso do nível.
Efeitos Sonoros e Música: Áudio imersivo para tiros, explosões e música de fundo.
Fallback de Recursos: O jogo cria formas geométricas coloridas caso as imagens ou sons não sejam encontrados, evitando que o jogo quebre.
Como Jogar
Controles
Tecla
Ação
Setas (Cima, Baixo, Esquerda, Direita)
Movimentar o caça
W
Atirar projéteis
E
Lançar míssil teleguiado
Barra de Espaço
Ativar/Desativar o turbo
R
Reiniciar o jogo após "Game Over" ou "Vitória"
ESC
Sair do jogo
Objetivo
O objetivo principal é sobreviver aos 20 níveis do jogo. Para avançar de nível, você deve derrotar um número específico de inimigos. A cada 5 níveis, um chefe (Boss) aparecerá, e você precisará derrotá-lo para continuar. Acumule pontos destruindo inimigos e tente zerar o jogo!
Estrutura do Projeto
Requisitos
Python 3.x
Pygame: pip install pygame
Instalação
Clone o repositório:
Bash
git clone https://github.com/seu-usuario/dogfighter-pygame.git
cd dogfighter-pygame
Instale as dependências:
Bash
pip install pygame
Execute o jogo:
Bash
python nome_do_arquivo.py
(Substitua nome_do_arquivo.py pelo nome do seu script principal ).
Estrutura de Arquivos
O código espera que as imagens e sons estejam organizados em pastas específicas. Certifique-se de que a variável PASTA_IMAGENS no código aponta para o local correto.
Plain Text
seu_projeto/
├── nome_do_arquivo.py      # O script principal do jogo
└── fithter_plane/          # Pasta principal de recursos (assets)
    ├── background.png
    ├── boss.png
    ├── bullet.png
    ├── ... (outras imagens)
    └── sons/
        ├── shoot.wav
        ├── explosion.wav
        ├── ... (outros sons)
Análise do Código
O código é bem estruturado, utilizando programação orientada a objetos para definir os elementos do jogo.
Módulos Utilizados
pygame: Biblioteca principal para desenvolvimento de jogos em Python.
random: Usado para gerar posições e comportamentos aleatórios dos inimigos.
math: Utilizado para cálculos de movimento, como a perseguição de mísseis.
sys: Para encerrar a aplicação de forma limpa.
os: Para construir os caminhos dos arquivos de imagem e som de forma compatível com qualquer sistema operacional.
Classes Principais
Jogo: A classe central que gerencia o loop principal, eventos, atualizações de estado, colisões e renderização de todos os elementos na tela.
Jogador(pygame.sprite.Sprite): Controla a nave do jogador, suas vidas, pontuação, armamentos e habilidades especiais como turbo e escudo.
InimigoAereo, InimigoCacador, InimigoTerrestre, Boss: Classes que definem os diferentes tipos de adversários, cada um com seu próprio comportamento, vida e padrão de ataque.
Projetil, Missil, ProjetilInimigo, MissilInimigo: Classes para os diferentes tipos de disparos, tanto do jogador quanto dos inimigos.
PowerUp(pygame.sprite.Sprite): Representa os itens coletáveis (vida, escudo, mísseis).
Lógica do Jogo
Inicialização: O Pygame é iniciado, a tela é configurada e todos os recursos (imagens e sons) são carregados através de funções auxiliares (carregar_imagem, carregar_som).
Loop Principal (run): A classe Jogo contém o loop que mantém o jogo em execução.
handle_events(): Captura entradas do jogador (teclado, fechar janela).
update(): Atualiza a posição e o estado de todos os sprites (jogador, inimigos, projéteis), verifica colisões e a lógica de progressão de nível.
draw(): Limpa a tela e desenha todos os elementos, incluindo o fundo com rolagem, os sprites e a interface do usuário (HUD).
Game Over / Vitória: O jogo transita para um estado de "Game Over" se as vidas do jogador chegam a zero, ou para uma tela de "Vitória" se o nível 20 for superado, oferecendo a opção de reiniciar.
Como Contribuir
Este é um projeto de código aberto e contribuições são bem-vindas! Você pode contribuir de várias formas:
Reportando Bugs: Se encontrar um problema, abra uma "Issue" no GitHub.
Sugerindo Melhorias: Tem ideias para novos inimigos, power-ups ou funcionalidades? Abra uma "Issue" para discutirmos.
Enviando Pull Requests:
Faça um "fork" do projeto.
Crie uma nova "branch" para sua funcionalidade (git checkout -b feature/nova-feature).
Faça o "commit" de suas alterações (git commit -m 'Adiciona nova-feature').
Envie para a sua "branch" (git push origin feature/nova-feature).
Abra um "Pull Request".
