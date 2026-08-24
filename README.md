ＸＥＮＯＮ ～夢幻の肢体～

XENON \~The limbs of phantasmagoria\~ : Translation project

### Advancement

    Translation : 100% of the story is translated and proofchecked.
    Insertion   : 100% of the story is inserted into the game. With the exception of the main load menu
                       and the omake, as they are harcoded into the program (executable) and I didn't 
                       found a reliable way to edit those.

### Workflow

1. Update translation/_script-japanese.txt from Xenon-PC98-Translation (if needed)
```
./copy_translation.sh
```
2. Use merger.sh from the tools dir, to insert translations into the files. Example:
```
./merger.sh
```
3. Run compress.sh or 2_compress.bat from the tools dir, to prepare the files to be added to the image.
```
./compress.sh
```
4. Run insert.sh or 3_insert.bat from the tools dir, to open the hdi inserter tool.
```
./insert.sh
```
    This will bring up a directory and run DiskExplorer.
    Just click OK to the selection (Anex86 HDD) and drag and drop all the CC files from scripts_build into the window.
5. Test on your favorite emulator, Neko Project II is recommended to run the game



### Credits

    OldCorpo - Translation completion, Tools
 dvo - Proofreading and translation improvements
           Laukku - Some proofreading
          Asterix - Some proofreading
        Xanderzone - Testing, Support
           Fuzion - Testing, Support

       ~ based on the original work of ~
                    HempTL
                  siriusxiv
                 esperknight
                 MulletDonkey
                   OmBadai
    

