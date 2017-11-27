# Games4Cinema - Minesweeper
#### Cinema 4D Python Script

Play Minesweeper on Cinema 4D

Please visit: https://safina3d.blogspot.com


![Minesweeper Default](https://2.bp.blogspot.com/-4XRDPBu7wX0/WhwIyitZi-I/AAAAAAAAB90/0SmgPvatbrE_It5lzJDC-UoN6c7gFJSlACKgBGAs/s1600/minesweeper.png)
![Minesweeper Game Over](https://3.bp.blogspot.com/-RXk8Jo73Fck/WhwIyrwhZqI/AAAAAAAAB90/RxUWiaBPiAgFFrFHbiSfm0rfJcPaJ0RegCKgBGAs/s1600/minesweeper2.png)


### Installation:

- Clone the project or download the zip file and extract it into the Maxon scripts directory.
  - Windows: C:\Program Files\MAXON\CINEMA 4D R18\library\scripts\
  - MacOS: /Applications/MAXON/CINEMA 4D R1<version>/library/scripts/

- Restart Cinema 4D

Go to Cinema 4D Menu:
  - Script >> User scripts >> minesweeper >> minesweeper

You can change the size of the grid and difficulty by changing the values passed to the `MinesweeperGui` object.
The args are: Rows, Columns, Difficulty[EASY|Medium|Difficult]
```
if __name__ == '__main__':
    dlg = MinesweeperGui(15, 10, Level.EASY)
    dlg.Open(dlgtype=c4d.DLG_TYPE_ASYNC)
```
