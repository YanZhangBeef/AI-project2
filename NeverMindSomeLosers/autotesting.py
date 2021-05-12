"""
#this file should be placed in the outtest folder
import os
import re
f = open("result.txt",'w')
f.close()

for i in range(100):

    os.system('python -m referee NeverMindSomeLosers/player NeverMindSomeLosers/randy')

file = open('result.txt')
win = 0
lose = 0
draw = 0
lines = file.readlines()
for l in lines:
    if 'upper' in l:
        win += 1
    elif 'lower' in l:
        lose += 1
    else:
        draw +=1
total = win+lose+draw
print("win rate=" + str(win / total) +"  lose rate =" + str(lose/total) +"  out of" +str(total))
"""