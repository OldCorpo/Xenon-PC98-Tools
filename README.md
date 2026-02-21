ＸＥＮＯＮ ～夢幻の肢体～

XENON \~The limbs of phantasmagoria\~ : Translation project

### Advancement

    Translation : Roughly the 98.5% ~ 100% is translated (but may need style revisions and other things)
    Insertion   : Between 80% and 90% of the translation is being inserted into the game files

### Workflow

1. Update translation/_script-japanese.txt from Xenon-PC98-Translation (if needed)
```
cp script-japanese-with-translation.txt translation/_script-japanese.txt
```
2. Use xenreplacer.py from the tools dir, to insert translations into the files. Example:
```
xenreplacer.py ../scripts_cc/S0104.U.CC   
```
3. Run 2_compress.bat from the tools dir, to prepare the files to be added to the image.
```
2_compress.bat
```
4. Run 3_insert.bat from the tools dir, to open the hdi inserter tool.
```
3_insert.bat
```
    This will bring up a directory and run DiskExplorer.
    Just click OK to the selection (Anex86 HDD) and drag and drop all the CC files from scripts_build into the window.
5. Run on your favorite emulator or, use 4a_play_eng.bat and Neko Project will automatically run the game
```
4a_play_eng.bat
```
6. An option to use the original Japanese version for comparison using 4b_play_jap.bat is available.
