import SudokuGame, time, sys

game = SudokuGame.SudokuGame()
start = time.time()
game.solve()
end = time.time()
print("size of states: {}".format(sys.getsizeof(game.game_states)))
print(end - start)

