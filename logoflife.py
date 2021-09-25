#----------------------------------------------------------------#
from money import Money
from sex import Sex

import sys
import locale
#----------------------------------------------------------------#

if __name__ == '__main__':

    money = Money("money.txt")
    money.process()

    command = input("command:").lower()

    if (command == 's') or (command == 'ы') :
        sex = Sex("history+.txt")
        sex.process()
    