import win32file

class WinOps():

    def __init__(self,drive_letter: str = "F") -> None:
        self.drive_letter = drive_letter
    
    #Check if drive letter exists
    def drive_letter_exists(self) -> bool:

        #ZYXWVUTSRQPONMLKJIHGFEDCBA  
        #00000000000000000001001100
        #Each bit corresponds to a letter, -65 is to offset first letter A(65)
        #i.e if checking letter F then...
        #F(70)-65=5 00111100 >> 5  would be 00000001 bitwise AND (&) would be 1 which means F exists
        return win32file.GetLogicalDrives() >> (ord(self.drive_letter) - 65) & 1 == 1
