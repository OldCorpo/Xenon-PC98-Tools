ＸＥＮＯＮ ～夢幻の肢体～

XENON \~The limbs of phantasmagoria\~ : Translation project

### Advancement

    Translation : Roughly the 98.5% ~ 100% is translated (but may need style revisions and other things)
    Insertion   : Latest patch covers 99.8% of the translation into the game files, it should cover all storylines

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
        Xanderzone - Testing, Support
           Fuzion - Testing, Support
              dvo - Proofreading
          Asterix - Some proofreading

          ~ additional translation ~
         HempTL - English translation

       ~ based on the original work of ~
                  siriusxiv
                 esperknight
                 MulletDonkey
                   OmBadai
    

