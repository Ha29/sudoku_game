import pygame, time
import SudokuGame

size = width, height = 500, 500
pygame.init()
screen = pygame.display.set_mode(size)
def blit_game_piece(position, text, color=(0, 0, 0)):
    """
    Blits game piece onto board, call after creating the board
    :param position: position of the screen
    :param text: game piece
    :param color: rgb value represented in a tuple of 3 elements
    :return:
    """
    font = pygame.font.SysFont(None, 40)
    img = font.render(text, True, color)
    screen.blit(img, position)


def draw_board():
    """
    Draws 9 by 9 board
    :return: None
    """
    for row in range(0, 9):
        for col in range(0, 9):
            pygame.draw.rect(screen, [0, 0, 0], [50 * row, 50 * col, 50, 50])
            pygame.draw.rect(screen, [255, 255, 255], [50 * row + 1, 50 * col + 1, 48, 48])

def create_buttons():
    new_game_button = pygame.Rect(0, 462, 100, 26)
    # pygame.draw.rect(screen, [255, 0, 0], [1, 463, 98, 24])
    solve_button = pygame.Rect(120, 462, 100, 25)
    # pygame.draw.rect(screen, [255, 0, 0], [121, 463, 98, 24])
    return new_game_button, solve_button

def main():
    screen.fill((255, 255, 255))
    blit_game_piece((20, 460), 'Computing board...', (0, 0, 0))
    pygame.display.update()
    # start = time.time()
    game = SudokuGame.SudokuGame()
    screen.fill((255, 255, 255))
    draw_board()
    new_game_button , solve_button = create_buttons()
    for r in range(9):
        for c in range(9):
            if game.given_pieces[c][r]:
                blit_game_piece((50 * r + 5, 50 * c + 5), str(game.board[c][r]), (100, 200, 100))
            elif game.board[c][r] != 0:
                blit_game_piece((50 * r + 5, 50 * c + 5), str(game.board[c][r]))
    pygame.draw.rect(screen, [255, 0, 0], new_game_button)
    pygame.draw.rect(screen, [255, 255, 255], [1, 463, 98, 24])
    pygame.draw.rect(screen, [255, 0, 0], solve_button)
    pygame.draw.rect(screen, [255, 255, 255], [121, 463, 98, 24])
    pygame.display.update()
    while True:
        while (not game.game_over):
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    running = False
                    pygame.quit()
            screen.fill((255, 255, 255))
            draw_board()
            game.solve_picking_min_constraints()
            for r in range(9):
                for c in range(9):
                    if game.given_pieces[c][r]:
                        blit_game_piece((50 * r + 18, 50 * c + 10), str(game.board[c][r]), (100, 200, 100))
                    elif game.board[c][r] != 0:
                        blit_game_piece((50 * r + 18, 50 * c + 10), str(game.board[c][r]))
            pygame.draw.rect(screen, [255, 0, 0], new_game_button)
            pygame.draw.rect(screen, [255, 0, 0], solve_button)
            pygame.display.update()
            print("len game_states: {}".format(len(game.game_states)))
        # end = time.time()
        # print("Solved in {} seconds".format(end - start))
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                running = False
                pygame.quit()

if __name__ == '__main__':
    main()



