import pygame
import random
import math
import sys
import os

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()  # Inicializa o sistema de áudio

# --- CONFIGURAÇÕES GERAIS ---
LARGURA, ALTURA = 1365, 701
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dogfighter - Missão Caça 2.0")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL_CEU = (135, 206, 235)
CINZA = (100, 100, 100)
AMARELO = (255, 255, 0)
LARANJA = (255, 165, 0)
CIANO = (0, 255, 255)
ROXO = (128, 0, 128)

# Caminho da pasta de imagens e sons
PASTA_IMAGENS = r"E:\01_Desenvolvimento_jogos_unity\fithter_plane"
PASTA_SONS = os.path.join(PASTA_IMAGENS, "sons")

# --- FUNÇÃO PARA CARREGAR RECURSOS ---
def carregar_imagem(nome, escala=None, fallback_cor=VERMELHO, fallback_forma='retangulo'):
    caminho = os.path.join(PASTA_IMAGENS, nome)
    try:
        imagem = pygame.image.load(caminho).convert_alpha()
        if escala:
            imagem = pygame.transform.scale(imagem, escala)
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"❌ Não foi possível carregar a imagem: {caminho}. Criando fallback.")
        escala = escala if escala else (50, 50)
        superficie = pygame.Surface(escala, pygame.SRCALPHA)
        if fallback_forma == 'triangulo':
             pygame.draw.polygon(superficie, fallback_cor, [(escala[0]//2, 0), (0, escala[1]), (escala[0], escala[1])])
        elif fallback_forma == 'circulo':
             pygame.draw.circle(superficie, fallback_cor, (escala[0]//2, escala[1]//2), escala[0]//2)
        else: # Retangulo por padrão
            superficie.fill(fallback_cor)
        return superficie

def carregar_som(nome):
    caminho = os.path.join(PASTA_SONS, nome)
    try:
        return pygame.mixer.Sound(caminho)
    except (pygame.error, FileNotFoundError):
        print(f"❌ Não foi possível carregar o som: {caminho}")
        return None

# --- CARREGAMENTO DE IMAGENS ---
IMAGEM_JOGADOR = carregar_imagem('fighter_jet.png', (80, 60))
IMAGEM_INIMIGO_AEREO = carregar_imagem('enemy_fighter.png', (60, 45), fallback_forma='triangulo')
IMAGEM_INIMIGO_TERRESTRE = carregar_imagem('tank.png', (50, 30))
IMAGEM_INIMIGO_CACADOR = carregar_imagem('enemy_hunter.png', (70, 50), fallback_cor=ROXO, fallback_forma='triangulo')
IMAGEM_BOSS = carregar_imagem('boss.png', (150, 120), fallback_cor=ROXO, fallback_forma='retangulo')

IMAGEM_PROJETIL_JOGADOR = carregar_imagem('bullet.png', (10, 20))
IMAGEM_PROJETIL_INIMIGO = carregar_imagem('enemy_bullet.png', (12, 12), VERMELHO, 'circulo')
IMAGEM_MISSIL_JOGADOR = carregar_imagem('missile.png', (20, 40), LARANJA, 'triangulo')
IMAGEM_MISSIL_INIMIGO = carregar_imagem('enemy_missile.png', (18, 36), VERMELHO, 'triangulo')

IMAGEM_POWERUP_VIDA = carregar_imagem('heart.png', (30, 30), VERDE, 'circulo')
IMAGEM_POWERUP_ESCUDO = carregar_imagem('shield.png', (30, 30), CIANO, 'circulo')
IMAGEM_POWERUP_MISSIL = carregar_imagem('missile_powerup.png', (30, 30), LARANJA, 'circulo')

# Carregar imagens de fundo - usando apenas background.png para evitar erros
IMAGEM_FUNDO = carregar_imagem('background.png', (LARGURA, ALTURA), AZUL_CEU)

# --- CARREGAMENTO DE SONS ---
# Inicializar todas as variáveis de som como None
SOM_TIRO = None
SOM_EXPLOSAO = None
SOM_POWERUP = None
SOM_MISSIL = None
SOM_DANO = None
SOM_LEVEL_UP = None

try:
    SOM_TIRO = carregar_som('shoot.wav')
    SOM_EXPLOSAO = carregar_som('explosion.wav')
    SOM_POWERUP = carregar_som('powerup.wav')
    SOM_MISSIL = carregar_som('missile.wav')
    SOM_DANO = carregar_som('damage.wav')
    SOM_LEVEL_UP = carregar_som('level_up.wav')
    
    # Música de fundo
    pygame.mixer.music.load(os.path.join(PASTA_SONS, 'background_music.mp3'))
    pygame.mixer.music.set_volume(0.5)
except Exception as e:
    print(f"Aviso: Erro ao carregar sons. O jogo funcionará sem áudio. Erro: {e}")

# Relógio para controlar FPS
clock = pygame.time.Clock()
FPS = 60

# --- CLASSES DO JOGO (AGORA COMO SPRITES) ---

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_original = IMAGEM_JOGADOR
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA - 100))
        self.velocidade = 7
        self.vidas = 3
        self.pontuacao = 0
        self.invencivel_timer = 0
        self.municao = 100
        self.misseis = 5
        self.municao_timer = 0
        self.missil_timer = 0
        self.angulo = 0
        
        # Atributos do Turbo
        self.turbo_energia = 100
        self.turbo_ativo = False
        
        # Atributos do Escudo
        self.escudo_ativo = False
        self.escudo_timer = 0

    def update(self):
        teclas = pygame.key.get_pressed()
        
        # Movimento (mais rápido com turbo)
        velocidade_atual = self.velocidade * 1.5 if self.turbo_ativo else self.velocidade
        
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= velocidade_atual
            self.angulo = 10
        elif teclas[pygame.K_RIGHT] and self.rect.right < LARGURA:
            self.rect.x += velocidade_atual
            self.angulo = -10
        else:
            self.angulo = 0
        
        if teclas[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= velocidade_atual
        if teclas[pygame.K_DOWN] and self.rect.bottom < ALTURA:
            self.rect.y += velocidade_atual
        
        # Rotação da imagem
        self.image = pygame.transform.rotate(self.image_original, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Timers
        if self.invencivel_timer > 0:
            self.invencivel_timer -= 1
        if self.escudo_timer > 0:
            self.escudo_timer -= 1
        else:
            self.escudo_ativo = False
        
        # Recarga de munição
        self.municao_timer += 1
        if self.municao_timer >= 30 and self.municao < 100:
            self.municao += 1
            self.municao_timer = 0
            
        # Recarga de mísseis
        self.missil_timer += 1
        if self.missil_timer >= 180 and self.misseis < 10:  # Recarrega a cada 3 segundos
            self.misseis += 1
            self.missil_timer = 0
            
        # Atualização do Turbo
        if not self.turbo_ativo and self.turbo_energia < 100:
            self.turbo_energia += 0.2
        if self.turbo_ativo:
            self.turbo_energia -= 1.5
            if self.turbo_energia <= 0:
                self.turbo_ativo = False
                self.turbo_energia = 0

    def draw(self, superficie):
        # Efeito de piscar se invencível (mas não se escudo estiver ativo)
        if (self.invencivel_timer == 0 or self.invencivel_timer % 10 < 5) or self.escudo_ativo:
            superficie.blit(self.image, self.rect.topleft)
        
        # Desenha o escudo
        if self.escudo_ativo:
            pygame.draw.circle(superficie, CIANO, self.rect.center, self.rect.width // 2 + 5, 3)

    def ativar_escudo(self):
        self.escudo_ativo = True
        self.escudo_timer = 300  # 5 segundos de escudo
        if SOM_POWERUP:
            SOM_POWERUP.play()

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem, dano=1):
        super().__init__()
        self.image = imagem
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = 10
        self.dano = dano

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.bottom < 0:
            self.kill()  # Remove o projétil se sair da tela

class Missil(Projetil):
    def __init__(self, x, y, imagem, alvo=None, dano=3):
        super().__init__(x, y, imagem, dano)
        self.alvo = alvo
        self.velocidade = 7
        self.raio_explosao = 50

    def update(self):
        # Se tem alvo, persegue o alvo
        if self.alvo and self.alvo.alive():
            dx = self.alvo.rect.centerx - self.rect.centerx
            dy = self.alvo.rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            self.rect.x += (dx/dist) * self.velocidade
            self.rect.y += (dy/dist) * self.velocidade
        else:
            # Movimento reto se não tem alvo
            self.rect.y -= self.velocidade
            
        if self.rect.bottom < 0 or self.rect.top > ALTURA or self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()

class ProjetilInimigo(Projetil):
    def __init__(self, x, y, imagem, dano=1):
        super().__init__(x, y, imagem, dano)
        self.velocidade = -8  # Inverte a velocidade para ir para baixo

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.top > ALTURA:
            self.kill()

class MissilInimigo(Missil):
    def __init__(self, x, y, imagem, alvo, dano=2):
        super().__init__(x, y, imagem, alvo, dano)
        self.velocidade = -6  # Movimento para baixo

    def update(self):
        # Persegue o jogador
        if self.alvo and self.alvo.alive():
            dx = self.alvo.rect.centerx - self.rect.centerx
            dy = self.alvo.rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            self.rect.x += (dx/dist) * self.velocidade
            self.rect.y += (dy/dist) * self.velocidade
        else:
            # Movimento reto se não tem alvo
            self.rect.y -= self.velocidade
            
        if self.rect.top > ALTURA or self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()

class InimigoAereo(pygame.sprite.Sprite):
    def __init__(self, all_sprites, projeteis_inimigos, nivel):
        super().__init__()
        self.image_original = IMAGEM_INIMIGO_AEREO
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(
            center=(random.randint(50, LARGURA - 50), random.randint(-100, -20))
        )
        self.velocidade_y = random.uniform(1.0, 3.0) + (nivel * 0.1)
        self.vida = 1 + (nivel // 3)
        self.angulo = 0
        self.shoot_delay = max(30, 100 - nivel * 5)  # Intervalo entre tiros diminui com o nível
        self.last_shot = pygame.time.get_ticks()
        self.shots_fired_in_burst = 0
        self.burst_reset_time = pygame.time.get_ticks()
        self.all_sprites = all_sprites
        self.projeteis_inimigos = projeteis_inimigos
        self.nivel = nivel

    def update(self):
        self.rect.y += self.velocidade_y
        self.rect.x += math.sin(pygame.time.get_ticks() * 0.001) * (0.5 + self.nivel * 0.1)
        self.angulo = math.sin(pygame.time.get_ticks() * 0.002) * 5
        self.image = pygame.transform.rotate(self.image_original, self.angulo)
        
        if self.rect.top > ALTURA:
            self.kill()

        self.atirar()

    def atirar(self):
        now = pygame.time.get_ticks()

        # Reinicia o contador de tiros a cada 5 segundos
        if now - self.burst_reset_time > 5000:  # 5000 ms = 5 segundos
            self.shots_fired_in_burst = 0
            self.burst_reset_time = now

        # Atira apenas se não excedeu o limite de 3 tiros no burst e o delay passou
        if self.shots_fired_in_burst < 3 and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            proj = ProjetilInimigo(self.rect.centerx, self.rect.bottom, IMAGEM_PROJETIL_INIMIGO)
            self.all_sprites.add(proj)
            self.projeteis_inimigos.add(proj)
            self.shots_fired_in_burst += 1
            if SOM_TIRO:
                SOM_TIRO.play()

class InimigoCacador(InimigoAereo):
    def __init__(self, all_sprites, projeteis_inimigos, jogador, nivel):
        super().__init__(all_sprites, projeteis_inimigos, nivel)
        self.image_original = IMAGEM_INIMIGO_CACADOR
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(
            center=(random.randint(50, LARGURA - 50), random.randint(-200, -50))
        )
        self.velocidade_y = random.uniform(2.0, 4.0) + (nivel * 0.15)
        self.vida = 2 + (nivel // 2)
        self.jogador = jogador
        self.missil_delay = 2000  # 2 segundos entre mísseis
        self.last_missil = pygame.time.get_ticks()

    def update(self):
        # Movimento mais agressivo
        self.rect.y += self.velocidade_y
        # Persegue o jogador horizontalmente
        if self.jogador.alive():
            if self.rect.centerx < self.jogador.rect.centerx:
                self.rect.x += min(2, (self.jogador.rect.centerx - self.rect.centerx) * 0.05)
            else:
                self.rect.x -= min(2, (self.rect.centerx - self.jogador.rect.centerx) * 0.05)
        
        if self.rect.top > ALTURA:
            self.kill()

        self.atirar()
        self.lancar_missil()

    def lancar_missil(self):
        now = pygame.time.get_ticks()
        if now - self.last_missil > self.missil_delay and self.jogador.alive():
            self.last_missil = now
            missil = MissilInimigo(self.rect.centerx, self.rect.bottom, IMAGEM_MISSIL_INIMIGO, self.jogador)
            self.all_sprites.add(missil)
            self.projeteis_inimigos.add(missil)
            if SOM_MISSIL:
                SOM_MISSIL.play()

class InimigoTerrestre(pygame.sprite.Sprite):
    def __init__(self, nivel):
        super().__init__()
        self.image_original = IMAGEM_INIMIGO_TERRESTRE
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(
            center=(random.randint(50, LARGURA - 50), ALTURA - 40)
        )
        self.velocidade_x = random.uniform(0.5, 1.5) + (nivel * 0.1)
        self.vida = 2 + (nivel // 3)
        self.direcao = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.velocidade_x * self.direcao
        if self.rect.left < 0 or self.rect.right > LARGURA:
            self.direcao *= -1
        
        # Vira a imagem
        if self.direcao < 0:
            self.image = pygame.transform.flip(self.image_original, True, False)
        else:
            self.image = self.image_original

class Boss(pygame.sprite.Sprite):
    def __init__(self, all_sprites, projeteis_inimigos, nivel):
        super().__init__()
        self.image_original = IMAGEM_BOSS
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(LARGURA // 2, 100))
        self.vida = 20 + (nivel * 5)
        self.vida_maxima = self.vida
        self.velocidade_x = 3
        self.direcao = 1
        self.all_sprites = all_sprites
        self.projeteis_inimigos = projeteis_inimigos
        self.shoot_delay = 500  # Meio segundo entre tiros
        self.missil_delay = 3000  # 3 segundos entre mísseis
        self.last_shot = pygame.time.get_ticks()
        self.last_missil = pygame.time.get_ticks()
        self.nivel = nivel

    def update(self):
        # Movimento lateral
        self.rect.x += self.velocidade_x * self.direcao
        if self.rect.left < 0 or self.rect.right > LARGURA:
            self.direcao *= -1
            
        self.atirar()
        self.lancar_misseis()

    def atirar(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # Dispara vários projéteis
            for offset in [-40, -20, 0, 20, 40]:
                proj = ProjetilInimigo(self.rect.centerx + offset, self.rect.bottom, IMAGEM_PROJETIL_INIMIGO, 2)
                self.all_sprites.add(proj)
                self.projeteis_inimigos.add(proj)
            if SOM_TIRO:
                SOM_TIRO.play()

    def lancar_misseis(self):
        now = pygame.time.get_ticks()
        if now - self.last_missil > self.missil_delay:
            self.last_missil = now
            # Lança mísseis para ambos os lados
            for direcao in [-1, 1]:
                missil = ProjetilInimigo(self.rect.centerx, self.rect.bottom, IMAGEM_MISSIL_INIMIGO, 3)
                missil.velocidade = -6
                self.all_sprites.add(missil)
                self.projeteis_inimigos.add(missil)
            if SOM_MISSIL:
                SOM_MISSIL.play()

    def draw_vida(self, superficie):
        # Desenha a barra de vida do boss
        bar_width = 200
        bar_height = 20
        x = LARGURA // 2 - bar_width // 2
        y = 10
        
        # Fundo da barra
        pygame.draw.rect(superficie, CINZA, (x, y, bar_width, bar_height))
        # Vida atual
        vida_width = int((self.vida / self.vida_maxima) * bar_width)
        pygame.draw.rect(superficie, VERDE, (x, y, vida_width, bar_height))
        # Borda
        pygame.draw.rect(superficie, BRANCO, (x, y, bar_width, bar_height), 2)
        
        # Texto
        fonte = pygame.font.SysFont(None, 24)
        texto = fonte.render(f"BOSS: {self.vida}/{self.vida_maxima}", True, BRANCO)
        superficie.blit(texto, (x + bar_width // 2 - texto.get_width() // 2, y + bar_height + 5))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.tipo = random.choice(['vida', 'escudo', 'missil'])
        if self.tipo == 'vida':
            self.image = IMAGEM_POWERUP_VIDA
        elif self.tipo == 'escudo':
            self.image = IMAGEM_POWERUP_ESCUDO
        else:
            self.image = IMAGEM_POWERUP_MISSIL
        self.rect = self.image.get_rect(center=center)
        self.velocidade_y = 2

    def update(self):
        self.rect.y += self.velocidade_y
        if self.rect.top > ALTURA:
            self.kill()

# --- CLASSE PRINCIPAL DO JOGO ---
class Jogo:
    def __init__(self):
        self.rodando = True
        self.game_over = False
        self.fonte = pygame.font.SysFont(None, 36)
        
        # Fundo com rolagem
        self.bg_y1 = 0
        self.bg_y2 = -ALTURA
        self.bg_velocidade = 2

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.inimigos_aereos = pygame.sprite.Group()
        self.inimigos_terrestres = pygame.sprite.Group()
        self.projeteis_jogador = pygame.sprite.Group()
        self.projeteis_inimigos = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.misseis_jogador = pygame.sprite.Group()
        self.misseis_inimigos = pygame.sprite.Group()
        
        self.jogador = Jogador()
        self.all_sprites.add(self.jogador)
        
        # Variáveis de jogo
        self.tempo_inimigo = 0
        self.nivel = 1
        self.inimigos_derrotados = 0
        self.inimigos_para_proximo_nivel = 10
        self.boss = None
        
        # Inicia a música de fundo
        try:
            pygame.mixer.music.play(-1)  # -1 para repetir indefinidamente
        except:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.rodando = False
                if event.key == pygame.K_w and not self.game_over:
                    self.atirar()
                if event.key == pygame.K_e and not self.game_over and self.jogador.misseis > 0:
                    self.lancar_missil()
                if event.key == pygame.K_SPACE and not self.game_over:
                    if self.jogador.turbo_energia > 20:
                        self.jogador.turbo_ativo = not self.jogador.turbo_ativo
                if event.key == pygame.K_r and self.game_over:
                    self.reiniciar()

    def reiniciar(self):
        self.__init__()

    def atirar(self):
        if self.jogador.municao > 0:
            if self.jogador.turbo_ativo:
                p1 = Projetil(self.jogador.rect.centerx, self.jogador.rect.top, IMAGEM_PROJETIL_JOGADOR)
                p2 = Projetil(self.jogador.rect.centerx - 20, self.jogador.rect.centery, IMAGEM_PROJETIL_JOGADOR)
                p3 = Projetil(self.jogador.rect.centerx + 20, self.jogador.rect.centery, IMAGEM_PROJETIL_JOGADOR)
                self.all_sprites.add(p1, p2, p3)
                self.projeteis_jogador.add(p1, p2, p3)
                self.jogador.municao -= 2
            else:
                proj = Projetil(self.jogador.rect.centerx, self.jogador.rect.top, IMAGEM_PROJETIL_JOGADOR)
                self.all_sprites.add(proj)
                self.projeteis_jogador.add(proj)
                self.jogador.municao -= 1
                
            if SOM_TIRO:
                SOM_TIRO.play()

    def lancar_missil(self):
        if self.jogador.misseis > 0:
            # Encontrar o inimigo mais próximo
            alvo = None
            menor_distancia = float('inf')
            
            for inimigo in self.inimigos_aereos:
                dist = math.hypot(inimigo.rect.centerx - self.jogador.rect.centerx, 
                                 inimigo.rect.centery - self.jogador.rect.centery)
                if dist < menor_distancia:
                    menor_distancia = dist
                    alvo = inimigo
            
            for inimigo in self.inimigos_terrestres:
                dist = math.hypot(inimigo.rect.centerx - self.jogador.rect.centerx, 
                                 inimigo.rect.centery - self.jogador.rect.centery)
                if dist < menor_distancia:
                    menor_distancia = dist
                    alvo = inimigo
            
            if self.boss and self.boss.alive():
                dist = math.hypot(self.boss.rect.centerx - self.jogador.rect.centerx, 
                                 self.boss.rect.centery - self.jogador.rect.centery)
                if dist < menor_distancia:
                    alvo = self.boss
            
            missil = Missil(self.jogador.rect.centerx, self.jogador.rect.top, IMAGEM_MISSIL_JOGADOR, alvo)
            self.all_sprites.add(missil)
            self.misseis_jogador.add(missil)
            self.jogador.misseis -= 1
            
            if SOM_MISSIL:
                SOM_MISSIL.play()

    def spawn_inimigos(self):
        self.tempo_inimigo += 1
        
        # Ajusta a velocidade do background baseado no nível
        self.bg_velocidade = 2 + (self.nivel * 0.2)
        
        # Inimigos aéreos comuns
        if self.tempo_inimigo % (max(40, 120 - self.nivel * 8)) == 0:
            inimigo = InimigoAereo(self.all_sprites, self.projeteis_inimigos, self.nivel)
            self.all_sprites.add(inimigo)
            self.inimigos_aereos.add(inimigo)
        
        # Inimigos caçadores (a partir do nível 3)
        if self.nivel >= 3 and self.tempo_inimigo % (max(60, 180 - self.nivel * 10)) == 0:
            inimigo = InimigoCacador(self.all_sprites, self.projeteis_inimigos, self.jogador, self.nivel)
            self.all_sprites.add(inimigo)
            self.inimigos_aereos.add(inimigo)
        
        # Inimigos terrestres
        if self.tempo_inimigo % (max(80, 200 - self.nivel * 12)) == 0 and len(self.inimigos_terrestres) < (3 + self.nivel // 2):
            inimigo = InimigoTerrestre(self.nivel)
            self.all_sprites.add(inimigo)
            self.inimigos_terrestres.add(inimigo)
        
        # Boss a cada 5 níveis
        if self.nivel % 5 == 0 and not self.boss and self.inimigos_derrotados >= self.inimigos_para_proximo_nivel - 5:
            self.boss = Boss(self.all_sprites, self.projeteis_inimigos, self.nivel)
            self.all_sprites.add(self.boss)

    def update(self):
        if self.game_over:
            return
        
        self.all_sprites.update()
        self.spawn_inimigos()
        
        # Colisões: Projéteis do jogador vs Inimigos Aéreos
        atingidos = pygame.sprite.groupcollide(self.inimigos_aereos, self.projeteis_jogador, False, True)
        for inimigo, projeteis in atingidos.items():
            dano_total = sum(proj.dano for proj in projeteis)
            inimigo.vida -= dano_total
            if inimigo.vida <= 0:
                if SOM_EXPLOSAO:
                    SOM_EXPLOSAO.play()
                self.jogador.pontuacao += 100 * self.nivel
                self.inimigos_derrotados += 1
                if random.random() > 0.7:  # 30% de chance de dropar powerup
                    powerup = PowerUp(inimigo.rect.center)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
                inimigo.kill()

        # Colisões: Mísseis do jogador vs Inimigos
        for missil in self.misseis_jogador:
            # Verifica colisão com inimigos aéreos
            atingidos = pygame.sprite.spritecollide(missil, self.inimigos_aereos, False)
            for inimigo in atingidos:
                inimigo.vida -= missil.dano
                if inimigo.vida <= 0:
                    if SOM_EXPLOSAO:
                        SOM_EXPLOSAO.play()
                    self.jogador.pontuacao += 150 * self.nivel
                    self.inimigos_derrotados += 1
                    if random.random() > 0.7:  # 30% de chance de dropar powerup
                        powerup = PowerUp(inimigo.rect.center)
                        self.all_sprites.add(powerup)
                        self.powerups.add(powerup)
                    inimigo.kill()
                missil.kill()
                break
                
            # Verifica colisão com inimigos terrestres
            atingidos = pygame.sprite.spritecollide(missil, self.inimigos_terrestres, False)
            for inimigo in atingidos:
                inimigo.vida -= missil.dano
                if inimigo.vida <= 0:
                    if SOM_EXPLOSAO:
                        SOM_EXPLOSAO.play()
                    self.jogador.pontuacao += 200 * self.nivel
                    self.inimigos_derrotados += 1
                    if random.random() > 0.7:  # 30% de chance de dropar powerup
                        powerup = PowerUp(inimigo.rect.center)
                        self.all_sprites.add(powerup)
                        self.powerups.add(powerup)
                    inimigo.kill()
                missil.kill()
                break
                
            # Verifica colisão com boss
            if self.boss and missil.rect.colliderect(self.boss.rect):
                self.boss.vida -= missil.dano
                if self.boss.vida <= 0:
                    if SOM_EXPLOSAO:
                        SOM_EXPLOSAO.play()
                    self.jogador.pontuacao += 1000 * self.nivel
                    self.inimigos_derrotados += 10
                    self.boss.kill()
                    self.boss = None
                missil.kill()

        # Colisões: Projéteis do jogador vs Inimigos Terrestres
        atingidos = pygame.sprite.groupcollide(self.inimigos_terrestres, self.projeteis_jogador, False, True)
        for inimigo, projeteis in atingidos.items():
            dano_total = sum(proj.dano for proj in projeteis)
            inimigo.vida -= dano_total
            if inimigo.vida <= 0:
                if SOM_EXPLOSAO:
                    SOM_EXPLOSAO.play()
                self.jogador.pontuacao += 200 * self.nivel
                self.inimigos_derrotados += 1
                if random.random() > 0.7:  # 30% de chance de dropar powerup
                    powerup = PowerUp(inimigo.rect.center)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
                inimigo.kill()

        # Colisões: Projéteis do jogador vs Boss
        if self.boss:
            atingidos = pygame.sprite.spritecollide(self.boss, self.projeteis_jogador, True)
            for proj in atingidos:
                self.boss.vida -= proj.dano
                if self.boss.vida <= 0:
                    if SOM_EXPLOSAO:
                        SOM_EXPLOSAO.play()
                    self.jogador.pontuacao += 1000 * self.nivel
                    self.inimigos_derrotados += 10
                    self.boss.kill()
                    self.boss = None

        # Colisões: Projéteis inimigos vs Jogador
        if self.jogador.invencivel_timer == 0:
            if self.jogador.escudo_ativo:
                # Com escudo, apenas destrói os projéteis
                atingido = pygame.sprite.spritecollide(self.jogador, self.projeteis_inimigos, True)
                if atingido and SOM_DANO:
                    SOM_DANO.play()
            else:
                # Sem escudo, toma dano
                atingido = pygame.sprite.spritecollide(self.jogador, self.projeteis_inimigos, True)
                if atingido:
                    if SOM_DANO:
                        SOM_DANO.play()
                    self.jogador.vidas -= 1
                    self.jogador.invencivel_timer = 120  # 2 segundos de invencibilidade
                    if self.jogador.vidas <= 0:
                        self.game_over = True

        # Colisões: Mísseis inimigos vs Jogador
        if self.jogador.invencivel_timer == 0:
            if self.jogador.escudo_ativo:
                # Com escudo, apenas destrói os mísseis
                atingido = pygame.sprite.spritecollide(self.jogador, self.misseis_inimigos, True)
                if atingido and SOM_DANO:
                    SOM_DANO.play()
            else:
                # Sem escudo, toma dano
                atingido = pygame.sprite.spritecollide(self.jogador, self.misseis_inimigos, True)
                if atingido:
                    if SOM_DANO:
                        SOM_DANO.play()
                    self.jogador.vidas -= 2  # Mísseis causam mais dano
                    self.jogador.invencivel_timer = 120  # 2 segundos de invencibilidade
                    if self.jogador.vidas <= 0:
                        self.game_over = True

        # Colisões: Jogador vs PowerUps
        coletados = pygame.sprite.spritecollide(self.jogador, self.powerups, True)
        for powerup in coletados:
            if powerup.tipo == 'vida':
                self.jogador.vidas += 1
            elif powerup.tipo == 'escudo':
                self.jogador.ativar_escudo()
            elif powerup.tipo == 'missil':
                self.jogador.misseis += 3
            if SOM_POWERUP:
                SOM_POWERUP.play()

        # Colisões: Jogador vs Inimigos
        if self.jogador.invencivel_timer == 0:
            if self.jogador.escudo_ativo:
                # Com escudo, apenas destrói os inimigos
                inimigos_atingidos = pygame.sprite.spritecollide(self.jogador, self.inimigos_aereos, True)
                inimigos_atingidos += pygame.sprite.spritecollide(self.jogador, self.inimigos_terrestres, True)
                for inimigo in inimigos_atingidos:
                    if SOM_EXPLOSAO:
                        SOM_EXPLOSAO.play()
                    self.jogador.pontuacao += 100 * self.nivel
                    self.inimigos_derrotados += 1
            else:
                # Sem escudo, morre
                inimigos_atingidos = pygame.sprite.spritecollide(self.jogador, self.inimigos_aereos, True)
                inimigos_atingidos += pygame.sprite.spritecollide(self.jogador, self.inimigos_terrestres, True)
                if inimigos_atingidos:
                    if SOM_DANO:
                        SOM_DANO.play()
                    self.jogador.vidas -= 1
                    self.jogador.invencivel_timer = 120
                    if self.jogador.vidas <= 0:
                        self.game_over = True

        # Avança para o próximo nível
        if self.inimigos_derrotados >= self.inimigos_para_proximo_nivel and self.nivel < 20:
            self.nivel += 1
            self.inimigos_derrotados = 0
            self.inimigos_para_proximo_nivel = 10 + (self.nivel * 2)
            if SOM_LEVEL_UP:
                SOM_LEVEL_UP.play()
            
            # Limpa os inimigos restantes
            for inimigo in self.inimigos_aereos:
                inimigo.kill()
            for inimigo in self.inimigos_terrestres:
                inimigo.kill()
            if self.boss:
                self.boss.kill()
                self.boss = None

    def draw(self):
        # Desenha o fundo com rolagem
        self.bg_y1 += self.bg_velocidade
        self.bg_y2 += self.bg_velocidade
        
        if self.bg_y1 > ALTURA:
            self.bg_y1 = self.bg_y2 - ALTURA
        if self.bg_y2 > ALTURA:
            self.bg_y2 = self.bg_y1 - ALTURA
            
        # Usa a imagem de fundo padrão
        tela.blit(IMAGEM_FUNDO, (0, self.bg_y1))
        tela.blit(IMAGEM_FUNDO, (0, self.bg_y2))
        
        # Desenha todos os sprites
        self.all_sprites.draw(tela)
        
        # Desenha o jogador por último para garantir que fique sobre os outros elementos
        self.jogador.draw(tela)
        
        # Desenha a barra de vida do boss se existir
        if self.boss and self.boss.alive():
            self.boss.draw_vida(tela)
        
        # Desenha HUD
        self.desenhar_hud()
        
        # Tela de Game Over
        if self.game_over:
            self.desenhar_game_over()
            
        # Tela de vitória (completou todos os 20 níveis)
        if self.nivel > 20:
            self.desenhar_vitoria()

    def desenhar_hud(self):
        # Fundo semi-transparente para o HUD
        hud_surface = pygame.Surface((LARGURA, 60), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 128))
        tela.blit(hud_surface, (0, 0))
        
        # Vidas
        for i in range(self.jogador.vidas):
            tela.blit(IMAGEM_POWERUP_VIDA, (10 + i * 35, 15))
        
        # Pontuação
        texto_pontuacao = self.fonte.render(f"Pontos: {self.jogador.pontuacao}", True, BRANCO)
        tela.blit(texto_pontuacao, (LARGURA // 2 - texto_pontuacao.get_width() // 2, 20))
        
        # Nível
        texto_nivel = self.fonte.render(f"Nível: {self.nivel}/20", True, BRANCO)
        tela.blit(texto_nivel, (LARGURA - texto_nivel.get_width() - 10, 20))
        
        # Munição
        texto_municao = self.fonte.render(f"Munição: {self.jogador.municao}/100", True, BRANCO)
        tela.blit(texto_municao, (10, ALTURA - 30))
        
        # Mísseis
        for i in range(min(self.jogador.misseis, 10)):
            tela.blit(IMAGEM_POWERUP_MISSIL, (LARGURA - 40 - i * 35, ALTURA - 40))
        
        # Turbo
        pygame.draw.rect(tela, CINZA, (10, ALTURA - 70, 150, 20))
        if self.jogador.turbo_energia > 0:
            cor_turbo = VERDE if self.jogador.turbo_ativo else AMARELO
            pygame.draw.rect(tela, cor_turbo, (10, ALTURA - 70, (self.jogador.turbo_energia / 100) * 150, 20))
        pygame.draw.rect(tela, BRANCO, (10, ALTURA - 70, 150, 20), 2)
        texto_turbo = self.fonte.render("Turbo", True, BRANCO)
        tela.blit(texto_turbo, (165, ALTURA - 70))
        
        # Escudo
        if self.jogador.escudo_ativo:
            tempo_restante = self.jogador.escudo_timer // 60
            texto_escudo = self.fonte.render(f"Escudo: {tempo_restante}s", True, CIANO)
            tela.blit(texto_escudo, (LARGURA - 150, ALTURA - 70))
        
        # Progresso do nível
        texto_progresso = self.fonte.render(f"Inimigos: {self.inimigos_derrotados}/{self.inimigos_para_proximo_nivel}", True, BRANCO)
        tela.blit(texto_progresso, (LARGURA // 2 - texto_progresso.get_width() // 2, ALTURA - 30))

    def desenhar_game_over(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        
        fonte_game_over = pygame.font.SysFont(None, 72)
        texto_game_over = fonte_game_over.render("GAME OVER", True, VERMELHO)
        tela.blit(texto_game_over, (LARGURA // 2 - texto_game_over.get_width() // 2, ALTURA // 2 - 50))
        
        fonte_reiniciar = pygame.font.SysFont(None, 36)
        texto_reiniciar = fonte_reiniciar.render("Pressione R para reiniciar", True, BRANCO)
        tela.blit(texto_reiniciar, (LARGURA // 2 - texto_reiniciar.get_width() // 2, ALTURA // 2 + 20))
        
        texto_pontuacao = fonte_reiniciar.render(f"Pontuação final: {self.jogador.pontuacao}", True, BRANCO)
        tela.blit(texto_pontuacao, (LARGURA // 2 - texto_pontuacao.get_width() // 2, ALTURA // 2 + 60))
        
        texto_nivel = fonte_reiniciar.render(f"Nível alcançado: {self.nivel}", True, BRANCO)
        tela.blit(texto_nivel, (LARGURA // 2 - texto_nivel.get_width() // 2, ALTURA // 2 + 100))

    def desenhar_vitoria(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        
        fonte_vitoria = pygame.font.SysFont(None, 72)
        texto_vitoria = fonte_vitoria.render("VITÓRIA!", True, VERDE)
        tela.blit(texto_vitoria, (LARGURA // 2 - texto_vitoria.get_width() // 2, ALTURA // 2 - 50))
        
        fonte_reiniciar = pygame.font.SysFont(None, 36)
        texto_reiniciar = fonte_reiniciar.render("Pressione R para jogar novamente", True, BRANCO)
        tela.blit(texto_reiniciar, (LARGURA // 2 - texto_reiniciar.get_width() // 2, ALTURA // 2 + 20))
        
        texto_pontuacao = fonte_reiniciar.render(f"Pontuação final: {self.jogador.pontuacao}", True, BRANCO)
        tela.blit(texto_pontuacao, (LARGURA // 2 - texto_pontuacao.get_width() // 2, ALTURA // 2 + 60))

    def run(self):
        while self.rodando:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

# --- EXECUÇÃO DO JOGO ---
if __name__ == "__main__":
    jogo = Jogo()
    jogo.run()
    pygame.quit()
    sys.exit()