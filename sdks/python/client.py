#!/usr/bin/python
import sys
import json
import socket
import random

def sort_moves(valids,moves,avoid):
  #just sorts the already valid moves into the sublists.
  for valid in valids:
    if valid == [0,0] or valid == [0,7] or valid == [7,7] or valid == [7,0]:
      moves[0].append(valid)
    elif valid in avoid:
      if board[0][0] == player and (valid == [1,1] or valid == [0,1] or valid == [1,0]):
          moves[2].append(valid)
      if board[7][0] == player and (valid == [6,1] or valid == [7,1] or valid == [6,0]):
        moves[2].append(valid)
      if board[7][7] == player and (valid == [6,7] or valid == [7,6] or valid == [6,6]):
        moves[2].append(valid)
      if board[0][7] == player and (valid == [1,6] or valid == [1,7] or valid == [0,6]):
        moves[2].append(valid)
      else:
        moves[4].append(valid)
    elif 6 in valid or 1 in valid:
      moves[3].append(valid)
    elif 0 in valid or 7 in valid:
      moves[1].append(valid)
    else:
      moves[2].append(valid)     
  return moves         

def return_highest_priority_move(moves):
  print(moves)
  #checks if highest priority list is empty, returns a move if not.
  if len(moves[0]) > 0:
    return moves[0][0]
  elif len(moves[2]) > 0:
    return random.choice(moves[2])
  elif len(moves[1]) > 0:
    return random.choice(moves[1])
  elif len(moves[3]) > 0:
    return random.choice(moves[3])
  elif len(moves[4]) > 0:
    return random.choice(moves[4])

def find_valid_moves(row,col,combos):
    #Moves further in the possible directions in order to determine if the move is viable 
    moves = []
    secondItem = combos[0][1]
    firstItem = combos[0][0]
    while len(combos) > 0:
      if (row + firstItem >= 0 and row + firstItem <= 7) and (col + secondItem >= 0 and col + secondItem <= 7):
        if board[row + firstItem][col+secondItem] == 0:
          moves.append([row+firstItem,col+secondItem])
          combos.pop(0)
          try:
            firstItem = combos[0][0]
            secondItem = combos[0][1]
          except:
            break
          continue
        elif board[row+firstItem][col+secondItem] == player:
          #not an option anymore. move on to the next combo and reset the items
          combos.pop(0)
          try:
            firstItem = combos[0][0]
            secondItem = combos[0][1]
          except:
            break
        else:
          firstItem += combos[0][0]
          secondItem += combos[0][1]
          
      else: 
        combos.pop(0)
        try:
          firstItem = combos[0][0]
          secondItem = combos[0][1]
        except:
          break
    return moves

def get_adjacent(row, col):
  #applies all direction possibilities to the current chip. Returns the possible directions.
  combos = [[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1]]
  validCombos = []
  n = 0
  while n < 8:
        secondItem = combos[n][1]
        firstItem = combos[n][0]  
        if (row+firstItem <= 7 and row+firstItem >= 0) and (col+secondItem <= 7 and col+secondItem >= 0):
          if board[row+firstItem][col+secondItem] != player and board[row+firstItem][col+secondItem] != 0:
            validCombos.append(combos[n])  
        n+=1
  return validCombos
          

def get_move(player, board):
  placesToAvoid = [[1,1],[1,0],[0,1],[1,7],[7,1],[6,6],[6,7],[7,6],[0,6],[1,6],[6,0],[6,1]]
  moves = [[],[],[],[],[]]
  row = 0
  while row <= 7:
    col = 0
    while col <=7:
      if board[row][col] == player:
        potentialDirections = get_adjacent(row, col)
        if potentialDirections != []:
          valid = find_valid_moves(row, col,potentialDirections)
          if valid != []:
            finalmoves = sort_moves(valid,moves,placesToAvoid)   
      col +=1     
    row += 1
  return return_highest_priority_move(finalmoves)

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response), "\n")
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    while True:
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      #print(player, maxTurnTime, board)

      move = get_move(player, board)
      response = prepare_response(move)
      sock.sendall(response)
  finally:
    sock.close()
